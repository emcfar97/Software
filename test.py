def Controller():
    
    from pathlib import Path
    from Webscraping import start, insert_records#, Favorites, Photos, Illus
    # from Webscraping.twitter import main

    # Photos.toplesspulp.start()
    # Favorites.favorites.start()
    # start()
    # insert_records.start()

def Artist_statistics():

    from Webscraping import CONNECT

    CONNECTION = CONNECT()

    SELECT = 'SELECT DISTINCT artist FROM imagedata GROUP BY artist HAVING COUNT(artist) > 100 ORDER BY artist'
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
    from os.path import exists

    CONNECTION = CONNECT()        
    SELECT = 'SELECT path, artist, tags FROM imageData WHERE path Like "C%"'
    UPDATE = 'UPDATE imageData SET artist=%s, tags=%s WHERE path=%s'
    DELETE = 'DELETE FROM imageData WHERE path=%s'

    for (path, artist, tags,) in CONNECTION.execute(SELECT, fetch=1):

        if not exists(path): 
            CONNECTION.execute(DELETE, (path,))
            continue
        artist = f' {" ".join(set(artist.split()))} '
        tags = f' {" ".join(set(tags.split()))} '
        CONNECTION.execute(UPDATE, (artist, tags, path))

    CONNECTION.commit()

def Normalize_database():
    
    from pathlib import Path
    from Webscraping import CONNECT

    CONNECTION = CONNECT()
    DELETE = 'DELETE FROM imageData WHERE path=%s'

    database = set(
        Path(path) for path, in CONNECTION.execute(
            'SELECT path FROM imageData WHERE path LIKE "C:%"', fetch=1
            )
        )
    windows = set(
        Path(r'C:\Users\Emc11\Dropbox\ん').glob('エラティカ */*')
        )
    y = windows - database
    x = database - windows
    
    for num1, file in enumerate(y, 1):
        file.replace(Path(r'C:\Users\Emc11\Downloads\Images') / file.name)
    else: 
        try: print(f'{num1} files moved')
        except: print('0 files moved')
    
    for num2, file in enumerate(x, 1):
        CONNECTION.execute(DELETE, (str(file),), commit=1)
    else: 
        try: print(f'{num2} records deleted')
        except: print('0 records deleted')

def Find_symmetric_videos():

    from pathlib import Path
    from cv2 import VideoCapture
    from Webscraping import CONNECT
    
    CONNECTION = CONNECT()

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
    
    # path=6cc7368796da38a173b09a67c45dfd0

def Get_images_dataset():
    
    import tempfile, hashlib   
    from math import log
    from PIL import Image 
    from pathlib import Path
    from Webscraping.utils import Progress
    from cv2 import VideoCapture, imencode

    HASHER = hashlib.md5()
    DEST = Path(r'E:\Users\Emc11\Training\New folder')

    def save_images(path, dest, crop_=False, gray_=False):
        
        for file in path:
            print(progress)
            
            try:
                
                if file.suffix in (('.jpeg', '.jpg', '.png')): images = [file]
                
                elif file.suffix in (('.gif', '.mp4', '.webm', '.mp4')):
                    
                    images = []
                    temp_dir = tempfile.TemporaryDirectory()
                    vidcap = VideoCapture(str(file))
                    success, frame = vidcap.read()
            
                    while success:
                        
                        data = imencode('.jpg', frame)[-1]
                        HASHER.update(data)
                        temp = Path(temp_dir.name) / f'{HASHER.hexdigest()}.jpg'
                        temp.write_bytes(data)
                        images.append(temp)
                        success, frame = vidcap.read()

                    else: 
                        step = round(90 * log((len(images) * .0007) + 1) + 1)
                        images = images[::step]
                
                for file in images:
                    
                    image = Image.open(file)
                    if crop_: image = crop(image)
                    if gray_: file, image = gray(image, file)
                    image.thumbnail([512, 512])
                    image.save(dest / file.name)
                
            except: continue
        
        print(progress)

    def crop(image):
        
        standard = image.height if image.height < image.width else image.width
        standard //= 2
        center = image.size[0] // 2, image.size[1] // 2
        
        left  = center[0] - standard
        upper = center[1] - standard
        right = center[0] + standard
        lower = center[1] + standard

        return image.crop((left, upper, right, lower))

    def gray(image, file):
        
        image = image.convert('L')
        HASHER.update(image.tobytes())
        name = file.with_name(f'{HASHER.hexdigest()}.jpg')
        
        return name, image
    
    images = [
    ]
    # images = list(Path(r'E:\Users\Emc11\Training\Temp').iterdir())
    progress = Progress(len(images), '')
    save_images(images, DEST)

def Get_images():
    
    from Webscraping import get_images
    
    # get_images.unsplash(1000, r'')
    # get_images.shutterstock(2000, r'Medium\Illustration', 'landscape', 'illustration')
    # get_images.boards = ['your-pinterest-likes'], ['']
    # get_images.pinterest(125, r'Medium\Photograph', boards, 0)
    # get_images.pinterest(220, r'Medium\Illustration', boards, 1)
    # get_images.fineartamerica(500, r'Medium\Illustration', 'paintings')
    # get_images.localfiles(1000, r'Medium', r'Medium\Illustration')
    get_images.turbosquid(3000, r'Medium\3-Dimensional', 'low-poly')

def Clean_dataset():
    
    from pathlib import Path
    
    j = Path(r'E:\Users\Emc11\Training')
    k = j / r'New folder\Illustrations'
    l = j / r'New folder\Photographs'

    move = [
    ]
    delete = [
    ]
    
    while move:
        path = move.pop()
        photo = l / path
        illus = k / path
        if illus.exists(): illus.replace(j / path)
        
        # if photo.exists() == illus.exists(): 
        #     photo.replace(photo.parent)
        #     illus.replace(illus.parent)

        # else:
        #     if not photo.exists(): illus.replace(photo)
            
    while delete:
        
        path = delete.pop()
        photo = l / path
        illus = k / path

        if photo.exists() == illus.exists(): 
            photo.replace(k.parent / path)
            illus.replace(k.parent / path)
    
        else:
            if illus.exists(): illus.unlink()
            elif photo.exists(): photo.unlink()
        
def Check_Predictions():
    
    import cv2, random
    import numpy as np
    from PIL import Image
    from MachineLearning import Model, Path

    model = Model('Medium-07.hdf5')
    path = Path(r'E:\Users\Emc11\Dropbox\ん')
    glob = path.glob('エラティカ *\*jpg')

    for image in random.choices(list(glob), k=25):

        prediction = model.predict(image)

        image = np.array(Image.open(image))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        cv2.imshow(prediction, image)
        cv2.waitKey(0)

def Pyqt5_mysql():
    
    from configparser import ConfigParser
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtSql import QSqlDatabase
    
    class Database():

        def __init__(self):
        
            credentials = ConfigParser(delimiters='=') 
            credentials.read('credentials.ini')

            self.db=QSqlDatabase.addDatabase("QMYSQL")
            self.db.setHostName(credentials.get('mysql', 'hostname'))
            self.db.setUserName(credentials.get('mysql', 'username'))
            self.db.setPassword(credentials.get('mysql', 'password'))
            self.db.setDatabaseName(credentials.get('mysql', 'database'))
            ok = self.db.open()

    Qapp = QApplication([])

    mydb = Database()

    Qapp.exec_()

    # pip install --ignore-installed pyqt5==5.12.6
    
# Controller()
# Find_symmetric_videos()
# Normalize_database() 
# Get_images_dataset()
# Clean_dataset()
# Check_Predictions()
# Get_images()
Pyqt5_mysql()