from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import Progress, save_image, get_hash, get_name, generate_tags, bs4, requests, re
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

SITE = 'gelbooru'
    
def initialize(url, query=0):
    
    def next_page(pages):

        try: return pages[pages.index(' ') + 3].get('href')
        except IndexError: return False

    if not query:
        query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))
        
    DRIVER.get(f'https://gelbooru.com/index.php{url}')
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')

    hrefs = [
        (target.get('href'), SITE) for target in 
        html.findAll('a', id=re.compile(r'p\d+'), href=True)
        if (target.get('href'),) not in query
        ]
    CONNECTION.execute(INSERT[0], hrefs, many=1)
        
    next = next_page(html.find(id='paginator').contents)   
    if hrefs and next: initialize(next, query)
    
    CONNECTION.commit()

def page_handler(hrefs):

    if not hrefs: return
    progress = Progress(len(hrefs), SITE)

    for href, in hrefs:
        
        print(progress)
        page_source = requests.get(f'https://gelbooru.com/{href}').content
        html = bs4.BeautifulSoup(page_source, 'lxml')

        metadata = ' '.join(
            '_'.join(tag.text.split(' ')[1:-1]) for tag in 
            html.findAll(class_='tag-type-metadata')
            )
        tags = ' '.join(
            '_'.join(tag.text.split(' ')[1:-1]) for tag in 
            html.findAll(class_='tag-type-general')
            )
        type_ = 1 if 'photo_(medium)' in tags else 2
        artists = [
            '_'.join(artist.text.split(' ')[1:-1]) for artist in 
            html.findAll(class_='tag-type-artist')
            ]
        tags, rating, exif = generate_tags(
            tags, metadata, True, artists, True
            )
        
        image = html.find(href=True, text='Original image').get('href')
        name = get_name(image.split('/')[-1], type_-1, 0)
        hash_ = get_hash(image, 1)
        
        if CONNECTION.execute(UPDATE[0], (
            name.name, ' '.join(artists), tags, rating, type_, image, hash_, href
            )):
            if save_image(name, image, exif): CONNECTION.commit()
            else: CONNECTION.rollback()

    print(progress)

def start(initial=True):
    
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER()
    
    if initial: 
        url = DRIVER.login(SITE)
        initialize(url)
    DRIVER.close()
    page_handler(CONNECTION.execute(SELECT[2], (SITE,), fetch=1))
