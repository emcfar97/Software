from .. import CONNECT, WEBDRIVER, INSERT, SELECT, DELETE
from ..utils import IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests

SITE = 'elitebabes'

def initialize(url=1, query=0):

    def next_page(page):
                
        try: return page.contents[0].get('href').split('/')[-2]
        except IndexError: return False

    if not query:
        query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))

    DRIVER.get(f'https://www.{SITE}.com/my-favorite-galleries/page/{url}/')
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (href, SITE) for target in 
        html.find(class_='gallery-a e').findAll(href=True)
        if (
            href := re.sub('(.+)-\d+', r'\1', target.get('href').split('/')[-2]),
            ) not in query
        ]

    next = next_page(html.find(class_='next'))
    if hrefs and next: return hrefs + initialize(next, query)
    else: return hrefs

def page_handler(hrefs):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=len(hrefs))

    for href, in hrefs:
        
        page_source = requests.get(f'https://www.{SITE}.com/{href}')
        try:
            html = bs4.BeautifulSoup(page_source.content, 'lxml')
            artist = html.find(href=re.compile(
                f'https://www.{SITE}.com/model/.+'
                )).get('href')
            artist = artist.split('/')[-2].replace('-', '_')
            images = html.find(class_='list-justified-container').findAll('a')
        except: continue

        for image in images:

            src = image.get('href')
            name = get_name(src, 0, 1)
            if not save_image(name, src): break

            tags, rating, exif = generate_tags(
                general=get_tags(DRIVER, name, True), 
                custom=True, rating=True, exif=True
                )
            save_image(name, src, exif)
            hash_ = get_hash(name)

            CONNECTION.execute(INSERT[3],
                (name.name, artist, tags, rating, 1, hash_, src, SITE, href), 
                )
        else: CONNECTION.execute(DELETE[0], (href,), commit=1)
    
        progress.next()

def start(initial=True, headless=True):
        
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(headless)

    if initial: 
        CONNECTION.execute(INSERT[0], initialize(), many=1, commit=1)
    page_handler(CONNECTION.execute(SELECT[2], (SITE,), fetch=1))
    DRIVER.close()