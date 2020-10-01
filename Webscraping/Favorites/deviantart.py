from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import Progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, time, re

SITE = 'deviantArt'

def initialize():#, url='/my-favorite-galleries/page/1/', query=0):
    
    # def next_page(page):
             
    #     try: return page.get('href')[26:]
    #     except IndexError: return False

    # if not query:
    #     query = set(execute(SELECT[1], (SITE,), fetch=1))
    DRIVER.get(f'https://www.deviantart.com/notifications/watch')
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    # x = html.findAll()
    pass

def page_handler(): pass

def setup(initial=True):
    
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(False)
    
    DRIVER.login(SITE)
    if initial: initialize()
    page_handler(CONNECTION.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()
