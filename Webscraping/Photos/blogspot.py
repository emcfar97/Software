import argparse
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests

SITE = 'blogspot'
URL = [
    ['http://publicnudityproject.blogspot.com/', ' casual_nudity'],
    ['https://ggulbest.blogspot.com/', ' asian']
    ]

def initialize(url, query=0):
    
    def next_page(page):
             
        try: return page.get('href')
        except AttributeError: return False

    if not query: query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))

    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    hrefs = [
        (target.get('href'), SITE) for target in 
        html.findAll('a', href=re.compile('.+://\d.bp.blogspot.com+'))
        if (target.get('href'),) not in query
        ]
    MYSQL.execute(INSERT[0], hrefs, 1)
        
    next = next_page(html.find(title='Older Posts'))
    if hrefs and next: initialize(next, query)
    else: MYSQL.commit()

def page_handler(hrefs, tag):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        name = get_name(href)
        if not save_image(name, href): continue
        tags, rating, exif = generate_tags(
            get_tags(DRIVER, name, True) + tag,
            custom=True, rating=True, exif=True
            )
        save_image(name, href, exif)
        hash_ = get_hash(name)
        
        MYSQL.execute(UPDATE[0],
            (str(name), ' ', tags, rating, href, hash_, href),
            commit=1
            )
        progress.next()
        
    print()

def main(index, headless=True):

    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless, None)
    
    url = URL[index]
    page_source = requests.get(url[0]).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    
    for page in html.findAll('li'):
        try: initialize(page.contents[0].get('href'))
        except:
            for page in page.findAll(class_='post-count-link'):
                initialize(page.get('href'))
    page_handler(MYSQL.execute(SELECT[2], (SITE,), fetch=1), url[1])
        
    DRIVER.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='sankaku', 
        )
    parser.add_argument(
        '-i', '--index', type=bool,
        help='Index argument'
        )
    parser.add_argument(
        '-he', '--head', type=bool,
        help='Headless argument (default True)',
        default=True
        )

    args = parser.parse_args()
    
    main(args.index, args.head)