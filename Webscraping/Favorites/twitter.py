import time
from .. import CONNECT, INSERT, SELECT, DELETE, WEBDRIVER
from ..utils import PATH, IncrementalBar, bs4, re
from selenium.webdriver.common.keys import Keys

SITE = 'twitter'

def initialize(url, retry=0):

    DRIVER.get(f'https://twitter.com/{url}/likes')

    while True:

        query = set(MYSQL.execute(SELECT[1], (SITE,), fetch=1))
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        hrefs = [
            (*href, SITE) for href in
            {
                (re.sub('/photo/\d+', '', href.get('href')),) for href in 
                html.findAll(
                    href=re.compile('/.+/status/.+')
                    )
                } - query
            ]
        MYSQL.execute(INSERT[1], hrefs, many=1)
        
        if not hrefs: 
            if retry >= 2: break
            else: retry += 1
        else: retry = 0
            
        for _ in range(2): DRIVER.find('html', Keys.PAGE_DOWN, type_=6)
                
    MYSQL.commit()

def page_handler(hrefs):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:

        DRIVER.get(f'https://twitter.com{href}')

        for _ in range(3):
            try:
                time.sleep(3)
                html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                images = html.findAll(
                    alt='Image', src=re.compile('.+?format=.+')
                    )
                images[0].get('src'); images[-1].get('src')
                artist = href.split('/')[1].lower()
                break

            except (IndexError, AttributeError, TypeError): 
                try:
                    continue
                    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                    images = html.findAll('video')
                    images[0].get('src'); images[-1].get('src')
                    artist = href.split('/')[1].lower()
                    break

                except (IndexError, AttributeError, TypeError): continue
        
        if not images: continue
        
        for image in images:

            image = re.sub('(name)=.+', r'\1=large', image.get('src'))
            name = image.replace('?format=', '.').split('/')[-1]
            name = PATH / 'Images' / SITE / f'{artist} - {name.split("&")[0]}'

            MYSQL.execute(INSERT[5], (str(name), image, href, SITE))
        else: MYSQL.execute(DELETE[1], (href,), commit=1)
        
        progress.next()

def start(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    if initial: 
        url = DRIVER.login(SITE)
        initialize(url)
    page_handler(MYSQL.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()