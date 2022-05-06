from Webscraping import get_starred
from Webscraping.Illus import main

import argparse

parser = argparse.ArgumentParser(
    prog='Illus', 
    )
parser.add_argument(
    '-i', '--init', type=int,
    help='Initial argument (default 1)',
    default=1
    )
parser.add_argument(
    '-f', '--fav', type=int,
    help='Favorites argument (default 1)',
    default=1
    )
parser.add_argument(
    '-d', '--depth', type=int,
    help='Favorites argument (default 1)',
    default=1000
    )
args = parser.parse_args()

main(args.init, args.fav, args.depth)

get_starred()