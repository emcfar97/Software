import os, json, bs4, re, requests
from os.path import join, exists
from utils import DATAB, CURSOR, get_driver, get_name, get_hash, get_tags, generate_tags, save_image, execute

root = os.getcwd()[:2].upper()
PATH = rf'{root}\Users\Emc11\Downloads'
INSERT = 'INSERT IGNORE INTO imageData(path, tags, rating, hash, type) VALUES(REPLACE(%s, "E:", "C:"), %s, %s, %s, 0)'

def page_handler(url, title):
    
    try: url = f'{url}?gid={url.split("/")[4]}&view=2'
    except IndexError: url = f'https://{title}&view=2'
    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    images = html.findAll(href=re.compile('/photo/.+'))

    for image in images:

        href = f'https://www.imagefap.com/{image.get("href")}'
        page_source = requests.get(href).content
        target = bs4.BeautifulSoup(page_source, 'lxml')
        src = target.find(src=re.compile('https://cdn.imagefap.com/images/full/.+')).get('src')
        name = get_name(src, 0, 1)
        if exists(name): continue

        if name.endswith(('jpg', 'jpeg')):
            
            save_image(name, src)
            try: tags = get_tags(driver, name)
            except: return 1
            tags, rating, exif = generate_tags(
                type='Erotica 2', general=tags, 
                custom=True, rating=True, exif=True
                )
            save_image(name, src, exif)

        elif name.endswith(('.gif', '.webm', '.mp4')): 
            
            save_image(name, src)
            try: tags = get_tags(driver, name)
            except: return 1
            tags, rating = generate_tags(
                type='Erotica 2', general=tags, 
                custom=True, rating=True, exif=False
                )

        hash_ = get_hash(name)
        execute(INSERT, (name, f' {tags} ', rating, hash_))
        DATAB.commit()
    
driver = get_driver()
files = [
    join(PATH, file) for file in os.listdir(PATH) 
    if file.endswith('json')
    ]

for file in files:

    window = json.load(open(file))[0]['windows']
    try:
        for val in window.values():
            for url in val.values():
                error = page_handler(url['url'], url['title'])
                if error: continue
    except: continue
    os.remove(file)

driver.close()