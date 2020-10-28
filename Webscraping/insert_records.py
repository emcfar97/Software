import json
from PIL import Image
from urllib.parse import urlparse
from . import ROOT, CONNECT, INSERT, WEBDRIVER
from .utils import Progress, get_hash, get_name, get_tags, generate_tags, save_image

EXT = 'jp.*g|png|gif|webm|mp4'

def extract_files(path):
    
    errors = []
    errors_txt = path / 'Errors.txt'
    if errors_txt.exists():
        for image in errors_txt.read_text().split('\n'):
            image = urlparse(image.strip())
            name = path.parent / image.path.split('?')[0][1:]
            save_image(name, image.geturl())
        errors_txt.unlink()
    
    for file in path.iterdir():
        
        urls = [
            value for window in 
            json.load(open(file, encoding='utf-8'))[0]['windows'].values() 
            for value in window.values()
            ]

        for url in urls:
            
            name = path.parent / urlparse(url['url']).path[1:]
            if name.suffix == '.png': name = name.with_suffix('.jpg')
            if name.exists(): continue
            image = (
                f'https://{url["title"]}'
                if url['url'] == 'about:blank' else 
                url['url']
                )
            if not save_image(name, image): errors.append(image)
        
        file.unlink()
    
    if errors: errors_txt.write_text('\n'.join(errors))

def start(path=ROOT / r'\Users\Emc11\Downloads\Images'):

    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER()
    
    # extract_files(path / 'Generic')
    files = [file for file in path.iterdir() if file.is_file()]
    progress = Progress(len(files) - 2, 'Files')

    for file in files:
        
        print(progress)
        
        try:
            if (dest := get_name(file, 0, 1)).exists():
                file.unlink()
                continue
            
            hash_ = get_hash(file)

            if dest.suffix.lower() == '.jpg':

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

            CONNECTION.execute(
                INSERT[5], 
                (str(dest), '', tags, rating, 1, hash_, None, None), 
                commit=1
                )
            file.replace(dest)
            
        except Exception as error: print('\n', error)
    
    print(progress)
    DRIVER.close()

    print('\nDone')