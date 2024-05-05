import argparse, bs4, re, time
from . import CONNECT, INSERT, SELECT, DELETE, WEBDRIVER
from .utils import ARTIST, REPLACE, IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags

SITE = 'sankaku'
MODE = [
    ['idol', 1],
    ['chan', 2]
    ]
EXCESSIVE = '(Too many requests)|(Please slow down)'
DELETION = '(404: Page Not Found)|(This post was deleted)'

def initialize(mode, url, query):
    
    def next_page(page):
        try: 
            next_url = page.get('next-page-url')
            next_page, = re.findall('page=\d+', next_url)
            return re.sub('page=\d+', next_page, url)
        
        except: return False

    DRIVER.get(f'https://{mode[0]}.sankakucomplex.com/{url}', wait=2)
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    target = html.find('div', class_='content')
    try:
        hrefs = [
            (href.get('href'), SITE, mode[1]) for href in 
            target.findAll('a', href=re.compile('/post/+'))
            if (href.get('href'),) not in query
            ]
        
        next = next_page(html.find('div', {'next-page-url': True}))
        if hrefs and next: return hrefs + initialize(mode, next, query)
        else: return hrefs
    except:
        time.sleep(60)   
        return initialize(mode, url, query)

def page_handler(hrefs, mode):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs[::-1]:
        
        progress.next()
        DRIVER.get(f'https://{mode[0]}.sankakucomplex.com{href}')
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        
        while html.find(text=re.compile(EXCESSIVE)):
            time.sleep(60)
            DRIVER.get(f'https://{mode[0]}.sankakucomplex.com{href}')  
            html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
            
        try:
            src = html.find(id="highres", href=True)
            image = f'https:{src.get("href")}'
        except AttributeError:
            if html.find(text=re.compile(DELETION)): 
                MYSQL.execute(DELETE[4], (href, mode[1]), commit=1)
            continue
        
        # get tags
        metadata = ' '.join(
            '_'.join(tag.find('a').text.split()) for tag in 
            html.findAll(class_='tag-type-medium')
            )
        try:tags = ' '.join(
            tag.find('a').text for tag in 
            html.findAll(class_='tag-type-general')
            )
        except TypeError: continue
        artists = [
            '_'.join(artist.find('a').text.split()) for artist in 
            html.findAll(class_=re.compile('tag-type-artist|idol|studio'))
            ]

        name = get_name(image.split('/')[-1].split('?e=')[0], 0)
        
        # check tags
        if len(tags.split()) < 10 and save_image(name, image):
            try: tags += ' ' + get_tags(name, filter=(mode[1] == 1))
            except AttributeError: continue
        try: tags, rating = generate_tags(tags, metadata, True, True)
        except: continue
        tags = tags.encode('ascii', 'ignore').decode()
        for key, value in REPLACE.items():
            tags = re.sub(f' {value} ', f' {key} ', tags)

        artists = [ARTIST.get(artist, [artist])[0] for artist in artists]
        artists = ' '.join(artists).encode('ascii', 'ignore').decode()

        hash_ = get_hash(image, 1)

        # insert image
        if MYSQL.execute(INSERT[3], (
            name.name, artists, tags, rating, mode[1], hash_, image, SITE, href
            )):
            if save_image(name, image):
                MYSQL.execute(DELETE[4], (href, mode[1]))
                MYSQL.commit()
            else: MYSQL.rollback()
    
    print()

def main(initial=True, headless=True, mode=1):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    mode = MODE[mode]

    if initial:
        
        url = DRIVER.login(SITE)
        query = set(MYSQL.execute(
            f'{SELECT[0]} AND type=%s', (SITE, mode[1]), fetch=1
            ))
        hrefs = initialize(mode, url, query)
        MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)

    page_handler(MYSQL.execute(
        f'{SELECT[1]} AND type=%s', (SITE, mode[1]), fetch=1
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
