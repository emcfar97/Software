import argparse, bs4, re, json
from . import CONNECT, WEBDRIVER, INSERT, SELECT, DELETE
from .utils import IncrementalBar, USER, ARTIST, save_image, get_hash, get_name, get_tags, generate_tags

SITE = 'nhentai'
COMIC = json.load(open(r'Webscraping\comic_data.json'))

def get_artist(text):

    targets = re.findall(r'[^[]*\[([^]]*)\]', text)
    targets = sum([i.split() for i in targets], [])
    targets = [i for i in targets if i not in ['decensored', 'digital']]
    targets = '_'.join([i.replace(',', '') for i in targets])

    return targets.replace('_)', ')')

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
    
def page_handler(hrefs):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        progress.next()
        
        cover = None
        content = DRIVER.get(f'https://{SITE}.net{href}')
        html = bs4.BeautifulSoup(content, 'lxml')
        
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

        for image in html.findAll('a', class_='gallerythumb'):
            
            try:
                content = DRIVER.get(f'https://{SITE}.net{image.get("href")}')
                image = bs4.BeautifulSoup(content, 'lxml')
                src = image.find(src=re.compile('.+galleries.+')).get('src')
                name = get_name(src)

                if cover is None: # if this is the first image
                    cover = name
                    COMIC[cover.name] = COMIC.get(
                        cover.name, {'imagedata': [], 'comics': []}
                        )
                
                if name.name in [i[0] for i in COMIC[cover.name]['comics']]: continue
                if not save_image(name, src, 1): break
            
                tags, rating = generate_tags(
                    general=get_tags(name, True), 
                    custom=True, rating=True
                    )
                hash_ = get_hash(name)

                COMIC[cover.name]['imagedata'].append(
                    (name.name, ' '.join(artists), tags,
                    rating, 3, hash_, src, SITE, href)
                    )
                COMIC[cover.name]['comics'].append(
                    (name.name, cover.name)
                    )
        
            except Exception as error:
                print('\n', error, href)
                break
            
        else:
            if cover is None: break
            imagedata = COMIC[cover.name]['imagedata']
            comics = COMIC[cover.name]['comics']

            if (
                MYSQL.execute(INSERT[3], imagedata, many=1) and
                MYSQL.execute(INSERT[4], comics, many=1)
                ):
                
                del COMIC[cover.name]
                MYSQL.execute(DELETE[5], (href,), commit=1)
                
            else:
                MYSQL.rollback()
                break
            
        json.dump(
            COMIC, 
            open(r'Webscraping\comic_data.json', 'w'),
            indent=4
            )

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
        
def main(initial=1, headless=True, mode=1):
    
    global MYSQL, DRIVER

    MYSQL = CONNECT()
        
    if mode == 1:
            
        DRIVER = WEBDRIVER(headless)
        
        if initial:
            query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
            hrefs = initialize(query)
            MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
                    
        page_handler(MYSQL.execute(SELECT[1], (SITE,), fetch=1))
    
    elif mode == 0:
        
        DRIVER = WEBDRIVER(headless, None)

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