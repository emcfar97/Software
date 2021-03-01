def Controller(arg=None):
    
    import Webscraping
    from Webscraping import insert_records
    from Webscraping.Photos import elitebabes, posespace, blogspot

    elitebabes.start()
    # posespace.start(0)
    # blogspot.start(1, 0)
    
    if arg == 0: Webscraping.start()
    elif arg == 1:
        insert_records.start()
        Update_Autocomplete()

def Artist_statistics():

    from Webscraping import CONNECT

    CONNECTION = CONNECT()

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

    for artist, in CONNECTION.execute(SELECT, fetch=1)[1:101]:

        sum, star = CONNECTION.execute(STATS, (artist, artist), fetch=1)
        try: print(f'{artist.strip():<25} (Num: {sum:>4}, Stars: {star:>4}): {star / (sum*5):>4.2%}')
        except: continue

def Remove_redundancies():

    from Webscraping import CONNECT

    CONNECTION = CONNECT()        
    SELECT = 'SELECT path, artist, tags FROM imageData WHERE path Like "C%"'
    UPDATE = 'UPDATE imageData SET artist=%s, tags=%s WHERE path=%s'

    for (path, artist, tags,) in CONNECTION.execute(SELECT, fetch=1):

        artist = f' {" ".join(set(artist.split()))} '
        tags = f' {" ".join(set(tags.split()))} '
        CONNECTION.execute(UPDATE, (artist, tags, path))

    CONNECTION.commit()

def Normalize_database():

    from os import path
    from pathlib import Path
    from Webscraping import CONNECT, ROOT
    
    CONNECTION = CONNECT()
    DROPBOX = ROOT / path.expandvars(r'\Users\$USERNAME\Dropbox\ん')
    CASE = r'''
        case type
        when 1 then CONCAT('{0}\エラティカ ニ\', path)
        when 2 then CONCAT('{0}\エラティカ 三\', path)
        when 3 then CONCAT('{0}\エラティカ 四\', path)
        end
        '''.format(DROPBOX).replace('\\', '\\\\')
    SELECT = f'SELECT {CASE} FROM imageData WHERE NOT ISNULL(path)'
    DELETE = 'DELETE FROM imageData WHERE path=SUBSTRING(%s, 34)'

    database = set(
        Path(path) for path, in CONNECTION.execute(SELECT, fetch=1)
        )
    windows = set(
        DROPBOX.glob('エラティカ */*')
        )
    y = windows - database
    x = database - windows
    
    for num, file in enumerate(y, 1):
        file.replace(USER / r'\Downloads\Test' / file.name)
    else:
        try: print(f'{num} files moved')
        except: print('0 files moved')
    
    for num, file in enumerate(x, 1):
        CONNECTION.execute(DELETE, (str(file),), commit=1)
    else:
        try: print(f'{num} records deleted')
        except: print('0 records deleted')

def Check_Predictions():
    
    import cv2, random
    from PIL import Image
    from MachineLearning import Model, USER, np

    model = Model('medium-01.hdf5')
    path = USER / r'\Dropbox\ん'
    glob = list(path.glob('エラティカ *\*jpg'))

    for image in random.choices(glob, k=25):

        prediction = model.predict(image)

        image_ = np.aray(Image.open(image))
        image_ = cv2.cvtColor(image_, cv2.COLOR_RGB2BGR)
        cv2.imshow(prediction, image_)
        cv2.waitKey(0)

def Update_Autocomplete():

    from pathlib import Path
    from Webscraping import CONNECT

    CONNECTION = CONNECT()
    CONNECTION.execute('SET GLOBAL group_concat_max_len=10000000')
    artist, tags = CONNECTION.execute(
        '''SELECT 
        GROUP_CONCAT(DISTINCT artist ORDER BY artist SEPARATOR ""), 
        GROUP_CONCAT(DISTINCT tags ORDER BY tags SEPARATOR "") 
        FROM imagedata''',
        fetch=1)[0]
    text = (
        ' '.join(sorted(set(artist.split()))), 
        ' '.join(sorted(set(tags.split())))
        )
    text = ('\n'.join(text)).encode('ascii', 'ignore')
    Path(r'GUI\autocomplete.txt').write_text(text.decode())

