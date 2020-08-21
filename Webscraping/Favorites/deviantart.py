from selenium.common.exceptions import WebDriverException

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

def setup(initial=True):
    
    try:
        driver = WEBDRIVER(headless=True)
        login(driver, SITE)
        if initial: initialize(driver)
        page_handler(driver, execute(SELECT[2],(SITE,), fetch=1))
    except Exception as error: print(f'{SITE}: {error}')
        
    driver.close()

if __name__ == '__main__': from utils import *
else: from .utils import *