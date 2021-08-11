import argparse, threading

parser = argparse.ArgumentParser(
    prog='test', 
    description='Run test functions'
    )
parser.add_argument(
    '-a', '--arg', type=int,
    help='argument', default=None
    )
parser.add_argument(
    '-i', '--init', type=int,
    help='initialize', default=1
    )
args = parser.parse_args()

if args.arg == 0: # webscraping

    from Webscraping import get_starred
    
    from Webscraping import Photos, Illus, comics
    
    threads = [
        threading.Thread(target=Photos.start, args=(args.initialize,)),
        threading.Thread(target=Illus.start, args=(args.initialize,)),
        # threading.Thread(target=comics.start)
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    get_starred()

    print('\nComplete')


elif args.arg == 1: # insert_records

    from Webscraping import insert_records, get_starred
    
    from Webscraping.Photos import imagefap

    threads = [
        threading.Thread(target=insert_records.start),
        threading.Thread(target=imagefap.start),
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    get_starred()

    print('\nComplete')

else:

    # from Webscraping.Favorites import deviantart
    from Webscraping.Photos import posespace, blogspot

    # deviantart.start(1, 0)
    posespace.start()
    # blogspot.start(1, 0)