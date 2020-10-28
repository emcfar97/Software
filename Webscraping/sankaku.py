from . import CONNECT, INSERT, SELECT, UPDATE, DELETE, WEBDRIVER
from .utils import Progress, save_image, get_hash, get_name, get_tags, generate_tags
import time, bs4, requests, re
from PIL import ImageFile
from urllib.parse import urlparse
ImageFile.LOAD_TRUNCATED_IMAGES = True

SITE = 'sankaku'
MODE = [
    ['idol', 1],
    ['chan', 2]
    ]

def initialize(mode, url='?tags=fav%3Achairekakia', query=0):
    
    def next_page(pages):
        try: return pages.get('next-page-url')
        except: return False

    if not query:
         query = set(
            CONNECTION.execute(
                f'{SELECT[0]} AND type=%s', (SITE, mode[1]), fetch=1
                )
            )
    page_source = requests.get(
        f'https://{mode[0]}.sankakucomplex.com/{url}'
        ).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    try:
        hrefs = [
            (target.get('href'), mode[1], SITE) for target in 
            html.findAll('a', {'onclick': True}, href=re.compile('/p+'))
            if (target.get('href'),) not in query
            ]
        CONNECTION.execute(INSERT[0], hrefs, 2)
        
        next = next_page(html.find('div', {'next-page-url': True}))   
        if hrefs and next: initialize(mode, next, query)
    except:
        time.sleep(60)   
        initialize(mode, url, query)

    CONNECTION.commit()

def page_handler(hrefs, mode):

    if not hrefs: return
    progress = Progress(len(hrefs), SITE)

    for href, in hrefs:
        
        print(progress)
        
        page_source = requests.get(
            f'https://{mode[0]}.sankakucomplex.com{href}'
            ).content      
        html = bs4.BeautifulSoup(page_source, 'lxml')
        while html.find(text=re.compile('(Too many requests)|(Please slow down)')):
            time.sleep(60)
            page_source = requests.get(
                f'https://{mode[0]}.sankakucomplex.com{href}'
                ).content   
            html = bs4.BeautifulSoup(page_source, 'lxml')
            
        metadata = ' '.join(
            '_'.join(tag.text.split()[:-2]) for tag in 
            html.findAll(class_='tag-type-medium')
            )
        tags = ' '.join(
            '_'.join(tag.text.split()[:-2]) for tag in 
            html.findAll(class_='tag-type-general')
            )
        artists = [
            '_'.join(artist.text.split()[:-2]) for artist in 
            html.findAll(class_=re.compile('tag-type-artist|idol|studio'))
            ]
        
        try: 
            image = urlparse(
                f'https:{html.find(id="highres", href=True).get("href")}'
                )
        except AttributeError:
            if html.find(text='404: Page Not Found'): 
                CONNECTION.execute(DELETE[0], (href,), commit=1)
            continue
        
        name = get_name(image.path[12:], mode[1]-1, 0)        
        hash_ = get_hash(image.geturl())

        if len(tags.split()) < 10:
            save_image(name, image.geturl())
            tags = ' '.join((tags, get_tags(DRIVER, name)))
        tags, rating, exif = generate_tags(
            tags, metadata, True, artists, True
            )

        if save_image(name, image.geturl(), exif):
             
            CONNECTION.execute(
                UPDATE[3],
                (str(name), ' '.join(artists), tags, rating, image.geturl(), hash_, href), 
                commit=1
                )
    
    print(progress)

def start(mode=1, initial=True):
    
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER()
    mode = MODE[mode]

    if initial: 
        try: initialize(mode)
        except: pass
    page_handler(
        CONNECTION.execute(f'{SELECT[2]} AND type=%s',(SITE, mode[1]),fetch=1), 
        mode
        )
    DRIVER.close()
