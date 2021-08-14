import argparse, time
from . import CONNECT, SELECT, UPDATE, DELETE, WEBDRIVER
from .utils import IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, re, ARTIST

SITE = 'sankaku'
MODE = [
    ['idol', 1],
    ['chan', 2]
    ]

def initialize(mode, url, query=0):
    
    def next_page(page):
        try: return page.get('next-page-url')
        except: return False

    if not query:
        query = set(
            MYSQL.execute(
                f'{SELECT[0]} AND type=%s', (SITE, mode[1]), fetch=1
                )
            )
    page_source = requests.get(
        f'https://{mode[0]}.sankakucomplex.com/{url}'
        )
    html = bs4.BeautifulSoup(page_source.content, 'lxml')
    try:
        hrefs = [
            (target.get('href'), mode[1], SITE) for target in 
            html.findAll('a', {'onclick': True}, href=re.compile('/p+'))
            if (target.get('href'),) not in query
            ]
        
        next = next_page(html.find('div', {'next-page-url': True})) 
        if hrefs and next: return hrefs + initialize(mode, next, query)
        else: return hrefs
    except:
        time.sleep(60)   
        initialize(mode, url, query)

def page_handler(hrefs, mode):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        progress.next()
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
        try: image = f'https:{html.find(id="highres", href=True).get("href")}'
        except AttributeError:
            if html.find(text='404: Page Not Found'): 
                MYSQL.execute(DELETE[0], (href,), commit=1)
            continue
            
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

        name = get_name(image.split('/')[-1].split('?e=')[0], 0)
        if len(tags.split()) < 10 and save_image(name, image):
            tags += ' ' + get_tags(DRIVER, name)
        tags, rating, exif = generate_tags(
            tags, metadata, True, artists, True
            )
        tags = tags.encode('ascii', 'ignore').decode()

        artists = [ARTIST.get(artist, [artist])[0] for artist in artists]
        artists = ' '.join(artists).encode('ascii', 'ignore').decode()

        hash_ = get_hash(image, 1)

        if MYSQL.execute(UPDATE[0], (
            name.name, artists, tags, rating, mode[1], image, hash_, href
            )):
            if save_image(name, image, exif): MYSQL.commit()
            else: MYSQL.rollback()
    
    print()

def start(initial=True, headless=True, mode=1):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    mode = MODE[mode]

    if initial: 
        url = DRIVER.login(SITE)
        hrefs = initialize(mode, url)
        MYSQL.execute(
            'INSERT INTO imagedata(href, type, site) VALUES(%s, %s, %s)', hrefs, many=1, commit=1
            )
    page_handler(
        MYSQL.execute(
            f'{SELECT[2]} AND type=%s', (SITE, mode[1]), fetch=1
            ), 
        mode
        )
    DRIVER.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='sankaku', 
        )
    parser.add_argument(
        '-i', '--init', type=int,
        help='Initial argument (default 1)',
        default=1
        )
    parser.add_argument(
        '-he', '--head', type=int,
        help='Headless argument (default 1)',
        default=1
        )
    parser.add_argument(
        '-m', '--mode', type=int,
        help='Mode argument (default 1)',
        default=1
        )
    
    args = parser.parse_args()
    
    start(args.initial, args.head, args.mode)
