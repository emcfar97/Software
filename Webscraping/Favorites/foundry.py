from .. import CONNECTION, INSERT, SELECT, UPDATE, sql
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, time, re
from selenium.webdriver.common.action_chains import ActionChains

SITE = 'foundry'

def initialize(driver, url='/user/Chairekakia/faves/pictures/enterAgree/1/size/1550/page/1', query=0):
    
    def next_page(pages):
        
        try: return pages.contents[0].get('href')
        except IndexError: return False

    driver.get(f'http://www.hentai-foundry.com{url}')
    if not query:
        query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))
        driver.find_element_by_xpath('//*[@id="frontPage"]').click()
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    hrefs = [
        (*href, SITE) for href in {(target.get('href'),) for target in 
        html.findAll(class_='thumbLink')} - query
        ]
    CONNECTION.executemany(INSERT[1], hrefs)

    next = next_page(html.find('li', class_='next')) 
    if hrefs and next: initialize(driver, next, query)

    CONNECTON.commit()

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

        
        CONNECTION.execute(UPDATE[1], (name, hash, image, href), commit=1)
    
    progress(size, size, SITE)

def setup(driver, initial=True):
    
    try:
        if initial: initialize(driver)
        page_handler(driver, CONNECTION.execute(SELECT[3], (SITE,), fetch=1))
    except Exception as error: print(f'{SITE}: {error}')
        
    driver.close()
