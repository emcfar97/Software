from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
import mysql.connector as sql
from .utils import *

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 
SITE = 'foundry'
TYPE = 'Erotica 3'
host = '192.168.1.43' if ('e:\\' in __file__) else '127.0.0.1'

def initialize(driver, url='/user/Chairekakia/faves/pictures/enterAgree/1/size/1550/page/1', query=0):
    
    def next_page(pages):
        
        try: return pages.contents[0].get('href')
        except IndexError: return False

    driver.get(f'http://www.hentai-foundry.com{url}')
    if not query:
        query = set(execute(SELECT[0], (SITE,)))
        driver.find_element_by_xpath('//*[@id="frontPage"]').click()
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    while True:
        try:
            hrefs = [
                (*href, SITE) for href in {(target.get('href'),) for target in 
                html.findAll(class_='thumbLink')} - query
                ]
            break
        except sql.errors.OperationalError: continue
    while True:
        try: CURSOR.executemany(INSERT[1], hrefs); break
        except sql.errors.OperationalError: continue

    next = next_page(html.find('li', class_='next')) 
    if hrefs and next: initialize(driver, next, query)
    while True:
        try: DATAB.commit(); break
        except sql.errors.OperationalError: continue

def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        driver.get(f'http://www.hentai-foundry.com{href}')
        driver.find_element_by_xpath('//body/main/div/section[1]/div[2]/img').click()
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')

        artist = html.find(class_='breadcrumbs').text.split(' » ')[1]
        image = f'http:{html.find(class_="center", src=True).get("src")}'
        name = join(
            PATH, 'Images', SITE, re.sub(
            r'-\d+-', ' - ', image.split('/')[-1])
            )
        hash = get_hash(image) 

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
        driver = get_driver(headless=True)
        if initial: initialize(driver)
        page_handler(driver, execute(SELECT[3], (SITE,)))
    except WebDriverException:
        if input(f'{SITE}: Browser closed\nContinue?').lower() in 'yes':
            setup(False)
    except Exception as error:
        print(f'{SITE}: {error}')
        
    driver.close()
    DATAB.close()

if __name__ == '__main__':    

    driver = get_driver(headless=True)
    initialize(driver)
    driver.close()
    DATAB.close()
