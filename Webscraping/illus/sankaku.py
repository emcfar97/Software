SITE = 'sankaku'
MODE = {
    0:['idol', 'エラティカ ニ', 0],
    1:['chan', 'エラティカ 三', 1]
    }

def initialize(mode, url='?tags=fav%3Achairekakia', query=0):
    
    def next_page(pages):
        return 1
        try: return pages.get('next-page-url')
        except: return False

    if not query:
        CURSOR.execute(SELECT[0], (SITE,))
        query = CURSOR.fetchall()
    requests.get(f'https://{mode[0]}.sankakucomplex.com/{url}')
    html = bs4.BeautifulSoup(page_source, 'lxml')
    try: 
        hrefs = [
            (target.get('href'), mode[2], SITE) for target in 
            html.findAll('a', {'onclick': True}, href=re.compile('/p+'))
            if (target.get('href'),) not in query
            ]
        execute(INSERT[0], hrefs, 1)

        next = next_page(html.find('div', {'next-page-url': True}))   
        if hrefs and next: initialize(next, query)
    except: 
        time.sleep(60)   
        initialize(url, query)

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

        metadata = [
            '_'.join(tag.text.split()[:-2]) for tag in 
            html.findAll(class_='tag-type-medium')
            ]
        artists = [
            '_'.join(artist.text.split()[:-2]) for artist in 
            html.findAll(class_=re.compile('tag-type-(artist)|(idol)'))
            ]
        tags = [
            '_'.join(tag.text.split()[:-2]) for tag in 
            html.findAll(class_='tag-type-general')
            ]
        tags, rating, exif = generate_tags(
            artists, metadata, tags, True, True
            )
        
        image = f'https:{html.find(id="highres", href=True).get("href")}'
        name = get_name(imaimage.split('/')[-1].split('?e=')[0], mode[1])
        save_image(name, image, exif)
        hash_ = get_hash(name)

        try:
            execute(UPDATE[3], (
                name, f"{' '.join(artists)}", f' {tags} ', 
                rating, image, hash_, mode[2], href)
                )
        except sql.errors.IntegrityError:
            execute(UPDATE[3], (
                f'202 - {href}', f"{' '.join(artists)}", 
                f' {tags} ', rating, image, hash_, mode[2], href)
            )
        except (sql.errors.OperationalError, sql.errors.DatabaseError): continue
    
    progress(size, size, SITE)

def setup(initial=True, mode=1):
    
    try:
        if initial: initialize(MODE[mode])
        CURSOR.execute(SELECT[2], (SITE,))
        page_handler(CURSOR.fetchall(), MODE[mode])
    except Exception as error: print(f'{SITE}: {error}')

if __name__ == '__main__':
    
    from utils import *
    setup(1, mode=0)

else: from .utils import *