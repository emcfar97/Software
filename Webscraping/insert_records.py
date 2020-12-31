import json, cv2
from PIL import Image
from urllib.parse import urlparse
from . import ROOT, CONNECT, INSERT, WEBDRIVER
from .utils import Progress, get_hash, get_name, get_tags, generate_tags, save_image

EXT = '.jpg', '.jpeg', '.png', '.gif', '.webp', '.webm', '.mp4'
MATCH = cv2.imread(r'Webscraping\match.jpg')

def extract_files(path, dest=None):
    
    if dest is None: dest = path.parent

    errors = []
    errors_txt = path / 'Errors.txt'
    if errors_txt.exists():
        for image in errors_txt.read_text().split('\n'):
            image = image.strip()
            name = path.parent / image.split('/')[-1]
            save_image(name, image)
        errors_txt.unlink()
    
    for file in path.iterdir():
        
        urls = [
            value for window in 
            json.load(open(file, encoding='utf-8'))[0]['windows'].values() 
            for value in window.values()
            ]

        for url in urls:
            
            path = urlparse(url['url']).path[1:]
            name = dest / path.split('/')[-1]
            if name.exists(): continue
            image = (
                f'https://{url["title"]}'
                if url['url'] == 'about:blank' else 
                url['url']
                )
            if name.suffix == '.gifv': 
                name = name.with_suffix('.mp4')
                image = image.replace('gifv', 'mp4')
            if not save_image(name, image): errors.append(image)
        
        file.unlink()
    
    errors_txt.write_text('\n'.join(errors))

def similarity(path):

    if path.suffix in EXT[:2]: 
        image = cv2.imread(str(path))
    else:
        image = cv2.VideoCapture(str(path)).read()[-1]

    if image.shape == MATCH.shape:
        k = cv2.subtract(image, MATCH)
        return (k.min() + k.max()) == 0

    return False

def start(path=ROOT / r'\Users\Emc11\Downloads\Images'):
    
    extract_files(path / 'Generic')
    files = [file for file in path.iterdir() if file.suffix in EXT]
    progress = Progress(len(files), 'Files')
    
    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER()

    for file in files:
        
        print(progress)
        
        try:
            if (dest := get_name(file, 0, 1)).exists() or similarity(file):
                file.unlink()
                continue
            
            if not (hash_ := get_hash(file)): continue

            if dest.suffix.lower() ('.jpg', '.png'):

                tags, rating, exif = generate_tags(
                    general=get_tags(DRIVER, file), 
                    custom=True, rating=True, exif=True
                    )
                Image.open(file).save(file, exif=exif)

            elif dest.suffix.lower() in ('.gif', '.webm', '.mp4'):
                
                tags, rating = generate_tags(
                    general=get_tags(DRIVER, file), 
                    custom=True, rating=True, exif=False
                    )

            if CONNECTION.execute(INSERT[3], (
                dest.name, '', tags, rating, 1, hash_, None, None
                )):
                if file.replace(dest): CONNECTION.commit()
                else: CONNECTION.rollback()
            
        except Exception as error: print(error, '\n')
    
    print(progress)
    DRIVER.close()

    print('\nDone')

