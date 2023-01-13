import argparse
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import PATH, IncrementalBar, bs4, re

SITE = 'furaffinity'

def initialize(url, query=0):
    
    def next_page(pages):
        
        try: return pages.get('href')
        except AttributeError: return False

    if not query:
        query = set(MYSQL.execute(SELECT[1], (SITE,), fetch=1))
    DRIVER.get(f'https://www.{SITE}.net{url}')
    
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (*href, SITE) for href in {(target.get('href'),) for target in 
        html.findAll(href=re.compile('/view+'))} - query
        ]
    MYSQL.execute(INSERT[1], hrefs, many=1)
    next = next_page(html.find(class_='button standard right')) 
    if hrefs and next: initialize(next, query)

    MYSQL.commit()

def page_handler(hrefs):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        progress.next()
        DRIVER.get(f'https://www.{SITE}.net{href}')
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        
        if html.find(text=re.compile('not in our database.+')):
            
            MYSQL.execute('DELETE FROM favorites WHERE href=%s', (href,), commit=1)
            continue      
                        
        image = html.find('a', href=re.compile('//d.+')).get('href')
        name = re.sub('.+\.(.+)_(.+)', r'\1 - \2', image)
        name = PATH / 'Images' / SITE / name
        
        if name.suffix == ' ':
            artist = html.find(
                'a', href=re.compile('/user/+(?!chairekakia)'), id=False
                ).get('href').split('/')[2]
            name = f'{artist} - {image.split("/")[-1]}png'
            # continue
        name = PATH / 'Images' / SITE / name

        MYSQL.execute(UPDATE[2], (str(name), image, href), commit=1)
    
    print()

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
        prog='furaffinity', 
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