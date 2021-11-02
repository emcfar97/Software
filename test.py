import argparse
import json

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
    
def Check_Predictions(sql=False, num=25):
    
    from Webscraping import USER
    from MachineLearning import Model

    path = USER / r'Dropbox\ん'
    model = Model('deepdanbooru.hdf5')

    if sql:
        
        from Webscraping import CONNECT
        
        MYSQL = CONNECT()
        SELECT = f'''
            SELECT full_path(path), tags, type 
            FROM imagedata 
            WHERE SUBSTR(path, 32, 5) IN ('.jpg', '.png')
            ORDER BY RAND() LIMIT {num}
            '''

        for image, tags, type_ in MYSQL.execute(SELECT, fetch=1):

            tags = sorted(tags.split())
            image = path / image
            prediction = model.predict(image)
            similar = set(tags) & set(prediction)

    else:

        import cv2
        import numpy as np
        from PIL import Image
        from random import choices

        glob = list(path.glob('[0-9a-f]/[0-9a-f]/*jpg'))

        for image in choices(glob, k=num):

            prediction = model.predict(image)

            image_ = np.aray(Image.open(image))
            image_ = cv2.cvtColor(image_, cv2.COLOR_RGB2BGR)
            cv2.imshow(prediction, image_)
            cv2.waitKey(0)

def Copy_Files(files, dest, sym=False):
    
    from pathlib import Path

    paths = [Path(file) for file in files]
    dest = Path(dest)

    for path in paths:

        name = dest / path.name    
        if sym and not name.exists(): name.symlink_to(path)
        else: name.write_bytes(path.read_bytes())

def Artist_statistics():

    from Webscraping import CONNECT

    MYSQL = CONNECT()

    SELECT = 'SELECT artist FROM imagedata GROUP BY artist HAVING COUNT(artist) > 100 ORDER BY artist'
    STATS = '''SELECT (
        SELECT COUNT(*) FROM imagedata 
        WHERE MATCH(tags, artist) AGAINST(%s IN BOOLEAN MODE) AND stars
        ) AS TOTAL,
        (
        SELECT SUM(stars) FROM imagedata 
        WHERE MATCH(tags, artist) AGAINST(%s IN BOOLEAN MODE)
        ) AS STARS
        '''

    for artist, in MYSQL.execute(SELECT, fetch=1)[1:101]:

        sum, star = MYSQL.execute(STATS, (artist, artist), fetch=1)
        try: print(f'{artist.strip():<25} (Num: {sum:>4}, Stars: {star:>4}): {star / (sum*5):>4.2%}')
        except: continue

