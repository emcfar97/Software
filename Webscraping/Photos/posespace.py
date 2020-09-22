import cv2, imutils, imageio, pathlib
import numpy as np
from PIL import Image
from .. import CONNECT, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import login, progress, get_hash, get_name, get_tags, generate_tags, bs4, requests, tempfile

CONNECTION = CONNECT()
DRIVER = WEBDRIVER(True)
SITE = 'posespace'

def initialize(url='/posetool/favs.aspx'):

    database = set(CONNECTION.execute(SELECT[2], (SITE,), fetch=1))

    DRIVER.get(f'https://www.posespace.com{url}')
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
    hrefs = [
        (*href, 1, SITE) for href in 
        {(target.text,) for target in 
        html.findAll(class_='emph')} - database
        ]
    CONNECTION.execute(INSERT[0], hrefs, commit=1)
        
def page_handler(hrefs):
    
    if not hrefs: return
    size = len(hrefs)
    url = 'https://www.posespace.com/img/contact/'

    for num, (href,) in enumerate(hrefs):
        progress(size, num, SITE)

        image_a = np.asarray(bytearray(
            requests.get(f'{url}{href}contacta.jpg').content)
            )
        image_b = np.asarray(bytearray(
            requests.get(f'{url}{href}contactb.jpg').content)
            )
        image_c = np.array(
            [[255, 255, 255]]
        )
        image   = cv2.vconcat([
            cv2.imdecode(image_a, -1), cv2.imdecode(image_b, -1)
            ])
        image = make_gif(image, href)
        continue

        tags, rating = generate_tags(
            general=get_tags(image) + ' reference', 
            custom=True, rating=True, exif=False
            )
        name = get_name(image, 0)
        hash_ = get_hash(image)
        artist = href[:-3]
        image.replace(name)

        CONNECTION.execute(
            UPDATE[3], (str(name), f' {artist} ', tags, rating, None, hash_, href), commit=1
            )
        
    progress(size, size, SITE)

def make_gif(image, name):

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
        tuple(int(i/10) for i in cv2.boundingRect(shape)[2:]) 
        for shape in shapes[:24]
        }
    
    # for num, shape in enumerate(shapes[:24:], 1):
        
    #     M = cv2.moments(shape)
    #     cX, cY = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
    #     # draw the countour number on the image
    #     cv2.putText(image, f"#{num}", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    #     cv2.drawContours(image, [shape], -1, (0, 255, 0), 2)

    # print(f'\n{name:<15}: {len(total):>2} total animate? {len(total)<3}')
    # cv2.imshow(name, image)
    # cv2.waitKey(0)
    temps = []

    if len(total) < 3:

        images = []
        gif = tempfile.TemporaryFile(suffix='.gif').name
        
        for shape in shapes[:24]:
            
            x, y, w, h = cv2.boundingRect(shapes.pop(0))
            crop = cv2.cvtColor(image[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
            images.append(Image.fromarray(crop))

        new = Image.new('RGB', total.pop())
        new.save(gif, save_all=True, append_images=images, duration=100)
        # imageio.mimsave(gif, images, fps=12,)
        temps.append(pathlib.Path(gif))
    return
    for shape in shapes:

        temp = tempfile.TemporaryFile(suffix='.jpg').name
        x, y, w, h = cv2.boundingRect(shape)
        cv2.imwrite(temp, image[y:y+h, x:x+w])
        temps.append(pathlib.Path(temp))
    
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

def setup(initial=True):
    
    # try:
    DRIVER.close()
    # login(SITE)
    # if initial: initialize(DRIVER)
    page_handler(CONNECTION.execute(SELECT[2], (SITE,), fetch=1))
    # except Exception as error:
    #     print(f'{SITE}: {error}')
        
    DRIVER.close()
