import hashlib
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException
import mysql.connector as sql
from .utils import *
    
DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor()
SITE = 'flickr'
TYPE = 'Erotica 2'

def initialize(driver, url='/photos/140284163@N04/favorites/page1', query=0):
    
    def next_page(page):
             
        try: return page.get('href')[:-1]
        except IndexError: return False

    if not query:
        CURSOR.execute(SELECT[0], (SITE,))
        query = set(CURSOR.fetchall())
    driver.get(f'https://www.flickr.com{url}')
    for _ in range(2):
        driver.find_element_by_tag_name('html').send_keys(Keys.END)
        time.sleep(2)

    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    while True:
        try:
            hrefs = [
                (target.get('href'), SITE) for target in 
                html.findAll('a', class_='overlay', href=True)
                if (target.get('href'),) not in query
                ]
            break
        except sql.errors.OperationalError: continue
    while True:
        try: CURSOR.executemany(INSERT[0], hrefs); break
        except sql.errors.OperationalError: continue
        
    next = next_page(html.find('a', {'data-track':'paginationRightClick'}))
    if hrefs and next: initialize(driver, next, query)
    while True:
        try: DATAB.commit(); break
        except sql.errors.OperationalError: continue
    
def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)
    hasher = hashlib.md5()
    view = 'view.photo-notes-scrappy-view'
    elment = 'view.photo-well-scrappy-view.requiredToShowOnServer'

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        driver.get(f'https://www.flickr.com{href}')
        try:
            element = driver.find_element_by_class_name(view)
            ActionChains(driver).move_to_element(element).perform()
            for _ in range(50):
                try: driver.find_element_by_class_name(elment).click()
                except ElementClickInterceptedException: break
            else: continue

            image = driver.find_element_by_class_name('zoom-large').get_attribute('src')
            exif, = generate_tags(TYPE)
            hasher.update(requests.get(image).content)
            ext = image.split('.')[-1]
            name = join(PATH, 'エラティカ ニ', f'{hasher.hexdigest()}.{ext}')

        except:
            try:
                video = driver.find_element_by_xpath(
                    '//*[@id="video_1_html5_api"]'
                    )
                image = video.get_attribute('src')
                data = requests.get(image).content
                hasher.update(data)
                
                name = join(PATH, 'エラティカ ニ', f'{hasher.hexdigest()}.mp4')
                with open(name, 'wb') as file: file.write(data) 

            except:
                try:
                    status = driver.find_element_by_class_name('statusCode')
                    if status.text == '404': 
                        exif = None
                        image = None
                        name = f'404 - {href}'
                except: continue
            
        hash = None if name.startswith('404') else save_image(name, image, exif, 1)
        # hash = save_image(name, image, 1)
        if name.endswith('.png'): name = name.replace('.png', '.jpg')
        
        while True:
            try:
                CURSOR.execute(UPDATE[0], (name, image, hash, 0, href))
                DATAB.commit()
                break
            except sql.errors.OperationalError: continue
            except sql.errors.IntegrityError:
                name, ext = name.split('.')
                name = f'{name}1.{ext}'
                CURSOR.execute(UPDATE[0], (name, image, hash, 0, href))
                DATAB.commit()
                break
    
    progress(size, size, SITE)

def setup(initial=True):
    
    try:
        driver = get_driver(headless=True)
        login(driver, SITE)
        if initial: initialize(driver)
        CURSOR.execute(SELECT[2],(SITE,))
        page_handler(driver, CURSOR.fetchall())
        driver.close()
    except WebDriverException:
        if input(f'{SITE}: Browser closed\nContinue?').lower() in 'yes': 
            setup(False)
    DATAB.close()

if __name__ == '__main__':
    
    driver = get_driver(headless=True)
    login(driver, SITE)
    initialize(driver)
    driver.close()
    DATAB.close()
