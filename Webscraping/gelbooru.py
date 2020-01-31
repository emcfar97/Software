from PIL import ImageFile
from selenium.common.exceptions import TimeoutException, WebDriverException
ImageFile.LOAD_TRUNCATED_IMAGES = True
import mysql.connector as sql
from .utils import *

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 
SITE = 'gelbooru'
TYPE = 'Erotica 3'
    
def initialize(driver, url='?page=favorites&s=view&id=173770&pid=0', query=0):
    
    def next_page(pages):
        
        try: return pages[pages.index(' ') + 3].get('href')
        except IndexError: return False

    if not query:
        CURSOR.execute(SELECT[0], (SITE,))
        query = set(CURSOR.fetchall())
    driver.get(f'https://gelbooru.com/index.php{url}')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    while True:
        try:
            hrefs = [
                (*href, SITE) for href in {(target.get('href'),) for target in 
                html.findAll('a', id=re.compile(r'p\d+'), href=True)} - query
                ]
            break
        except sql.errors.OperationalError: continue
    while True:
        try: CURSOR.executemany(INSERT[0], hrefs); break
        except sql.errors.OperationalError: continue
        
    next = next_page(html.find(id='paginator').contents)   
    if hrefs and next: initialize(driver, next, query)
    DATAB.commit()

def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        try: driver.get(f'https://gelbooru.com/{href}')
        except TimeoutException: input('\nContinue?')

        if 'page=post&s=list' in driver.current_url:
            CURSOR.execute('UPDATE imageDatabase SET path=? WHERE href=?', (f'404 - {href}', href,))
            DATAB.commit()
            continue
        
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        artists = [
            '_'.join(artist.text.split(' ')[1:-1]) for artist in 
            html.findAll(class_='tag-type-artist')
            ]
        tags = [
            '_'.join(tag.text.split(' ')[1:-1]) for tag in 
            html.findAll(class_='tag-type-general')
            ]
        metadata = [
            '_'.join(tag.text.split(' ')[1:-1]) for tag in 
            html.findAll(class_='tag-type-metadata')
            ]
        tags, rating, exif = generate_tags(
            TYPE, artists, metadata, tags, True, True
            )
        image = driver.find_element_by_link_text('Original image')
        image = image.get_attribute('href')
        name = join(PATH, 'エラティカ 三', image.split('/')[-1])
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
    initialize(driver)
    driver.close()
    DATAB.close()
