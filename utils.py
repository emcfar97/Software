import argparse

def run():

    args = parser.parse_args()
    if not (args.args or args.func): return

    function = args.func
    arguments = args.args
    
    exec(f'{function}({arguments})')

def Normalize_Database():
    ''''''

    import re, send2trash
    from pathlib import Path
    from Webscraping import CONNECT, USER, utils
    
    MYSQL = CONNECT()
    DROPBOX = USER / r'Dropbox\ん'
    RESERVE = USER / r'Downloads\Reserve'
    parts = ", ".join([f"'{part}'" for part in DROPBOX.parts]).replace('\\', '')
    SELECT = f'SELECT full_path(path, {parts}) FROM imagedata'
    select = 'SELECT src, href FROM imagedata WHERE path=%s'
    UPDATE = 'UPDATE imagedata SET path=NULL WHERE path=%s'
    DELETE = 'DELETE FROM imagedata WHERE path=%s LIMIT 1'

    database = set(Path(path) for path, in MYSQL.execute(SELECT, fetch=1))
    windows = set(DROPBOX.glob('[0-9a-f][0-9a-f]/[0-9a-f][0-9a-f]/*.*'))
    rows, files = database - windows, windows - database
    
    print(f'{len(rows)} rows not in files')
    print(f'{len(files)} files not in database')
    
    if not input('Go through with deletes? ').lower() in ('y', 'ye', 'yes'):
        
        return
    
    for num, row in enumerate(rows, 1):
        if any(MYSQL.execute(select, (row.name,), fetch=1)):
            MYSQL.execute(UPDATE, (row.name,))
        else:
            MYSQL.execute(DELETE, (row.name,))
    else:
        try: print(f'{num} records deleted')
        except: print('0 records deleted')
        MYSQL.commit()

    SELECT = 'SELECT path FROM imagedata WHERE hash=%s OR path=%s'

    for num, file in enumerate(files, 1):

        if re.match('.+ \(.+\)\..+', file.name):
            clean = re.sub(' \(.+\)', '', file.name)
            if file.with_name(clean).exists():
                send2trash.send2trash(str(file))
                continue

        hash_ = utils.get_hash(file)
        name = utils.get_name(file)

        image = MYSQL.execute(SELECT, (hash_, name.name), fetch=1)
        if image:
            try: 
                if not file.exists(): file.rename(name)
                else: file.replace(USER / RESERVE / file.name)
            except FileExistsError: send2trash.send2trash(str(file))
        else:
            try: file.replace(USER / RESERVE / file.name)
            except: continue
    else:
        try: print(f'{num} files moved')
        except: print('0 files moved')
    
def Copy_Files(files, dest, sym=False):
    '''Copies list of files to a specified directory, either as a direct copy or a symlink'''
    
    from pathlib import Path

    paths = [Path(file) for file in files]
    dest = Path(dest)

    for path in paths:

        name = dest / path.name    
        if sym and not name.exists(): name.symlink_to(path)
        else: name.write_bytes(path.read_bytes())