def Find_symmetric_videos():

    from pathlib import Path
    from cv2 import VideoCapture
    from Webscraping import CONNECT

    def compare(seq):
        
        return [
            (left == right).all() for left, right, num in
            zip(seq, reversed(seq), range(len(seq) // 2))
            ]

    def symmetric(seq):
        
        if len(seq) % 2 != 0: del seq[len(seq) // 2]
        
        return any([
            compare(seq[1:]), compare(seq), compare(seq[:-1])
            ])
    
    MYSQL = CONNECT()
    SELECT = 'SELECT path FROM imagedata WHERE MATCH(tags, artist) AGAINST("animated -audio" IN BOOLEAN MODE) AND type=0'

    for path, in MYSQL.execute(SELECT, fetch=1):

        frames = []
        vidcap = VideoCapture(path)
        success, frame = vidcap.read()

        while success:
            
            frames.append(frame)
            success, frame = vidcap.read()
            
        if symmetric(frames): print(path)

def Download_Youtube():

    import os
    from Webscraping import USER, json_generator
    from Webscraping.utils import IncrementalBar

    path = USER / r'Downloads\Images\Youtube'
    username = ""
    password = ""

    for file in path.iterdir():
        
        error = 0
        urls = list(json_generator(file))
        progress = IncrementalBar('Files', max=len(urls))

        for url in urls[::-1]:

            progress.next()

            try:
                
                url = url['url']
                name = "youtube-dl -u "+username+" -p "+password+' -o "'+str(path)+'" '+url
                cmd = f'youtube-dl -u "{username}" -p "{password}" -o "{path}"  {url}"'
                os.system(cmd)

            except Exception as error_:

                print('\n', error_)
                error = error_
                continue
        
        if not error: file.unlink()

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

def Remove_Intro(path):

    def contrast(img, k_size=25):

        # convert to LAB color space
        lab = cv2.cvtColor(img,cv2.COLOR_BGR2LAB)

        # separate channels
        L,A,B=cv2.split(lab)

        # compute minimum and maximum in 5x5 region using erode and dilate
        kernel = np.ones((k_size,k_size),np.uint8)
        min = cv2.erode(L,kernel,iterations = 1)
        max = cv2.dilate(L,kernel,iterations = 1)

        # convert min and max to floats
        min = min.astype(np.float64) 
        max = max.astype(np.float64) 

        # compute local contrast
        contrast = (max-min) / (max+(min+1))

        # get average across whole image
        average_contrast = 100*np.mean(contrast)

        return average_contrast

    import ffmpeg, cv2, tempfile
    import numpy as np
    from pathlib import Path
    from Webscraping import CONNECT
    from Webscraping.utils import get_hash

    np.seterr(divide='ignore', invalid='ignore')
    SQL = CONNECT()
    UPDATE = 'UPDATE imagedata SET hash=%s WHERE path=%s'

    path = Path(path)
    vidcap = cv2.VideoCapture(str(path))
    success, frame = vidcap.read()
    # highest = 0

    while success:

        # min, max = frame.min(), frame.max()
        # x = frame.max() > 5 or frame.min() > 250
        # g = contrast(frame)
        # if g > highest: 
        #     highest = g
        # if frame.max() > 5 or frame.min() > 250:

        #     msec = vidcap.get(cv2.CAP_PROP_POS_MSEC) / 100
        msec = vidcap.get(cv2.CAP_PROP_POS_MSEC) / 100
        if (x:=contrast(frame)) > 5: break
        success, frame = vidcap.read()

    sec = msec / 1000
    # print(f'{path} {sec:.4f}, {x:.4f}\n'); return
    temp = Path(tempfile.gettempdir(), path.name)
    ffmpeg.input(str(path)) \
        .trim(start=sec) \
        .setpts('PTS-STARTPTS') \
        .output(str(temp)) \
        .run()

    SQL.execute(UPDATE, (get_hash(temp), path.name))
    path.write_bytes(temp.read_bytes())
    SQL.commit()

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

def make_stitch():
    
    import cv2
    from pathlib import Path
    from Webscraping import USER

    def get_frames(path):
        
        frames = []
        vidcap = cv2.VideoCapture(str(path))
        success, frame = vidcap.read()

        while success:
            
            frames.append(frame)
            success, frame = vidcap.read()
        
        return tuple(frames)

    test = USER / r'Downloads\Test'
    stitcher = cv2.Stitcher.create(cv2.Stitcher_SCANS)
    stitcher.setPanoConfidenceThresh(0.1)
    
    path = Path(input('Enter path: '))
    if path.is_file(): frames = get_frames(path)
    else: frames = [cv2.imread(str(path)) for path in path.iterdir()]
    
    status, image = stitcher.stitch(frames)
    cv2.imwrite(str(test / 'p.jpg'), image)

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
# from pathlib import Path
# from PIL import Image

# path = Path(r"C:\Users\Emc11\Dropbox\Pictures\Artwork\Fanart\Hime Hajime\2")
# foreground = r"C:\Users\Emc11\Dropbox\Pictures\Artwork\Fanart\Hime Hajime\Hime Lewd 2 Text Japanese Post Sex.png"
# fg = Image.open(foreground)

# for image in path.glob('Japanese*/*Pubic Hair/Post-Sex*'):

#     bg = Image.open(str(image))

#     bg.paste(fg, (0, 0), fg)
#     bg.save(str(image))

# from Webscraping.Favorites import twitter

# twitter.start(0, 0)
raise

# import sqlite3, re
# from pathlib import Path

# select1 = 'SELECT save_name FROM pixiv_master_image WHERE save_name=?'
# select2 = 'SELECT save_name FROM pixiv_manga_image WHERE save_name=?'
# update1 = 'UPDATE pixiv_master_image SET save_name=? WHERE save_name=?'
# update2 = 'UPDATE pixiv_manga_image SET save_name=? WHERE save_name=?'
# datab = sqlite3.connect(r'Webscraping\Pixivutil\db.sqlite')
# cursor = datab.cursor()
# path = Path(r'C:\Users\Emc11\Dropbox\ん\Images\pixiv')
# emoji = '🔞🍚🍀🍣🐄🌊'

# for file in path.glob(f'*[{emoji}]*'):

#     new = re.sub('|'.join(emoji), '', file.name)
#     new = file.with_name(new)
#     path = cursor.execute(select1, (str(file),)).fetchone()
#     cursor.execute(update1, (str(new), str(file)))
#     path = cursor.execute(select2, (str(file),)).fetchone()
#     cursor.execute(update2, (str(new), str(file)))
    
#     file.rename(new)
#     datab.commit()

# raise

paths = [
    r'C:\Users\Emc11\Dropbox\ん\c6\1c\c61c30759d7b9a2ba34d646775695c35.mp4', r'C:\Users\Emc11\Dropbox\ん\fd\e0\fde0789fdd44258db28b576861ad82a2.mp4', r'C:\Users\Emc11\Dropbox\ん\66\b1\66b1fd936d220d46d0b7fcffa699ef47.webm', r'C:\Users\Emc11\Dropbox\ん\22\af\22af3168e136f1dce57b4e9f7b605fd8.mp4', r'C:\Users\Emc11\Dropbox\ん\d9\ba\d9ba8bda9e57fd775fbf08c37392e830.mp4', r'C:\Users\Emc11\Dropbox\ん\41\bd\41bdd27cf5392e3ae931e4e7374fbf60.mp4', r'C:\Users\Emc11\Dropbox\ん\05\e8\05e8f5d988371a33094b5c2055251f3f.mp4', r'C:\Users\Emc11\Dropbox\ん\96\d7\96d7bab0ae25412dfed8b75561c77526.mp4', r'C:\Users\Emc11\Dropbox\ん\34\99\349998b4ba3796e12dd2424587915c5f.mp4', r'C:\Users\Emc11\Dropbox\ん\6b\9d\6b9d7a76159c6cdd17c234b6d01b3e96.mp4', r'C:\Users\Emc11\Dropbox\ん\a1\42\a1429a40d91073e0f08b6c45198a8eff.mp4', r'C:\Users\Emc11\Dropbox\ん\4a\df\4adfaa34fff22fd7b14a306659358a3b.mp4', r'C:\Users\Emc11\Dropbox\ん\89\12\89121a6355c5b3572c41f260be48eeff.mp4', r'C:\Users\Emc11\Dropbox\ん\54\d6\54d6693e1d78247da9922160e9c87140.mp4', r'C:\Users\Emc11\Dropbox\ん\73\7a\737a957f427c68d0db37e2dbc6171c7d.mp4', r'C:\Users\Emc11\Dropbox\ん\7a\20\7a2077ecf4e287f7557a6fdfc1f2c188.mp4', r'C:\Users\Emc11\Dropbox\ん\e1\a8\e1a8fe07661571251e7f53a718dd266b.mp4', r'C:\Users\Emc11\Dropbox\ん\30\d4\30d4ae75ccf85c25a61f62b3b04072e2.mp4', r'C:\Users\Emc11\Dropbox\ん\25\05\2505df22c62033e3cd920fd2da2304cb.mp4', r'C:\Users\Emc11\Dropbox\ん\76\c0\76c0beb2657d7179ab142f42acaca68b.mp4', r'C:\Users\Emc11\Dropbox\ん\0f\a0\0fa053a22a7e5ee6edce99375b4ae1a6.mp4', r'C:\Users\Emc11\Dropbox\ん\7d\c2\7dc21a5a268c2e04fe6a5aeb07c5f79b.mp4', r'C:\Users\Emc11\Dropbox\ん\4f\7d\4f7d34b134aeef311445d218ecf9d97b.mp4', r'C:\Users\Emc11\Dropbox\ん\fa\b3\fab3e48cc283855160be6d110dc8f627.mp4', r'C:\Users\Emc11\Dropbox\ん\67\3d\673d71eee74cf2ebc38359e831e05804.gif', r'C:\Users\Emc11\Dropbox\ん\0a\e8\0ae81505dc459f40388b7289220b9cfd.mp4', r'C:\Users\Emc11\Dropbox\ん\ce\98\ce98e51945c582c374bfddde563dc390.mp4', r'C:\Users\Emc11\Dropbox\ん\b1\3d\b13d314595154dced737168d045a98e3.webm', r'C:\Users\Emc11\Dropbox\ん\0f\5c\0f5c85cb9028769027a6a462eda1ee26.webm', r'C:\Users\Emc11\Dropbox\ん\34\ac\34ac79fd81ce8999c75495b47e5a3bbc.mp4', r'C:\Users\Emc11\Dropbox\ん\b5\9b\b59b2e6a1b015b6f1f4290123ec2e2dc.mp4', r'C:\Users\Emc11\Dropbox\ん\ab\77\ab779256fd4e1f52e270d784b17766dc.mp4', r'C:\Users\Emc11\Dropbox\ん\b4\d9\b4d9166574a2db637cc5da522dab4b3b.webm', r'C:\Users\Emc11\Dropbox\ん\45\85\4585958f488b78f350ec59f0fce34abe.mp4', r'C:\Users\Emc11\Dropbox\ん\9a\10\9a1023e1259b546f1cb022bd4abbdca5.mp4', r'C:\Users\Emc11\Dropbox\ん\26\b1\26b1c675043c5b9a58f2a2d17122f584.mp4', r'C:\Users\Emc11\Dropbox\ん\a1\6e\a16eeeb612e2ad9da5ec8da637bdf83c.mp4', r'C:\Users\Emc11\Dropbox\ん\a7\1a\a71abf6b0cd2d54853b07bf867a87197.mp4', r'C:\Users\Emc11\Dropbox\ん\a7\d0\a7d02f6ba480bcf516048883d8bcaa4e.mp4', r'C:\Users\Emc11\Dropbox\ん\93\81\9381234fb04f75a4962782e1112d503a.mp4', r'C:\Users\Emc11\Dropbox\ん\38\a7\38a72772f7105d10f56ead237040d5c4.mp4', r'C:\Users\Emc11\Dropbox\ん\b4\16\b416789224ec85da99a52abb2990f452.gif', r'C:\Users\Emc11\Dropbox\ん\dd\89\dd896cb2ceebfb1906cea540d1270af9.mp4', r'C:\Users\Emc11\Dropbox\ん\8d\cd\8dcd1016ecf1f714898b06320aa468e9.mp4', r'C:\Users\Emc11\Dropbox\ん\b7\9c\b79c62743b68e1101628b7390f1bc7a2.mp4', r'C:\Users\Emc11\Dropbox\ん\cb\38\cb380e27fab914948e3fe45ee002462e.mp4', r'C:\Users\Emc11\Dropbox\ん\72\ca\72caa03ef6057497506c3d0b4c210ccc.gif', r'C:\Users\Emc11\Dropbox\ん\98\07\98070d62de2cea1f4d6ab945eb8ef3b6.webm', r'C:\Users\Emc11\Dropbox\ん\e9\fa\e9fa0cca3eb28f87fee0a8ccad3737dd.webm', r'C:\Users\Emc11\Dropbox\ん\70\d5\70d57620a3f0d95e950863dcaaeebbda.mp4', r'C:\Users\Emc11\Dropbox\ん\db\29\db294619193672f83d0c09e177ede21e.mp4', r'C:\Users\Emc11\Dropbox\ん\d6\05\d6056f4b8f6023191daa5fbf04938fd9.mp4', r'C:\Users\Emc11\Dropbox\ん\f2\d3\f2d325e480d11b765e389f2b9e0f188f.mp4', r'C:\Users\Emc11\Dropbox\ん\39\09\390930f0bc9b72c49cb041227dc897db.mp4', r'C:\Users\Emc11\Dropbox\ん\7a\05\7a05f4d211dd2277475a3b89ef5d2f2c.webm', r'C:\Users\Emc11\Dropbox\ん\59\d9\59d9c90ce6b17f891984532dce18e356.mp4', r'C:\Users\Emc11\Dropbox\ん\3e\e2\3ee2b205c8a6c5211d4a96fb495b20e1.mp4', r'C:\Users\Emc11\Dropbox\ん\35\47\3547443efb784e59fe3ba01452a1b128.webm', r'C:\Users\Emc11\Dropbox\ん\14\17\141728937d8880a363e64c9fcd0970ce.mp4', r'C:\Users\Emc11\Dropbox\ん\10\76\1076a6050bc53aa8484d01c7e0ebad25.mp4', r'C:\Users\Emc11\Dropbox\ん\b9\47\b9473812bf91ffd9265a2612a73d2a67.mp4', r'C:\Users\Emc11\Dropbox\ん\88\f7\88f7bfeec90866e9b3929e8cf3f98ac5.mp4', r'C:\Users\Emc11\Dropbox\ん\06\ca\06ca76aa4a201120294b4f0a97081686.mp4', r'C:\Users\Emc11\Dropbox\ん\a2\4a\a24ab0ed3910d4ffa80c5769d82ec886.mp4', r'C:\Users\Emc11\Dropbox\ん\fc\8c\fc8c3ba59af17e49e198fd9512eab3ff.mp4', r'C:\Users\Emc11\Dropbox\ん\3a\05\3a050b1d4131884bbee3a1808af78528.mp4', r'C:\Users\Emc11\Dropbox\ん\f1\26\f12628a66b7126f705c5802e13449e31.mp4', r'C:\Users\Emc11\Dropbox\ん\62\60\626009fc4190a30a087e70dbd8bb1a8c.mp4', r'C:\Users\Emc11\Dropbox\ん\0d\f8\0df8ac8872cb3423969bba5055580ebb.mp4', r'C:\Users\Emc11\Dropbox\ん\2b\e8\2be8c06630a6cdbccf2ba8be22d5a521.mp4', r'C:\Users\Emc11\Dropbox\ん\ea\67\ea67ad3af4fdde6d458a936cd4e0fe92.mp4', r'C:\Users\Emc11\Dropbox\ん\2e\93\2e935d6bbf299b9215883b4c7eeb2d0d.mp4', r'C:\Users\Emc11\Dropbox\ん\39\8f\398fad85cdaa47aa19dca078fcc65a35.mp4', r'C:\Users\Emc11\Dropbox\ん\3a\57\3a57574815bcd1ac30c9bde04fa6dec6.webm', r'C:\Users\Emc11\Dropbox\ん\be\3e\be3e9c881705d1527ac0f8b8b6ab7ff1.mp4', r'C:\Users\Emc11\Dropbox\ん\bd\4f\bd4fd257915ba22615b0ae2e88d94317.mp4', r'C:\Users\Emc11\Dropbox\ん\32\dc\32dcb7cff4a06fb3e54af0efed23a225.mp4', r'C:\Users\Emc11\Dropbox\ん\7c\cd\7ccdedac49cb8242e7f43866fb3129ab.mp4', r'C:\Users\Emc11\Dropbox\ん\f9\51\f951212869be0c4ff5a9d3661965eeb5.webm', r'C:\Users\Emc11\Dropbox\ん\f6\27\f6276304186d11782e973cef75a18c5c.mp4', r'C:\Users\Emc11\Dropbox\ん\01\62\01626b0a8749ad33196c4746c055e399.mp4', r'C:\Users\Emc11\Dropbox\ん\d4\6b\d46b15a071ae57088968373251ba2816.webm', r'C:\Users\Emc11\Dropbox\ん\ee\b2\eeb2c0464cb73991fafe7d631c03e30f.webm', r'C:\Users\Emc11\Dropbox\ん\d4\f8\d4f890d9855f5ae9f1e30ee038d024e9.mp4', r'C:\Users\Emc11\Dropbox\ん\32\c0\32c05eaca9085298fc3f8850bd3c07ef.mp4', r'C:\Users\Emc11\Dropbox\ん\ff\cf\ffcf4fa89ab91b341945c8aaebb4d15e.mp4', r'C:\Users\Emc11\Dropbox\ん\68\77\6877b6027db95f15e5fec43744ae9fa1.webm', r'C:\Users\Emc11\Dropbox\ん\61\c7\61c7e84ce2b18599b1f8ed69c083daca.mp4', r'C:\Users\Emc11\Dropbox\ん\44\8c\448cb49fbcf35a9b2931ae937d95bd92.mp4', r'C:\Users\Emc11\Dropbox\ん\61\79\617969d4f2051f2f4302e6fbf5eb581b.mp4', r'C:\Users\Emc11\Dropbox\ん\09\75\0975f3bba8847d1e4e36075a18ae09e6.mp4', r'C:\Users\Emc11\Dropbox\ん\a0\cd\a0cd180b9c569a322ee780bce34bc84d.mp4', r'C:\Users\Emc11\Dropbox\ん\4b\24\4b24f38a23e6ad3c8f1b617646b7f0aa.mp4', r'C:\Users\Emc11\Dropbox\ん\aa\24\aa248160b11ee102e43fd9b41a4dcff2.mp4', r'C:\Users\Emc11\Dropbox\ん\da\6f\da6f89b79b74ce0aae438cf64ad22585.mp4', r'C:\Users\Emc11\Dropbox\ん\b7\37\b737d834c5154629118755a5910c80c6.mp4', r'C:\Users\Emc11\Dropbox\ん\98\d1\98d17738b3e23abe5aea710ccee581d5.mp4', r'C:\Users\Emc11\Dropbox\ん\f9\fa\f9fa827fa88a350a09c4514fdd79775f.mp4', r'C:\Users\Emc11\Dropbox\ん\a0\d7\a0d72a879fce5ef75e61d5945ec49635.mp4', r'C:\Users\Emc11\Dropbox\ん\98\5e\985e38d6e4d297cfec2cd6ffb80685ab.mp4', r'C:\Users\Emc11\Dropbox\ん\a0\cb\a0cba59a99739cdecd377ea21f54724c.mp4', r'C:\Users\Emc11\Dropbox\ん\42\7f\427f670f9ceb7fcff7386e24b84acbee.webm', r'C:\Users\Emc11\Dropbox\ん\0f\c6\0fc656f5779741a0942dfe3923856a4c.mp4', r'C:\Users\Emc11\Dropbox\ん\0a\9c\0a9c5e3072f95cab2852b64938f08a7c.webm', r'C:\Users\Emc11\Dropbox\ん\f5\36\f53612c15b44c92e98d2f596a4550c68.mp4', r'C:\Users\Emc11\Dropbox\ん\9f\34\9f342dec7e4d20f8e5a4bba56279b477.webm', r'C:\Users\Emc11\Dropbox\ん\6d\64\6d64ae097bb7f42eab358754c538304a.webm', r'C:\Users\Emc11\Dropbox\ん\aa\dd\aaddd22da75ea329988bf2a39300858d.mp4', r'C:\Users\Emc11\Dropbox\ん\ff\42\ff42182fdc04a789248466f6f52c1971.mp4', r'C:\Users\Emc11\Dropbox\ん\64\71\6471f3d96f714b2d5e504c495eb07636.webm', r'C:\Users\Emc11\Dropbox\ん\31\7e\317e8616d69db90b4fc52590c8f97f44.mp4', r'C:\Users\Emc11\Dropbox\ん\37\96\3796b3458efc0a8a168c5615fa8a40ff.webm', r'C:\Users\Emc11\Dropbox\ん\b8\f7\b8f72bbf60cd1c7c2bd3be426281c697.webm', r'C:\Users\Emc11\Dropbox\ん\91\29\9129ba862beca80d02aca5728024b392.mp4', r'C:\Users\Emc11\Dropbox\ん\2b\a1\2ba167d7e0ffaa8fe101585deaf745b5.webm', r'C:\Users\Emc11\Dropbox\ん\1e\38\1e381265da05043a69684e955bb15590.webm', r'C:\Users\Emc11\Dropbox\ん\a0\c1\a0c1ec22dd0a16db5074cae77715d9a2.webm', r'C:\Users\Emc11\Dropbox\ん\d5\e2\d5e2cd2428aa810cdc19362a4a80cd06.mp4', r'C:\Users\Emc11\Dropbox\ん\2e\63\2e6388eb8db71d88d131ab39ea9eb076.mp4', r'C:\Users\Emc11\Dropbox\ん\92\0a\920a9b612d2f325732651d10846793ac.mp4', r'C:\Users\Emc11\Dropbox\ん\a2\6e\a26eb1aa357320451958b6fe75579f98.webm', r'C:\Users\Emc11\Dropbox\ん\7f\f8\7ff85aca49a138d55e6183d03335b563.mp4', r'C:\Users\Emc11\Dropbox\ん\cf\74\cf7495e3e3d301fe4fa567cd6f236a31.webm', r'C:\Users\Emc11\Dropbox\ん\c9\d6\c9d6f9b5eca96969ae568ffaa646e89e.mp4', r'C:\Users\Emc11\Dropbox\ん\47\6a\476a1f5e11d6a7c44d6e1ca97e93707e.webm', r'C:\Users\Emc11\Dropbox\ん\3f\1f\3f1f3c65fd3f18e566f47d2485edae23.mp4', r'C:\Users\Emc11\Dropbox\ん\8f\43\8f4312e3b2ee19d09f8322c1963c151f.mp4', r'C:\Users\Emc11\Dropbox\ん\7f\b6\7fb61f2a718dcca444c4f5995637f9b2.webm', r'C:\Users\Emc11\Dropbox\ん\bc\c0\bcc05f26739d4404eaf06ea469d2e171.webm', r'C:\Users\Emc11\Dropbox\ん\94\4c\944c5eac5561f29ada737827a528df69.gif', r'C:\Users\Emc11\Dropbox\ん\9d\38\9d387a7148b024ace4b9a128046d2830.webm', r'C:\Users\Emc11\Dropbox\ん\c1\83\c183f5b5c1fe1ce3475c464634c403ee.mp4', r'C:\Users\Emc11\Dropbox\ん\79\4b\794b5c497fdc2818a3c396fa0070fcae.mp4', r'C:\Users\Emc11\Dropbox\ん\56\6b\566bf4f1920c09337b5bf53a4d7dbae8.webm', r'C:\Users\Emc11\Dropbox\ん\e6\e0\e6e0782c4f9eff43d2d25b8354ed6c6c.webm', r'C:\Users\Emc11\Dropbox\ん\a1\97\a19757cc98363968617375a014919c93.mp4', r'C:\Users\Emc11\Dropbox\ん\07\85\07853bd34ac6da304409d6cdc667122a.gif', r'C:\Users\Emc11\Dropbox\ん\25\26\2526bdcae7be525a1a7ed29b0e30b6be.mp4', r'C:\Users\Emc11\Dropbox\ん\ee\3b\ee3bb449d175ad2c78e615bcc77c9e4a.mp4', r'C:\Users\Emc11\Dropbox\ん\7b\2c\7b2c9f1b23b69e94595549b2eaeb19b5.mp4', r'C:\Users\Emc11\Dropbox\ん\d6\ab\d6ab5816c79202844a97e6f1dbbf399b.mp4', r'C:\Users\Emc11\Dropbox\ん\ca\51\ca5177c2f8241639b335c635becf6ce9.webm', r'C:\Users\Emc11\Dropbox\ん\fc\ec\fcec9833773b783948df21b1e5e108c4.mp4', r'C:\Users\Emc11\Dropbox\ん\18\f9\18f9ec320521f804eaa904aac33aae0f.webm', r'C:\Users\Emc11\Dropbox\ん\21\70\21701a01eeb2907808b6158ea8135d53.webm', r'C:\Users\Emc11\Dropbox\ん\12\2c\122c98b2b9db8d72175bdb9b5bbd0d82.webm', r'C:\Users\Emc11\Dropbox\ん\f9\1f\f91f7fd773fd882e6dbe669d0d120038.mp4', r'C:\Users\Emc11\Dropbox\ん\b0\fc\b0fc481bd04bc284eed888e273e10e0a.gif', r'C:\Users\Emc11\Dropbox\ん\53\91\53917954a143949ead1349a9942d5178.mp4', r'C:\Users\Emc11\Dropbox\ん\a2\61\a261f9f4ebb489378f7960c42d48e4e4.webm', r'C:\Users\Emc11\Dropbox\ん\15\36\1536247b790f0328b08dc6fa73dfffe1.webm', r'C:\Users\Emc11\Dropbox\ん\19\37\19373c9ff87f317dc7c023350c3bcdb4.mp4', r'C:\Users\Emc11\Dropbox\ん\46\2b\462b346b4da71e888f9afdd94233386a.webm', r'C:\Users\Emc11\Dropbox\ん\41\ee\41ee5a632dd3f0c254ed43135ee83181.webm', r'C:\Users\Emc11\Dropbox\ん\15\14\1514a18e78b8058dd0c794bf82648ae6.webm', r'C:\Users\Emc11\Dropbox\ん\60\89\6089d7fb9cb563a6144ac3526b6b3620.mp4', r'C:\Users\Emc11\Dropbox\ん\20\33\203385ab8bf2bb26dcd0bebb1919cd1a.webm', r'C:\Users\Emc11\Dropbox\ん\c4\81\c481391c8a9c98b836d9c9b258351ba0.mp4', r'C:\Users\Emc11\Dropbox\ん\00\59\0059c5475677dae5ff85f19b438b83fc.mp4', r'C:\Users\Emc11\Dropbox\ん\89\c6\89c67e0df1c6fafd6b25c8ea2a2c1222.mp4', r'C:\Users\Emc11\Dropbox\ん\96\51\9651e3a83042359a4729ce4eaed8648a.webm'
    ]

for path in paths: Remove_Intro(path)