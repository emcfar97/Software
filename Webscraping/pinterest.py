from os.path import exists, join
from Webscraping.utils import DATAB, CURSOR, get_driver, get_hash, get_name, get_tags, generate_tags, save_image, progress, sql
from selenium.common.exceptions import WebDriverException

def initialize(driver):

    for board, sections in boards.items():
        for section in sections:
            
            driver.get(f'https://pinterest.com/chairekakia/{board}/{section}')
            time.sleep(2)
            
            while len(total) < images:
                html = bs4.BeautifulSoup(driver.page_source, 'lxml')
                targets = html.find(class_="gridCentered").findAll(
                    'img', src=re.compile(f'https://i.pinimg.com/+')
                    )
                targets = set(targets) - total
                if not targets: break
                
                for target in targets:
                    src = target.get('src')
                    image = Image.open(BytesIO(requests.get(src).content))
                    name = f"{hash(src)}.{image.format}"
                    if exists(name): continue
                    image.save(join(path, folder, name))
                
                total = total | targets
                for _ in range(2):
                    driver.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
                    time.sleep(2)

def page_handler(hrefs):

    for num, (href,) in enumerate(hrefs):
        progress(size, num, 'pinterest')
        
        tags = get_tags(driver, file)

        if dest.endswith(('jpg', 'jpeg')):

            tags, rating, exif = generate_tags(
                general=tags, custom=True, rating=True, exif=True
                )
            Image.open(file).save(file, exif=exif)

        elif dest.endswith(('.gif', '.webm', '.mp4')): 
            
            tags, rating = generate_tags(
                general=tags, custom=True, rating=True, exif=False
                )

        hash_ = get_hash(file)

        CURSOR.execute(INSERT, (dest, tags, rating, hash_))
        shutil.move(file, dest)
        DATAB.commit()
            
driver = get_driver(False)
login(driver, 'pinterest')
boards = {
    'winter-casual':['',],
    'summer-casual':['',],
    'athletic-wear':['',],
    'dresses':['',],
    'business':['',],
    }   
driver.close()