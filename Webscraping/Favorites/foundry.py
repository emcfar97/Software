from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import PATH, IncrementalBar, bs4, re

SITE = 'foundry'

def initialize(url, query=0):
    
    def next_page(pages):
        
        if 'hidden' in pages.get('class'): return
        else: return pages.contents[0].get('href')

    DRIVER.get(f'http://www.hentai-foundry.com{url}')
    if not query:
        query = set(MYSQL.execute(SELECT[1], (SITE,), fetch=1))
        if element := DRIVER.find('//*[@id="frontPage"]', type_=1):
            element.click()
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
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
        
        DRIVER.get(f'http://www.hentai-foundry.com{href}')
        if element := DRIVER.find('//*[@id="frontPage"]', type_=1):
            element.click()
        DRIVER.find(
            '//body/main/div/section[1]/div[2]/img', click=True, type_=1
            )
        try: html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        except: continue

        artist = html.find(class_='breadcrumbs').text.split(' » ')[1]
        image = f'http:{html.find(class_="center", src=True).get("src")}'
        name = re.sub(f'({artist})-\d+', r'\1 - ', image.split('/')[-1])
        name = PATH / 'Images' / SITE / name

        MYSQL.execute(UPDATE[2], (str(name), image, href), commit=1)
    
        progress.next()
    print()

def start(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    if initial:
        url = DRIVER.login(SITE)
        initialize(url)
    page_handler(MYSQL.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()
