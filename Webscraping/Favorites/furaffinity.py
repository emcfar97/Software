from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException

SITE = 'furaffinity'
TYPE = 'Erotica 3'

def initialize(driver, url='/favorites/chairekakia', query=0):
    
    def next_page(pages):
        
        try: return pages.get('href')
        except AttributeError: return False

    if not query:
        query = set(execute(SELECT[0], (SITE,), fetch=1))
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
        
        if html.find(text=re.compile('not in our database.+')):
            
            while True:
                try:
                    CURSOR.execute('DELETE FROM imageData WHERE href=%s', (href,))
                    DATAB.commit()
                    break
                except sql.errors.OperationalError: continue 
            continue      
                        
        artist = html.find('a', href=re.compile('/user/+(?!chairekakia)'), id=False).get('href')
        image = f'https:{html.find("a", href=re.compile("//d.+")).get("href")}'
        
        name = image.split('/')[-1].split('.')[1:]
        name[0] = re.sub(r'_\d+_-_', ' - ', name[0])
        name = join(PATH, 'Images', SITE, ".".join(name))
        hash_ = get_hash(image) 

        while True:
            try:
                CURSOR.execute(UPDATE[1], (name, hash_, image, href))
                DATAB.commit()
                break
            except sql.errors.OperationalError: continue
            except sql.errors.IntegrityError:
                CURSOR.execute(UPDATE[1], (f'202 - {href}', hash_, image, href))
                DATAB.commit()
                break
    
    progress(size, size, SITE)

def setup(initial=True):
    
    try:
        driver = WEBDRIVER()
        login(driver, SITE)
        if initial: initialize(driver)
        page_handler(driver, execute(SELECT[3], (SITE,), fetch=1))
    except Exception as error: print(f'{SITE}: {error}')
        
    driver.close()

if __name__ == '__main__':

    from utils import *
    setup()

else: from .utils import *