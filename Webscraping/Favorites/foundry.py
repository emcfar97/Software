import argparse, bs4, requests
import selenium.common.exceptions as exceptions
from .. import CONNECT, INSERT, SELECT, UPDATE, DELETE, WEBDRIVER, get_credentials
from ..utils import PATH, HEADERS, IncrementalBar, re, save_image

SITE = 'foundry'

def get_session():
    
    sess = requests.Session()
    sess.headers.update(HEADERS)
    
    payload = {
        'username': get_credentials(SITE, 'username'),
        'password': get_credentials(SITE, 'password'),
        'YII_CSRF_TOKEN': get_credentials(SITE, 'csrf_token'),
        'dest': 'www.hentai-foundry.com',
        }
    
    response = sess.get('https://www.hentai-foundry.com/site/login')
    cookies = dict(response.cookies)
    response = sess.post(
        'https://www.hentai-foundry.com/site/login', 
        data=payload, cookies=cookies
        )
    
    return sess

def initialize(url, query):
    
    def next_page(pages):
        
        try:
            if 'hidden' in pages.get('class'): return
            else: return pages.contents[0].get('href')
        except AttributeError: 
            return 

    content = DRIVER.get(f'http://www.hentai-foundry.com{url}')
    # response = SESSION.get(f'http://www.hentai-foundry.com{url}')
    html = bs4.BeautifulSoup(content, 'lxml')
    hrefs = [
        (*href, SITE) for href in 
        {(target.get('href'),) for target in 
        html.findAll(class_='thumbLink')} - query
        ]
    MYSQL.execute(INSERT[1], hrefs, many=1)

    next = next_page(html.find(class_='next')) 
    if hrefs and next: initialize(next, query)
    else: MYSQL.commit()

def page_handler(hrefs):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)
    
    for href, in hrefs:
        
        progress.next()

        try: DRIVER.get(f'http://www.hentai-foundry.com{href}')
        except exceptions.UnexpectedAlertPresentException: pass

        try:
            image = DRIVER.find('//img[@class="center"]', fetch=1).get_attribute('src')
            error = 0
            
        except exceptions.NoSuchElementException:
            error = DRIVER.find('//*[@id="errorBox"]')
            MYSQL.execute(DELETE[1], (href,), commit=1)
            continue
            
        except: continue
        
        if 'thumbs' in image:
            
            artist = href.split('/')[3]
            id = re.findall('.+pid=(\d+)&', image)[0]
            name = f'{artist} - {id}.jpg'

        elif 'pictures' in image:

            artist, id_, suffix = re.findall('.+/\w/([\w-]+)/(\d+).+\.(.+)', image)[0]
            name = f'{artist} - {id_}.{suffix}'

        else: 

            parts = image.split('/') + [image.split('.')[-1]]
            name = f'{parts[4]} - {parts[5]}.{parts[-1]}'

        name = PATH / 'Images' / SITE / name
        
        MYSQL.execute(UPDATE[2], (str(name), image, href), commit=1)
        if error: save_image(name, image)
    
    print()

def main(initial=True, headless=True):
    
    global MYSQL, DRIVER, SESSION
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    # SESSION = get_session()
    
    if initial:
        url = get_credentials(SITE, 'url')
        query = set(MYSQL.execute(SELECT[2], (SITE,), fetch=1))
        initialize(url, query)
    page_handler(MYSQL.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='foundry', 
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