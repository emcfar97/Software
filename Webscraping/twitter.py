import itertools
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import mysql.connector as sql
from .utils import *

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 
SITE = 'twitter'
TYPE = 'Erotica 3'
DELETE = 'DELETE FROM imageDatabase WHERE href=? AND path IS NULL'

def initialize(driver, retry=0):

    CURSOR.execute(SELECT[1], (SITE,))
    query = set(CURSOR.fetchall())
    driver.get('https://twitter.com/Chairekakia1/likes')
    time.sleep(4)    

    while True:

        html = bs4.BeautifulSoup(driver.page_source, 'lxml')
        while True:
            try: 
                targets = html.findAll('article', {'role':'article', 'tabindex':'0'})
                hrefs = [
                    (*href, SITE) for href in
                    {(target.find('a', {'aria-haspopup':False}, href=True
                    ).get('href'),) for target in targets} - query
                    ] 
                break
            except sql.errors.OperationalError: continue
        while True:
            try: CURSOR.executemany(INSERT[1], hrefs); break
            except sql.errors.OperationalError: continue
        
        if not hrefs: 
            if retry == 2: break
            else: retry += 1
        else: retry = 0
            
        for _ in range(3):
            driver.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
        time.sleep(4)
                
    while True:
        try: DATAB.commit(); break
        except sql.errors.OperationalError: continue

def page_handler(driver, hrefs):
    
    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)   

        driver.get(f'https://twitter.com{href}')
        artist = href.split('/')[1]
        x, y, exif, = generate_tags(TYPE, [artist.lower()])

        for _ in range(3):
            try:
                time.sleep(1)
                html = bs4.BeautifulSoup(driver.page_source, 'lxml')
                images = html.findAll(href=re.compile(f'{href}/photo/.+'))
                images[0].findAll(alt=True)[0]
                images[-1].findAll(alt=True)[0]
            except IndexError:
                time.sleep(1)
                # for _ in range(3):
                #     try:
                #         html = bs4.BeautifulSoup(driver.page_source, 'lxml')
                #         # target = html.findAll(href=re.compile('https://help.twitter.com.+'))[0].parent.parent.parent
                #         images = html.findAll(
                #             'video', src=True, type_='video/mp4'#attrs={"type": "video/mp4"}
                #             )
                #         images[0].get('src'); images[-1].get('src')
                #     except IndexError: time.sleep(1)
                # try: 
                #     if 'video' == images[0].name: break
                # except: continue
            
        for image in images:
            try:
                image = image.findAll(alt=True)[0].get('src').replace('small', 'large')
                x = image.replace("?format=",".")
                name = join(
                    PATH, 'Images', SITE, 
                    f'{artist} - {x.split("/")[-1].split("&")[0]}'
                    )
            except:
                image = image.get('src')
                name = join(
                    PATH, 'Images', SITE,
                    f'{artist} - {image.split("/")[-1]}'
                    )
            hash = save_image(name, image, exif)
            if name.endswith('.png'): name = name.replace('.png', '.jpg')

            if len(images) == 1: 
                while True:
                    try:
                        CURSOR.execute(UPDATE[1], (name, hash, image, href))
                        DATAB.commit()
                        break
                    except sql.errors.OperationalError: continue
                    except sql.errors.IntegrityError:
                        try:
                            CURSOR.execute(UPDATE[1], (f'202 - {href}', hash, image, href))
                            DATAB.commit()
                            break
                        except sql.errors.IntegrityError: break
                        
            else: 
                while True:
                    try:
                        CURSOR.execute(UPDATE[2], (name, hash, image, href,SITE))
                        DATAB.commit()
                        break
                    except sql.errors.OperationalError: continue
        else: 
            if len(images) > 1: 
                while True:
                    try:
                        CURSOR.execute(DELETE, (href,))
                        DATAB.commit()
                        break
                    except sql.errors.OperationalError: continue 
        DATAB.commit()
        
def xpath_soup(element):
    """
    Generate xpath of soup element
    :param element: bs4 text or node
    :return: xpath as string
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        previous = itertools.islice(parent.children, 0, parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()

    return '/%s' % '/'.join(components)

def setup(initial=True):
    
    try:
        driver = get_driver(True)
        login(driver, SITE)
        if initial: initialize(driver)
        CURSOR.execute(SELECT[3], (SITE,))
        page_handler(driver, CURSOR.fetchall())
        driver.close()
    except WebDriverException:
        if input(f'{SITE}: Browser closed\nContinue?').lower() in 'yes':
            setup(False)
    DATAB.close()

if __name__ == '__main__':

    driver = get_driver(headless=True)
    login(driver, SITE)
    initialize(driver)
    driver.close()
    DATAB.close()
