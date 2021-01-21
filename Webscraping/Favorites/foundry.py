from urllib.parse import urlparse
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import PATH, Progress, get_hash, bs4, re

SITE = 'foundry'

def initialize(url='/user/Chairekakia/faves/pictures/enterAgree/1/size/1550/page/1', query=0):
    
    def next_page(pages):
        
        try: return pages.contents[0].get('href')
        except IndexError: return False

    DRIVER.get(f'http://www.hentai-foundry.com{url}')
    if not query:
        DRIVER.find('//*[@id="frontPage"]', click=True, type_=1)
        query = set(CONNECTION.execute(SELECT[1], (SITE,), fetch=1))
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (*href, SITE) for href in {(target.get('href'),) for target in 
        html.findAll(class_='thumbLink')} - query
        ]
    CONNECTION.execute(INSERT[1], hrefs, many=1)

    next = next_page(html.find('li', class_='next')) 
    if hrefs and next: initialize(next, query)

    CONNECTION.commit()

def page_handler(hrefs):

    if not hrefs: return
    progress = Progress(len(hrefs), SITE)

    for href, in hrefs:
        
        print(progress)

        DRIVER.get(f'http://www.hentai-foundry.com{href}')
        DRIVER.find(
            '//body/main/div/section[1]/div[2]/img', click=True, type_=1
            )
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')

        artist = html.find(class_='breadcrumbs').text.split(' » ')[1]
        image = f'http:{html.find(class_="center", src=True).get("src")}'
        name = re.sub(f'{artist}-\d+', f'{artist}', image.split('/')[-1])
        name = PATH / 'Images' / SITE / name

        CONNECTION.execute(UPDATE[2], (str(name), image, href), commit=1)
    
    print(progress)

def start(initial=True, headless=True):
    
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    if initial: initialize()
    page_handler(CONNECTION.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()