def Prepare_Art_Files(project, parents=''):
    ''''''

    import shutil, ffprobe
    from Webscraping.utils import USER

    dropbox = USER / 'Dropbox'
    downloads = USER / 'Downloads'
    project_dir = downloads / project
    project_dir.mkdir(exist_ok=True)

    # files
    print('Files')
    head = dropbox / 'Pictures' / 'Projects' / parents
    files = project_dir / 'Files'
    files.mkdir(exist_ok=True)
    
    clip = (head / project).with_suffix('.clip')
    psd = (head / project).with_suffix('.psd')
    
    shutil.copy(clip, files / clip.name)
    shutil.copy(psd, files / psd.name)

    # videos
    print('Videos')
    head = dropbox / 'Videos' / 'Captures' / parents
    videos = project_dir / 'Videos'
    videos.mkdir(exist_ok=True)
    
    obs = list((dropbox / 'Videos' / 'Captures').glob('*.mp4'))[0]
    clip_time = (head / project / project).with_suffix('.mp4')
    
    shutil.copy(clip_time, videos / clip_time.name)
    shutil.copy(obs, videos / obs.name)
    
    # illustrations
    print('Illustrations')
    head = dropbox / 'Pictures' / 'Artwork' / parents
    illus = project_dir / 'Illustrations'
    shutil.copytree(head / project, illus, dirs_exist_ok=True)
    
    # downscale
    downscaled = project_dir / 'Downscaled'
    downscaled = shutil.copytree(illus, downscaled, dirs_exist_ok=True)
    downscaled = Resize_Images(downscaled, '**/*.*', inplace=True)
    
    # zips
    print('Zip')
    names = {
        files:  ['Files', 'ファイル'],
        videos: ['Videos', 'タイムラプス'],
        illus:  ['Illustrations', 'CG'],
        }
    for name, langs in names.items():
        
        for lang in langs:
            
            if (downloads / (lang + 'zip')).exists(): continue
            folder = shutil.copytree(
                str(name), str(downloads / lang), dirs_exist_ok=True
                )
            shutil.make_archive(str(project_dir / lang), 'zip', str(name))
            shutil.rmtree(folder)

    # text
    print('Text')
    project_struct = project_dir / 'Structure.txt'
    project_struct.touch()

    clip = round(float(ffprobe.FFProbe(clip_time).video[0].duration) / 60)
    obs_time = round(float(ffprobe.FFProbe(obs).video[0].duration) / 60)
    
    text = ''
    langs = [
        [
            f'Contents ({len(list(illus.iterdir()))} files in total):\n',
            f'Contents (4 files in total):\n    CSP\n    PSD\n    CSP ({clip} min)\n    OBS ({obs_time} min)\n\n',
            '{} ({} files)',
            ],
        [
            f'【内容】（合計{len(list(illus.iterdir()))}ファイル）:\n',
            f'【内容】（合計4ファイル）:\n    ・CSP\n    ・PSD\n    ・CSP （{clip}分）\n    ・OBS（{obs_time}分）',
            '{} （{}ファイル）',
            ],
        {
            'Nude': '全裸 ',
            'Lineart': 'ラインアート',
            'Sketch': '落書き',                
        }
        ]    
    
    for lang in langs[:2]:
        
        # Add illustration segment
        text += lang[0]
        
        # Add illustration files
        for dir in illus.glob('**/*.*'):

            if dir.is_dir():

                text += lang[2].format(dir.stem, len(dir.iterdir()))

            else:
                
                text += f'    ・{dir.stem}\n'.replace(f'{project} - ', '')
                for eng, jap in langs[2].items(): text.replace(eng, jap)
            
        text += '\n'
            
        # Add files/timelapse segment
        text += lang[1]
    
    else:
        project_struct.write_text(text, encoding="utf-8")
             
    psd.unlink()
    obs.unlink()

def Resize_Images(folder, pattern='*', size=[1280, 1280], inplace=False):
    '''Reisizes all images from folder matching the pattern to a given size'''
    
    from PIL import Image
    from pathlib import Path
    from Webscraping.utils import USER
    
    num = 0
    folder = Path(folder)
    
    if inplace: dest = folder
    
    else: 
        
        dest = USER / 'Downloads' / f'{folder.name} Downscaled'
        dest.mkdir(exist_ok=True)
    
    for root, dirs, files in pathwalk(folder):
        
        if not inplace: (dest / root.name).mkdir(exist_ok=True)
        
        for file in files:
            
            try: image = Image.open(file)
            except: continue
            image.thumbnail(size)

            if inplace: image.save(file)
            else: image.save(dest / root.name / file.name)
            num += 1
        
    print(f'{num} images resized')
    
    return dest

