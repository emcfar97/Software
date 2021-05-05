import re, send2trash
from . import USER, CONNECT, INSERT, WEBDRIVER
from .utils import ARTIST, IncrementalBar, get_name, get_hash, get_tags, generate_tags

path = USER / r'Downloads\Images\Comics'

def get_artist(text):

    targets = re.findall(r'[^[]*\[([^]]*)\]', text)
    targets = sum([i.split() for i in targets], [])
    targets = [i for i in targets if i not in ['decensored', 'digital']]
    targets = '_'.join([i.replace(',', '') for i in targets])

    return targets.replace('_)', ')')

def start(headless=True):
    
    MYSQL = CONNECT()
    DRIVER = WEBDRIVER(headless, None)
    
    folders = list(path.iterdir())
    if not (length := len(folders)): return
    progress = IncrementalBar('Comic', max=length)

    for folder in folders:
        
        artist = ' '.join(
            ARTIST.get(artist, [artist])[0] for artist in 
            [get_artist(folder.stem.lower())]
            )
        images = [
            (
                num, get_hash(file), name:=get_name(file, 2, 1),
                name.write_bytes(file.read_bytes())
                )
            for num, file in enumerate(folder.iterdir())
            ]
        cover = images[0][2]
        
        for num, hash_, image, _ in images:

            tags, rating = generate_tags(
                general=get_tags(DRIVER, image), 
                custom=True, rating=True, exif=False
                )
            imageData = MYSQL.execute(INSERT[3], (
                    image.name, artist, tags, rating, 
                    3, hash_, None, None, None
                    )
                )
            comics = MYSQL.execute(INSERT[4], (
                    image.name, cover.name, num
                    )
                )
            if not (imageData and comics): break; continue

        MYSQL.commit()
        send2trash.send2trash(str(folder))
        
        progress.next()

    DRIVER.close()