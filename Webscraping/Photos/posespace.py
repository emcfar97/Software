import cv2, imutils, pathlib, time
import numpy as np
from .. import CONNECT, INSERT, SELECT, DELETE, WEBDRIVER
from ..utils import IncrementalBar, get_hash, get_name, get_tags, generate_tags, bs4, requests, save_image, tempfile

SITE = 'posespace'

def initialize(url='/posetool/favs.aspx'):

    query = set(MYSQL.execute(SELECT[2], (SITE,), fetch=1))

    DRIVER.get(f'https://www.posespace.com{url}')
    time.sleep(1)
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (*href, SITE) for href in 
        {
            (target.text,) for target in html.findAll(class_='emph')
            } - query
        ]
    MYSQL.execute(INSERT[0], hrefs, many=1, commit=1)
        
def page_handler(hrefs, url='https://www.posespace.com/img/contact/'):
    
    if not hrefs: return
    progress = IncrementalBar(SITE, max=len(hrefs))

    for href, in hrefs:

        image_a = np.asarray(bytearray(
            requests.get(f'{url}{href}contacta.jpg').content)
            )
        image_b = np.asarray(bytearray(
            requests.get(f'{url}{href}contactb.jpg').content)
            )
        image   = cv2.vconcat([
            cv2.imdecode(image_a, -1), cv2.imdecode(image_b, -1)
            ])
        
        make_gif(image); continue

        for image in make_gif(image):

            tags, rating = generate_tags(
                general=get_tags(DRIVER, image, True) + ' reference', 
                custom=True, rating=True, exif=False
                )
            name = get_name(image, 0)
            hash_ = get_hash(image)
            image.replace(name)

            MYSQL.execute(INSERT[3], 
                (name.name, href[:-3], tags, rating, 1, hash_, None, SITE, None)
                )
        else: MYSQL.execute(DELETE[0], (href,), commit=1)
        
        progress.next()
        
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
        tuple(
            int(i/10) for i in cv2.boundingRect(shape)[2:]
            ) 
        for shape in shapes[:24]
        }
    
    # copy = image.copy()
    # for num, shape in enumerate(shapes[:24:], 1):
        
    #     M = cv2.moments(shape)
    #     cX, cY = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
    #     # draw the countour number on the image
    #     cv2.putText(copy, f"#{num}", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    #     cv2.drawContours(copy, [shape], -1, (0, 255, 0), 2)
    # copy = ResizeWithAspectRatio(copy, 900, 600)

    temps = []
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir = pathlib.Path(temp_dir.name)

    for num, shape in enumerate(shapes):

        x, y, w, h = cv2.boundingRect(shape)
        if w < 10 or h < 10: continue
        temp = temp_dir / f'{num:03}.jpg'
        temp.mkdir()
        cv2.imwrite(str(temp), image[y:y+h, x:x+w])
        temps.append(temp)

    # cv2.imshow('name', image)
    # cv2.waitKey(0)

    if len(total) <= 3:
    
        DRIVER.get('https://ezgif.com/maker')
        for temp in temps[:24]:
            DRIVER.find(
                '//body/div/div[2]/div[2]/form/fieldset/p[1]/input', 
                keys=str(temp)
                )
        DRIVER.find(
            '//body/div/div[2]/div[2]/form/fieldset/p[3]/input', click=True
            )
        DRIVER.find(
            '//body/div/div[2]/div[2]/form/p[4]/input', click=True
            )
        time.sleep(5)
        
        # gif = pathlib.Path(tempfile.TemporaryFile((suffix='.gif').name)
        # src = DRIVER.find(
        #     '/html/body/div/div[2]/div[2]/div[2]/p[1]/img'
        #     )
        # save_image(gif, src.get_attribute('src'))

        # return [*temps[24:], gif]
    
    return temps


def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


def start(initial=True, headless=True):
    
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
    if initial: initialize()
    page_handler(MYSQL.execute(SELECT[2], (SITE,), fetch=1))
    DRIVER.close()
