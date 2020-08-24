from .. import CONNECTION, INSERT, SELECT, UPDATE, sql
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, time, re

SITE = 'deviantArt'

def initialize(driver):#, url='/my-favorite-galleries/page/1/', query=0):
    
    # def next_page(page):
             
    #     try: return page.get('href')[26:]
    #     except IndexError: return False

    # if not query:
    #     query = set(execute(SELECT[0], (SITE,), fetch=1))
    driver.get(f'https://www.deviantart.com/notifications/watch')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    # x = html.findAll()
    pass

def page_handler(driver): pass

def setup(driver, initial=True):
    
    try:
        login(driver, SITE)
        if initial: initialize(driver)
        page_handler(driver, execute(SELECT[2],(SITE,), fetch=1))
    except Exception as error: print(f'{SITE}: {error}')
        
    driver.close()
