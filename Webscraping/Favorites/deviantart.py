from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, time, re

CONNECTION = CONNECT()
DRIVER = WEBDRIVER()
SITE = 'deviantArt'

def initialize():#, url='/my-favorite-galleries/page/1/', query=0):
    
    # def next_page(page):
             
    #     try: return page.get('href')[26:]
    #     except IndexError: return False

    # if not query:
    #     query = set(execute(SELECT[0], (SITE,), fetch=1))
    DRIVER.get(f'https://www.deviantart.com/notifications/watch')
    html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
    # x = html.findAll()
    pass

def page_handler(): pass

def setup(initial=True):
    
    try:
        login(DRIVER, SITE)
        if initial: initialize(DRIVER)
        page_handler(CONNECTION.execute(SELECT[2], (SITE,), fetch=1))
    except Exception as error: print(f'{SITE}: {error}')
        
    DRIVER.close()
