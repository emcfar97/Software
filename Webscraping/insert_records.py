import argparse, re, send2trash
from . import USER, CONNECT, INSERT
from .utils import IncrementalBar, EXT, get_hash, get_name, get_tags, generate_tags, save_image

PATH = USER / r'Downloads\Images'

def main(add='', path=PATH):
    
    if isinstance(path, str): path = USER / path
    
    MYSQL = CONNECT()
        
    files = [
        file for file in path.iterdir() 
        if re.search(EXT, file.suffix, re.IGNORECASE)
        ]
    progress = IncrementalBar('Files', max=len(files))

    for file in files:
        
        progress.next()
                
        if (dest := get_name(file, 1)).exists():
            
            send2trash.send2trash(str(file))
            continue
        
        if not (hash_ := get_hash(file)): continue
        
        try:
            tags, rating = generate_tags(
            general=get_tags(file, True), 
            custom=True, rating=True
            )
        except (SyntaxError, AttributeError): continue
        
        tags = tags.replace('aphorisms', '')
        
        if MYSQL.execute(INSERT[3], (
            dest.name, '', ' '.join((tags, add)), 
            rating, 1, hash_, '', '', None
            )):
            if save_image(dest, file): MYSQL.commit()
            else: MYSQL.rollback()
    
    print('\nDone')

if __name__ == '__main__':

    from Webscraping import get_starred
    
    parser = argparse.ArgumentParser(
        prog='insert records', 
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
    
    main(args.add, args.path)
    get_starred()