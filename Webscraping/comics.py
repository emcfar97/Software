import shutil, re, send2trash
from . import ROOT, CONNECT, INSERT, WEBDRIVER
from .utils import Progress, get_name, get_hash, get_tags, generate_tags

CONNECTION = CONNECT()
DRIVER = WEBDRIVER(True)
path = ROOT / r'\Users\Emc11\Downloads\Images\Comics'

def get_artist(text):

    targets = re.findall(r'[^[]*\[([^]]*)\]', text)
    targets = sum([i.split() for i in targets], [])
    targets = [i for i in targets if i not in ['decensored', 'digital']]
    targets = '_'.join([i.replace(',', '') for i in targets])

    return targets.replace('_)', ')')

def start():
    
    folders = list(path.iterdir())
    if not len(folders): return
    progress = Progress(len(folders), '\nComic')

    for folder in folders:
        
        print(progress)
        
        commit = 1
        artist = get_artist(folder.stem.lower())
        images = [
            (num, get_hash(file), shutil.copy(file, get_name(file, 2, 1)))
            for num, file in enumerate(folder.iterdir())
            ]
        cover = images[0][2]

        for num, hash_, image in images:

            tags, rating = generate_tags(
                general=get_tags(DRIVER, image), 
                custom=True, rating=True, exif=False
                )
            
            if not (
                CONNECTION.execute(INSERT[3], 
                    (image.name, artist, tags, 
                    rating, 3, hash_, None, None)
                    )
                and 
                CONNECTION.execute(INSERT[4], (
                    image.name, cover.name, num)
                    )
                ): commit = 0
        if commit: 
            CONNECTION.commit()
            send2trash.send2trash(str(folder))
        
    print(progress)
    DRIVER.close()