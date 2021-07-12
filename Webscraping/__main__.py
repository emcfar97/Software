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

    import Webscraping
    
    Webscraping.start()
    Update_Autocomplete()
    Get_Starred()

elif args.arg == 1: # insert_records

    from Webscraping import insert_records
    from Webscraping.Photos import imagefap

    insert_records.start()
    imagefap.start()
    Remove_Redundancies()

else:

    from Webscraping.Favorites import deviantart
    from Webscraping.Photos import posespace, blogspot

    deviantart.start(1, 0)
    # posespace.start(0)
    # blogspot.start(1, 0)