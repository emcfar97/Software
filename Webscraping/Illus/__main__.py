from Webscraping.Illus import start

import argparse

parser = argparse.ArgumentParser(
    prog='Illus', 
    )
parser.add_argument(
    '-i', '--initial', type=int,
    help='Initial argument (default 1)',
    default=1
    )
parser.add_argument(
    '-f', '--fav', type=int,
    help='Favorites argument (default 1)',
    default=1
    )
args = parser.parse_args()

start(args.initial, args.fav)