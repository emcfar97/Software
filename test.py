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
    from utils import pathwalk
    
    def tabber(parts, tabbed='', folders=['', '', '', '', '', '']):
        
        for num, part in enumerate(parts[6:-1], start=1):
            
            if part != folders[num]:
                folders[num] = part
                tabbed += '{}{}\n'.format('\t' * num, part)
                
        return tabbed
    
    projects = USER / r'Dropbox\Pictures\Projects'
    artwork = USER / r'Dropbox\Pictures\Artwork'
    videos = USER / r'Dropbox\Videos\Captures'
    video_glob = '[0-9]*-[0-9]*-[0-9]*.mp4'
    
    open = 'Open Projects:\n'
    closed = 'Closed Projects:\n'
    planned = 'Planned Projects:\n'
    
    for projects in projects.glob('**/*.clip'):
        
        if len(project.parts[6:-1]) < 2: continue
        
        head = r'\\'.join(project.parts[6:-1])
        head = re.sub(r'\\page\d+.clip', '', head)
        
        video = videos / head / project.stem
        art = artwork / head / project.stem
        
        if re.match('page\d+', project.stem): video = videos.parent
        if re.match('page\d+', project.stem): art = artwork.parent
        
        video_path = video.exists()
        videos_exist = bool(list(video.glob(video_glob))) if video_path else False
        art_path = art.exists()
        art_exists = bool(list(art.iterdir())) if art_path else False
        
        if videos_exist and not art_exists:

            latest = list(video.glob(video_glob))[-1]
            
            open += tabber(project.parts)
            open += f'\t\t\t\t{project.stem} ({latest.stem})\n'

        elif videos_exist and art_exists:
            
            closed += tabber(project.parts)
            closed += f'\t\t\t\t{project.stem}\n'
                    
        elif not (video_path and art_path):
            
            planned += tabber(project.parts)
            planned += f'\t\t\t\t{project.stem}\n'

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
        
        if file.suffix not in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.webm', 'mp4'): continue
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

    import bs4, re
    from PIL.Image import open
    from Webscraping import WEBDRIVER, USER
    from Webscraping.utils import save_image

    DRIVER = WEBDRIVER(0, 0)
    path = USER / r'Dropbox\ん'
    regex = '(.+img2.+png)'

    for file in path.glob('**/*g'):
        
        image = open(file)
        
        if min(image.height, image.width) < 500 and (not image.height == 1320 and not image.width == 1000):
            
            DRIVER.get('https://www.google.com/imghp?hl=en&tab=wi&ogbl')
            DRIVER.find('//body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]', click=1)
            DRIVER.find('//body/div[1]/div[3]/div/div[2]/form/div[1]/div/a', click=1)
            DRIVER.find('//*[@id="awyMjb"]', keys=str(file))
            
            try: DRIVER.find('//*[text()="All sizes"]', click=True, fetch=1)
            except: continue
            html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
            images = html.findAll('div', {'data-ow':True, 'data-oh':True})
            largest = sorted(images, key=lambda x:int(x.get('data-oh')))[-1]
            href = largest.find('a', target='_blank')
            
            DRIVER.get(href.get('href'), wait=5)
            html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')
            src = html.findAll('img', src=re.compile(regex))
            if len(src) == 1:
                save_image(file, src[0].get('src'))
            else:
                continue

def check_predictions(num=25):
    
    import cv2
    import numpy as np
    from PIL import Image
    from pathlib import Path
    from Webscraping import CONNECT, WEBDRIVER
    from Webscraping.utils import PATH, get_tags
    from MachineLearning.Tensorflow import Model

    model = Model(
        r'deepdanbooru.hdf5', 
        r'deepdanbooru\tags.txt'
        )
    driver = WEBDRIVER(profile=0)
    mysql = CONNECT()

    parts = ", ".join([f"'{part}'" for part in PATH.parts]).replace('\\', '')
    SELECT = f'''
        SELECT full_path(path, {parts}) FROM imagedata 
        WHERE SUBSTR(path, 33, 5) IN ('.jpg', '.png')
        ORDER BY RAND() LIMIT {num}
        '''

    for image, in mysql.execute(SELECT, fetch=1):

        prediction_1 = model.predict(image)
        prediction_2 = get_tags(driver, Path(image)).split()

        # print(sorted(prediction_1), sorted(prediction_2))
        print(f'Difference: {len(set(prediction_1) ^ set(prediction_2))} Intersection: {len(set(prediction_1) & set(prediction_2))}')
        
        # image_ = np.array(Image.open(image))
        # image_ = cv2.cvtColor(image_, cv2.COLOR_RGB2BGR)
        # cv2.imshow(image, image_)
        # cv2.waitKey(0)

def f():
    
    from Webscraping import CONNECT, WEBDRIVER
    from Webscraping.utils import PATH, get_tags, generate_tags

    DRIVER = WEBDRIVER(profile=None)
    mysql = CONNECT()
    SELECT = 'SELECT path FROM userdata.imagedata WHERE (tags=" qwd " OR tags=" qwd animated " OR tags=" animated qwd ") AND NOT ISNULL(path)'
    UPDATE = 'UPDATE userdata.imagedata SET tags=%s, rating=%s WHERE path=%s'
    DELETE = 'DELETE FROM userdata.imagedata WHERE path=%s'
    x = mysql.execute(SELECT, fetch=1)
    for file, in mysql.execute(SELECT, fetch=1)[::-1]:
            
        file = PATH / file[0:2] / file[2:4] / file
        if not file.exists(): mysql.execute(DELETE, (file.name,), commit=1)

        try:
            if len(file.read_bytes()) == 0:
                if mysql.execute(DELETE, (file.name,)):
                    file.unlink()
                    mysql.commit()
        except FileNotFoundError:
            mysql.execute(DELETE, (file.name,), commit=1)
        
        tags, rating = generate_tags(
            general=get_tags(DRIVER, file, True), 
            custom=True, rating=True, exif=False
            )
        
        mysql.execute(UPDATE, (f' {tags} ', rating, file.name), commit=1)
    
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