def iterate():

    import requests, bs4
    from Webscraping import CONNECT
    from Webscraping.utils import METADATA, IncrementalBar

    def fetch_row():

        while True:
            row = CONNECTION.CURSOR.fetchone()
            if not row: break
            yield row

    METADATA = set(METADATA.keys())
    CONNECTION = CONNECT()
    SELECT = 'SELECT {} FROM imageData WHERE site IN ("sankaku", "gelbooru") AND type=2'
    UPDATE = 'UPDATE imageData SET tags=CONCAT(tags, %s) WHERE path=%s'
    progress = IncrementalBar(
        '', max=CONNECTION.execute(SELECT.format('COUNT(*)',), fetch=1)[0]
        )
    CONNECTION.execute(SELECT.format('path, tags, href, site',))

    for (path, tags, href, site,) in fetch_row():

        progress.next()
        if site == 'sankaku':
            page_source = requests.get(f'https://chan.sankakucomplex.com{href}')
            html = bs4.BeautifulSoup(page_source.content, 'lxml')
            metadata = set(
                '_'.join(tag.text.split()[:-2]) for tag in 
                html.findAll(class_='tag-type-medium')
                )
        else:
            page_source = requests.get(f'https://gelbooru.com/{href}')
            html = bs4.BeautifulSoup(page_source.content, 'lxml')
            metadata = set(
                '_'.join(tag.text.split(' ')[1:-1]) for tag in 
                html.findAll(class_='tag-type-metadata')
                )
        
        tags = ' '.join((metadata & METADATA) - set(tags.split()))
        if tags:
            CONNECTION.execute(UPDATE, (f'{tags} ', path), commit=1)
            CONNECTION.execute(SELECT.format('path, tags, href, site',))

def Find_symmetric_videos():

    from pathlib import Path
    from cv2 import VideoCapture
    from Webscraping import CONNECTION 

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

    SELECT = 'SELECT path FROM imageData WHERE MATCH(tags, artist) AGAINST("animated -audio" IN BOOLEAN MODE) AND type=0'
    
    for path, in CONNECTION.execute(SELECT, fetch=1):

        frames = []
        vidcap = VideoCapture(path)
        success, frame = vidcap.read()

        while success:
            
            frames.append(frame)
            success, frame = vidcap.read()
            
        if symmetric(frames): print(path)

def parsing_test():
    
    import pyparsing as pp

    # arithOp = pp.oneOf("AND OR NOT")
    # number = pp.pyparsing_common.number()
    # word = pp.Word(pp.alphas, pp.alphanums + "_-*(1234567890,)")
    # term = word | number | pp.quotedString
    # expression = 
    # condition = pp.Group(term + arithOp + term)

    lparen = pp.Suppress("(")
    rparen = pp.Suppress(")")

    and_ = pp.Literal("AND")
    or_ = pp.Literal("OR")
    not_ = pp.Literal("NOT")

    operator = pp.oneOf(("=", "!=", ">", ">=", "<", "<="))

    alphaword = pp.Word(pp.alphanums + "_")
    string = pp.QuotedString(quoteChar="'")

    number = (
        pp.Word(pp.nums) + pp.Optional("." + pp.OneOrMore(pp.Word(pp.nums)))
        )

    identifier = alphaword

    expr = pp.Forward()

    condition = pp.Group(
        identifier + (operator + (string | number))
        )
    condition = condition | (lparen + expr + rparen)

    and_condition = (condition + pp.ZeroOrMore(and_ + condition))

    expr << (and_condition + pp.ZeroOrMore(or_ + and_condition))

    expr = pp.operatorPrecedence(condition,
        [('NOT', 1, pp.opAssoc.RIGHT,),
        ('AND', 2, pp.opAssoc.LEFT,),
        ('OR', 2, pp.opAssoc.LEFT,)]
        )

    query = 'a AND b OR x AND y' 
    print(expr.parseString(query))

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
    
    folder = Path(input('Enter path: '))
    for num, path in enumerate(folder.iterdir()):
        status, image = stitcher.stitch(get_frames(path))
        cv2.imwrite(str(test / f'{num:03}'), image)

def Get_Starred():

    from Webscraping import WEBDRIVER, CONNECT
    import bs4, time

    CONNECTION = CONNECT()
    DRIVER = WEBDRIVER(0)
    UPDATE = 'UPDATE imageData SET stars=4 WHERE path=%s AND stars=0'
    address = '//body/div[1]/div[6]/div/div/div[1]/div/div/main/div/section[3]/div[2]/div/div[1]/div[1]/div[1]/button'

    DRIVER.get('https://www.dropbox.com/h')
    time.sleep(5)
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')

    while starred:=html.findAll(class_='starred-item__content'):

        paths = [(target.text,) for target in starred]
        CONNECTION.execute(UPDATE, paths, many=1, commit=1)
        [
            DRIVER.find(address, click=True) for _ in range(5)
            ]

Controller()
# Remove_redundancies()
# Normalize_database() 
# Clean_dataset()
# Find_symmetric_videos()
# make_stitch()
# Get_Starred()