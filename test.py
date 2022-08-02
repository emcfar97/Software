import argparse

def run():

    args = parser.parse_args()
    if not (args.args or args.func): return

    function = args.func
    arguments = args.args
    
    exec(f'{function}({arguments})')

def Check_Predictions(sql=False, num=25):
    
    from Webscraping import USER
    from MachineLearning.Tensorflow import Model

    path = USER / r'Dropbox\ん'
    model = Model('Medium-07.hdf5')

    if sql:
        
        import cv2
        import numpy as np
        from PIL import Image
        from os import path
        from Webscraping import CONNECT, ROOT
        
        PATH = ROOT / path.expandvars(r'\Users\$USERNAME\Dropbox\ん')
        parts = ", ".join([f"'{part}'" for part in PATH.parts]).replace('\\', '')

        MYSQL = CONNECT()
        SELECT = f'''
            SELECT full_path(path, {parts}) FROM imagedata 
            WHERE SUBSTR(path, 33, 5) IN ('.jpg', '.png')
            ORDER BY RAND() LIMIT {num}
            '''

        for image, in MYSQL.execute(SELECT, fetch=1):

            prediction = model.predict(image)

            image_ = np.array(Image.open(image))
            image_ = cv2.cvtColor(image_, cv2.COLOR_RGB2BGR)
            cv2.imshow(prediction, image_)
            cv2.waitKey(0)

    else:

        from random import choices

        glob = list(path.glob('[0-9a-f]/[0-9a-f]/*jpg'))

        for image in choices(glob, k=num):

            prediction = model.predict(image)

            image_ = np.array(Image.open(image))
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

def Download_Youtube(username='', password=''):

    import os, send2trash
    from Webscraping import USER, json_generator
    from Webscraping.utils import IncrementalBar

    path = USER / r'Downloads\Images\Youtube'

    for file in path.iterdir():
        
        error = 0
        urls = list(json_generator(file))
        progress = IncrementalBar('Files', max=len(urls))

        for url in urls:

            progress.next()

            try:
                
                url = url['url']
                name = path.parent / f"{url.split('=')[-1]}.mp4"
                cmd = f'youtube-dl -u "{username}" -p "{password}" -o "{name}"  "{url}"'
                os.system(cmd)

            except Exception as error_:

                print('\n', error_)
                error = error_
                continue
        
        # if not error: send2trash.send2trash(file)

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

def Extract_Sprite(path):
    
    import cv2, skimage
    import numpy as np
    from pathlib import Path

    path = Path(path)

    for file in path.glob('**/*.jpg'):
        
        image = cv2.imread(str(file))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
        alpha = cv2.threshold(gray, 16, 255, cv2.THRESH_BINARY)[1]

        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        # temp = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)
        # temp = cv2.erode(temp, (3,3), iterations=3)
        # temp = temp[:, :, 3]
        # temp[np.all(temp[:, :, 0:3] == (0, 0, 0), 2)] = 0
        # alpha
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)
        alpha = cv2.erode(alpha, (3,3), iterations=3)
        
        b, g, r, a = cv2.split(image)
        rgba = [b, g, r, alpha]
        image = cv2.merge(rgba, 4)
        
        cv2.imwrite(str(file.parent / file.with_suffix('.png').name), image)

def Project_Stats():

    import re
    from Webscraping import USER

    projects = USER / r'Dropbox/Pictures/Projects'
    artwork = USER / r'Dropbox/Pictures/Artwork'
    videos = USER / r'Dropbox/Videos/Captures'
    
    open = 'Open Projects:\n'
    closed = 'Closed Projects\n'
    planned = 'Planned Projects\n'
    
    for file in projects.glob('**/*.clip'):
        
        project = r'\\'.join(file.parts[6:-1])
        if len(file.parts[6:-1]) < 2: continue
        
        video = videos / project / file.stem
        art = artwork / project / re.findall('.+ (\d+)', file.stem)[0]
        if not video.exists():
            video = videos / project / re.findall('.+ (\d+)', file.stem)[0]
        # if not art.exists():
        #     art = artwork / project
        
        if list(video.iterdir()) and not art.exists(): 
            
            latest = list(video.iterdir())[-1]
            open += f'\t{file.name} ({latest.stem})\n'
            # open += f'\t\t{file.name}\n'

        elif list(video.iterdir()) and art.exists(): 
            
            closed += f'\t{file.name}\n'
            # closed += f'\t\t{file.name}\n'

        elif not (video.exists() and art.exists()): 
            
            planned += f'\t{file.name}\n'
            # planned += f'\t\t{file.name}\n'

        # print(file)
        # print(f'{video}: {video.exists()} | {art}: {art.exists()}\n')
    print(open)
    print(closed)
    print(planned)
        
def unnamed(path):

    from Webscraping import CONNECT, utils
    from pathlib import Path

    MYSQL = CONNECT()
    SELECT = 'SELECT path FROM imagedata WHERE hash=%s OR path=%s'
    path = Path(path)
    num = 0

    for file in path.glob('**/*.*'):
        
        if file.suffix not in ('.jpg', '.jpeg', '.png', '.gif', '.webm', 'mp4'): continue
        hash_ = utils.get_hash(file)
        target = MYSQL.execute(SELECT, (hash_, file.name), fetch=1)
        if len(target) == 1 and (target:=target[0][0]) is not None:
            
            if (utils.PATH / target[:2] / target[2:4] / target).exists():
                
                file.unlink()
                num += 1
                
    print(f'{num} files deleted')

def parser():
    
    import re
    import pyparsing as pp
    from pyparsing import pyparsing_common

    LPAR, RPAR = map(pp.Suppress, '()')
    expr = pp.Forward()
    operand = pyparsing_common.real | pyparsing_common.integer | pyparsing_common.identifier
    factor = operand | pp.Group(LPAR + expr + RPAR)
    term = factor + pp.ZeroOrMore(pp.oneOf('* AND ') + factor )
    expr <<= term + pp.ZeroOrMore(pp.oneOf('+ OR') + term )

    expr = pp.infixNotation(operand,
        [
        (pp.oneOf('- NOT'), 1, pp.opAssoc.RIGHT),
        (pp.oneOf('* AND'), 2, pp.opAssoc.LEFT),
        (pp.oneOf('+ OR'), 2, pp.opAssoc.LEFT),
        ])

    string = 'standing sex ass'

    print(expr.parseString(string))

def Find_Larger_Image():

    from PIL.Image import open
    from pathlib import Path
    from Webscraping import WEBDRIVER

    webdriver = WEBDRIVER(0, 0)
    path = Path(r'C:\Users\Emc11\Dropbox\ん')

    for file in path.glob('**/*g'):
        
        image = open(file)
        
        if image.height < 500 or image.width < 500:
            
            webdriver.get('https://www.google.com/imghp?hl=en&tab=wi&ogbl')
            webdriver.find('//body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]', click=1)
            webdriver.find('//body/div[1]/div[3]/div/div[2]/form/div[1]/div/a', click=1)
            webdriver.find('//*[@id="awyMjb"]', keys=str(file))


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