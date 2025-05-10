import argparse, bs4, requests
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER, get_credentials
from ..utils import PATH, HEADERS, IncrementalBar, re

SITE = 'furaffinity'

def get_session():
    
    sess = requests.Session()
    sess.headers.update(HEADERS)
    
    payload = {
        'name': get_credentials(SITE, 'username'),
        'pass': get_credentials(SITE, 'password'),
        'action': 'login',
        'dest': 'www.furaffinity.net',
        }
    
    sess.post('https://www.furaffinity.net/login/', data=payload)
    
    return sess

def initialize(url, query):
    
    def next_page(pages):
        
        try: return pages.get('href')
        except AttributeError: return False

    content = DRIVER.get(f'https://www.{SITE}.net{url}')
    html = bs4.BeautifulSoup(content, 'lxml')
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
        content = DRIVER.get(f'https://www.{SITE}.net{href}')
        html = bs4.BeautifulSoup(content, 'lxml')
        
        if html.find(text=re.compile('not in our database.+')):
            
            MYSQL.execute('DELETE FROM favorites WHERE href=%s', (href,), commit=1)
            continue      
                        
        image = 'https:' + html.find(
            'img', src=re.compile('//d.furaffinity.net/art/.+')
            ).get('src')
        parts = image.split('/') + [image.split('.')[-1]]
        name = f'{parts[4]} - {parts[5]}.{parts[-1]}'
        name = PATH / 'Images' / SITE / name
        
        if name.suffix == ' ': name.with_suffix('.png')

        MYSQL.execute(UPDATE[2], (str(name), image, href), commit=1)
    
    print()

def main(initial=True, headless=True):

    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    if initial:
        url = get_credentials(SITE, 'url')
        query = set(MYSQL.execute(SELECT[2], (SITE,), fetch=1))
        initialize(url, query)
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