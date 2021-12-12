import argparse

def run():

    args = parser.parse_args()
    if not (args.args or args.func): return

    function = args.func
    arguments = args.args
    
    exec(f'{function}({arguments})')

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

def Clean_Database():

    import sqlite3, re
    from pathlib import Path

    select1 = 'SELECT save_name FROM pixiv_master_image WHERE save_name=?'
    select2 = 'SELECT save_name FROM pixiv_manga_image WHERE save_name=?'
    update1 = 'UPDATE pixiv_master_image SET save_name=? WHERE save_name=?'
    update2 = 'UPDATE pixiv_manga_image SET save_name=? WHERE save_name=?'
    datab = sqlite3.connect(r'Webscraping\Pixivutil\db.sqlite')
    cursor = datab.cursor()
    path = Path(r'C:\Users\Emc11\Dropbox\ん\Images\pixiv')
    emoji = '🔞🍚🍀🍣🐄🌊'

    for file in path.glob(f'*[{emoji}]*'):

        new = re.sub('|'.join(emoji), '', file.name)
        new = file.with_name(new)
        path = cursor.execute(select1, (str(file),)).fetchone()
        cursor.execute(update1, (str(new), str(file)))
        path = cursor.execute(select2, (str(file),)).fetchone()
        cursor.execute(update2, (str(new), str(file)))
        
        file.rename(new)
        datab.commit()

def unnamed(path):

    from Webscraping import CONNECT, utils
    from pathlib import Path

    MYSQL = CONNECT()
    SELECT = 'SELECT path FROM imagedata WHERE hash=%s OR path=%s'
    path = Path(path)
    num = 0

    for file in path.glob('**/*.*'):

        hash_ = utils.get_hash(file)
        target = MYSQL.execute(SELECT, (hash_, file.name), fetch=1)
        if len(target) == 1 and (target:=target[0][0]) is not None:
            
            p = utils.PATH / target[:2] / target[2:4] / target
            
            if p.exists():
                
                file.unlink()
                num += 1
                
    print(f'{num} files deleted')

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