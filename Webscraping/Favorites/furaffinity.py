from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, time, re
from selenium.webdriver.common.action_chains import ActionChains

CONNECTION = CONNECT()
DRIVER = WEBDRIVER()
SITE = 'furaffinity'

def initialize(url='/favorites/chairekakia', query=0):
    
    def next_page(pages):
        
        try: return pages.get('href')
        except AttributeError: return False

    if not query:
        query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))
    DRIVER.get(f'https://www.furaffinity.net{url}')
    
    html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
    hrefs = [
        (*href, SITE) for href in {(target.get('href'),) for target in 
        html.findAll(href=re.compile('/view+'))} - query
        ]
    CONNECTION.execute(INSERT[1], hrefs, many=1)
    next = next_page(html.find(class_='button standard right')) 
    if hrefs and next: initialize(next, query)

    CONNECTION.commit()

def page_handler(hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        DRIVER.get(f'https://www.furaffinity.net{href}')
        html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
        
        if html.find(text=re.compile('not in our database.+')):
            
            CONNECTION.execute('DELETE FROM imageData WHERE href=%s', (href,), commit=1)
            continue      
                        
        artist = html.find('a', href=re.compile('/user/+(?!chairekakia)'), id=False).get('href')
        image = f'https:{html.find("a", href=re.compile("//d.+")).get("href")}'
        
        name = image.split('/')[-1].split('.')[1:]
        name[0] = re.sub(r'_\d+_-_', ' - ', name[0])
        name = join(PATH, 'Images', SITE, ".".join(name))
        hash_ = get_hash(image) 

        CONNECTION.execute(UPDATE[1], (name, hash_, image, href), commit=1)
    
    progress(size, size, SITE)

def setup(initial=True):
    
    try:
        login(DRIVER, SITE)
        if initial: initialize(DRIVER)
        page_handler(CONNECTION.execute(SELECT[3], (SITE,), fetch=1))
    except Exception as error: print(f'{SITE}: {error}')
        
    DRIVER.close()
