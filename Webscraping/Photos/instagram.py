import argparse, bs4, time
from .. import CONNECT, INSERT, SELECT, DELETE, WEBDRIVER
from ..utils import IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, re
from selenium.webdriver.common.keys import Keys

SITE = 'instagram'

def initialize(url, retry=0):
    
    DRIVER.get(f'https://www.{SITE}.com{url}')
    query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
    
    while True:

        DRIVER.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
        time.sleep(2)

        html = bs4.BeautifulSoup(DRIVER.page_source, 'lxml')
        hrefs = [
            (target.get('href'), SITE) for target in 
            html.findAll('a', href=re.compile('/p/.+'))
            if (target.get('href'),) not in query
            ]
        MYSQL.execute(INSERT[0], hrefs, 1)
            
        if not hrefs:
            if retry >= 2: break
            else: retry += 1
        else:
            query = set(MYSQL.execute(SELECT[0], (SITE,), fetch=1))
            retry = 0

    MYSQL.commit()
    
def page_handler(hrefs, retry=2):

    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)

    for href, in hrefs:
        
        progress.next()
        DRIVER.get(f'https://www.{SITE}.com{href}')
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        artist = html.find(
            alt=re.compile('.+ profile picture')
            ).get('alt').split("'")[0]
        url = DRIVER.current_url()

        DRIVER.get('https://www.w3toys.com/')
        DRIVER.find('//*[@id="link"]', keys=url, enter=1)
        time.sleep(5)
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
        images = [
            'https://www.w3toys.com/' + target.get('href') 
            for target in html.findAll(
                'a', href=True, text='Download file'
                )
            ]
        # while True:
            
            # html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
            # target = html.find('div', role='presentation')
            # src = target.find('video', src=True).get('src')[5:]
            # if not src: src = target.find('img', src=True).get('src')
            # if src in images: 
            #     if retry > 4: break
            #     retry += 1

            # else: images.add(src)
            
            # try: 
            #     try: DRIVER.find(button, click=True, fetch=1)
            #     except: DRIVER.find(button[:-3], click=True, fetch=1)
            # except: break
            # time.sleep(4)
        
        for image in images:

            name = get_name(image)
            save_image(name, image)
            hash_ = get_hash(name) 

            tags, rating, exif = generate_tags(
                general=get_tags(name, True), 
                custom=True, rating=True, exif=True
                )
            if name.suffix.endswith(('jpg', 'png')): 
                save_image(name, image, exif)

            MYSQL.execute(INSERT[0], (
                name.name, artist, tags, rating, 1, hash_, image, SITE, href),
                commit=1
                )
        else: MYSQL.execute(DELETE[0], (href,), commit=1)
    
    print()

def main(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    url = DRIVER.login(SITE)
    if initial: initialize(url)
    page_handler(MYSQL.execute(SELECT[2], (SITE,), fetch=1)[10:])
    DRIVER.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='instagram', 
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