import os, shutil, re
from os.path import join, split, splitext
from utils import execute, get_driver, get_name, get_hash, get_tags, generate_tags

INSERT = [
    'INSERT INTO imageData(path, artist, tags, rating, type, hash) VALUES(%s, %s, %s, %s, %s, %s)',
    'INSERT INTO comics(path, hash) VALUES(%s, %s)'
    ]

driver = get_driver()
path = r'C:\Users\Emc11\Downloads\Comics'

for folder in os.listdir(path):

    folder = join(path, folder)
    artist = re.sub('\[|\]|,\s', ' ', re.findall('\[.+\]', folder)[0]).lower()
    images = [
        shutil.copy(
            join(folder, file), 
            get_name(join(folder, file), 2, 1)
            )
        for file in sorted(os.listdir(folder))
        ]

    cover = images[0]
    hash_ = get_hash(cover)
    id = split(splitext(cover)[0])[1]
    execute(INSERT[1], [(i, id) for i in images], 1)

    tags = get_tags(driver, images, comic=1)
    tags, rating = generate_tags(
        general=tags, custom=True, rating=True, exif=False
        )
    execute(INSERT[0], (cover, artist, tags, rating, 2, hash_), commit=1)

    # shutil.rmtree(folder)

driver.close()