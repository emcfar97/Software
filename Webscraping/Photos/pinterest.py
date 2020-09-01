from .. import CONNECTION, WEBDRIVER, INSERT, SELECT, UPDATE
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests, time
from selenium.webdriver.common.keys import Keys

SITE = 'pinterest'

def page_handler(driver, hrefs):
    
    size = len(hrefs)

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)
        
        if dest.suffix.lower() in '.jpg':

            tags, rating, exif = generate_tags(
                general=get_tags(driver, href), 
                custom=True, rating=True, exif=True
                )
            Image.open(file).save(file, exif=exif)

        elif dest.suffix.lower() in ('.gif', '.webm', '.mp4'):
            
            tags, rating = generate_tags(
                general=get_tags(driver, href), 
                custom=True, rating=True, exif=False
                )

        hash_ = get_hash(file)

        CONNECTION.execute(INSERT[5], (dest, tags, rating, hash_, 1), commit=0)
        shutil.move(file, dest)
        CONNECTION.commit()
        
    progress(size, size, SITE)
    
def start():

    driver = WEBDRIVER()
    login(driver, SITE)
    boards = {
        # 'winter-casual':['jeans', 'leggings', 'shorts', 'skirt'],
        'summer-casual':['jeans', 'leggings', 'shorts', 'skirt'],
        # 'athletic-wear':['',],
        # 'dresses':['',],
        # 'business':['',],
        # 'your-pinterest-likes': ['']
        }  

    for board, sections in boards.items():

        total = {}

        for section in sections:
            
            driver.get(f'https://pinterest.com/chairekakia/{board}/{section}')
            time.sleep(2)
            
            while len(total) < 500:
                html = bs4.BeautifulSoup(driver.page_source, 'lxml')
                targets = html.find(class_="gridCentered").findAll(
                    'img', src=re.compile(f'https://i.pinimg.com/+')
                    )
                targets = set(targets) - total
                if not targets: break
                
                total = total | targets
                for _ in range(2):
                    driver.find('html', Keys.PAGE_DOWN, type=6)
                    time.sleep(2)
            
            else: page_handler(driver, total)
                
    driver.close()