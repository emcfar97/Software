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

import piexif, os, time, re, tempfile, cv2
import mysql.connector as sql
from Webscraping.utils import get_driver, get_tags, generate_tags, bs4
from os.path import exists, join
from PIL import Image

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor() 

driver = get_driver(True)
# path = r'C:\Users\Emc11\Downloads'
# SELECT = 'SELECT path FROM imageData WHERE NOT type AND ISNULL(artist)'
# UPDATE = 'UPDATE imageData SET tags=tags | %s | " " WHERE path=%s'

# for file in os.listdir(path):
    
#     if file.lower().endswith(('jpg','jpeg')):
#         file = join(path, file)
#         try: artist = piexif.load(file)['0th'][40094]
#         except KeyError: continue
#         except Exception as error:
#             continue
#         artist = ''.join(chr(i) for i in artist if i).lower()
#         artist = artist.replace(';', ' ').replace('erotica 2','')
#         CURSOR.execute(UPDATE, (artist, file))
#         DATAB.commit()

# path = r'C:\Users\Emc11\Dropbox\Videos\ん\Images'
# SELECT = 'SELECT path, site FROM favorites WHERE ISNULL(src) AND NOT saved'
# UPDATE = 'UPDATE imageData SET src=%s WHERE path=%s'
#
    # CURSOR.execute(SELECT)
    # driver = get_driver()

    # for path, site, in CURSOR.fetchall():
        
    #     driver.get('https://www.google.com/imghp?hl=en&tab=wi&ogbl')
    #     driver.find_element_by_xpath('//body/div[1]/div[4]/div[2]/form/div[2]/div[1]/div[1]/div/div[3]/div').click()
    #     driver.find_element_by_xpath('//body/div[1]/div[4]/div[2]/div/div[2]/form/div[1]/div/a').click()
    #     try: driver.find_element_by_xpath('//*[@id="qbfile"]').send_keys(path)
    #     except: continue

    #     time.sleep(5)
    #     html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    #     if 'No other sizes' in html.find(class_='O1id0e').text: continue
    #     time.sleep(2)
    #     html = bs4.BeautifulSoup(driver.page_source, 'lxml')
    #     target = html.find(alt=re.compile(
    #         'hentai-foundry.com|twitter.com|pixiv.net|furaffinity.net'
    #         ))
    #     href = target.parent.parent.get('href')

    #     CURSOR.execute(UPDATE, (src, path))
    #     DATAB.commit()

path = r'C:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ'
SELECT = 'SELECT path FROM imageData WHERE NOT type AND NOT rating)'
UPDATE = 'UPDATE imageData SET tags=%s, rating=%s WHERE path=%s'

for file in os.listdir(path)[::-1]:
       
    file = join(path, file)
    if file.endswith('.ini'): continue

    if file.lower().endswith(('jpg', 'jpeg')):

        try: general = get_tags(driver, file)
        except: continue
        tags, rating, exif = generate_tags(
            type='Erotica 2', general=general, 
            custom=True, rating=True, exif=True
            )
        tags += ' '.join(general)
        try: Image.open(file).save(file, exif=exif)
        except: pass

    if file.lower().endswith(('.gif', '.webm', '.mp4')):
    
        general = set()
        temp_dir = tempfile.TemporaryDirectory()
        vidcap = cv2.VideoCapture(file)
        success, frame = vidcap.read()

        while success:

            temp = tempfile.mkstemp(dir=temp_dir.name, suffix='.jpg')
            with open(temp[-1], 'wb') as temp: 
                temp.write(cv2.imencode('.jpg', frame)[-1]) 
            success, frame = vidcap.read() 
        
        for image in os.listdir(temp_dir.name)[::5]:

            image = join(temp_dir.name, image)
            general.update(get_tags(driver, image))

        tags, pack, rating = generate_tags(
            type='Erotica 2', general=list(general), 
            custom=True, rating=True, exif=False
            )
        for tag in tags + pack: general.add(tag)
        tags = ' '.join(general)
        
    CURSOR.execute(UPDATE, (f" {tags} ", rating, file))
    DATAB.commit()
