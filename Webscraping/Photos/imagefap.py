import json, spacy
from os import path
from .. import ROOT, CONNECT, WEBDRIVER, INSERT
from ..utils import Progress, save_image, get_hash, get_name, get_tags, generate_tags, bs4, re, requests

REMOVE = 'gif.|girl.|sex.|pic.|ass|cock|naked|nude|pornstar|porn|&|\d'
PATH = ROOT / path.expandvars(r'\Users\$USERNAME\Downloads\Images\Imagefap')
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
    progress = Progress(len(images), 'Images')

    for image in images:
        
        print(progress)

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
                general=get_tags(DRIVER, name, True), 
                custom=True, rating=True, exif=True
                )
            save_image(name, src, exif)

        elif name.suffix in ('.gif', '.webm', '.mp4'):
            
            tags, rating = generate_tags(
                general=get_tags(DRIVER, name, True), 
                custom=True, rating=True, exif=False
                )

        hash_ = get_hash(name)
        CONNECTION.execute(INSERT[3], 
            (name.name, artist, tags, rating, 1, hash_, None, SITE), 
            commit=1
            )
    
    print(progress)

def start(headless=True):
        
    global CONNECTION, DRIVER
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(headless)
    
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