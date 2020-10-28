from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import Progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests
import time

SITE = 'elitebabes'

def initialize(url='/my-favorite-galleries/page/1/', query=0):
    
    def next_page(page):
             
        try: return page.contents[0].get('href')[26:]
        except IndexError: return False

    if not query:
        query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))

    DRIVER.get(f'https://www.{SITE}.com{url}')
    html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
    targets = html.find('ul', class_='gallery-a e')
    
    for target in targets.findAll(href=True, title=True, class_=False):
        
        page_source = requests.get(target.get('href')).content
        page = bs4.BeautifulSoup(page_source, 'lxml')
        try: artist = page.find(
            href=re.compile('.+/model/.+')
            ).text.lower().replace(' ', '_')
        except AttributeError: artist = page.find(
            class_='unlinkedtag'
            ).text.lower().replace(' ', '_')            

        hrefs = [
            (f' {artist} ', 1, image.get('href'), SITE) for image in 
            page.findAll('a', href=re.compile('https://k5x5n5g8.+'))
            if (image.get('href'),) not in query
            ]
        CONNECTION.execute(INSERT[3], hrefs, 1)
        
    next = next_page(html.find(class_='next'))
    if hrefs and next: initialize(next, query)
    
    CONNECTION.commit()
    
def page_handler(hrefs):

    if not hrefs: return
    progress = Progress(len(hrefs), SITE)

    for (image, artist) in hrefs:
        
        print(progress)

        name = get_name(image, 0, 1)
        save_image(name, image)
        tags = get_tags(DRIVER, name)
        tags, rating, exif = generate_tags(
            tags, custom=True, artists=artist, rating=True
            )
        hash_ = get_hash(image) 
    
        CONNECTION.execute(UPDATE[3].replace('href', 'src'), 
            (name, artist, tags, rating, image, hash_, image),
            )
        if save_image(name, image, exif): CONNECTION.commit()
    
    print(progress)

def setup(initial=True):
    
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER()
    
    DRIVER.login(SITE)
    if initial: initialize()
    page_handler(DRIVER, CONNECTION.execute(SELECT[2].replace('href', 'src, artist'), (SITE,), fetch=1))
    DRIVER.close()
