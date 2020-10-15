import time
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import Progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests

SITE = 'blogspot'
url = 'http://publicnudityproject.blogspot.com/p/blog-page.html'

def initialize(url, query=0):
    
    def next_page(page):
             
        try: return page.get('href')
        except AttributeError: return False

    if not query: query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))

    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    hrefs = [
        (target.get('href'), 1, SITE) for target in 
        html.findAll('a', href=re.compile('.+://\d.bp.blogspot.com+'))
        if (target.get('href'),) not in query
        ]
    CONNECTION.execute(INSERT[0], hrefs, 1)
        
    next = next_page(html.find(title='Older Posts'))
    if hrefs and next: initialize(next, query)
    else: CONNECTION.commit()

def page_handler(hrefs):

    if not hrefs: return
    progress = Progress(len(hrefs), SITE)

    for href, in hrefs:
        
        print(progress)

        name = get_name(href, 0, hasher=1)
        if not save_image(name, href): continue
        tags, rating, exif = generate_tags(
            get_tags(DRIVER, name) + ' casual_nudity',
            custom=True, rating=True, exif=True
            )
        save_image(name, href, exif)
        hash_ = get_hash(name)
        
        CONNECTION.execute(UPDATE[3],
            (str(name), ' ', tags, rating, href, hash_, href),
            commit=1
            )

def start():

    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER()
    
    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')

    for page in html.findAll('li'): initialize(page.contents[0].get('href'))
    page_handler(CONNECTION.execute(SELECT[2], (SITE,), fetch=1))
        
    DRIVER.close()
