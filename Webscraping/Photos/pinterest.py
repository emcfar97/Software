import argparse, bs4, time
from .. import CONNECT, INSERT, SELECT, WEBDRIVER
from ..utils import IncrementalBar, get_hash, get_name, get_tags, generate_tags, re, save_image
from selenium.webdriver.common.keys import Keys

SITE = 'pinterest'

def page_handler(hrefs, section):
    
    progress = IncrementalBar(section, max=len(hrefs))

    for href in hrefs:
        
        progress.next()
        DRIVER.get(f'https://www.{SITE}.com{href.get("href")}', wait=1)
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        target = html.find('a', href=True, attrs={'data-test-id':'image-link'})
        try: src = target.findAll('img', src=re.compile('.+pinimg.+'))[-1].get('src')
        except: continue

        if (name:=get_name(src)).exists(): continue
        save_image(name, src)

        if name.suffix in ('.jpg'):

            tags, rating = generate_tags(
                general=get_tags(name, True), 
                custom=True, rating=True
                )
            save_image(name)

        elif name.suffix in ('.gif', '.webm', '.mp4'):
            
            tags, rating = generate_tags(
                general=get_tags(name, True), 
                custom=True, rating=True
                )

        if section not in tags: tags += f' {section}'
        hash_ = get_hash(src, True)

        MYSQL.execute(INSERT[3], 
            (name.name, '', tags, rating, 1, hash_, src, SITE, href), 
            commit=1
            )
        
    print()
    
def main(retry=0, headless=True):

    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    DRIVER.login(SITE)
    boards = {
        # 'winter-casual':['jeans', 'leggings', 'shorts', 'skirt'],
        'summer-casual':{'jeans', 'leggings', 'shorts', 'skirt'},
        # 'athletic-wear':['',],
        # 'dresses':['',],
        # 'business':['',],
        # 'your-pinterest-likes': ['']
        }
    query = set(
        href for href, in MYSQL.execute(SELECT[0], (SITE,), fetch=1)
        )

    for board, sections in boards.items():

        total = set()

        for section in sections:
            
            DRIVER.get(
                f'https://{SITE}.com/chairekakia/{board}/{section}', wait=1
                )
            
            while True:
                
                html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                targets = html.find(class_='gridCentered').findAll(
                    'a', href=re.compile('/pin/\d+/')
                    )
                targets = set(targets) - total
                total = (total | targets) - query
                
                if not targets:
                    if retry >= 2:
                        page_handler(total, section)
                        break
                    else: retry += 1
                else: retry = 0
                
                for _ in range(3):
                    DRIVER.find('html', Keys.PAGE_DOWN, type_=6)
                    time.sleep(2)
            
    DRIVER.close()
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='pinterest', 
        )
    parser.add_argument(
        '-r', '--retry', type=bool,
        help='Retry argument (default 0)',
        default=0
        )
    parser.add_argument(
        '-he', '--head', type=bool,
        help='Headless argument (default True)',
        default=True
        )

    args = parser.parse_args()
    
    main(args.retry, args.head)