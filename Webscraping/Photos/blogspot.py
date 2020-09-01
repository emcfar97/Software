from .. import CONNECTION, INSERT, SELECT, UPDATE
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests, time

SITE = 'blogspot'
url = 'http://publicnudityproject.blogspot.com/p/blog-page.html'

def initialize(url, query=0):
    
    def next_page(page):
             
        try: return page.get('href')
        except AttributeError: return False

    if not query: query = set(CONNECTION.execute(SELECT[0], (SITE,), fetch=1))

    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    hrefs = [
        (target.get('href'), 1, SITE) for target in 
        html.findAll('a', href=re.compile('.+://\d.bp.blogspot.com+'))
        if (target.get('href'),) not in query
        ]
    CONNECTION.execute(INSERT[0], hrefs, 1)
        
    next = next_page(html.find(title='Older Posts'))
    if hrefs and next: initialize(next, query)
    else: CONNECTION.commit()

def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):

        progress(size, num, SITE)

        name = get_name(href, 0, hasher=1)
        if not save_image(name, href): continue
        tags, rating, exif = generate_tags(
            get_tags(driver, name) + ' casual_nudity',
            custom=True, rating=True, exif=True
            )
        save_image(name, href, exif, exists=True)
        hash_ = get_hash(name)
        
        CONNECTION.execute(UPDATE[3], (
            name, ' ', tags, rating, href, hash_, href),
            commit=1
            )

def setup(driver):

    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')

    for page in html.findAll('li'): initialize(page.contents[0].get('href'))
    
    try: page_handler(driver, CONNECTION.execute(SELECT[2], (SITE,), fetch=1))
    except Exception as error: print(f'\n{SITE}: {error}')
        
    driver.close()
