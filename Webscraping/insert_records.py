import argparse, cv2, re, send2trash
from . import USER, CONNECT, INSERT, EXT, extract_files
from .utils import IncrementalBar, get_hash, get_name, get_tags, generate_tags, save_image

PATH = USER / r'Downloads\Images'
MATCH = cv2.imread(r'Webscraping\image.jpg'), cv2.imread(r'Webscraping\video.jpg')

def similarity(path):

    if re.search(EXT[:14], path.suffix, re.IGNORECASE):
        match = MATCH[0]
        image = cv2.imread(str(path))
    else:
        match = MATCH[1]
        image = cv2.VideoCapture(str(path)).read()[-1]

    try:
        if divmod(*image.shape[:2])[0] == divmod(*match.shape[:2])[0]:

            image = cv2.resize(image, match.shape[1::-1])
            k = cv2.subtract(image, match)
            return (k.min() + k.max()) < 20
            
    except: return True
    
def main(extract=True, add='', path=PATH):
    
    if isinstance(path, str): path = USER / path
    if extract: extract_files.main(path / 'Generic', path)
    
    MYSQL = CONNECT()
        
    files = [
        file for file in path.iterdir() 
        if re.search(EXT, file.suffix, re.IGNORECASE)
        ]
    progress = IncrementalBar('Files', max=len(files))

    for file in files:
        
        progress.next()
        try:
            if (dest := get_name(file, 1)).exists() or similarity(file):
                send2trash.send2trash(str(file))
                continue
            
            if not (hash_ := get_hash(file)): continue
            
            tags, rating = generate_tags(
                general=get_tags(file, True), 
                custom=True, rating=True
                )

            if dest.suffix.lower() not in ('.webp', '.webm'):

                save_image(file)

            tags = tags.replace('aphorisms', '')
            
            if MYSQL.execute(INSERT[3], (
                dest.name, '', ' '.join((tags, add)), 
                rating, 1, hash_, None, None, None
                )):
                if file.replace(dest): MYSQL.commit()
                else: MYSQL.rollback()
        
        except SyntaxError:
           
           url = f'https://i.imgur.com/{file.stem}.mp4'
           file.unlink()
           save_image(file, url)
           
           tags, rating = generate_tags(
                general=get_tags(file, True), 
                custom=True, rating=True
                ) 
        
        except Exception as error: print('\n', type(error), error, '\n')
    
    print('\nDone')

if __name__ == '__main__':

    from Webscraping import get_starred
    
    parser = argparse.ArgumentParser(
        prog='insert records', 
        )
    parser.add_argument(
        '-e', '--extract', type=int,
        help='Mode argument (default 1)',
        default=1
        )
    parser.add_argument(
        '-a', '--add', type=str,
        help='Add tag argument (default "")',
        default=''
        )
    parser.add_argument(
        '-p', '--path', type=str,
        help=f'Path argument (default {PATH})',
        default=PATH
        )

    args = parser.parse_args()
    
    main(args.extract, args.add, args.path)
    get_starred()