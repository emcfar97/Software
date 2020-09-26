from .. import CONNECT, WEBDRIVER, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests, time
from PIL import Image
from selenium.webdriver.common.keys import Keys

SITE = 'pinterest'
CONNECTION = CONNECT()
DRIVER = WEBDRIVER(True)

def page_handler(hrefs):
    
    size = len(hrefs)

    for num, href in enumerate(hrefs):
        progress(size, num, SITE)

        page_source = requests.get(f'https://www.pinterest.com{href}')
        html = bs4.BeautifulSoup(page_source, 'lxml')
        src = 0
        if (name:=get_name(src, 0, 1)).exists(): continue
        
        if name.suffix.lower() in ('.jpg'):

            tags, rating, exif = generate_tags(
                general=get_tags(DRIVER, href), 
                custom=True, rating=True, exif=True
                )
            Image.open(name).save(name, exif=exif)

        elif name.suffix.lower() in ('.gif', '.webm', '.mp4'):
            
            tags, rating = generate_tags(
                general=get_tags(DRIVER, href), 
                custom=True, rating=True, exif=False
                )

        hash_ = get_hash(src, True)

        CONNECTION.execute(
            INSERT[5], (name, tags, rating, 0, hash_, src, SITE), commit=1
            )
        
    progress(size, size, SITE)
    
def start():

    DRIVER = WEBDRIVER()
    login(DRIVER, SITE)
    boards = {
        # 'winter-casual':['jeans', 'leggings', 'shorts', 'skirt'],
        'summer-casual':['jeans', 'leggings', 'shorts', 'skirt'],
        # 'athletic-wear':['',],
        # 'dresses':['',],
        # 'business':['',],
        # 'your-pinterest-likes': ['']
        }  

    for board, sections in boards.items():

        total = set()

        for section in sections:
            
            DRIVER.get(f'https://pinterest.com/chairekakia/{board}/{section}')
            time.sleep(2)
            
            while len(total)<100:
                html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
                targets = html.find(class_="gridCentered").findAll(
                    'a', href=re.compile('/pin/\d+/')
                    )
                targets = set(targets) - total
                total = total | targets
                if not targets: 
                    page_handler(total)
                    break
                
                for _ in range(2):
                    DRIVER.find('html', Keys.PAGE_DOWN, type_=6)
                    time.sleep(2)
            
    DRIVER.close()