from selenium.common.exceptions import WebDriverException
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

SITE = 'gelbooru'
    
def initialize(driver, url='?page=favorites&s=view&id=173770&pid=0', query=0):
    
    def next_page(pages):

        try: return pages[pages.index(' ') + 3].get('href')
        except IndexError: return False

    if not query:
        query = CONNECTION.execute(SELECT[0], (SITE,), fetch=1)
        
    driver.get(f'https://gelbooru.com/index.php{url}')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')

    hrefs = [
        (target.get('href'), 1, SITE) for target in 
        html.findAll('a', id=re.compile(r'p\d+'), href=True)
        if (target.get('href'),) not in query
        ]
    CONNECTION.execute(INSERT[0], hrefs, 1, commit=1)
        
    next = next_page(html.find(id='paginator').contents)   
    if hrefs and next: initialize(driver, next, query)
    
    DATAB.commit()

def page_handler(hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):

        progress(size, num, SITE)
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
        artists = [
            '_'.join(artist.text.split(' ')[1:-1]) for artist in 
            html.findAll(class_='tag-type-artist')
            ]
        tags, rating, exif = generate_tags(
            tags, metadata, True, artists, True
            )
        
        image = html.find(href=True, text='Original image').get('href')
        name = get_name(image.split('/')[-1], 1)
        if not save_image(name, image, exif): continue
        hash_ = get_hash(name)
        
        try:
            CONNECTION.execute(UPDATE[3], (
                name, f"{' '.join(artists)}", tags, rating, image, hash_, href
                ), commit=1
                )
        except sql.errors.IntegrityError:
            CONNECTION.execute('DELETE FROM imageData WHERE href=%s', (href,), commit=1)
        except sql.errors.DatabaseError: continue

    progress(size, size, SITE)

def setup(initial=True):
    
    try:
        driver = WEBDRIVER(headless=True)
        login(driver, SITE)
        if initial: initialize(driver)
        page_handler(CONNECTION.execute(SELECT[2], (SITE,), fetch=1))
    except Exception as error: print(f'\n{SITE}: {error}')

    finally: driver.close()

if __name__ == '__main__':
    
    from utils import *
    setup()

else: from ..utils import login

