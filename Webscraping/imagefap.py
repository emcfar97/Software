from utils import *

root = os.getcwd()[:2].upper()
PATH = rf'{root}\Users\Emc11\Downloads\Images\Imagefap'
INSERT = f'INSERT IGNORE INTO imageData(path, artist, tags, rating, hash, site, type) VALUES(REPLACE(%s, "{root}", "C:"), %s, %s, %s, %s, %s, 0)'

def page_handler(url, title):
    
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
        src = target.find(src=re.compile('https://cdn.imagefap.com/images/full/.+')).get('src')

        name = get_name(src, 0, 1)
        name = name.split('?')[0]
        if exists(name): continue
        save_image(name, src)
        tags = get_tags(driver, name)

        if name.endswith(('jpg', 'jpeg')):
            
            tags, rating, exif = generate_tags(
                general=tags, custom=True, rating=True, exif=True
                )
            save_image(name, src, exif)

        elif name.endswith(('.gif', '.webm', '.mp4')):
            
            tags, rating = generate_tags(
                general=tags, custom=True, rating=True, exif=False
                )

        hash_ = get_hash(name)
        execute(
            INSERT, (name, f' {artist} ', tags, rating, hash_, 'imagefap'), commit=1
            )
    
driver = get_driver(True)
files = [
    join(PATH, file) for file in os.listdir(PATH) 
    if file.endswith('json')
    ]

for file in files:

    window = json.load(open(file))[0]['windows']
    try:
        for val in window.values():
            for url in val.values():
                page_handler(url['url'], url['title'])
    except Exception as error: print(error, '\n'); continue
    except KeyboardInterrupt: break
    os.remove(file)

driver.close()