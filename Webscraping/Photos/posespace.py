import cv2, imutils, pathlib, time
import numpy as np
from .. import CONNECT, INSERT, SELECT, DELETE, WEBDRIVER
from ..utils import IncrementalBar, get_hash, get_name, get_tags, generate_tags, bs4, requests, save_image, tempfile

SITE = 'posespace'

def initialize(url='/posetool/favs.aspx'):

    query = set(MYSQL.execute(SELECT[2], (SITE,), fetch=1))

    DRIVER.get(f'https://www.{SITE}.com{url}')
    time.sleep(1)
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (*href, SITE) for href in 
        {
            (target.text,) for target in 
            html.findAll(class_='emph')
            } - query
        ]
    MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
        
def page_handler(hrefs, url=f'https://www.{SITE}.com/img/contact/'):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=MYSQL.rowcount)
    add = ' reference turnaround'

    for href, in hrefs:

        progress.next()
        image_a = np.asarray(bytearray(
            requests.get(f'{url}{href}contacta.jpg').content)
            )
        image_b = np.asarray(bytearray(
            requests.get(f'{url}{href}contactb.jpg').content)
            )
        image   = cv2.vconcat([
            cv2.imdecode(image_a, -1), cv2.imdecode(image_b, -1)
            ])
        
        try:

            for image in make_gif(image):

                tags, rating = generate_tags(
                    general=get_tags(DRIVER, image, True), 
                    custom=True, rating=True, exif=False
                    )
                name = get_name(image)
                hash_ = get_hash(image)
                image.replace(name)

                MYSQL.execute(INSERT[3], 
                    (name.name, href[:-3], ' '.join((tags, add)),
                    rating, 1, hash_, None, SITE, None)
                    )
            
            else: MYSQL.execute(DELETE[0], (href,), commit=1)
            
        except: continue
    print()
        
def make_gif(image):

    def precedence(contour, cols, tolerance=30):

        origin = cv2.boundingRect(contour)
        return ((origin[1] // tolerance) * tolerance) * cols + origin[0]

    shapeMask = cv2.inRange(
        image, np.array([243, 243, 243]), np.array([255, 255, 255])
        )
    shapes = imutils.grab_contours(cv2.findContours(
        cv2.bitwise_not(shapeMask), 
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        ))
    shapes.sort(key=lambda x:precedence(x, image.shape[1]))
    
    total = {
        size for shape in shapes[:24] if
        (
            size := tuple(
                i//10 for i in cv2.boundingRect(shape)[2:] 
                )
            ) != (0, 0)
        }
    
    temps = []
    temp_dir = tempfile.TemporaryDirectory()

    for num, shape in enumerate(shapes):

        x, y, w, h = cv2.boundingRect(shape)
        if w < 10 or h < 10: continue

        temp = tempfile.NamedTemporaryFile(
            dir=temp_dir.name, prefix=f'{num:03}-', suffix='.jpg', delete=False
            )
        temp = pathlib.Path(temp.name)
        temp.write_bytes(
            cv2.imencode('.jpg', image[y:y+h, x:x+w])[-1]
            )
        temps.append(temp)

    if len(total) < 3:
    
        DRIVER.get('https://ezgif.com/maker')
        for temp in temps[:24]:
            DRIVER.find('//input[@type="file"]', keys=str(temp))
        DRIVER.find('//input[@type="submit"]', click=True)
        time.sleep(10)
        DRIVER.find('//input[@type="submit"]', click=True)
        time.sleep(10)
        
        gif = tempfile.TemporaryFile(suffix='.gif', delete=False)
        gif = pathlib.Path(gif.name)
        src = DRIVER.find('//img[@alt="[animate output image]"]')
        save_image(gif, src.get_attribute('src'))

        return [gif, *temps[25:]]
    
    return temps

def start(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless, None)
    
    if initial: initialize()
    page_handler(MYSQL.execute(SELECT[2], (SITE,), fetch=1)[::2])
    DRIVER.close()

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        prog='posespace', 
        )
    parser.add_argument(
        '-i', '--initial', type=bool,
        help='Initial argument (default True)',
        default=True
        )
    parser.add_argument(
        '-he', '--headless', type=bool,
        help='Headless argument (default True)',
        default=True
        )

    args = parser.parse_args()
    
    start(args.initial, args.headless)