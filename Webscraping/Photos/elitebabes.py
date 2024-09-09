import argparse, bs4
from .. import CONNECT, WEBDRIVER, INSERT, SELECT, DELETE
from ..utils import ARTIST, IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, re, requests

SITE = 'elitebabes'

def initialize(url, query):

    def next_page(page):
                
        try: return page.find(href=True).get('href')
        except AttributeError: return False

    content = DRIVER.get(f'https://www.{SITE}.com{url}', wait=5)
    html = bs4.BeautifulSoup(content, 'lxml')
    hrefs = [
        (href, SITE, 1) for target in
        html.find(class_='list-gallery').findAll(href=re.compile('https.+'))
        if (
            href := target.get('href').split('/')[-2],
            ) not in query
        ]

    next = next_page(html.find(class_='next'))
    if hrefs and next: return hrefs + initialize(next, query)
    else: return hrefs

def page_handler(hrefs):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        progress.next()
        response = requests.get(f'https://www.{SITE}.com/{href}')
        html = bs4.BeautifulSoup(response.content, 'lxml')
        try:
            artists = [
                artist.get('href').split('/')[-2].replace('-', '_') 
                for artist in html.findAll(href=re.compile(
                f'https://www.{SITE}.com/model/.+'
                ))
                ]
        except AttributeError:
            try: artists = html.find(class_='unlinkedtag').text
            except:continue
        
        artists = [ARTIST.get(artist, [artist])[0] for artist in artists]
        images = html.find(class_=re.compile('list-gallery.+'))
        if images is None: continue

        for image in images.findAll('a'):

            src = image.get('href')
            if (name:=get_name(src)).exists(): continue
            if not save_image(name, src): break

            tags, rating = generate_tags(
                general=get_tags(name, True), 
                custom=True, rating=True
                )
            
            save_image(name, src)
            hash_ = get_hash(name)

            if not MYSQL.execute(INSERT[3],
                (name.name, ' '.join(artists), tags, 
                rating, 1, hash_, src, SITE, href), 
                ):
                MYSQL.rollback()
                break
        else: MYSQL.execute(DELETE[0], (href,), commit=1)
    
    print()

def main(initial=True, headless=True):
        
    global MYSQL, DRIVER
    MYSQL = CONNECT()

    if initial:
        
        DRIVER = WEBDRIVER(headless)
        query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
        hrefs = initialize(DRIVER.login(SITE), query)
        MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
        DRIVER.close()
    
    page_handler(MYSQL.execute(SELECT[1], (SITE,), fetch=1))

if __name__ == '__main__':   

    parser = argparse.ArgumentParser(
        prog='elitebabes', 
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