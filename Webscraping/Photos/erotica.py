
from .. import CONNECT, WEBDRIVER, INSERT
from ..utils import Progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests

SITE = 'metarthunter', 'femjoyhunter', 'elitebabes'

def page_handler(hrefs, artist):

    progress = Progress(len(hrefs), 'Images')

    for href in hrefs:
        
        print(progress)

        src = href.get('href')
        if (name:=get_name(src, 0, 1)).exists(): continue
        if not save_image(name, src): continue

        tags, rating, exif = generate_tags(
            general=get_tags(DRIVER, name), 
            custom=True, rating=True, exif=True
            )
        save_image(name, src, exif)
        artist = artist.replace('-', '_')
        hash_ = get_hash(name)

        CONNECTION.execute(INSERT[3], 
            (name.name, artist, tags, rating, 1, hash_, src, SITE), 
            commit=1
            )
    
    print(progress)

def next_page(page):
             
    try: return page.contents[0].get('href').split('/')[-2]
    except IndexError: return False

def start(mode, page=1):
        
    global CONNECTION, DRIVER, SITE
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(0)
    SITE = SITE[mode]

    DRIVER.login(SITE)
    while page:

        DRIVER.get(f'https://www.{SITE}.com/my-favorite-galleries/page/{page}/')
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        
        for target in html.find(class_='gallery-a e').findAll(href=True):
            
            page_source = requests.get(target.get('href'))
            page = bs4.BeautifulSoup(page_source.content, 'lxml')
            images = page.find(class_='list-justified-container')
            artist = page.find(href=re.compile(
                f'https://www.{SITE}.com/model/.+'
                )).get('href')

            page_handler(images.findAll('a'), artist.split('/')[-2])

        page = next_page(html.find(class_='next'))

    DRIVER.close()