#
    # import tensorflow as tf
    # from tensorflow import keras
    # from tensorflow.keras import Model, Input, layers

    # inputs = Input(shape=(512,), name='input')
    # x = layers.Dense(64, activation='relu', name='dense_1')(inputs)
    # x = layers.Dense(64, activation='relu', name='dense_2')(x)
    # outputs = layers.Dense(3, activation='softmax', name='predictions')(x)

    # model = Model(inputs=inputs, outputs=outputs, name='medium layer')
    # model.compile(
    #     optimizer='adam', metrics=['accuracy'],
    #     loss='sparse_categorical_crossentropy'
    #     )
    # model.save(r'Machine Learning\Master\medium.h5')

import os, shutil, hashlib, imagehash
from os.path import join, isdir, splitext
import mysql.connector as sql
from PIL import Image
from selenium.common.exceptions import WebDriverException
from Webscraping.utils import get_driver, get_tags, generate_tags

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 

INSERT = 'INSERT IGNORE INTO imageData(path, tags, rating, hash, type) VALUES(%s, %s, %s, %s, 0)'

hasher = hashlib.md5()
driver = get_driver(True)
path = r'C:\Users\Emc11\Dropbox\Pictures\4.Reference\3.Gifs'
dest = r'C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ'
paths = {
    'Casual nudity': 'casual_nudity',
    "Cumming":"cum",
    "Cunnilingus":"cunnilingus",
    "Dance":"dancing",
    "Exercise":"exercise",
    "Fellatio":"fellatio",
    'Girl on top': 'cow_girl',
    'Guy on top': 'missionary',
    "Lactation":"lactation",
    "Masturbation":"masturbation",
    "Penetration":"insertion",
    "Presenting":"presenting",
    "Public Nudity":"public_nudity",
    }

for root, dirs, files in os.walk(path):

    if root.endswith(('Videos', 'No Sex', 'Not Nude', 'Special')): continue
    for file in files: 
        
        if file.endswith('ini'): continue
        file = join(root, file)
        try: tags = get_tags(driver, file)
        except WebDriverException: continue
        except: continue

        tag = root.split('\\')[-1]
        if tag in paths and paths[tag] not in tags: 
            tags.append(paths[tag])
        tags, rating = generate_tags(
            'Erotica 2', general=tags, custom=True, rating=True, exif=False
            )

        if file.endswith('gif'):
            img = Image.open(file)
            img.thumbnail([32, 32])
            img = img.convert('L')
            hash = f'{imagehash.dhash(img)}'
        else: hash = None

        head, ext = splitext(file)
        with open(file, 'rb') as file: 
            hasher.update(file.read())
        name = join(dest, f'{hasher.hexdigest()}{ext}')
        shutil.move(file.name, name)
        CURSOR.execute(INSERT, (name, tags, rating, hash))
        DATAB.commit()

