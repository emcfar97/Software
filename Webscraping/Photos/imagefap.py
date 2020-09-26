import json
from .. import ROOT, CONNECT, WEBDRIVER, INSERT, SELECT, UPDATE, WEBDRIVER
from ..utils import progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests, time

PATH = ROOT / r'\Users\Emc11\Downloads\Images\Imagefap'
REMOVE = 'ass|big|cock|gifs|gif|girls|naked|nude|pics|pornstar|porn|sexy|&|\d'
SITE = 'imagefap'

def page_handler(url, title):
    
    try: url = f'{url}?gid={url.split("/")[4]}&view=2'
    except IndexError: url = f'https://{title}&view=2'
    artist = ' '.join(
        string.strip().replace(' ', '_') for string in 
        re.split(',|-|~', re.sub(REMOVE, '', title.lower()))
        )

    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    images = html.findAll(href=re.compile('/photo/.+'))
    size = len(images)

    for num, image in enumerate(images):

        progress(size, num, 'Images')

        href = f'https://www.imagefap.com/{image.get("href")}'
        page_source = requests.get(href).content
        target = bs4.BeautifulSoup(page_source, 'lxml')
        src = target.find(
            src=re.compile('https://cdn.imagefap.com/images/full/.+')
            ).get('src')

        if (name:=get_name(src, 0, 1)).exists(): continue
        save_image(name, src)

        if name.suffix in ('.jpg', '.jpeg'):
            
            tags, rating, exif = generate_tags(
                general=get_tags(DRIVER, name), 
                custom=True, rating=True, exif=True
                )
            save_image(name, src, exif)

        elif name.suffix in ('.gif', '.webm', '.mp4'):
            
            tags, rating = generate_tags(
                general=get_tags(DRIVER, name), 
                custom=True, rating=True, exif=False
                )

        hash_ = get_hash(name)
        CONNECTION.execute(
            INSERT[5], 
            (str(name), artist, tags, rating, 1, hash_, None, SITE), 
            commit=1
            )
    
    progress(size, size, 'Images')

def start():
        
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER()
    
    for file in PATH.iterdir():

        window = json.load(open(file))[0]['windows']
        try:
            for val in window.values():
                for url in val.values():
                    page_handler(url['url'], url['title'])
        except Exception as error: print(error, '\n'); continue
        file.unlink()
        print()

    DRIVER.close()