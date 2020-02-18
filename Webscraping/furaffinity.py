from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
import mysql.connector as sql
from .utils import *

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 
SITE = 'furaffinity'
TYPE = 'Erotica 3'

def initialize(driver, url='/favorites/chairekakia', query=0):
    
    def next_page(pages):
        
        try: return pages.get('href')
        except AttributeError: return False

    if not query:
        CURSOR.execute(SELECT[1], (SITE,))
        query = set(CURSOR.fetchall())
    driver.get(f'https://www.furaffinity.net{url}')
    
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    while True:
        try:
            hrefs = [
                (*href, SITE) for href in {(target.get('href'),) for target in 
                html.findAll(href=re.compile('/view+'))} - query
                ]
            break
        except sql.errors.OperationalError: continue
    while True:
        try: CURSOR.executemany(INSERT[1], hrefs); break
        except sql.errors.OperationalError: continue
    next = next_page(html.find(class_='button standard right')) 
    if hrefs and next: initialize(driver, next, query)
    while True:
        try: DATAB.commit(); break
        except sql.errors.OperationalError: continue

def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        driver.get(f'https://www.furaffinity.net{href}')
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')

        artist = html.find('a', href=re.compile('/user/+(?!chairekakia)'), id=False).get('href')
        x, y, exif, = generate_tags(TYPE, [artist.split('/')[2].lower()])
        image = f'https:{html.find("a", href=re.compile("//d.+")).get("href")}'
        
        name = image.split('/')[-1].split('.')[1:]
        name[0] = re.sub(r'_\d+_-_', ' - ', name[0])
        name = join(PATH, 'Images', SITE, ".".join(name))
        hash = save_image(name, image, exif)
        if name.endswith('.png'): name = name.replace('.png', '.jpg')

        while True:
            try:
                CURSOR.execute(UPDATE[1], (name, hash, image, href))
                DATAB.commit()
                break
            except sql.errors.OperationalError: continue
            except sql.errors.IntegrityError:
                CURSOR.execute(UPDATE[1], (f'202 - {href}', hash, image, href))
                DATAB.commit()
                break
    
    progress(size, size, SITE)

def setup(initial=True):
    
    try:
        driver = get_driver()
        login(driver, SITE)
        if initial: initialize(driver)
        CURSOR.execute(SELECT[3], (SITE,))
        page_handler(driver, CURSOR.fetchall())
        driver.close()
    except WebDriverException:
        if input(f'{SITE}: Browser closed\nContinue?').lower() in 'yes':
            setup(False)
    DATAB.close()

if __name__ == '__main__':

    driver = get_driver()
    login(driver, SITE)
    initialize(driver)
    driver.close()
    DATAB.close()
