from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, time, re
from selenium.webdriver.common.action_chains import ActionChains

CONNECTION = CONNECT()
DRIVER = WEBDRIVER()
SITE = 'foundry'

def initialize(url='/user/Chairekakia/faves/pictures/enterAgree/1/size/1550/page/1', query=0):
    
    def next_page(pages):
        
        try: return pages.contents[0].get('href')
        except IndexError: return False

    DRIVER.get(f'http://www.hentai-foundry.com{url}')
    if not query:
        query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))
        DRIVER.find_element_by_xpath('//*[@id="frontPage"]').click()
    html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
    hrefs = [
        (*href, SITE) for href in {(target.get('href'),) for target in 
        html.findAll(class_='thumbLink')} - query
        ]
    CONNECTION.executemany(INSERT[1], hrefs)

    next = next_page(html.find('li', class_='next')) 
    if hrefs and next: initialize(next, query)

    CONNECTON.commit()

def page_handler(hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        DRIVER.get(f'http://www.hentai-foundry.com{href}')
        DRIVER.find_element_by_xpath('//body/main/div/section[1]/div[2]/img').click()
        html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')

        artist = html.find(class_='breadcrumbs').text.split(' » ')[1]
        image = f'http:{html.find(class_="center", src=True).get("src")}'
        name = join(
            PATH, 'Images', SITE, re.sub(
            r'-\d+-', ' - ', image.split('/')[-1])
            )
        hash = get_hash(image) 

        CONNECTION.execute(UPDATE[1], (name, hash, image, href), commit=1)
    
    progress(size, size, SITE)

def setup(initial=True):
    
    try:
        if initial: initialize(DRIVER)
        page_handler(CONNECTION.execute(SELECT[3], (SITE,), fetch=1))
    except Exception as error: print(f'{SITE}: {error}')
        
    DRIVER.close()
