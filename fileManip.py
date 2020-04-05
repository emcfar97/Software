import os, shutil, piexif, json, requests, hashlib, imagehash, bs4
from os.path import join, isfile, splitext, exists
from io import BytesIO
from PIL import Image
from Webscraping.utils import get_driver, get_hash, get_tags, generate_tags, progress
import mysql.connector as sql
from selenium.common.exceptions import WebDriverException

ROOT = os.getcwd()[:2].upper()
DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor()
INSERT = 'INSERT IGNORE INTO imageData(path, tags, rating, hash, type) VALUES(REPLACE(%s, "E:", "C:"), %s, %s, %s, 0)'

def rename(path):
    
    for file in os.listdir(path):
    
        if file.startswith('stunnsfw-'):    
        # if file.endswith(('.png', '.jpg', '.gif')):
            
            old = join(path, file)
            new = join(path, file.replace('stunnsfw-', 'stunnsfw - '))
            # new = join(path, f'OptionalTypo - {file}')
            try: os.rename(old, new)
            except: FileExistsError: os.remove(old)
            
def delete(path):

    jpg = [i for i in os.listdir(path) if 'jpg' in i[1]]
    png = [i for i in os.listdir(path) if 'png' in i[1]]

    # for file in enumerate([file for file in x if file[1] in y]):
    #     # os.remove(file[1])
    #     print(file[1])

def move(path):

    dest = r'C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三'
    
    for folder in os.listdir(path):
        if os.path.isdir(folder):
            for file in os.listdir(join(path,folder)):
                # print(join(path, folder, file))
                shutil.move(join(path,folder,file), dest)

    # for folder in os.listdir(path):
    #     if folder.startswith('Chapter') or folder in ['Epilogue','prologue']:
    #         for root, dirs, files in os.walk(folder):
    #             for num, file in enumerate(os.listdir(root)):
    #                 print(file)
    #                 print(
    #                     r'{}\{}\{}'.format(path, root, file),
    #                     r'{}\{}'.format(path, folder)
    #                     )
    #                 # shutil.move(
    #                 #     r'{}\{}\{}'.format(path,root, file),
    #                 #     r'{}\{}{:03d}'.format(path, folder,num)
    #                 #     )
            
def convert_images(path):
    
    for file in os.listdir(path):
        
        if file.lower().endswith(('png', 'jfif')):
            file = join(path, file)
            jpg = Image.open(file).convert("RGB")
            jpg.save(f'{splitext(file)[0]}.jpg', quality=100)
            if isfile(f'{splitext(file)[0]}.jpg'): os.remove(file) 

def edit_properties(path):

    for root, dir, files in os.walk(path):
        
        if root == path: continue
        artist = ['_'.join(root.split('\\')[-1].lower().split())]
        for file in files:
            
            file = join(root, file)
            zeroth_ifd = {
                piexif.ImageIFD.XPAuthor: [
                    byte for char in '; '.join(artist) for byte in [ord(char), 0]
                    ]}
            exif_ifd = {piexif.ExifIFD.DateTimeOriginal: u'2000:1:1 00:00:00'}
            metadata = piexif.dump({"0th":zeroth_ifd, "Exif":exif_ifd})
            Image.open(file).save(file, exif=metadata)
            try:
                shutil.move(file, path)
            except: pass

def extract_files(path):
    
    for file in [i for i in os.listdir(path) if i.endswith('.json')]:
        
        file = join(path, file)
        window = json.load(open(file))[0]['windows']

        try:
            for val in window.values():
                for url in val.values():
                    
                    image = url['url']
                    if url['url'] == 'about:blank':
                        image = f'https://{url["title"]}'
                    title = url['title'].split('/')[-1]
                    name = join(path, title.split()[0])
                    
                    if name.endswith(('.jpg', '.jpeg')):

                        try: 
                            jpg = Image.open(BytesIO(requests.get(image).content))
                            jpg.save(name)

                        except requests.exceptions.SSLError:
                            print(f'Error at {image}')

                        except OSError:
                            name = name.replace('.png', '.jpg')
                            png = Image.open(BytesIO(requests.get(image).content))
                            png = png.convert('RGBA')
                            background = Image.new('RGBA', png.size, (255,255,255))
                            png = Image.alpha_composite(background, png)
                            png.convert('RGB').save(name)

                    elif name.endswith('.png'):

                        name = name.replace('.png', '.jpg')
                        png = Image.open(BytesIO(requests.get(image).content))
                        png = png.convert('RGBA')
                        background = Image.new('RGBA', png.size, (255,255,255))
                        png = Image.alpha_composite(background, png)
                        png.convert('RGB').save(name)

                    elif name.endswith(('.gif','.webm', 'mp4')):

                        with open(name, 'wb') as temp:
                            temp.write(requests.get(image).content)
            
            os.remove(file)

        except: continue

def insert_files(path):

    extract_files(path)
    
    driver = get_driver(True)
    hasher = hashlib.md5()
    ext = 'jpg', 'jpeg', 'gif', 'webm', 'mp4'
    files = [
        join(path, file) for file in os.listdir(path)
        if  (file.lower().endswith(ext) and isfile(join(path, file)))
        ]
    size = len(files)

    for num, file in enumerate(files):
        progress(size, num, 'Files')
        
        ext = splitext(file)[-1].lower()
        try: 
            with open(file, 'rb') as data: hasher.update(data.read())
            dest = join(
                rf'{ROOT}\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ', 
                f'{hasher.hexdigest()}{ext}'
                )
            
            if exists(dest):
                os.remove(file)
                continue
            
            tags = get_tags(driver, file)

            if file.lower().endswith(('jpg', 'jpeg')):

                tags, rating, exif = generate_tags(
                    type='Erotica 2', general=tags, 
                    custom=True, rating=True, exif=True
                    )
                Image.open(file).save(file, exif=exif)

            elif file.lower().endswith(('.gif', '.webm', '.mp4')): 
                
                tags.append('animated')
                if file.lower().endswith(('.webm', '.mp4')):
                    tags.append('audio')
                tags, rating = generate_tags(
                    type='Erotica 2', general=tags, 
                    custom=True, rating=True, exif=False
                    )

            hash_ = get_hash(file.lower())

            CURSOR.execute(INSERT, (dest, f" {tags} ", rating, hash_))
            shutil.move(file, dest)
            DATAB.commit()
            
        except (OSError, WebDriverException): continue

        except: break
    
    progress(len(files), num, 'Files')
    driver.close()
    DATAB.close()

paths = [
    rf'{ROOT}\Users\Emc11\Downloads'
    ]
    
for path in paths: insert_files(path)

print('Done')