import argparse, re, send2trash
from . import USER, CONNECT, INSERT, EXT, extract_files
from .utils import IncrementalBar, get_hash, get_name, get_tags, generate_tags, save_image

PATH = USER / r'Downloads\Images'

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
            dest = get_name(file, 1)
            
            if dest.exists():
                send2trash.send2trash(str(file))
                continue
            
            if not (hash_ := get_hash(file)): continue
            
            tags, rating = generate_tags(
                general=get_tags(file, True), 
                custom=True, rating=True
                )

            if dest.suffix in ('.jpg', '.png'):

                dest = dest.with_suffix('.webp')
                dest = save_image(dest, file)
            
            elif dest.suffix in ('.gif', '.mp4'):

                dest = dest.with_suffix('.webm')
                dest = save_image(dest, file)

            tags = tags.replace('aphorisms', '')
            
            if MYSQL.execute(INSERT[3], (
                dest.name, '', ' '.join((tags, add)), 
                rating, 1, hash_, None, None, None
                )):
                if file.replace(dest): MYSQL.commit()
                else: MYSQL.rollback()
                
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