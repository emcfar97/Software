import imageio, cv2, hashlib
import numpy as np
from selenium.common.exceptions import WebDriverException
import mysql.connector as sql
from os.path import join

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 
SITE = 'posespace'
TYPE = 'Erotica 2'

def initialize(driver, url='/posetool/favs.aspx'):

    query = set(execute(SELECT[0], (SITE,), fetch=1))
    driver.get(f'https://www.posespace.com{url}')
    html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    while True:
        try:
            hrefs = [
                (*href, SITE) for href in {(target.text,) 
                for target in html.findAll(class_='emph')} - query
                ]
            break
        except sql.errors.OperationalError: continue
    while True:
        try: CURSOR.executemany(INSERT[0], hrefs,); break
        except sql.errors.OperationalError: continue
        
    DATAB.commit()

def page_handler(driver, hrefs):
    
    if not hrefs: return
    size = len(hrefs)
    hasher = hashlib.md5()
    url = 'https://www.posespace.com/img/contact/'

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        image_a = Image.open(
            BytesIO(requests.get(f'{url}{href}contacta.jpg').content)
            )
        image_b = Image.open(
            BytesIO(requests.get(f'{url}{href}contactb.jpg').content)
            )

        image = Image.new('RGB', (image_a.width, image_a.height+image_b.height))
        image.paste(image_a)
        image.paste(image_b, (0, image_a.height))

        image.save(join(r'C:\Users\Emc11\Downloads\test', f'{href}.gif'))

        continue
        name = join(PATH, 'エラティカ ニ', f'{hasher.hexdigest()}.gif')
        hash = get_hash(name)

        while True:
            try:
                CURSOR.execute(UPDATE[3], (name, href[:-2], hash, image, href))
                DATAB.commit()
                break
            except sql.errors.OperationalError: continue
            except sql.errors.IntegrityError:
                CURSOR.execute(UPDATE[3], (f'202 - {href}', hash, image, href))
                DATAB.commit()
                break
        
    progress(size, size, SITE)

def make_gif(path, name, error=False):

    image = Image.open(join(path, f'{name}.jpg'))
    corners = find_corners(join(path, f'{name}.jpg'))
    images = [
        image.crop((*corner[0], *corner[1]))
        for corner in zip(corners[0][:24], corners[1][:24])
        ]
    os.mkdir(join(path[:-6], name))
    for num, image in enumerate(images, 1):
        image.save(join(path[:-6], name, f'{name}_{num:02d}.jpg'))
    imageio.mimsave(join(path[:-6], f'{name}.gif'), images, duration=.20)
    
def find_corners(path):

    def find_row(row):
        
        above = gray.shape[1] - np.count_nonzero(gray[row-1])
        center= gray.shape[1] - np.count_nonzero(gray[row])
        below = gray.shape[1] - np.count_nonzero(gray[row+1])
        
        return (
            above<center and above<below and below!=0 and above<1,
            below<center and below<above and above!=0 and below<1
            )

    def find_col(row, col, span=20):

        rght = 2*span - np.count_nonzero(gray[row-span:row+span,col-1])
        midd = 2*span - np.count_nonzero(gray[row-span:row+span,col])
        left = 2*span - np.count_nonzero(gray[row-span:row+span,col+1])
        
        return (
            rght<midd and rght<left and left!=0 and rght<=1,
            left<midd and left<rght and rght!=0 and left<=1
            )

    corners = [], []
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY, 21, 4
        )
     
    for row in range(1, gray.shape[0]-1):

        top, bot = find_row(row)
        if top or bot:
            
            for col in range(1, gray.shape[1]-1):
              
                rght, left = find_col(row, col)
                if rght and top: corners[0].append([col, row])
                elif left and bot: corners[1].append([col, row])
        
    return corners

def setup(initial=True):
    
    try:
        driver = get_driver(headless=True)
        login(driver, SITE)
        if initial: initialize(driver)
        page_handler(driver, execute(SELECT[2], (SITE,), fetch=1))
    except WebDriverException:
        if input(f'{SITE}: Browser closed\nContinue?').lower() in 'yes':
            setup(False)
    except Exception as error:
        print(f'{SITE}: {error}')
        
    driver.close()
    DATAB.close()

if __name__ == '__main__':

    from .utils import *
    driver = WEBDRIVER(True)
    # login(driver, SITE)
    # initialize(driver)
    
    page_handler(driver, execute(SELECT[2], (SITE,), fetch=1))

    driver.close()
    DATAB.close()

else: 
    from ..utils import *