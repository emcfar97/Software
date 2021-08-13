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
        
        progress.next()
        DRIVER.get(f'http://www.hentai-foundry.com{href}')
        DRIVER.find('//*[@class="center"]', click=True)
        try: 
            html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')

            artist = html.find(class_='breadcrumbs').text.split(' » ')[1]
            image = f'http:{html.find(class_="center", src=True).get("src")}'
        except Exception as error: 
            print(error)
            continue
        
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
    page_handler(MYSQL.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        prog='foundry', 
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