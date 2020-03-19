import hashlib
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException
import mysql.connector as sql
    
DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor()
SITE = 'metart'
TYPE = 'Erotica 2'

def initialize(driver, url='/my-favorite-galleries/page/1/', query=0):
    
    def next_page(page):
             
        try: return page.get('href')[28:]
        except IndexError: return False

    if not query:
        CURSOR.execute(SELECT[0], (SITE,))
        query = set(CURSOR.fetchall())
    driver.get(f'https://www.metarthunter.com{url}')

    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    while True:
        try:
            targets = html.find('ul', class_='gallery-a e')
            hrefs = [
                (target.get('href')[28:], SITE) for target in 
                targets.findAll('a', class_=False, href=True)
                if (target.get('href')[28:],) not in query
                ]
            break
        except sql.errors.OperationalError: continue
    while True:
        try: CURSOR.executemany(INSERT[0], hrefs); break
        except sql.errors.OperationalError: continue
        
    next = next_page(html.find(class_='next'))
    if hrefs and next: initialize(driver, next, query)
    while True:
        try: DATAB.commit(); break
        except sql.errors.OperationalError: continue
    
def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)
    hasher = hashlib.md5()

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        driver.get(f'https://www.metarthunter.com{href}')
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')

        for image in html.findAll('img', src=True):
            image = image.get('src')
            exif, = generate_tags(TYPE)
            hasher.update(requests.get(image).content)
            ext = image.split('.')[-1]
            name = save_image(
                join(PATH, 'エラティカ ニ', f'{hasher.hexdigest()}.{ext}'), image, exif
                )
            hash = get_hash(name) 
            
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
        driver = get_driver(True)
        login(driver, SITE)
        if initial: initialize(driver)
        CURSOR.execute(SELECT[2], (SITE,))
        page_handler(driver, CURSOR.fetchall())
    except WebDriverException:
        if input(f'{SITE}: Browser closed\nContinue?').lower() in 'yes': 
            setup(False)
    except Exception as error:
        print(f'{SITE}: {error}')

    driver.close()
    DATAB.close()

if __name__ == '__main__':
    
    from utils import *

    driver = get_driver()#True)
    login(driver, SITE)
    # initialize(driver)

    CURSOR.execute(SELECT[2], (SITE,))
    page_handler(driver, CURSOR.fetchall())

    driver.close()
    DATAB.close()

else: from .utils import *