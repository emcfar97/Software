from selenium.common.exceptions import WebDriverException
# from .utils import *
from utils import *

SITE = 'deviantArt'

def initialize(driver):#, url='/my-favorite-galleries/page/1/', query=0):
    
    # def next_page(page):
             
    #     try: return page.get('href')[26:]
    #     except IndexError: return False

    # if not query:
    #     CURSOR.execute(SELECT[0], (SITE,))
    #     query = set(CURSOR.fetchall())
    driver.get(f'https://www.deviantart.com/notifications/watch')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    # x = html.findAll()
    pass

def page_handler(driver): pass

def setup(initial=True):
    
    try:
        driver = get_driver(headless=True)
        login(driver, SITE)
        if initial: initialize(driver)
        CURSOR.execute(SELECT[2],(SITE,))
        page_handler(driver, CURSOR.fetchall())
    except WebDriverException:
        if input(f'{SITE}: Browser closed\nContinue?').lower() in 'yes': 
            setup(False)
    except Exception as error:
        print(f'{SITE}: {error}')
        
    driver.close()

if __name__ == '__main__':
    
    try:
        driver = get_driver()#headless=True)
        login(driver, SITE)
        initialize(driver)
    except Exception as error:
        print(f'{SITE}: {error}')
    driver.close()