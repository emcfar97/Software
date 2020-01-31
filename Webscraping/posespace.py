from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
import mysql.connector as sql
from .utils import *

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 
SITE = 'posespace'

def initialize(driver, url='/posetool/favs.aspx'):

    CURSOR.execute(SELECT[0], (SITE,))
    query = set(CURSOR.fetchall())
    driver.get(f'https://www.posespace.com{url}')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    while True:
        try:
            hrefs = [
                (*href, SITE) for href in {(target.get('href'),) 
                for target in html.findAll(class_='emph')} - query
                ]
            break
        except sql.errors.OperationalError: continue
    while True:
        try: CURSOR.executemany(INSERT[0], hrefs,); break
        except sql.errors.OperationalError: continue
        
    DATAB.commit()

def page_handler(driver, hrefs):
    
    if not hrefs: return
    size = len(hrefs)
    url = 'https://www.posespace.com/img/contact/'

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        name = join(PATH, 'Images', SITE, f'{href}.gif')
        href_a = f'{url}{href}contacta.jpg'
        href_b = f'{url}{href}contactb.jpg'

        image_a = Image.open(BytesIO(requests.get(href_a).content))
        image_b = Image.open(BytesIO(requests.get(href_b).content))

        image = Image.new('RGB', (image_a.width, image_a.height+image_b.height))
        image.paste(image_a)
        image.paste(image_b, (0, image_a.height))
        image.show()

        continue
        while True:
            try:
                CURSOR.execute(UPDATE[3], (name, hash, image, href))
                DATAB.commit()
                break
            except sql.errors.OperationalError: continue
            except sql.errors.IntegrityError:
                CURSOR.execute(UPDATE[3], (f'202 - {href}', hash, image, href))
                DATAB.commit()
                break
        
    progress(size, size, SITE)

def setup(initial=True):
    
    try:
        driver = get_driver(headless=True)
        login(driver, SITE)
        if initial: initialize(driver)
        CURSOR.execute(SELECT[2], (SITE,))
        page_handler(driver, CURSOR.fetchall())
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
