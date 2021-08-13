from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import PATH, IncrementalBar, bs4, re

SITE = 'deviantart'

def initialize(url, query=0):
    
    def next_page(page):
             
        try: return page.get('href')
        except IndexError: return False

    if not query:
        query = set(MYSQL.execute(SELECT[1], (SITE,), fetch=1))
    DRIVER.get(f'https://www.deviantart.com/notifications/watch')
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    artists = html.findAll('div', {'aria-label': re.compile('\d+ Deviations by .*')})

    for artist in artists:

        href = artist.find('a', href=True)
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
    
    print()

def start(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    if initial:
        url = DRIVER.login(SITE)
        initialize(url)
    page_handler(MYSQL.execute(SELECT[2], (SITE,), fetch=1))
    DRIVER.close()

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        prog='daviantart', 
        )
    parser.add_argument(
        '-i', '--initial', type=bool,
        help='Initial argument (default True)',
        default=True
        )
    parser.add_argument(
        '-he', '--headless', type=bool,
        help='Headless argument (default True)',
        default=True
        )

    args = parser.parse_args()
    
    start(args.initial, args.headless)