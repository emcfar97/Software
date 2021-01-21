from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import PATH, Progress, bs4, re
import time
import itertools
from selenium.webdriver.common.keys import Keys

SITE = 'twitter'

def initialize(url, retry=0):

    query = set(CONNECTION.execute(SELECT[1], (SITE,), fetch=1))
    DRIVER.get(f'https://twitter.com/{url}/likes')
    time.sleep(4)    

    while True:

        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        targets = html.findAll('article', {'role':'article', 'tabindex':'0'})
        hrefs = [
            (*href, SITE) for href in
            {(target.find('a', {'aria-haspopup':False}, href=True
            ).get('href'),) for target in targets} - query
            ] 
        CONNECTION.execute(INSERT[1], hrefs, many=1)
        
        if not hrefs: 
            if retry >= 2: break
            else: retry += 1
        else: retry = 0
            
        for _ in range(3):
            DRIVER.find('html', Keys.PAGE_DOWN, type_=6)
        time.sleep(4)
                
    CONNECTION.commit()

def page_handler(hrefs):
    
    if not hrefs: return
    progress = Progress(len(hrefs), SITE)

    for href, in hrefs:
        
        print(progress) 

        DRIVER.get(f'https://twitter.com{href}')

        for _ in range(4):
            try:
                time.sleep(2)
                html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                if login := html.find(href='/login'):
                    xpath = xpath_soup(login)
                    DRIVER.find(xpath, click=True, type_=1)
                    DRIVER.back()
                    time.sleep(2)

                target = html.find('div', style=re.compile('padding-top: .+'))
                images = target.findAll(alt='Image',
                    src=re.compile('https://pbs.twimg.com/(card_img)|(media).+')
                    )
                images[0].get('src'); images[-1].get('src')
                artist = href.split('/')[1]

            except (IndexError, AttributeError, TypeError): 
                try:
                    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                    target = html.find('div', style=re.compile('padding-top: .+'))
                    images = target.findAll('video',
                        src=re.compile('https://video.twimg.com/tweet_video.+')
                        )
                    images[0].get('src'); images[-1].get('src')
                    artist = href.split('/')[1]

                except (IndexError, AttributeError, TypeError): continue

        if len(images) != 1: continue
        for image in images:

            image = image.get('src').replace('small', 'large')
            name = image.replace('?format=', '.').split('/')[-1]
            name = PATH / 'Images' / SITE / f'{artist} - {name.split("&")[0]}'

            CONNECTION.execute(UPDATE[2], (name, hash_, image, href), commit=1)
                              
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

def start(initial=True, headless=True):
    
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    url = DRIVER.login(SITE)
    if initial: initialize(url)
    page_handler(CONNECTION.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()