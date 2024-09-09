import argparse, bs4
import selenium.common.exceptions as exceptions
from .. import CONNECT, INSERT, SELECT, UPDATE, DELETE, WEBDRIVER, get_credentials
from ..utils import PATH, IncrementalBar, re, save_image

SITE = 'foundry'

def initialize(url, query):
    
    def next_page(pages):
        
        try:
            if 'hidden' in pages.get('class'): return
            else: return pages.contents[0].get('href')
        except AttributeError: 
            return 

    content = DRIVER.get(f'http://www.hentai-foundry.com{url}')
    html = bs4.BeautifulSoup(content, 'lxml')
    hrefs = [
        (*href, SITE) for href in 
        {(target.get('href'),) for target in 
        html.findAll(class_='thumbLink')} - query
        ]
    MYSQL.execute(INSERT[1], hrefs, many=1)

    next = next_page(html.find(class_='next')) 
    if hrefs and next: initialize(next, query)
    else: MYSQL.commit()

def page_handler(hrefs):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)
    
    for href, in hrefs:
        
        progress.next()
        DRIVER.get(f'http://www.hentai-foundry.com{href}')
        try:
            image = DRIVER.find('//img[@class="center"]').get_attribute('src')
            error = 0
            
        except exceptions.NoSuchElementException: 
            error = DRIVER.find('//*[@id="errorBox"]')
            MYSQL.execute(DELETE[1], (href,), commit=1)
            continue
            
        except: continue
        
        if 'thumbs' in image:
            continue
            artist = None
            id = re.findall('.+pid=(\d+)&')[0]
            name = f'{artist} - {id}.jpg'

        elif 'pictures' in image:
            name = re.findall('.+/\w/(\w+)/(\d+).+\.(.+)')
            print(name)
            continue
        else: 
            parts = image.split('/') + [image.split('.')[-1]]
            name = f'{parts[4]} - {parts[5]}.{parts[-1]}'
        name = PATH / 'Images' / SITE / name
        
        MYSQL.execute(UPDATE[2], (str(name), image, href), commit=1)
        if error: save_image(name, image)
    
    print()

def main(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    if initial:
        url = get_credentials(SITE, 'url')
        query = set(MYSQL.execute(SELECT[2], (SITE,), fetch=1))
        initialize(url, query)
    page_handler(MYSQL.execute(SELECT[3], (SITE,), fetch=1))
    DRIVER.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='foundry', 
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