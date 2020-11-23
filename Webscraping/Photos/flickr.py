from .. import CONNECT, INSERT, SELECT, UPDATE, DELETE, WEBDRIVER
from ..utils import Progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re
import time
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as exceptions

SITE = 'flickr'

def initialize(url='/photos/140284163@N04/favorites/page1', query=0):
    
    def next_page(page):
             
        try: return page.get('href')[:-1]
        except IndexError: return False

    if not query:
        query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))

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
    CONNECTION.execute(INSERT[0], hrefs, 1)
        
    next = next_page(html.find('a', {'data-track':'paginationRightClick'}))
    if hrefs and next: initialize(next, query)

    CONNECTION.commit()
    
def page_handler(hrefs):

    if not hrefs: return
    progress = Progress(len(hrefs), SITE)
    view = 'view.photo-notes-scrappy-view'
    target = 'view.photo-well-scrappy-view.requiredToShowOnServer'

    for href, in hrefs:
        
        print(progress)
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
                        CONNECTION.execute(DELETE, (href,), commit=1)
                break
            
            except (exceptions.WebDriverException, AttributeError): continue
        
        else:
            if image is None: continue

        name = get_name(image, 0, 1)
        if not save_image(name, image): continue
        tags, rating, exif = generate_tags(
            general=get_tags(DRIVER, name), custom=True, rating=True, exif=True
            )
        if name.suffix == '.jpg': save_image(name, image, exif)
        hash_ = get_hash(name) 
        
        CONNECTION.execute(
            UPDATE[0], 
            (name.name, ' ', tags, rating, 1, image, hash_, href),
            commit=1
            )
    
    print(progress)

def start(initial=True):
    
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER()
    
    DRIVER.login(SITE)
    if initial: initialize()
    page_handler(CONNECTION.execute(SELECT[2], (SITE,), fetch=1))
    DRIVER.close()
