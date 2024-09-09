import argparse, bs4, time
from .. import CONNECT, INSERT, SELECT, DELETE, Keys
from ..utils import PATH, IncrementalBar, re
from ..twitter_likes_exporter import download_tweets

SITE = 'twitter'
REMOVE = '(/(photo|video)/\d+)|(media_tags)|(analytics)|(people)'

def initialize(url, query, limit=5, retry=0):

    content = DRIVER.get(f'https://{SITE}.com/{url}/likes')
    last_pass = ()

    while True:
        
        html = bs4.BeautifulSoup(content, 'lxml')
        try:
            target = html.find('section').contents[-1]
            hrefs = [
                (*href, SITE) for href in
                {
                    (re.sub(REMOVE, '', href.get('href')),) for href in 
                    target.findAll(href=re.compile('/.+/status/.+'))
                    } - query
                ]
            MYSQL.execute(INSERT[1], hrefs, many=1)
        except AttributeError: continue
        
        if not hrefs or hrefs == last_pass:
            if retry < limit: retry += 1
            else: break
        else: 
            retry = 0
        last_pass = hrefs
        
        for _ in range(2): DRIVER.find('//body', keys=Keys.PAGE_DOWN)
        time.sleep(2)
                
    MYSQL.commit()

def page_handler(hrefs):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:

        progress.next()
        content = DRIVER.get(f'https://{SITE}.com{href}')
        
        for _ in range(3):
            try:
                time.sleep(3)
                html = bs4.BeautifulSoup(content, 'lxml')
                target = html.find('article', {'data-testid': 'tweet'})
                images = target.findAll(src=re.compile('.+?format=.+'))
                images[0].get('src'); images[-1].get('src')
                artist = href.split('/')[1].lower()
                break

            except (IndexError, AttributeError, TypeError): 
                try:
                    html = bs4.BeautifulSoup(content, 'lxml')
                    images = html.findAll('video')
                    images[0].get('src'); images[-1].get('src')
                    artist = href.split('/')[1].lower()
                    break

                except (IndexError, AttributeError, TypeError): 
                    html = bs4.BeautifulSoup(content, 'lxml')
                    
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

            try: image = re.sub('(name)=.+', r'\1=large', image.get('src'))
            except: break; continue
            name = image.replace('?format=', '.').split('/')[-1]
            name = PATH / 'Images' / SITE / f'{artist} - {name.split("&")[0]}'

            MYSQL.execute(INSERT[5], (str(name), image, href, SITE))

        else: MYSQL.execute(DELETE[1], (href,), commit=1)
        
def main(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    # DRIVER = WEBDRIVER(headless=headless)
    query = set(MYSQL.execute(SELECT[7], (SITE,), fetch=1))
    
    downloader = download_tweets.TweetDownloader()
    records = downloader.retrieve_all_likes(query)
    MYSQL.execute(INSERT[5], records, many=1, commit=1)
    
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