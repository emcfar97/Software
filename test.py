def Controller():
    
    import Webscraping
    from Webscraping import Photos, Illus, insert_records

    # Webscraping.start()
    # Webscraping.Favorites.favorites.start()
    # insert_records.start()
    # Photos.flickr.start()
    # Illus.start()

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

def Normalize_dataset():

    from pathlib import Path
    from Webscraping import CONNECTION

    DELETE = 'DELETE FROM imageData WHERE path=%s'

    database = set(
        Path(path) for path, in CONNECTION.execute(
            'SELECT path FROM imageData WHERE path LIKE "C:%"', fetch=1
            )
        )
    windows = set(
        Path(r'C:\Users\Emc11\Dropbox\Videos\ん').glob('エラティカ */*')
        )
    y = windows - database
    x = database - windows
    
    for num1, file in enumerate(y, 1):
        file.replace(Path(r'C:\Users\Emc11\Downloads\Images\Test') / file.name)
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

def Get_images_dataset():
    
    import tempfile, hashlib   
    from math import log
    from PIL import Image 
    from pathlib import Path
    from cv2 import VideoCapture, imencode, cvtColor, COLOR_BGR2RGB

    HASHER = hashlib.md5()

    def save_images(path, dest):
        
        # for file in path.iterdir():
        for file in path:
            
            new = dest / file.with_suffix('.jpg').name
            if len(list(dest.glob('*'))) > 100500: break
            
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
                    image = crop(image)
                    image.thumbnail([512, 512])
                    if image.size == (512, 512):
                        image.save(dest / file.name)
                
            except: continue

    def crop(image):
        
        standard = image.height if image.height < image.width else image.width
        standard //= 2
        center = image.size[0] // 2, image.size[1] // 2
        
        left = center[0] - standard
        upper = center[1] - standard
        right = center[0] + standard
        lower = center[1] + standard

        return image.crop((left, upper, right, lower))

    paths = [
        Path(r'E:\Users\Emc11\Dropbox\Videos\ん\エラティカ ニ'),
        Path(r'E:\Users\Emc11\Dropbox\Videos\ん\エラティカ 三')
        ]
    dests = [
        Path(r'E:\Users\Emc11\Training\Medium\Photographs'),
        Path(r'E:\Users\Emc11\Training\Medium\Illustrations')
        ]

    num = 1
    path = []
    save_images(path, dests[num])
    # save_images(paths[num], dests[num])

def Clean_dataset():
    
    from pathlib import Path
    
    j = Path(r'E:\Users\Emc11\Training')
    k = j / r'Medium\Illustrations'
    l = j / r'Medium\Photographs'

    move = []
    delete = []
    
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

    model = Model('Medium-06.hdf5')
    path = Path(r'C:\Users\Emc11\Dropbox\Videos\ん')
    glob = list(path.glob('エラティカ *\*jpg'))

    for image in random.choices(glob, k=25):

        prediction = model.predict(image)

        image = np.array(Image.open(image))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        cv2.imshow(prediction, image)
        cv2.waitKey(0)

Controller()
# Find_symmetric_videos()
# Normalize_database() 
# Get_images_dataset()
# Clean_dataset()
# Check_Predictions()