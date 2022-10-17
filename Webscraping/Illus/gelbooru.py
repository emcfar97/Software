import argparse
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import ARTIST, IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, bs4, requests, re 

SITE = 'gelbooru'
    
def initialize(url, query=0):
    
    def next_page(pages):

        try: return pages.find(alt="next").get('href')
        except AttributeError: return False

    if not query:
        query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
        
    DRIVER.get(f'https://{SITE}.com/index.php{url}')
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')

    hrefs = [
        (target.get('href'), SITE) for target in 
        html.findAll('a', id=re.compile(r'p\d+'), href=True)
        if (target.get('href'),) not in query
        ]
        
    next = next_page(html.find(id='paginator'))
    if hrefs and next: return hrefs + initialize(next, query)
    else: return hrefs
    
def page_handler(hrefs):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        progress.next()
        page_source = requests.get(f'https://{SITE}.com/{href}')
        html = bs4.BeautifulSoup(page_source.content, 'lxml')

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
        image = html.find(href=True, text='Original image').get('href')
        
        name = get_name(image.split('/')[-1], 0)
        if name.suffix in ('jpg', 'png'): name = name.with_suffix('.webp')
        elif name.suffix == 'mp4': name = name.with_suffix('.webm')
        
        type_ = 1 if 'photo_(medium)' in tags else 2
        if len(tags.split()) < 10 and save_image(name, image):
            tags += ' ' + get_tags(DRIVER, name)
        tags, rating, exif = generate_tags(
            tags, metadata, True, artists, True
            )
        
        artists = [ARTIST.get(artist, [artist])[0] for artist in artists]
        hash_ = get_hash(image, 1)
        
        if MYSQL.execute(UPDATE[0], (
            name.name, ' '.join(artists), tags, 
            rating, type_, image, hash_, href
            )):
            if save_image(name, image, exif): MYSQL.commit()
            else: MYSQL.rollback()

    print()

def main(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()    
    DRIVER = WEBDRIVER(headless)
        
    if initial:

        url = DRIVER.login(SITE)
        hrefs = initialize(url)
        MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
    
    page_handler(MYSQL.execute(SELECT[2], (SITE,), fetch=1))
    DRIVER.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='twitter', 
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

    args = parser.parse_args()
    
    main(args.init, args.head)