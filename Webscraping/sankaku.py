from selenium.common.exceptions import WebDriverException
import mysql.connector as sql

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 
SITE = 'sankaku'
TYPE = 'Erotica 3'
MODE = {
    0:['idol', 'エラティカ ニ'],
    1:['chan', 'エラティカ 三']
    }

def initialize(driver, url='?tags=fav%3Achairekakia', query=0):
    
    def next_page(pages):
        
        try: return pages.get('next-page-url')
        except: return False

    if not query:
        CURSOR.execute(SELECT[0], (SITE,))
        query = set(CURSOR.fetchall())
    driver.get(f'https://{MODE[0]}.sankakucomplex.com/{url}')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    try: 
        if 'On' in html.find('span', {'data-role':True}).contents:
            driver.find_element_by_xpath('//*[@id="sc-auto-toggle"]').click()
        while True:
            try: 
                hrefs = [
                    (target.get('href'), SITE) for target in 
                    html.findAll('a', {'onclick': True}, href=re.compile('/p+'))
                    if (target.get('href'),) not in query
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

        driver.get(f'https://{MODE[0]}.sankakucomplex.com{href}')        
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        if html.find(text=re.compile('(Too many requests)|(Please slow down)')):
            time.sleep(60)
            driver.refresh()   
            html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        if '404' in driver.current_url: continue

        artists = [
            '_'.join(artist.text.split()[:-2]) for artist in 
            html.findAll(class_=re.compile('tag-type-(artist)|(idol)'))
            ]
        tags = [
            '_'.join(tag.text.split()[:-2]) for tag in 
            html.findAll(class_='tag-type-general')
            ]
        metadata = [
            '_'.join(tag.text.split()[:-2]) for tag in 
            html.findAll(class_='tag-type-medium')
            ]
        tags, rating, exif = generate_tags(
            TYPE, artists, metadata, tags, True, True
            )
        try:
            image = f'https:{html.find(id="highres", href=True).get("href")}'
        
            name = save_image(
                join(PATH, MODE[1], image.split('/')[-1].split('?e=')[0]), 
                image, exif
                )
            hash_ = get_hash(name) 
        except: continue

        while True:
            try:
                CURSOR.execute(UPDATE[3], (
                    name, f" {' '.join(artists)} ", 
                    f" {tags} ", rating, image, hash_, 1, href)
                    )
                DATAB.commit()
                break
            except sql.errors.OperationalError: continue
            except sql.errors.IntegrityError:
                CURSOR.execute(UPDATE[3], (
                    f'202 - {href}', f" {' '.join(artists)} ", 
                    f" {tags} ", rating, image, hash_, 1, href)
                    )
                DATAB.commit()
                break
    
    progress(size, size, SITE)

def setup(initial=True, mode=1):

    global MODE
    # if initial: 
    MODE = MODE[mode]
    
    try:
        driver = get_driver()# True)
        login(driver, SITE, MODE[0])
        if initial: initialize(driver)
        CURSOR.execute(SELECT[2], (SITE,))
        page_handler(driver, CURSOR.fetchall()[1200:])
    except WebDriverException:
        if input(f'\n{SITE}:Browser closed\nContinue? ').lower() in 'yes':
            setup(False)
    except Exception as error:
        print(f'{SITE}: {error}')
        
    try: driver.close()
    except: pass
    DATAB.close()

if __name__ == '__main__':
    
    from utils import *
    setup(0, mode=1)

else: from .utils import *