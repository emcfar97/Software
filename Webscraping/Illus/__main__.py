from Webscraping.Illus import start

import argparse

parser = argparse.ArgumentParser(
    prog='Illus', 
    )
parser.add_argument(
    '-i', '--initial', type=bool,
    help='Initial argument (default True)',
    default=1
    )
parser.add_argument(
    '-f', '--fav', type=bool,
    help='Favorites argument (default True)',
    default=1
    )
args = parser.parse_args()

start(args.initial, args.fav)