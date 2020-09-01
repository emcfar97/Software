import json, re
from PIL import Image
from Webscraping import ROOT, CONNECTION, WEBDRIVER, INSERT
from Webscraping.utils import get_hash, get_name, get_tags, generate_tags, save_image, progress

EXT = 'jp.*g|png|gif|webp|webm|mp4'

def rename(path, pattern, string, ext):
    
    for file in path.iterdir():
    
        if file.endswith(ext):
            new = re.sub(pattern, string, file)
            file = path / file
            dest = path / new
            print(new)
            # os.rename(file, dest)
            
def delete(path, pattern, string, ext): pass

def move(path, pattern, string, ext):

    dest = r'C:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三'
    
    for folder in path.iterdir():
        if folder.isdir():
            for file in path / folder.iterdir():
                # print(path /  folder, file)
                path / folder / file.rename(dest)

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
    
    for file in path.glob('*png'):
        
        # if file.lower().endswith(('png', 'jfif')):
        file = path / file
        name = file.with_suffix('.jpg')
        jpg = Image.open(file).convert("RGB")
        jpg.save(name, quality=100)
        if name.exists(): file.unlink()

def edit_properties(path):

    import piexif, os

    for root, dir, files in os.walk(path):
        
        if root == path: continue
        artist = ['_'.join(root.split('\\')[-1].lower().split())]
        for file in files:
            
            file = root / file
            zeroth_ifd = {
                piexif.ImageIFD.XPAuthor: [
                    byte for char in '; '.join(artist) for byte in [ord(char), 0]
                    ]}
            exif_ifd = {piexif.ExifIFD.DateTimeOriginal: u'2000:1:1 00:00:00'}
            metadata = piexif.dump({"0th":zeroth_ifd, "Exif":exif_ifd})
            Image.open(file).save(file, exif=metadata)
            try: file.rename(path)
            except: pass

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

def insert_files(path):

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
                INSERT[5], (str(dest), tags, rating, hash_), commit=1
                )
            file.replace(dest)
            
        except Exception as error: print('\n', error)
    
    progress(size, size, 'Files')
    driver.close()

paths = [
    ROOT / r'\Users\Emc11\Downloads\Images'
    ]
    
for path in paths: insert_files(path)

print('\nDone')