from .. import CONNECT, WEBDRIVER, INSERT, SELECT, DELETE
from ..utils import IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests

SITE = 'elitebabes'

def initialize(url=1, query=0):

    def next_page(page):
                
        try: return page.contents[0].get('href').split('/')[-2]
        except IndexError: return False

    if not query:
        query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))

    DRIVER.get(f'https://www.{SITE}.com/my-favorite-galleries/page/{url}/')
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (href, SITE) for target in
        html.find(class_='gallery-a e').findAll(href=True)
        if (
            href := target.get('href').split('/')[-2],
            ) not in query
        ]

    next = next_page(html.find(class_='next'))
    if hrefs and next: return hrefs + initialize(next, query)
    else: return hrefs

def page_handler(hrefs):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        page_source = requests.get(f'https://www.{SITE}.com/{href}')
        html = bs4.BeautifulSoup(page_source.content, 'lxml')
        try:
            artist = html.find(href=re.compile(
                f'https://www.{SITE}.com/model/.+'
                )).get('href')
            artist = artist.split('/')[-2]
        except AttributeError:
            artist = html.find(class_='unlinkedtag').text
        
        images = html.find(
            class_=re.compile('list-(justified-container|gallery a css)')
            )

        for image in images.findAll('a'):

            src = image.get('href')
            try: name = get_name(src)
            except: continue
            if not save_image(name, src): break

            tags, rating, exif = generate_tags(
                general=get_tags(DRIVER, name, True), 
                custom=True, rating=True, exif=True
                )
            save_image(name, src, exif)
            hash_ = get_hash(name)

            MYSQL.execute(INSERT[3],
                (name.name, artist.replace('-', '_'), tags, 
                rating, 1, hash_, src, SITE, href), 
                )
        else: MYSQL.execute(DELETE[0], (href,), commit=1)
    
        progress.next()
    print()

def start(initial=True, headless=True):
        
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)

    if initial: 
        MYSQL.execute(INSERT[0], initialize(), many=1, commit=1)
    page_handler(MYSQL.execute(SELECT[2], (SITE,), fetch=1))
    DRIVER.close()