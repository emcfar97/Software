import argparse

def run():

    args = parser.parse_args()
    if not (args.args or args.func): return

    function = args.func
    arguments = args.args
    
    exec(f'{function}({arguments})')

def Normalize_Database():

    import re
    from pathlib import Path
    from Webscraping import CONNECT, USER, utils
    
    MYSQL = CONNECT()
    DROPBOX = USER / r'Dropbox\ん'
    RESERVE = r'Downloads\Test\Reserve'
    parts = ", ".join([f"'{part}'" for part in DROPBOX.parts]).replace('\\', '')
    SELECT = f'SELECT full_path(path, {parts}) FROM imagedata WHERE NOT ISNULL(path)'
    select = 'SELECT src, href FROM imagedata WHERE path=%s'
    UPDATE = 'UPDATE imagedata SET path=NULL WHERE path=%s'
    DELETE = 'DELETE FROM imagedata WHERE path=%s'

    database = set(
        Path(path) for path, in MYSQL.execute(SELECT, fetch=1)
        )
    windows = set(DROPBOX.glob('[0-9a-f][0-9a-f]/[0-9a-f][0-9a-f]/*.*'))
    x, y = database - windows, windows - database
    
    for num, file in enumerate(x, 1):
        if any(*MYSQL.execute(select, (file.name,), fetch=1)):
            MYSQL.execute(UPDATE, (file.name,))
        else:
            MYSQL.execute(DELETE, (file.name,))
    else:
        try: print(f'{num} records deleted')
        except: print('0 records deleted')
        MYSQL.commit()

    SELECT = 'SELECT path FROM imagedata WHERE hash=%s OR path=%s'

    for num, file in enumerate(y, 1):

        if re.match('+. \(.+\).\.+', file.name):
            clean = re.sub(' \(.+\)', '', file.name)
            if file.with_name(clean).exists():
                file.unlink()
                continue

        hash_ = utils.get_hash(file)
        name = utils.get_name(file)

        image = MYSQL.execute(SELECT, (hash_, name.name), fetch=1)
        if image:
            try: 
                if not file.exists(): file.rename(name)
                else: file.replace(USER / RESERVE / file.name)
            except FileExistsError: file.unlink()
        else:
            try: file.replace(USER / RESERVE / file.name)
            except: continue
    else:
        try: print(f'{num} files moved')
        except: print('0 files moved')
    
def Copy_Files(files, dest, sym=False):
    
    from pathlib import Path

    paths = [Path(file) for file in files]
    dest = Path(dest)

    for path in paths:

        name = dest / path.name    
        if sym and not name.exists(): name.symlink_to(path)
        else: name.write_bytes(path.read_bytes())

def Download_Nhentai(*args):
    '''Code, artist, range'''
    
    import requests, bs4, re
    from Webscraping import USER
    from Webscraping.utils import save_image

    path = USER / r'Downloads\Images\Comics'
    
    for arg in args:

        code, artist, range_ = arg

        comic = path / f'[{artist}] {range_[0]}-{range_[1]}'
        comic.mkdir(exist_ok=True)
        
        page_source = requests.get(f'https://nhentai.net/g/{code}')
        html = bs4.BeautifulSoup(page_source.content, 'lxml')
        pages = html.findAll('a', class_='gallerythumb')

        for page in pages[range_[0] - 1:range_[1]]:

            page = requests.get(f'https://nhentai.net{page.get("href")}')
            image = bs4.BeautifulSoup(page.content, 'lxml')
            src = image.find(src=re.compile('.+galleries.+')).get('src')       
            name = comic / src.split('/')[-1]
            save_image(name, src)

def Resize_Images(source, pattern, size=[800, 1200]):
    
    from PIL import Image
    from pathlib import Path

    source = Path(source)
    dest = Path(r'C:\Users\Emc11\Downloads') / f'{source.parent.name} Downscaled'
    dest.mkdir(exist_ok=True)

    for file in source.glob(pattern):

        image = Image.open(file)
        if image.height > image.width:
            image.thumbnail(size)
        else:
            image.thumbnail(size[::-1])

        image.save(dest / file.name)

def Prepare_Art_Files(project, parents=''):

    import shutil, re
    from Webscraping.utils import USER

    dropbox = USER / 'Dropbox'
    downloads = USER / 'Downloads'
    project_dir = downloads / project
    project_dir.mkdir(exist_ok=True)
    name, _ = re.split(' \d+\Z', project)
    _, version = re.split('^\D+', project)

    # files
    head = dropbox / 'Pictures' / 'Projects' / parents
    files = project_dir / 'Files'
    files.mkdir(exist_ok=True)
    
    clip = (head / project).with_suffix('.clip')
    psd = (head / project).with_suffix('.psd')
    
    shutil.copy(clip, files / clip.name)
    shutil.move(psd, files / psd.name)

    # videos
    head = dropbox / 'Videos' / 'Captures' / parents
    videos = project_dir / 'Videos'
    videos.mkdir(exist_ok=True)
    
    obs, = list((dropbox / 'Videos' / 'Captures').glob('*.mp4'))
    clip_time = (head / name / version / project).with_suffix('.mp4')
    
    shutil.move(obs, videos / obs.name)
    shutil.copy(clip_time, videos / clip_time.name)
    
    # illustrations
    head = dropbox / 'Pictures' / 'Artwork' / parents
    illus = project_dir / 'Illustrations'
    illus.mkdir(exist_ok=True)
    
    source_illus = head / name / version
    
    shutil.copytree(source_illus, illus, dirs_exist_ok=True)
    
    Resize_Images(source_illus, '**/*.*')

def Splice_Image(folder, foreground, pattern):

    from pathlib import Path
    from PIL import Image

    folder = Path(folder)
    foreground = Image.open(foreground)

    for image in folder.glob(pattern):

        background = Image.open(str(image))
        background.paste(foreground, (0, 0), foreground)
        
        background.save(str(image))

parser = argparse.ArgumentParser(
    prog='test', 
    description='Run test functions'
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