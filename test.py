def Controller(arg=None):
    
    if arg == 0:

        import Webscraping

        Webscraping.start()
        Get_Starred()

    elif arg == 1:

        from Webscraping import insert_records

        insert_records.start()
        Remove_redundancies()
        Update_Autocomplete()
    
    else:

        from Webscraping.Photos import posespace, blogspot

        # posespace.start(0)
        # blogspot.start(1, 0)

def Remove_redundancies():

    from Webscraping import CONNECT

    MYSQL = CONNECT()        
    SELECT = 'SELECT path, artist, tags FROM imageData WHERE NOT ISNULL(path)'
    UPDATE = 'UPDATE imageData SET artist=%s, tags=%s WHERE path=%s'

    for (path, artist, tags,) in MYSQL.execute(SELECT, fetch=1):

        artist = f' {" ".join(set(artist.split()))} '
        tags = f' {" ".join(set(tags.split()))} '
        MYSQL.execute(UPDATE, (artist, tags, path))

    MYSQL.commit()

def Update_Autocomplete():

    from pathlib import Path
    from Webscraping import CONNECT

    MYSQL = CONNECT()
    MYSQL.execute('SET GLOBAL group_concat_max_len=10000000')
    artist, tags = MYSQL.execute(
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

def Get_Starred():

    from Webscraping import WEBDRIVER, CONNECT
    import bs4

    MYSQL = CONNECT()
    DRIVER = WEBDRIVER()
    UPDATE = 'UPDATE imageData SET stars=4 WHERE path=%s AND stars=0'
    
    show = '//body/div[1]/div[6]/div/div/div[1]/div/div/main/div/section[3]/div/div[2]/button'
    address = '//body/div[1]/div[6]/div/div/div[1]/div/div/main/div/section[3]/div[2]/div/div[1]/div[1]/div[1]/button'

    DRIVER.get('https://www.dropbox.com/h', wait=4)
    if (element:=DRIVER.find(show, fetch=1)).text == 'Show':
        element.click()
    html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')

    while starred:=html.findAll(class_='starred-item__content'):

        paths = [(target.text,) for target in starred]
        MYSQL.execute(UPDATE, paths, many=1, commit=1)
        [DRIVER.find(address, click=True) for _ in range(5)]
        html = bs4.BeautifulSoup(DRIVER.page_source(), 'lxml')

    DRIVER.close()

def Normalize_database():

    from pathlib import Path
    from Webscraping import CONNECT, USER
    
    MYSQL = CONNECT()
    DROPBOX = USER / r'Dropbox\ん'
    CASE = r'''
        case type
        when 1 then CONCAT('{0}\エラティカ ニ\', path)
        when 2 then CONCAT('{0}\エラティカ 三\', path)
        when 3 then CONCAT('{0}\エラティカ 四\', path)
        end
        '''.format(DROPBOX).replace('\\', '\\\\')
    SELECT = f'SELECT {CASE} FROM imageData WHERE NOT ISNULL(path)'
    DELETE = 'DELETE FROM imageData WHERE path=%s'

    database = set(
        Path(path) for path, in MYSQL.execute(SELECT, fetch=1)
        )
    windows = set(DROPBOX.glob('エラティカ */*'))
    x, y = database - windows, windows - database
    
    for num, file in enumerate(y, 1):
        file.replace(DROPBOX / r'Downloads\Test' / file.name)
    else:
        try: print(f'{num} files moved')
        except: print('0 files moved')
    
    for num, file in enumerate(x, 1):
        MYSQL.execute(DELETE, (file.name,), commit=1)
    else:
        try: print(f'{num} records deleted')
        except: print('0 records deleted')

def Check_Predictions(sql=False, num=25):
    
    from MachineLearning import Model

    model = Model('deepdanbooru.hdf5')

    if sql:
        
        from Webscraping import USER, CONNECT

        path = USER / r'Dropbox\ん'
        
        TYPE = {
            'Photograph': 'エラティカ ニ',
            'Illustration': 'エラティカ 三',
            'Comic': 'エラティカ 四',
            }
        MYSQL = CONNECT()
        SELECT = f'''
            SELECT path, tags, type 
            FROM imageData 
            WHERE SUBSTR(path, 32, 5) IN ('.jpg', '.png')
            ORDER BY RAND() LIMIT {num}
            '''

        for image, tags, type_ in MYSQL.execute(SELECT, fetch=1):

            tags = sorted(tags.split())
            image = path / TYPE[type_] / image
            prediction = model.predict(image)
            similar = set(tags) & set(prediction)

    else:

        import cv2
        import numpy as np
        from PIL import Image
        from random import choices

        glob = list(path.glob('エラティカ *\*jpg'))

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
    SELECT = 'SELECT path FROM imageData WHERE MATCH(tags, artist) AGAINST("animated -audio" IN BOOLEAN MODE) AND type=0'

    for path, in MYSQL.execute(SELECT, fetch=1):

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
    
    path = Path(input('Enter path: '))
    # for num, path in enumerate(folder.iterdir()):
    status, image = stitcher.stitch(get_frames(path))
    cv2.imwrite(str(test / f'{num:03}'), image)

Controller()
# Remove_redundancies()
# Normalize_database()
# Check_Predictions(1)
# Find_symmetric_videos()
# make_stitch()
# Copy_Files()
