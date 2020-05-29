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
        execute(f'{SELECT[0]} AND type=%s', (SITE, mode[1]))
        query = CURSOR.fetchall()
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

def page_handler(hrefs, mode):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):

        progress(size, num, SITE)
        page_source = requests.get(
            f'https://{mode[0]}.sankakucomplex.com{href}'
            ).content      
        html = bs4.BeautifulSoup(page_source, 'lxml')
        if html.find(text=re.compile('(Too many requests)|(Please slow down)')):
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
            html.findAll(class_=re.compile('tag-type-(artist)|(idol)'))
            ]
        tags, rating, exif = generate_tags(
            tags, metadata, True, artists, True
            )
        
        try:
            image = f'https:{html.find(id="highres", href=True).get("href")}'
            name = get_name(image.split('/')[-1].split('?e=')[0], mode[1])
            save_image(name, image, exif)
            hash_ = get_hash(name)
        except: continue

        try:
            execute(UPDATE[3], (
                name, f"{' '.join(artists)}", f' {tags} ', 
                rating, image, hash_, mode[1], href),
                commit=1
                )
        except sql.errors.IntegrityError:
            execute(UPDATE[3], (
                f'202 - {href}', f"{' '.join(artists)}", 
                f' {tags} ', rating, image, hash_, mode[1], href),
                commit=1
                )
        except (sql.errors.OperationalError, sql.errors.DatabaseError): continue
    
    progress(size, size, SITE)

def setup(initial=True, mode=1):
    
    mode = MODE[mode]

    try:
        if initial: initialize(mode)
        CURSOR.execute(f'{SELECT[2]} AND type=%s', (SITE, mode[1]))
        page_handler(CURSOR.fetchall(), mode)
    except Exception as error: print(f'{SITE}: {error}')

if __name__ == '__main__':
    
    from utils import *
    setup(mode=0)

else: from .utils import *