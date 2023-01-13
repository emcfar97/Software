import time, argparse
from .. import CONNECT, INSERT, SELECT, DELETE, WEBDRIVER
from ..utils import PATH, IncrementalBar, bs4, re
from selenium.webdriver.common.keys import Keys

SITE = 'twitter'

def initialize(url, limit=3, retry=0):

    DRIVER.get(f'https://{SITE}.com/{url}/likes')

    while True:
        
        query = set(MYSQL.execute(SELECT[1], (SITE,), fetch=1))
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        try:
            target = html.find('section').contents[-1]
            hrefs = [
                (*href, SITE) for href in
                {
                    (re.sub('/photo/\d+', '', href.get('href')),) for href in 
                    target.findAll(href=re.compile('/.+/status/.+'))
                    } - query
                ]
            MYSQL.execute(INSERT[1], hrefs, many=1)
        except AttributeError: continue
        
        if not hrefs:
            if retry < limit: retry += 1
            else: break
        else: retry = 0
            
        for _ in range(3): 
            DRIVER.find('html', Keys.PAGE_DOWN, type_=6)
            time.sleep(2)
                
    MYSQL.commit()

def page_handler(hrefs):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:

        progress.next()
        DRIVER.get(f'https://{SITE}.com{href}')
        
        for _ in range(3):
            try:
                time.sleep(3)
                html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                target = html.find('article', {'data-testid': 'tweet'})
                images = target.findAll(src=re.compile('.+?format=.+'))
                images[0].get('src'); images[-1].get('src')
                artist = href.split('/')[1].lower()
                break

            except (IndexError, AttributeError, TypeError): 
                try:
                    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                    images = html.findAll('video')
                    images[0].get('src'); images[-1].get('src')
                    artist = href.split('/')[1].lower()
                    break

                except (IndexError, AttributeError, TypeError): 
                    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                    
                    if html.findAll(text='Hmm...this page doesn’t exist. Try searching for something else.'):
                    
                        MYSQL.execute(DELETE[1], (href,), commit=1)
                        continue
                    
                    elif html.findAll(text='This Tweet is from a suspended account. '):
                        MYSQL.execute(DELETE[2], (re.sub('(/.+/)\d+', r'\1', href),), commit=1)
                        continue
                    
                    # elif html.findAll(text='This Tweet is from a suspended account. '):
                    #     MYSQL.execute(DELETE[2], (re.sub('(/.+/)\d+', r'\1', href),), commit=1)
                    #     continue
        
        if not images: continue
        
        for image in images:

            image = re.sub('(name)=.+', r'\1=large', image.get('src'))
            name = image.replace('?format=', '.').split('/')[-1]
            name = PATH / 'Images' / SITE / f'{artist} - {name.split("&")[0]}'

            MYSQL.execute(INSERT[5], (str(name), image, href, SITE))

        else: MYSQL.execute(DELETE[1], (href,), commit=1)
        
def main(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT('desktop')
    DRIVER = WEBDRIVER(headless)
    
    if initial:
        url = DRIVER.login(SITE)
        initialize(url)
    page_handler(MYSQL.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='twitter', 
        )
    parser.add_argument(
        '-i', '--init', type=int,
        help='Initial argument (default 1)',
        default=1
        )
    parser.add_argument(
        '-he', '--head', type=bool,
        help='Headless argument (default True)',
        default=True
        )

    args = parser.parse_args()
    
    main(args.init, args.head)