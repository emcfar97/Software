from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

SITE = 'gelbooru'
    
def initialize(driver, url='?page=favorites&s=view&id=173770&pid=0', query=0):
    
    def next_page(pages):
        
        try: return pages[pages.index(' ') + 3].get('href')
        except IndexError: return False

    if not query:
        execute(SELECT[0], (SITE,))
        query = CURSOR.fetchall()
    driver.get(f'https://gelbooru.com/index.php{url}')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')

    hrefs = [
        (target.get('href'), 1, SITE) for target in 
        html.findAll('a', id=re.compile(r'p\d+'), href=True)
        if (target.get('href'),) not in query
        ]
    execute(INSERT[0], hrefs, 1)
        
    next = next_page(html.find(id='paginator').contents)   
    if hrefs and next: initialize(driver, next, query)
    
    DATAB.commit()

def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):

        progress(size, num, SITE)
        driver.get(f'https://gelbooru.com/{href}')
        html = bs4.BeautifulSoup(driver.page_source, 'lxml')

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
        
        image = driver.find_element_by_link_text(
            'Original image'
            ).get_attribute('href')
        name = get_name(image.split('/')[-1], 1)
        save_image(name, image, exif)
        hash_ = get_hash(name)
        
        try:
            execute(UPDATE[3], (
                name, f"{' '.join(artists)}", tags, 
                rating, image, hash_, 1, href),
                commit=1
                )
        except sql.errors.IntegrityError:
            execute(UPDATE[3], (
                f'202 - {href}', f"{' '.join(artists)}", 
                tags, rating, image, hash_, 1, href),
                commit=1
                )
        except (sql.errors.OperationalError, sql.errors.DatabaseError): continue

    progress(size, size, SITE)

def setup(initial=True):
    
    try:
        driver = get_driver(headless=0)
        login(driver, SITE)
        if initial: initialize(driver)
        CURSOR.execute(SELECT[2],(SITE,))
        page_handler(driver, CURSOR.fetchall())
    except Exception as error: print(f'{SITE}: {error}')

if __name__ == '__main__':
    
    from utils import *
    setup()

else: from .utils import *

