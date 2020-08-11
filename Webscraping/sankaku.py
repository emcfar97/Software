from selenium.common.exceptions import WebDriverException
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

SITE = 'sankaku'
MODE = {
    0:['idol', 0],
    1:['chan', 1]
    }

def initialize(mode, url='?tags=fav%3Achairekakia', query=0):
    
    def next_page(pages):
        try: return pages.get('next-page-url')
        except: return False

    if not query:
        query = execute(f'{SELECT[0]} AND type=%s', (SITE, mode[1]), fetch=1)
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
        execute(INSERT[0], hrefs, 1)
        
        next = next_page(html.find('div', {'next-page-url': True}))   
        if hrefs and next: initialize(mode, next, query)
    except:
        time.sleep(60)   
        initialize(mode, url, query)

    DATAB.commit()

def page_handler(driver, hrefs, mode):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        
        progress(size, num, SITE)
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
        image = f'https:{html.find(id="highres", href=True).get("href")}'
        name = get_name(image.split('/')[-1].split('?e=')[0], mode[1])
            
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
        if len(tags.split()) < 10:
            save_image(name, image)
            tags = tags + get_tags(driver, name)
        tags, rating, exif = generate_tags(
            tags, metadata, True, artists, True
            )        
        if not save_image(name, image, exif): continue
        hash_ = get_hash(name)

        try:
            execute(UPDATE[3], (
                name, f"{' '.join(artists)}", tags, 
                rating, image, hash_, href),
                commit=1
                )
        except sql.errors.IntegrityError:
            execute('DELETE FROM imageData WHERE href=%s', (href,), commit=1)
        except sql.errors.DatabaseError: continue
    
    progress(size, size, SITE)

def setup(initial=True, mode=1):
    
    mode = MODE[mode]

    try:
        driver = get_driver(True)
        if initial: initialize(mode)
        page_handler(driver, execute(f'{SELECT[2]} AND type=%s', (SITE, mode[1]), fetch=1), mode)
    except WebDriverException:
        user = input(f'\n{SITE}: Browser closed\nContinue? ')
        if user.lower() in 'yes': setup(False)
    except Exception as error: print(f'\n{SITE}: {error}')
    
    try: driver.close()
    except: pass

if __name__ == '__main__':
    
    from utils import *
    setup(mode=1)

else: from .utils import *