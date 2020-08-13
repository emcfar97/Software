import os, bs4, re, requests
from os.path import join
from utils import DATAB, CURSOR, INSERT, SELECT, UPDATE, sql, execute, get_driver, get_name, get_hash, get_tags, generate_tags, save_image, progress
from selenium.common.exceptions import WebDriverException

SITE = 'blogspot'

def initialize(url, query=0):
    
    def next_page(page):
             
        try: return page.get('href')
        except AttributeError: return False

    if not query:
        query = set(execute(SELECT[0], (SITE,), fetch=1))

    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    hrefs = [
        (target.get('href'), 0, SITE) for target in 
        html.findAll('a', href=re.compile('.+://\d.bp.blogspot.com+'))
        if (target.get('href'),) not in query
        ]
    execute(INSERT[0], hrefs, 1)
        
    next = next_page(html.find(title='Older Posts'))
    if hrefs and next: initialize(next, query)
    else: DATAB.commit()

def page_handler(driver, hrefs):

    if not hrefs: return
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):

        progress(size, num, SITE)

        name = get_name(href, 0, hasher=1)
        save_image(name, href)
        tags = get_tags(driver, name) + ' casual_nudity'
        tags, rating, exif = generate_tags(
            tags, custom=True, rating=True, exif=True
            )
        save_image(name, href, exif, exists=True)
        hash_ = get_hash(name)
        
        try:
            execute(UPDATE[3], (
                name, ' ', tags, rating, href, hash_, href),
                commit=1
                )
        except sql.errors.IntegrityError:
            execute('DELETE FROM imageData WHERE href=%s', (href,), commit=1)
        except sql.errors.DatabaseError: continue

def setup():
    
    try:
        driver = get_driver(headless=True)
        page_handler(driver, execute(SELECT[2], (SITE,), fetch=1))
    except WebDriverException:
        user = input(f'\n{SITE}: Browser closed\nContinue? ')
        if user.lower() in 'yes': setup()
    except Exception as error: print(f'\n{SITE}: {error}')
        
    try: driver.close()
    except: pass

url = 'http://publicnudityproject.blogspot.com/p/blog-page.html'
page_source = requests.get(url).content
html = bs4.BeautifulSoup(page_source, 'lxml')

for page in html.findAll('li'):
    
    initialize(page.contents[0].get('href'))

setup()