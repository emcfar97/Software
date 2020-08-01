import os, shutil, piexif, json, requests, re
from os.path import join, isfile, splitext, exists
from io import BytesIO
from PIL import Image
from Webscraping.utils import DATAB, CURSOR, get_driver, get_hash, get_name, get_tags, generate_tags, save_image, progress, sql
from selenium.common.exceptions import WebDriverException

ROOT = os.getcwd()[:2].upper()
EXT = 'jp.*g|png|gif|webp|webm|mp4'
INSERT = 'INSERT IGNORE INTO imageData(path, tags, rating, hash, type) VALUES(REPLACE(%s, "E:", "C:"), %s, %s, %s, 0)'

def rename(path, pattern, string, ext):
    
    for file in os.listdir(path):
    
        if file.endswith(ext):
            new = re.sub(pattern, string, file)
            file = join(path, file)
            dest = join(path, new)
            print(new)
            # os.rename(file, dest)
            
def delete(path, pattern, string, ext):

    jpg = [i for i in os.listdir(path) if 'jpg' in i[1]]
    png = [i for i in os.listdir(path) if 'png' in i[1]]

    # for file in enumerate([file for file in x if file[1] in y]):
    #     # os.remove(file[1])
    #     print(file[1])

def move(path, pattern, string, ext):

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
            name = f'{splitext(file)[0]}.jpg'
            jpg = Image.open(file).convert("RGB")
            jpg.save(name, quality=100)
            if exists(name): os.remove(file) 

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
    
    source = join(path, 'Generic')
    for file in os.listdir(source):
        
        file = join(source, file)
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
                name = join(path, title)
                if exists(name): continue
                image = (
                    f'https://{url["title"]}'
                    if url['url'] == 'about:blank' else 
                    url['url']
                    )
                save_image(name, image)
        
            except: break
        os.remove(file)

def insert_files(path):

    extract_files(path)
    convert_images(path)
    driver = get_driver(True)
    files = [
        join(path, file) for file in os.listdir(path)
        if isfile(join(path, file))
        ]
    size = len(files)

    for num, file in enumerate(files):
        progress(size, num, 'Files')
        
        try: 
            dest = get_name(file, 0, 1)
            
            if exists(dest):
                os.remove(file)
                continue
            
            tags = get_tags(driver, file)

            if dest.endswith(('jpg', 'jpeg')):

                tags, rating, exif = generate_tags(
                    general=tags, custom=True, rating=True, exif=True
                    )
                Image.open(file).save(file, exif=exif)

            elif dest.endswith(('.gif', '.webm', '.mp4')): 
                
                tags, rating = generate_tags(
                    general=tags, custom=True, rating=True, exif=False
                    )

            hash_ = get_hash(file)

            CURSOR.execute(INSERT, (dest, tags, rating, hash_))
            shutil.move(file, dest)
            DATAB.commit()
            
        except (OSError, WebDriverException): continue
        
        except KeyboardInterrupt: break
        
        except: continue
    
    progress(len(files), num, 'Files')
    driver.close()
    DATAB.close()

paths = [
    rf'{ROOT}\Users\Emc11\Downloads\Images'
    ]
    
for path in paths: insert_files(path)

print('Done')