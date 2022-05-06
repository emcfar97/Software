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
    RESERVE = r'Downloads\Reserve'
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
        
    print(f'{len(x)} not in files')
    print(f'{len(y)} not in database')
    
    if not input('Go through with deletes? ').lower() in ('y', 'ye', 'yes'):
        
        return
    
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

def Download_Nhentai():
    '''Code, artist, range'''
    
    import requests, bs4, re, ast
    from Webscraping import USER
    from Webscraping.utils import save_image

    path = USER / r'Downloads\Images\Comics'
    comic = USER / r'Dropbox\Software\comics.txt'
    
    for arg in comic.read_text().splitlines()[:-1]:
        
        code, artist, range_ = ast.literal_eval(arg)

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
            if name.exists(): continue
            save_image(name, src)
            
def Resize_Images(source, pattern='*', size=[800, 1200]):
    '''Reisizes all images from source matching the pattern to a given size'''
    
    from PIL import Image
    from pathlib import Path
    from Webscraping.utils import USER

    source = Path(source)
    dest = USER / 'Downloads' / f'{source.parent.name} Downscaled'
    dest.mkdir(exist_ok=True)

    for file in source.glob(pattern):

        image = Image.open(file)
        if image.height >= image.width:
            image.thumbnail(size)
        else:
            image.thumbnail(size[::-1])

        image.save(dest / file.name)
        
    return dest

def Prepare_Art_Files(project, parents=''):
    ''''''

    import shutil, re
    from Webscraping.utils import USER

    dropbox = USER / 'Dropbox'
    downloads = USER / 'Downloads'
    project_dir = downloads / project
    project_dir.mkdir(exist_ok=True)
    name, _ = re.split(' \d+\Z', project)
    _, version = re.split('^\D+', project)

    # files
    print('Files')
    head = dropbox / 'Pictures' / 'Projects' / parents / name
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
    
    obs, = list((dropbox / 'Videos' / 'Captures').glob('*.mp4'))
    clip_time = (head / name / version / project).with_suffix('.mp4')
    
    shutil.copy(obs, videos / obs.name)
    shutil.copy(clip_time, videos / clip_time.name)
    
    # illustrations
    print('Illustrations')
    head = dropbox / 'Pictures' / 'Artwork' / parents
    illus = project_dir / 'Illustrations'
    illus.mkdir(exist_ok=True)
    
    shutil.copytree(head / name / version, illus, dirs_exist_ok=True)
    
    downscaled = Resize_Images(illus, '**/*.*')
    # shutil.move(downscaled, project_dir)
    
    # zips
    print('Zip')
    names = {
        files:  ['Files', 'ファイル'],
        videos: ['Videos', 'タイムラプス'],
        illus:  ['Illustrations', 'CG'],
        }
    for name, langs in names.items():
        for lang in langs:
            if (downloads / lang + 'zip').exists(): continue
            folder = shutil.copytree(
                str(name), str(downloads / lang), dirs_exist_ok=True
                )
            shutil.make_archive(str(project_dir / lang), 'zip', str(name))
            shutil.rmtree(folder)

    # text
    print('Text')
    project_struct = project_dir / 'Structure.txt'
    project_struct.touch()
    
    text = 'English\n'
    text += f'Contents ({len(list(illus.iterdir()))} files in total):\n'
    
    for dir in illus.glob('**/*.*'):
        if dir.is_dir():
            text += f'・{dir.stem} ({len(dir.iterdir())} files)'
        else: text += f'\t{dir.stem}\n'.replace(f'{project} - ', '')
    else: project_struct.write_text(text)
            
    psd.unlink()
    obs.unlink()

def Splice_Images(folder, foreground, pattern):
    '''Combines all images matching the pattern in specified folder with a given foreground'''

    from pathlib import Path
    from PIL import Image

    folder = Path(folder)
    foreground = Image.open(foreground)

    for image in folder.glob(pattern):

        background = Image.open(str(image))
        background.paste(foreground, (0, 0), foreground)
        
        background.save(str(image))

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
        
        driver.get(url + i)
        content = requests.get(url + i).content
        time.sleep(5)
        html = bs4.BeautifulSoup(driver.page_source(), 'lxml')
        target = html.find('div', class_=re.compile('mb-\d mt-\d text-center'))
        option = max(target.contents[1:], key=lambda x: return_quality(x))
        href = option.find(href=True).get('href')
        name = path.parent / (href.split('=')[-1] + '.mp4')
        if not name.exists(): requests.get(href)
        
    input('Finished?')

def Download_Ehentai(url, wait=1, folder='Games'):
    ''''''
    
    import requests, re, time
    from Webscraping import USER, WEBDRIVER
    
    def download_image():
        
        src = driver.find('//*[@id="img"]').get_attribute('src')
        name = comic / src.split('/')[-1]
        if not name.exists():
            name.write_bytes(requests.get(src).content)
    
    def is_page_end():
        
        element = driver.find('//body/div[1]/div[1]/div[1]/div', fetch=1)
        current, total = element.text.split(' / ')
        
        return current == total
    
    path = USER / r'Downloads\Images' / folder
    driver = WEBDRIVER(headless=0, profile=None)
    
    driver.get(url)
    title = driver.find('//*[@id="gn"]').text
    comic = path / title
    comic.mkdir(exist_ok=True)
    
    while True:
        
        if re.match('.+/s/.+-\d', driver.current_url()):
            
            try: download_image()
            except: continue
            driver.find('//*[@id="next"]', click=True)
            time.sleep(wait)
            
        if is_page_end(): break

def Extract_Frames(source, fps=1, dest=None):
    '''Extracts frames from a given source animation, with optional fps and inital number'''
    
    from pathlib import Path
    from cv2 import VideoCapture, imencode, CAP_PROP_POS_FRAMES
    
    path = Path(source)
    if dest is None:
        from Webscraping import USER
        
        parent = USER / 'Pictures' / 'Screenshots' / path.stem
        parent.mkdir(exist_ok=1)
    
    vidcap = VideoCapture(source)
    success, frame = vidcap.read()

    while success:
        
        if (vidcap.get(CAP_PROP_POS_FRAMES) % fps) == 0:
            
            temp = parent / f'{vidcap.get(CAP_PROP_POS_FRAMES):003}.jpg'
            temp.write_bytes(imencode('.jpg', frame)[-1])
        
        success, frame = vidcap.read()
        
    else: vidcap.release()

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