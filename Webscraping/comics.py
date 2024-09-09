import argparse, bs4, requests, threading, re, json, time
from . import CONNECT, WEBDRIVER, INSERT, SELECT, DELETE, get_credentials
from .utils import IncrementalBar, USER, ARTIST, HEADERS, save_image, get_hash, get_name, get_tags, generate_tags

SITE = 'nhentai'
COMIC = json.load(open(r'Webscraping\comic_data.json'))

def get_artist(text):

    targets = re.findall(r'[^[]*\[([^]]*)\]', text)
    targets = sum([i.split() for i in targets], [])
    targets = [i for i in targets if i not in ['decensored', 'digital']]
    targets = '_'.join([i.replace(',', '') for i in targets])

    return targets.replace('_)', ')')

def get_session():
    
    sess = requests.Session()
    sess.headers.update(HEADERS)
    
    login_data = {
        'username': get_credentials(SITE, 'username'),
        'password': get_credentials(SITE, 'password'),
        'crsf_token': get_credentials(SITE, 'csrf_token'),
        'dest': 'https://www.nhentai.com',
        }
    
    sess.post('https://nhentai.net/login/?next=/', data=login_data)
    
    return sess

def initialize(query, page='/favorites/?page=1'):
    
    def next_page(pages):

        try: return pages.find(class_='next').get('href')
        except AttributeError: return False

    content = DRIVER.get(f'https://{SITE}.net{page}')
    html = bs4.BeautifulSoup(content, 'lxml')
    hrefs = [
        (href, SITE, 3) for target in 
        html.findAll('a', class_='cover', href=True)
        if (href:=target.get('href'),) not in query
        ]
        
    next = next_page(html.find(class_='pagination'))
    if hrefs and next: return hrefs + initialize(query, next)
    else: return hrefs
    
def page_handler(hrefs, limit=30):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)
    lock = threading.Lock()

    for href, in hrefs:
        
        progress.next()
        
        try: reponse = requests.get(f'https://{SITE}.net{href}')
        except: continue
        html = bs4.BeautifulSoup(reponse.content, 'lxml')
        
        if html.find(text=re.compile("404 – Not Found")):
            MYSQL.execute(DELETE[5], (href,), commit=1)
            continue
        
        target = html.findAll(href=re.compile('/(artist|group)/.+'))
        artists = [
            artist.get('href').split('/')[-2].replace('-', '_')
            for artist in target
            ]
        artists = [
            ARTIST.get(artist, [artist])[0] for artist in artists
            ]

        gallery = []
        images = html.findAll('a', class_='gallerythumb')
        step = len(images) // limit if len(images) > limit else 1
        
        for images in [images[i::step] for i in range(step)]:
            
            threads = [
                threading.Thread(
                    target=url_handler, 
                    args=(lock, gallery, image, artists, href)
                    ) 
                for image in images
                ]
            
            for thread in threads: thread.start()
            for thread in threads: thread.join()
            
            if None in gallery: break; continue
        
        if not gallery or None in gallery: continue
        gallery.sort(key=lambda x: int(*re.findall('.+/(\d+).jpg', x[6])))
        comics = [(gallery[0][0], image[0]) for image in gallery]
        
        if (
            MYSQL.execute(INSERT[3], gallery, many=1) and
            MYSQL.execute(INSERT[4], comics, many=1)
            ):
            
            MYSQL.execute(DELETE[5], (href,), commit=1)
            
        else: MYSQL.rollback(); break

    print()

def file_handler(folders):
    
    import send2trash
    
    if not (length := len(folders)): return
    progress = IncrementalBar('Comic', max=length)

    for folder in folders:
        
        progress.next()
        artist = ' '.join(
            ARTIST.get(artist, [artist])[0] for artist in 
            [get_artist(folder.stem.lower())]
            )
        images = [
            (
                num, get_hash(file), name:=get_name(file),
                name.write_bytes(file.read_bytes())
                )
            for num, file in enumerate(folder.iterdir())
            ]
        cover = images[0][2]
        imagedata, comics = [], []
        
        for num, hash_, image, _ in images:

            tags, rating = generate_tags(
                general=get_tags(image), 
                custom=True, rating=True
                )
            imagedata.append(
                (image.name, artist, tags, rating, 
                3, hash_, None, None, None)
                )
            comics.append((image.name, cover.name))
            
        else:
            
            if (
                MYSQL.execute(INSERT[3], imagedata, many=1) and
                MYSQL.execute(INSERT[4], comics, many=1)
                ):
                MYSQL.commit()
                
            else:
                MYSQL.rollback()
                break

        MYSQL.commit()
        send2trash.send2trash(str(folder))
    
def url_handler(lock, gallery, image, artists, href, backoff=1):

    try:        
        response = requests.get(f'https://{SITE}.net{image.get("href")}')
        while response.status_code == 429: # Too many requests
            backoff += backoff
            time.sleep(backoff)
            response = requests.get(f'https://{SITE}.net{image.get("href")}')
        image = bs4.BeautifulSoup(response.content, 'lxml')
        src = image.find(src=re.compile('.+galleries.+')).get('src')
        name = get_name(src)
        
        if not name.exists():
            if not save_image(name, src, 1):
                
                lock.acquire()
                gallery.append(None)
                lock.release()
    
        tags, rating = generate_tags(
            general=get_tags(name, True), 
            custom=True, rating=True
            )
        hash_ = get_hash(name)

        lock.acquire()
        gallery.append(
            (name.name, ' '.join(artists), tags, 
            rating, 3, hash_, src, SITE, href)
            )
        lock.release()

    except Exception as error:
        
        lock.acquire()
        gallery.append(None)
        lock.release()

def main(initial=1, headless=True, mode=1):
    
    global MYSQL, DRIVER

    MYSQL = CONNECT()
    
    if mode == 1:
            
        if initial:
            
            DRIVER = WEBDRIVER(headless, profile=mode)
            
            query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
            hrefs = initialize(query)
            MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
            
            DRIVER.close()
                    
        page_handler(MYSQL.execute(SELECT[1], (SITE,), fetch=1))
    
    elif mode == 0:
        
        DRIVER = WEBDRIVER(headless, profile=mode)
        
        path = USER / r'Downloads\Images\Comics'
        file_handler(list(path.iterdir()))

        DRIVER.close()

if __name__ == '__main__':

    from Webscraping import get_starred
    
    parser = argparse.ArgumentParser(
        prog='comics', 
        )
    parser.add_argument(
        '-i', '--init', type=int,
        help='Initial argument (default 1)',
        default=1
        )
    parser.add_argument(
        '-he', '--head', type=bool,
        help='Headless argument (default True)',
        default=True
        )
    parser.add_argument(
        '-m', '--mode', type=int,
        help='Mode argument (default 1)',
        default=1
        )
    
    args = parser.parse_args()

    main(args.init, args.head, args.mode)

    get_starred()