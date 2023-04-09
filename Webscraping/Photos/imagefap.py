import argparse, bs4, time, spacy, send2trash
from .. import USER, WEBDRIVER, CONNECT, INSERT, json_generator
from ..utils import IncrementalBar, save_image, get_hash, get_name, get_tags, generate_tags, re, requests

REMOVE = 'gif.|girl.|sex.|pic.|ass|cock|naked|nude|pornstar|porn|&|\d'
PATH = USER / r'Downloads\Images\Imagefap'
NLP = spacy.load('en_core_web_sm')
SITE = 'imagefap'

def get_artist(text):
    
    text = re.split(',|-|~', re.sub(REMOVE, '', text))
    entities = [NLP(text.strip()) for text in text]
    artists = [
        ents.text.replace(' ', '_')
        for entity in entities for ents in entity.ents
        if ents.label_ == 'PERSON'
        ]
                
    return ' '.join(artists)

def page_handler(url, title):

    try: url = f'{url}?gid={url.split("/")[4]}&view=2'
    except IndexError: url = f'https://{title}&view=2'
    artist = get_artist(title.lower())

    page_source = requests.get(url).content
    html = bs4.BeautifulSoup(page_source, 'lxml')
    images = html.findAll(href=re.compile('/photo/.+'))
    progress = IncrementalBar('Images', max=len(images))

    for image in images:
        
        time.sleep(1)
        progress.next()
        href = f'https://www.imagefap.com/{image.get("href")}'
        page_source = requests.get(href).content
        target = bs4.BeautifulSoup(page_source, 'lxml')
        src = target.find(
            src=re.compile('.+imagefap.com/images/full/.+')
            ).get('src')

        if (name:=get_name(src)).exists(): continue
        save_image(name, src)

        if name.suffix == 'webp':
            
            tags, rating, exif = generate_tags(
                general=get_tags(name, True), 
                custom=True, rating=True, exif=True
                )
            save_image(name, src, exif)

        elif name.suffix in ('.gif', '.webm'):
            
            tags, rating = generate_tags(
                general=get_tags(name, True), 
                custom=True, rating=True, exif=False
                )
        
        hash_ = get_hash(name)
        MYSQL.execute(INSERT[3], (
            name.name, artist, tags, rating,
            1, hash_, None, SITE, None
            ), 
            commit=1
            )
    
    print()

def main(headless=True):
        
    global MYSQL, DRIVER
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless, None)
    
    for file in PATH.iterdir():

        error = 0

        for url in json_generator(file):
            try: page_handler(url['url'], url['title'])
            except Exception as error_: 
                error = error_
                print(error, '\n'); continue
        
        if not error: send2trash.send2trash(str(file))
        print()

    DRIVER.close()
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='imagefap', 
        )
    parser.add_argument(
        '-he', '--head', type=bool,
        help='Headless argument (default True)',
        default=True
        )

    args = parser.parse_args()
    
    main(args.head)