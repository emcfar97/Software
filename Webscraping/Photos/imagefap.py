import json
from .. import ROOT, CONNECTION, WEBDRIVER, INSERT, SELECT, UPDATE
from ..utils import login, progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests, time

PATH = ROOT / r'\Users\Emc11\Downloads\Images\Imagefap'

def page_handler(driver, url, title):
    
    try: url = f'{url}?gid={url.split("/")[4]}&view=2'
    except IndexError: url = f'https://{title}&view=2'
    artist, = [
        re.sub(
            'pornstar|porn|pics|&|sexy|gifs|cock|\d', '', i.lower()
            ).strip().replace(' ', '_')
        for i in title.split(',|-|~')
        ]

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
                general=get_tags(driver, name), 
                custom=True, rating=True, exif=True
                )
            save_image(name, src, exif)

        elif name.suffix in ('.gif', '.webm', '.mp4'):
            
            tags, rating = generate_tags(
                general=get_tags(driver, name), 
                custom=True, rating=True, exif=False
                )

        hash_ = get_hash(name)
        CONNECTION.execute(
            INSERT[6], 
            (str(name), f' {artist} ', tags, rating, hash_, 'imagefap', 1), commit=1
            )
    
    progress(size, size, 'Images')

def start():
        
    driver = WEBDRIVER(True)

    for file in PATH.iterdir():

        window = json.load(open(file))[0]['windows']
        try:
            for val in window.values():
                for url in val.values():
                    page_handler(driver, url['url'], url['title'])
        except Exception as error: print(error, '\n'); continue
        file.unlink()

    driver.close()