import shutil, re
from . import ROOT, CONNECTION, WEBDRIVER
from .utils import get_name, get_hash, get_tags, generate_tags

path = ROOT / r'Downloads\Images\Comics'
driver = WEBDRIVER()

def start():

    for folder in path.iterdir():

        targets = re.findall('\[.+\]|\(\w+\)', folder.stem.lower())
        artist = ' '.join('_'.join(i[1:-1].split()) for i in targets)
        images = [
            (shutil.copy(file, get_name(file, 2, 1)), num)
            for num, file in enumerate(folder.iterdir())
            ]
        cover = images[0][1]

        for num, image in images:

            hash_ = get_hash(image)
            tags = get_tags(driver, image, comic=1)
            tags, rating = generate_tags(
                general=tags, custom=True, rating=True, exif=False
                )
            CONNECTION.execute(
                INSERT[4], 
                (str(image), artist, tags, rating, 2, hash_, cover.stem, num), 
                commit=1
                )
        shutil.rmtree(folder)

    driver.close()