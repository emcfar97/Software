import time, argparse
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, bs4
from selenium.webdriver.common.keys import Keys

SITE = 'topless'

def initialize(url='https://toplesspulp.com/category/', year=2020, query=0):
    
    if not query: query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))

    DRIVER.get(f'{url}{year}')
    for _ in range(10): 
        DRIVER.find('html', Keys.END, type_=6)
        time.sleep(1)
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')

    hrefs = [
        (target.find(href=True).get('href'), SITE) 
        for target in html.findAll('figure')
        if (target.find(href=True).get('href'),) not in query
        ]
    MYSQL.execute(INSERT[0], hrefs, 1)
       
    initialize(year-1, query)
    MYSQL.commit()

def page_handler(hrefs):

    if not hrefs: return
    progress = IncrementalBar(SITE, MYSQL.rowcount)

    for href, in hrefs:
        
        progress.next()
        name = get_name(href)
        if not save_image(name, href): continue
        tags, rating, exif = generate_tags(
            get_tags(DRIVER, name, True) + ' casual_nudity',
            custom=True, rating=True, exif=True
            )
        save_image(name, href, exif)
        hash_ = get_hash(name)
        
        MYSQL.execute(UPDATE[0],
            (str(name), ' ', tags, rating, href, hash_, href),
            commit=1
            )

    print()

def main(headless=True):

    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    initialize()
    page_handler(MYSQL.execute(SELECT[2], (SITE,), fetch=1))
        
    DRIVER.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='toplesspulp', 
        )
    parser.add_argument(
        '-he', '--head', type=bool,
        help='Headless argument (default True)',
        default=True
        )

    args = parser.parse_args()
    
    main(args.head)