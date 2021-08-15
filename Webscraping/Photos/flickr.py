import argparse, time
from .. import CONNECT, INSERT, SELECT, UPDATE, DELETE, WEBDRIVER
from ..utils import IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as exceptions

SITE = 'flickr'

def initialize(url, query=0):
    
    def next_page(page):
             
        try: return page.get('href')[:-1]
        except IndexError: return False

    if not query:
        query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))

    DRIVER.get(f'https://www.flickr.com{url}')
    for _ in range(2):
        DRIVER.find('html', Keys.END, type_=6)
        time.sleep(2)

    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (target.get('href'), SITE) for target in 
        html.findAll(class_='overlay', href=re.compile('/photos/.+/\Z'))
        if (target.get('href'),) not in query
        ]

    next = next_page(html.find('a', {'data-track':'paginationRightClick'}))
    if hrefs and next: return hrefs + initialize(next, query)
    else: return hrefs

def page_handler(hrefs):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)
    view = 'view.photo-notes-scrappy-view'
    target = 'view.photo-well-scrappy-view.requiredToShowOnServer'

    for href, in hrefs:
        
        progress.next()
        DRIVER.get(f'https://www.flickr.com{href}')
        image = None
        
        for _ in range(20):
            try:
                DRIVER.find(view, move=True, type_=7, fetch=1)
                DRIVER.find(target, click=True, type_=7, fetch=1)

            except exceptions.ElementClickInterceptedException:
                image = DRIVER.find('zoom-large', type_=7).get_attribute('src')
                break

            except exceptions.NoSuchElementException:
                try: # Video
                    image = DRIVER.find(
                        '//*[@id="video_1_html5_api"]', fetch=1
                        ).get_attribute('src')
                    
                except: # Image unavailable
                    status = DRIVER.find('statusCode', type_=7, fetch=1).text
                    if status in ('403', '404'):
                        MYSQL.execute(DELETE[0], (href,), commit=1)
                break
            
            except (exceptions.WebDriverException, AttributeError): continue
        
        if image is None: continue

        name = get_name(image)
        if not save_image(name, image): continue
        tags, rating, exif = generate_tags(
            general=get_tags(DRIVER, name, True), 
            custom=True, rating=True, exif=True
            )
        if name.suffix == '.jpg': save_image(name, image, exif)
        hash_ = get_hash(name) 
        
        MYSQL.execute(
            UPDATE[0], 
            (name.name, ' ', tags, rating, 1, image, hash_, href),
            commit=1
            )
    
    print()

def start(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    if initial:
        hrefs = initialize(DRIVER.login(SITE))
        MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
    page_handler(MYSQL.execute(SELECT[2], (SITE,), fetch=1))
    DRIVER.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='flickr', 
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
    
    start(args.init, args.head)