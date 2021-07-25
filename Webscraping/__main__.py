import argparse

parser = argparse.ArgumentParser(
    prog='test', 
    description='Run test functions'
    )
parser.add_argument(
    '-a', '--arg', type=int,
    help='argument'
    )
args = parser.parse_args()

if args.arg == 0: # webscraping

    from Webscraping import start, get_starred
    
    start()
    get_starred()

    print('\nComplete')


elif args.arg == 1: # insert_records

    import threading
    from Webscraping import insert_records
    from Webscraping.Photos import imagefap

    threads = [
        threading.Thread(target=insert_records.start),
        threading.Thread(target=imagefap.start),
        ]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

else:

    from Webscraping.Favorites import deviantart
    from Webscraping.Photos import posespace, blogspot

    deviantart.start(1, 0)
    # posespace.start(0)
    # blogspot.start(1, 0)