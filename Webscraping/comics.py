import shutil, re
from . import ROOT, CONNECTION, WEBDRIVER, INSERT
from .utils import progress, get_name, get_hash, get_tags, generate_tags

path = ROOT.parent / r'Downloads\Images\Comics'
driver = WEBDRIVER(True)

def start():

    folders = path.iterdir()
    size = len(folders)

    for num, folder in enumerate(folders):

        progress(size, num, '\nComics')

        targets = re.findall('\[.+\]|\(\w+\)', folder.stem.lower())
        artist = ' '.join('_'.join(i[1:-1].split()) for i in targets)
        images = [
            (num, shutil.copy(file, get_name(file, 2, 1)))
            for num, file in enumerate(folder.iterdir())
            ]
        cover = images[0][1]

        size_ = len(images)
        for num, image in images:

            progress(size_, num, artist)

            hash_ = get_hash(image)
            tags, rating = generate_tags(
                general=get_tags(driver, image), custom=True, rating=True, exif=False
                )
            CONNECTION.execute(
                INSERT[4], 
                (str(image), artist, tags, rating, 2, hash_, cover.stem, num)
                )
        CONNECTION.commit()
        shutil.rmtree(folder)

    driver.close()