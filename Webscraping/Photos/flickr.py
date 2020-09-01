from .. import CONNECTION, sql, INSERT, SELECT, UPDATE
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException, NoSuchElementException

SITE = 'flickr'

def initialize(driver, url='/photos/140284163@N04/favorites/page1', query=0):
    
    def next_page(page):
             
        try: return page.get('href')[:-1]
        except IndexError: return False

    if not query:
        query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))

    driver.get(f'https://www.flickr.com{url}')
    for _ in range(2):
        driver.find('html', Keys.END, type=6)
        time.sleep(2)

    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    hrefs = [
        (target.get('href'), 1, SITE) for target in 
        html.findAll('a', class_='overlay', href=True)
        if (target.get('href'),) not in query
        ]
    CONNECTION.execute(INSERT[0], hrefs, 1)
        
    next = next_page(html.find('a', {'data-track':'paginationRightClick'}))
    if hrefs and next: initialize(driver, next, query)

    CONNECTION.commit()
    
def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)
    view = 'view.photo-notes-scrappy-view'
    target = 'view.photo-well-scrappy-view.requiredToShowOnServer'

    for num, (href,) in enumerate(hrefs):
        
        progress(size, num, SITE)
        driver.get(f'https://www.flickr.com{href}')
        image = None
        
        for _ in range(20):
            try:
                element = driver.find(view, type=7, fetch=1)
                ActionChains(driver).move_to_element(element).perform()
                driver.find(target, click=True, type=7)

            except ElementClickInterceptedException:
                image = driver.find('zoom-large', type=7, fetch=1).get_attribute('src')
                break

            except NoSuchElementException:
                try: # Video
                    image = driver.find(
                        '//*[@id="video_1_html5_api"]', type=1, fetch=1
                        ).get_attribute('src')
                    
                except: # Image unavailable
                    status = driver.find('statusCode', type=7, fetch=1).text
                    if status in ('403', '404'):
                        CONNECTION.execute(
                            'DELETE FROM imageData WHERE href=%s', (href,), commit=1
                            )
                
                break
            
            except WebDriverException: pass
        
        else:
            if image is None: continue

        name = get_name(image, 0, 1)
        if not save_image(name, image): continue
        tags, rating, exif = generate_tags(
            general=get_tags(driver, name), 
            custom=True, rating=True, exif=True
            )
        if name.endswith(('jpg', 'jpeg')): save_image(name, image, exif)
        hash_ = get_hash(name) 
        
        CONNECTION.execute(
            UPDATE[3], 
            (str(name), ' ', tags, rating, image, hash_, href),
            commit=1
            )
    
    progress(size, size, SITE)

def setup(driver, initial=True):
    
    try:
        login(driver, SITE)
        if initial: initialize(driver)
        page_handler(driver, CONNECTION.execute(SELECT[2], (SITE,), fetch=1))
    except Exception as error: print(f'{SITE}: {error}')

    finally: driver.close()
