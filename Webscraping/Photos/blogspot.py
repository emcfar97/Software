import argparse, bs4
from .. import CONNECT, INSERT, SELECT, WEBDRIVER
from ..utils import IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, re, requests

SITE = 'blogspot'
URL = [
    ['http://publicnudityproject.blogspot.com/', ' casual_nudity'],
    ['https://ggulbest.blogspot.com/', ' asian']
    ]

def initialize(url, query):
    
    def next_page(page):
             
        try: return page.get('href')
        except AttributeError: return False


    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    hrefs = [
        (target.get('href'), SITE, 1) for target in 
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
        tags, rating = generate_tags(
            get_tags(name, True) + tag,
            custom=True, rating=True
            )
        save_image(name, href)
        hash_ = get_hash(name)
        
        MYSQL.execute(INSERT[3],
            (name.name, '', tags, rating, 1, hash_, href, SITE, None),
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
    query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
    
    for page in html.findAll('li'):
        try: initialize(page.contents[0].get('href'), query)
        except:
            for page in page.findAll(class_='post-count-link'):
                initialize(page.get('href'), query)
    page_handler(MYSQL.execute(SELECT[1], (SITE,), fetch=1), url[1])
        
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