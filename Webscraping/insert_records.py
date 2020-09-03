import json
from PIL import Image
from . import ROOT, CONNECTION, WEBDRIVER, INSERT
from ..utils import get_hash, get_name, get_tags, generate_tags, save_image, progress

def convert_images(path):
    
    for file in path.glob('*png'):
        
        # if file.lower().endswith(('png', 'jfif')):
        file = path / file
        name = file.with_suffix('.jpg')
        jpg = Image.open(file).convert("RGB")
        jpg.save(name, quality=100)
        if name.exists(): file.unlink()

def extract_files(path):
    
    source = path / 'Generic'
    for file in source.iterdir():
        
        urls = [
            value for window in 
            json.load(open(file))[0]['windows'].values() 
            for value in window.values()
            ]

        for url in urls:
                
            try:
                title = url['title'].split('/')[-1].split()[0]
                if not re.search(EXT, title):
                    title = url['url'].split('/')[-1]
                name = path / title
                if name.exists(): continue
                image = (
                    f'https://{url["title"]}'
                    if url['url'] == 'about:blank' else 
                    url['url']
                    )
                if not save_image(name, image): break
        
            except: break
        file.unlink()

def start(path):

    # extract_files(path)
    convert_images(path)
    driver = WEBDRIVER(True)
    files = [
        file for file in path.iterdir() if file.is_file()
        ]
    size = len(files) - 2

    for num, file in enumerate(files):
        progress(size, num, 'Files')
        
        try:
            if (dest := get_name(file, 0, 1)).exists():
                file.unlink()
                continue
            
            hash_ = get_hash(file)

            if dest.suffix.lower() == '.jpg':

                tags, rating, exif = generate_tags(
                    general=get_tags(driver, file), 
                    custom=True, rating=True, exif=True
                    )
                Image.open(file).save(file, exif=exif)

            elif dest.suffix.lower() in ('.gif', '.webm', '.mp4'):
                
                tags, rating = generate_tags(
                    general=get_tags(driver, file), 
                    custom=True, rating=True, exif=False
                    )

            CONNECTION.execute(
                INSERT[5], 
                (str(dest), '', tags, rating, hash_, None, 1), 
                commit=1
                )
            file.replace(dest)
            
        except Exception as error: print('\n', error)
    
    progress(size, size, 'Files')
    driver.close()

path = ROOT / r'\Users\Emc11\Downloads\Images'
start(path)
print('\nDone')