def Resize_Videos(folder, pattern='*', size=[1920, 1080], inplace=False):
    
    import ffmpeg
    from ffprobe import FFProbe
    from pathlib import Path
    from Webscraping.utils import USER
    
    num = 0
    folder = Path(folder)
    
    if inplace: dest = folder
    
    else: 
        
        dest = USER / 'Downloads' / f'{folder.name} Resized'
        dest.mkdir(exist_ok=True)
    
    for root, dirs, files in pathwalk(folder):
        
        if not inplace: (dest / root.name).mkdir(exist_ok=True)
        
        for file in files:
            
            stream = FFProbe(file).streams[0]
            
            if int(stream.width) == size[0] and int(stream.height) == size[1]:
            
                continue
            
            if inplace:
                
                temp = dest.parent / file.name
                
                ffmpeg.input(str(file)) \
                .filter('scale', width=size[0], height=size[1]) \
                .filter('setsar', sar='1/1') \
                .output(str(temp)) \
                .run(overwrite_output=True)
                
                temp.replace(file)
                
            else:

                ffmpeg.input(str(file)) \
                .filter('scale', width=size[0], height=size[1], setsar='1') \
                .filter('setsar', sar='1/1') \
                .output(str(dest / root.name / file.name)) \
                .run()
                
            num += 1
        
    print(f'{num} videos resized')
    
    return dest
    
def Splice_Images(folder, foreground, pattern='*.*'):
    '''Places a given foreground on all images matching the pattern in specified folder'''

    from pathlib import Path
    from PIL import Image

    num = 0
    folder = Path(folder)
    foreground = Image.open(foreground)

    for image in folder.glob(pattern):

        if image == foreground: continue
        
        background = Image.open(str(image))
        background.paste(foreground, (0, 0), foreground)
        
        background.save(str(image))
        num += 1
        
    print(f'{num} images spliced')

def Convert_Images(path, source='webp', target='png', ignore=' '):
    '''Convert all images with source extension to target, with optional ignoring'''
    
    import re, pillow_avif
    from pathlib import Path
    from PIL import Image

    lookup = {
        'png': 'RGBA',
        'jpg': 'RGB',
        'jpeg': 'RGB',
        'avif': 'RGB',
        'webp': 'RGBA',
        }
    
    num = 0
    path = Path(path)

    if path.is_dir():
        
        for image in path.glob(f'*{source}'):
            
            if re.search(ignore, image.suffix): continue
            rename = image.with_suffix(f'.{target}')
            new = Image.open(str(image)).convert(lookup[target])
            new.save(str(rename))
            image.unlink()
            
            num += 1
    else:

        rename = path.with_suffix(f'.{target}')
        new = Image.open(str(path)).convert(lookup[target])
        new.save(str(rename))
        path.unlink()
        
        num += 1
        
    print(f'{num} images converted')

def Download_Nhentai():
    '''Code, artist, range'''
        
    import bs4, re, json, threading, requests, time
    from Webscraping import USER
    from Webscraping.utils import IncrementalBar, save_image
    
    def url_handler(gallery, folder, image, backoff=1):
        
        response = requests.get(f'https://nhentai.net{image.get("href")}')
        
        # too many requests or server error
        while response.status_code in (429, 500):
            
            backoff += backoff
            time.sleep(backoff)
            response = requests.get(f'https://nhentai.net{image.get("href")}')
            
        image = bs4.BeautifulSoup(response.content, 'lxml')
        src = image.find(src=re.compile('.+galleries.+')).get('src')
        
        name = folder / src.split('/')[-1]
        name = name.with_suffix('.webp')
        
        if name.exists(): 
            
            lock.acquire()
            gallery.append(True)
            lock.release()
            return
        
        image = save_image(name, src)
        lock.acquire()
        gallery.append(image)
        lock.release()

    lock = threading.Lock()
    path = USER / r'Downloads\Images\Comics'
    comic = USER / r'Dropbox\Software\Webscraping\comics.json'
    comic_json = json.load(open(comic))
    
    progress = IncrementalBar('Images', max=len(comic_json))
    
    for code, data in list(comic_json.items())[::-1]:
        
        if not code: continue
            
        response = requests.get(f'https://nhentai.net/g/{code}')

        if response.status_code == 404:

            del comic_json[code]
            with open(comic, 'w') as file:
                json.dump(comic_json, file, indent=2)
                continue

        html = bs4.BeautifulSoup(response.content, 'lxml')
        pages = html.findAll('a', class_='gallerythumb')
    
        for key, range_ in list(data.items()):

            gallery = []
            artist = '_'.join(key.lower().split())
            comic_folder = path / f'{code} - {artist} [{range_[0]}-{range_[1]}]'
            comic_folder.mkdir(exist_ok=True)
                
            threads = [
                threading.Thread(
                    target=url_handler, 
                    args=(gallery, comic_folder, page)
                    )
                for page in pages[range_[0] - 1:range_[1]]
                ]
            
            for thread in threads: thread.start()
            for thread in threads: thread.join()
            
            if all(gallery):
                
                del comic_json[code][key]
                with open(comic, 'w') as file:
                    json.dump(comic_json, file, indent=2)
        
        if all(gallery):
            
            del comic_json[code]
            with open(comic, 'w') as file:
                json.dump(comic_json, file, indent=2)
        
        progress.next()
        
