from Webscraping.Favorites import start

import argparse

parser = argparse.ArgumentParser(
    prog='Favorites', 
    )
parser.add_argument(
    '-i', '--initial', type=bool,
    help='Initial argument (default True)',
    default=True
    )
args = parser.parse_args()

start(args.initial)