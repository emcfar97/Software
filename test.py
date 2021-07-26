import argparse

def run():

    args = parser.parse_args()
    if not (args.args or args.func): return

    function = args.func
    arguments = args.args

    exec(f'{function}({arguments})')

def Normalize_Database():

    from pathlib import Path
    from Webscraping import CONNECT, USER, utils
    
    MYSQL = CONNECT()
    DROPBOX = USER / r'Dropbox\ん'
    parts = ", ".join([f"'{part}'" for part in DROPBOX.parts]).replace('\\', '')
    SELECT = f'SELECT full_path(path, {parts}) FROM imagedata WHERE NOT ISNULL(path)'
    select = 'SELECT src, href FROM imagedata WHERE path=%s'
    UPDATE = 'UPDATE imagedata SET path=NULL WHERE path=%s'
    DELETE = 'DELETE FROM imagedata WHERE path=%s'

    database = set(
        Path(path) for path, in MYSQL.execute(SELECT, fetch=1)
        )
    windows = set(DROPBOX.glob('[0-9a-f]/[0-9a-f]/*'))
    x, y = database - windows, windows - database
    
    for num, file in enumerate(x, 1):
        if any(*MYSQL.execute(select, (file.name,), fetch=1)):
            MYSQL.execute(UPDATE, (file.name,), commit=1)
        else:
            MYSQL.execute(DELETE, (file.name,), commit=1)
    else:
        try: print(f'{num} records deleted')
        except: print('0 records deleted')

    SELECT = 'SELECT path FROM imageData WHERE hash=%s OR path=%s'

    for num, file in enumerate(y, 1):

        hash_ = utils.get_hash(file)
        name = utils.get_name(file)

        image = MYSQL.execute(SELECT, (hash_, name.name), fetch=1)
        if image:
            try:
                file.rename(name)
            except FileExistsError:
                file.unlink()
        else:
            try: file.replace(DROPBOX / r'Downloads\Test\Reserve' / file.name)
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

def Copy_Files(files, dest):
    
    from pathlib import Path

    dest = Path(dest)
    paths = [Path(file) for file in files]
    [
        (dest / path.name).write_bytes(path.read_bytes()) 
        for path in paths
        ]

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

    from pytube import YouTube
    from Webscraping import USER, json_generator
    from Webscraping.utils import IncrementalBar

    path = USER / r'Downloads\Images\Youtube'

    for file in path.iterdir():
        
        error = 0
        urls = list(json_generator(file))
        progress = IncrementalBar('Files', max=len(urls))

        for url in urls[::-1]:

            progress.next()
            video = YouTube(url['url'])
            try:
                func = video.streams.get_highest_resolution()
                func.download(path.parent)
            except Exception as error_: 
                error = error_
                continue
        
        if not error: file.unlink()

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

def path_walk(top, topdown=False, followlinks=False):
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
            for x in path_walk(name, topdown, followlinks):
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