def Download_Xhamster():
    ''''''
    
    import requests, bs4, re, time
    from Webscraping import USER, WEBDRIVER
    from Webscraping.utils import save_image, get_name

    def return_quality(element):
        
        return element.contents[0].contents[1].text
        
    driver = WEBDRIVER(headless=0)
    path = USER / r'Downloads\Images'
    xhamster = USER / r'Dropbox\Software\xhamster.txt'
    url = 'https://9xbuddy.org/process?url='
    
    for i in xhamster.read_text().split():
        
        content = DRIVER.get(url + i)
        content = requests.get(url + i).content
        time.sleep(5)
        html = bs4.BeautifulSoup(content, 'lxml')
        target = html.find('div', class_=re.compile('mb-\d mt-\d text-center'))
        option = max(target.contents[1:], key=lambda x: return_quality(x))
        href = option.find(href=True).get('href')
        name = path.parent / (href.split('=')[-1] + '.mp4')
        if not name.exists(): requests.get(href)
        
def Download_Ehentai(url, wait=2, folder='Games'):
    ''''''
    
    import requests, re, time
    from Webscraping import USER, WEBDRIVER
    from progress.bar import IncrementalBar
        
    def is_page_end():
        
        current = driver.current_url.split('-')[-1]
        
        return current == length
    
    path = USER / r'Downloads\Images' / folder
    driver = WEBDRIVER(profile=None)
    
    content = DRIVER.get(url)
    title = driver.find('//*[@id="gn"]').text
    dest = path / re.sub('[/\:*?"<>]', ' ', title)
    dest.mkdir(exist_ok=True)
    length = driver.find('//*[contains(text(),"pages")]').text.split()[0]
    progress = IncrementalBar('Images', max=int(length))
    driver.find(f'//img[@alt="{1:0{len(length)}d}"]', click=True)
    
    while not is_page_end():

        src = driver.find('//img[@id="img"]', fetch=1).get_attribute('src')
        name = dest / src.split('/')[-1]
        if not name.exists():
            name.write_bytes(requests.get(src).content)
            
        driver.find('//*[@id="next"]', click=True)
        time.sleep(wait)
        progress.next()
    
    DRIVER.close()

def Download_Redgif(url, dest):
    
    import requests
    from pathlib import Path
    from Webscraping.utils import get_redgif
    
    name = Path(dest) / f'{url}.mp4'
    response = requests.get(get_redgif(url))
    name.write_bytes(response.content)
    
    print(f'Video at {name.parent}')

def Extract_Frames(source, fps=1, dest=None):
    '''Extracts frames from a given source animation, with optional fps and destination'''
    
    import ffmpeg
    from pathlib import Path
    from Webscraping import USER
    
    path = Path(source)
    
    if dest is None:
        dest = USER / 'Pictures' / 'Screenshots' / path.stem
        
    if dest.exists(): 
        for file in dest.iterdir(): file.unlink()
        else: dest.rmdir()
    
    dest.mkdir(exist_ok=1)
    dest = dest / '%03d.jpg'
        
    ffmpeg.input(str(source)).filter('select', f'not(mod(n, {fps}))').output(str(dest), vsync=2, loglevel="error").run()
    
    # print(f'Extracted frames can be found at {dest}')
    return dest.parent

