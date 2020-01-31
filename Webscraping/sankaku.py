from selenium.common.exceptions import WebDriverException
import mysql.connector as sql
from .utils import *

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 
SITE = 'sankaku'
TYPE = 'Erotica 3'

def initialize(driver, url='?tags=fav%3Achairekakia', query=0):
    
    def next_page(pages):
        
        try: return pages.get('next-page-url')[1:]
        except IndexError: return False

    if not query:
        CURSOR.execute(SELECT[0], (SITE,))
        query = set(CURSOR.fetchall())
    driver.get(f'https://chan.sankakucomplex.com/{url}')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    try: 
        if 'On' in html.find('span', {'data-role':True}).contents:
            driver.find_element_by_xpath('//*[@id="sc-auto-toggle"]').click()
        while True:
            try: 
                hrefs = [
                    (*href, SITE) for href in 
                    {(target.get('href'),) for target in 
                    html.findAll('a', {'onclick': True}, href=re.compile('/p+'))
                    } - query
                    ]
                break
            except sql.errors.OperationalError: continue
        while True:
            try: CURSOR.executemany(INSERT[0], hrefs); break
            except sql.errors.OperationalError: continue

        next = next_page(html.find('div', {'next-page-url': True}))   
        if hrefs and next: initialize(driver, next, query)
    except: 
        time.sleep(60)   
        initialize(driver, url, query)
    while True:
        try: DATAB.commit(); break
        except sql.errors.OperationalError: continue

def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        driver.get(f'https://chan.sankakucomplex.com{href}')        
        time.sleep(1)
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        if html.find(text=re.compile('Too many requests')): 
            time.sleep(60)
            driver.get(f'https://chan.sankakucomplex.com{href}')        
            html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        artists = [
            '_'.join(artist.text.split(' ')[:-2]) for artist in 
            html.findAll(class_='tag-type-artist')
            ]
        tags = [
            '_'.join(tag.text.split(' ')[:-2]) for tag in 
            html.findAll(class_='tag-type-general')
            ]
        metadata = [
            '_'.join(tag.text.split(' ')[:-2]) for tag in 
            html.findAll(class_='tag-type-medium')
            ]
        tags, rating, exif = generate_tags(TYPE, artists, metadata, tags, True, True)
        image = f'https:{html.find(id="highres", href=True).get("href")}'
        name = join(PATH, 'エラティカ 三', image.split('/')[-1].split('?e=')[0])
        hash = save_image(name, image, exif, 1)
        if name.endswith('.png'): name = name.replace('.png', '.jpg')


        while True:
            try:
                CURSOR.execute(UPDATE[3], (
                    name, f" {' '.join(artists)} ", 
                    f" {tags} ", rating, image, hash, 1, href)
                    )
                DATAB.commit()
                break
            except sql.errors.OperationalError: continue
            except sql.errors.IntegrityError:
                CURSOR.execute(UPDATE[3], (
                    f'202 - {href}', f" {' '.join(artists)} ", 
                    f" {tags} ", rating, image, hash, 1, href)
                    )
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
        driver.close()
    except WebDriverException:
        if input(f'{SITE}:Browser closed\nContinue?').lower() in 'yes':
            setup(False)
    DATAB.close()

if __name__ == '__main__':
    
    driver = get_driver(headless=True)
    login(driver, SITE)
    initialize(driver)
    driver.close()
    DATAB.close()
