from .. import CONNECTION, INSERT, SELECT, UPDATE, sql
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, time, re
from selenium.webdriver.common.action_chains import ActionChains

SITE = 'furaffinity'

def initialize(driver, url='/favorites/chairekakia', query=0):
    
    def next_page(pages):
        
        try: return pages.get('href')
        except AttributeError: return False

    if not query:
        query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))
    driver.get(f'https://www.furaffinity.net{url}')
    
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    hrefs = [
        (*href, SITE) for href in {(target.get('href'),) for target in 
        html.findAll(href=re.compile('/view+'))} - query
        ]
    CURSOR.executemany(INSERT[1], hrefs)
    next = next_page(html.find(class_='button standard right')) 
    if hrefs and next: initialize(driver, next, query)

    CONNECTION.commit()

def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        driver.get(f'https://www.furaffinity.net{href}')
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        
        if html.find(text=re.compile('not in our database.+')):
            
            CURSOR.execute('DELETE FROM imageData WHERE href=%s', (href,), commit=1)
            continue      
                        
        artist = html.find('a', href=re.compile('/user/+(?!chairekakia)'), id=False).get('href')
        image = f'https:{html.find("a", href=re.compile("//d.+")).get("href")}'
        
        name = image.split('/')[-1].split('.')[1:]
        name[0] = re.sub(r'_\d+_-_', ' - ', name[0])
        name = join(PATH, 'Images', SITE, ".".join(name))
        hash_ = get_hash(image) 

        CURSOR.execute(UPDATE[1], (name, hash_, image, href), commit=1)
    
    progress(size, size, SITE)

def setup(driver, initial=True):
    
    try:
        login(driver, SITE)
        if initial: initialize(driver)
        page_handler(driver, CONNECTION.execute(SELECT[3], (SITE,), fetch=1))
    except Exception as error: print(f'{SITE}: {error}')
        
    driver.close()
