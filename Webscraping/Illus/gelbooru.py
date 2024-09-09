import argparse, requests, bs4, re
from .. import CONNECT, INSERT, SELECT, DELETE, WEBDRIVER, get_credentials
from ..utils import ARTIST, HEADERS, IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags 

SITE = 'gelbooru'
    
def initialize(url, query):
    
    def next_page(pages):

        try: return pages.find(alt="next").get('href')
        except AttributeError: return False

    content = DRIVER.get(f'https://{SITE}.com/index.php{url}')
    html = bs4.BeautifulSoup(content, 'lxml')

    hrefs = [
        (target.get('href'), SITE, 2) for target in 
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
        try: 
            page_source = requests.get(
                f'https://{SITE}.com/{href}&api_key={API_KEY}&user_id={USER_ID}', 
                headers=HEADERS, timeout=30
                )
            
        except requests.exceptions.ReadTimeout:

            print('\nReadTimeoutError')
            page_source = requests.get(
                f'https://{SITE}.com/{href}', headers=HEADERS, timeout=30
                )
        
        except ConnectionResetError:

            print('\nConnectionResetError')
            continue
        
        except requests.exceptions.ConnectionError:
            
            print('\nConnectionError')
            continue
            
        except Exception as error:

            print('\n', error)
            continue

        html = bs4.BeautifulSoup(page_source.content, 'lxml')
        
        # get tags
        metadata = ' '.join(
            '_'.join(data.text.split()) for data in 
            html.select('.tag-type-metadata > a')
            )
        tags = ' '.join(
            '_'.join(tag.text.split()) for tag in 
            html.select('.tag-type-general > a')
            )
        artists = [
            '_'.join(artist.text.split()) for artist in 
            html.select('.tag-type-artist > a')
            ]
        
        # get image
        try: image = html.find(href=True, text='Original image').get('href')
        except AttributeError:
        
            MYSQL.execute(DELETE[5], (href,), commit=1)
            continue
        
        name = get_name(image.split('/')[-1], 0)
        
        # check tags
        type_ = 1 if 'photo_(medium)' in tags else 2
        if len(tags.split()) < 10 and save_image(name, image):
            tags += ' ' + get_tags(name)
        tags, rating = generate_tags(tags, metadata, True, True)
        
        # get artist
        artists = [ARTIST.get(artist, [artist])[0] for artist in artists]
        hash_ = get_hash(image, 1)
        
        # insert image
        if MYSQL.execute(INSERT[3], (
            name.name, ' '.join(artists), tags, 
            rating, type_, hash_, image, SITE, href
            )):
            if save_image(name, image):
                MYSQL.execute(DELETE[5], (href,))
                MYSQL.commit()
            else: MYSQL.rollback()

    print()

def main(initial=True, headless=True):
    
    global MYSQL, DRIVER, API_KEY, USER_ID
    MYSQL = CONNECT()
    API_KEY, USER_ID = get_credentials(SITE, 'api_key', 'userid')
        
    if initial:

        DRIVER = WEBDRIVER(headless)
        url = get_credentials(SITE, 'url')[0]
        query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
        hrefs = initialize(url, query)
        MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
        DRIVER.close()
    
    page_handler(MYSQL.execute(SELECT[1], (SITE,), fetch=1))

if __name__ == '__main__':

    

    parser = argparse.ArgumentParser(
        prog='gelbooru', 
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