def Extract_Files(source, dest=None):

    from pathlib import Path
    from urllib.parse import urlparse
    from send2trash import send2trash
    from Webscraping import json_generator
    from Webscraping.utils import save_image
    
    source = Path(source)
    
    if source.is_file():
        
        if dest is None: dest = source.parent
            
        for url in json_generator(source):
            
            url = url['url']
            name = dest / url.split('/')[-1]
            save_image(name, url, False)
            
        send2trash(source)
    
    elif source.is_dir():
        
        if dest is None: dest = source
        
        for file in source.glob('*.json'):
            
            for url in json_generator(file):
                
                src = urlparse(url['url'])
                if '/' in src.path:
                    name = dest / src.path.split('/')[-1]
                else: name = dest / src.path
                
                save_image(name, url['url'], False)
                
            send2trash(file)
        
def Remove_Emoji():

    import sqlite3, emoji, re
    from Webscraping import USER

    path = USER / r'Dropbox\ん\Images\pixiv'
    emojis = ''.join(emoji.EMOJI_DATA.keys())
    files = 0
    
    select1 = 'SELECT save_name FROM pixiv_master_image WHERE save_name=?'
    select2 = 'SELECT save_name FROM pixiv_manga_image WHERE save_name=?'
    update1 = 'UPDATE pixiv_master_image SET save_name=? WHERE save_name=?'
    update2 = 'UPDATE pixiv_manga_image SET save_name=? WHERE save_name=?'
    datab = sqlite3.connect(r'Webscraping\PixivUtil2\db.sqlite')
    cursor = datab.cursor()

    for file in path.glob(f'*[{emojis}]*'):
        
        try:
            new = re.sub(f'({"|".join(emojis)})', '', file.name)
        except: continue
        new = file.with_name(new)
        
        path = cursor.execute(select1, (str(file),)).fetchone()
        cursor.execute(update1, (str(new), str(file)))
        
        path = cursor.execute(select2, (str(file),)).fetchone()
        cursor.execute(update2, (str(new), str(file)))
        
        try: file.rename(new)
        except FileExistsError: file.unlink()
        datab.commit()
        files += 1
        
    print(f'{files} files cleaned')

def Get_Tags(path, suffix='.jpg'):
    
    import tempfile, requests
    from deepdanbooru_onnx import DeepDanbooru
    from pathlib import Path
    
    MODEL = DeepDanbooru(
        tags_path=r'DeepLearning\general-tags.txt', threshold=0.475
        )
    
    try: 
        file = Path(path)
        
        if not file.exists(): 
        
            content = requests.get(path).content
            path = Path(tempfile.TemporaryFile().name).with_suffix(suffix)
            path.write_bytes(content)
        
    except FileNotFoundError: 
        
        content = requests.get(path).content
        path = Path(tempfile.TemporaryFile().name).with_suffix(suffix)
        path.write_bytes(content)  
        
    tags = set(MODEL(str(path)))
    
    print(' '.join(tags))

def pathwalk(top, topdown=False, followlinks=False):
    """
    See Python docs for os.walk, exact same behavior but it yields Path() instances instead
    """
    names = list(top.iterdir())

    dirs = (node for node in names if node.is_dir() is True)
    nondirs =(node for node in names if node.is_dir() is False)

    if topdown:
        yield top, dirs, nondirs

    for name in dirs:
        if followlinks or name.is_symlink() is False:
            for x in pathwalk(name, topdown, followlinks):
                yield x

    if topdown is not True:
        yield top, dirs, nondirs

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        prog='utils', 
        description='Run utility functions'
        )
    parser.add_argument(
        '-f', '--func', type=str,
        help='Name of function'
        )
    parser.add_argument(
        '-a', '--args', type=str,
        help='Arguments of function',
        default=''
        )

    run()