import argparse, threading

from Webscraping import get_starred
    
parser = argparse.ArgumentParser(
    prog='Webscraping', 
    description='Command line interface for common webscraping operations and projects'
    )
parser.add_argument(
    '-a', '--arg', type=int,
    help='argument', default=None
    )
parser.add_argument(
    '-i', '--init', type=bool,
    help='initialize', default=True
    )
parser.add_argument(
    '-f', '--fav', type=int,
    help='Favorites argument (default 1)',
    default=1
    )

args = parser.parse_args()

if args.arg == 1: # photos

    from Webscraping import Photos
    
    Photos.main(args.init)
    get_starred()

    print('\nComplete')

elif args.arg == 2: # illus

    from Webscraping import Illus

    Illus.main(args.init, args.fav)
    get_starred()

    print('\nComplete')
    
elif args.arg == 3: # comics

    from Webscraping import comics

    comics.main(args.init)
    get_starred()

    print('\nComplete')
    
else: # webscraping

    from Webscraping import Photos, Illus, comics
    
    threads = [
        threading.Thread(target=Photos.main, args=(args.init,)),
        threading.Thread(target=Illus.main, args=(args.init, args.fav)),
        threading.Thread(target=comics.main, args=(args.init,))
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    get_starred()

    print('\nComplete')