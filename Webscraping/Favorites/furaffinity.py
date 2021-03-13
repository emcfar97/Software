from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import PATH, IncrementalBar, bs4, re

SITE = 'furaffinity'

def initialize(url, query=0):
    
    def next_page(pages):
        
        try: return pages.get('href')
        except AttributeError: return False

    if not query:
        query = set(CONNECTION.execute(SELECT[1], (SITE,), fetch=1))
    DRIVER.get(f'https://www.furaffinity.net{url}')
    
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (*href, SITE) for href in {(target.get('href'),) for target in 
        html.findAll(href=re.compile('/view+'))} - query
        ]
    CONNECTION.execute(INSERT[1], hrefs, many=1)
    next = next_page(html.find(class_='button standard right')) 
    if hrefs and next: initialize(next, query)

    CONNECTION.commit()

def page_handler(hrefs):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=len(hrefs))

    for href, in hrefs:
        
        DRIVER.get(f'https://www.furaffinity.net{href}')
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        
        if html.find(text=re.compile('not in our database.+')):
            
            CONNECTION.execute('DELETE FROM favorites WHERE href=%s', (href,), commit=1)
            continue      
                        
        artist = html.find(
            'a', href=re.compile('/user/+(?!chairekakia)'), id=False
            ).get('href').split('/')[2]
        image = html.find('a', href=re.compile('//d.+')).get('href')
        try:
            name = ' - '.join((artist, re.findall('_.+', image)[0][1:]))
        except: continue
        name = PATH / 'Images' / SITE / name

        CONNECTION.execute(UPDATE[2], (str(name), image, href), commit=1)
    
        progress.next()

def start(initial=True, headless=True):
    
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    if initial: 
        url = DRIVER.login(SITE)
        initialize(url)
    page_handler(CONNECTION.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()
