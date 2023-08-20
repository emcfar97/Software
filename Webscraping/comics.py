import argparse, bs4, json
from . import CONNECT, INSERT, SELECT, DELETE, WEBDRIVER
from .utils import re, IncrementalBar, USER, ARTIST, save_image, get_hash, get_name, get_tags, generate_tags

SITE = 'nhentai'

def get_artist(text):

    targets = re.findall(r'[^[]*\[([^]]*)\]', text)
    targets = sum([i.split() for i in targets], [])
    targets = [i for i in targets if i not in ['decensored', 'digital']]
    targets = '_'.join([i.replace(',', '') for i in targets])

    return targets.replace('_)', ')')

def initialize(page='/favorites/?page=1', query=None):
    
    def next_page(pages):

        try: return pages.find(class_='next').get('href')
        except AttributeError: return False

    DRIVER.get(f'https://{SITE}.net{page}')
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (href, SITE) for target in 
        html.findAll('a', class_='cover', href=True)
        if (href:=target.get('href'),) not in query
        ]
        
    next = next_page(html.find(class_='pagination'))
    if hrefs and next: return hrefs + initialize(next, query)
    else: return hrefs
    
def page_handler(hrefs):
    
    from hentai import Hentai, Format

    if not hrefs: return
    comic_records = json.load(open(r'Webscraping\comic_data.json'))
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        progress.next()
        
        comic = Hentai(int(href.split('/')[2]))
        # DRIVER.get(f'/https://{SITE}.net{href}')
        # html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        
        cover = None
        target = html.findAll(href=re.compile('/artist/.+'))
        if target is None: target = html.findAll(href=re.compile('/group/.+'))
        artists = [
            artist.get('href').split('/')[-2].replace('-', '_')
            for artist in target
            ]
        artists = [
            ARTIST.get(artist, [artist])[0] for artist in artists
            ]

        for image in html.findAll('a', class_='gallerythumb'):
            
            try:
                DRIVER.get(f'https://{SITE}.net{image.get("href")}')
                image = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                src = image.find(src=re.compile('.+galleries.+')).get('src')
                name = get_name(src)

                if cover is None:
                    cover = name
                    comic_records[cover.name] = comic_records.get(
                        cover.name, {'imagedata': [], 'comics': []}
                        )
                if name.name in [i[0] for i in comic_records[cover.name]['comics']]: continue
                if not save_image(name, src):
                    break
            
                tags, rating = generate_tags(
                    general=get_tags(name, True), 
                    custom=True, rating=True
                    )
                
                save_image(name, src)
                hash_ = get_hash(name)

                comic_records[cover.name]['imagedata'].append(
                    (name.name, ' '.join(artists), tags,
                    rating, 3, hash_, src, SITE, href)
                    )
                comic_records[cover.name]['comics'].append(
                    (name.name, cover.name)
                    )
        
            except Exception as error:
                print('\n', error, href)
                break
            
        else:
            if cover is None: break
            imagedata = comic_records[cover.name]['imagedata']
            comics = comic_records[cover.name]['comics']

            if (
                MYSQL.execute(INSERT[3], imagedata, many=1) and
                MYSQL.execute(INSERT[4], comics, many=1)
                ):
                
                del comic_records[cover.name]
                MYSQL.execute(DELETE[0], (href,), commit=1)
                
            else:
                MYSQL.rollback()
                break
            
        json.dump(
            comic_records, 
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
        
    if mode:
            
        DRIVER = WEBDRIVER(headless)
        
        if initial:
            query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
            hrefs = initialize(query=query)
            MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
                    
        page_handler(MYSQL.execute(SELECT[1], (SITE,), fetch=1))
    
    else:
        
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