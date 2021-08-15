from Webscraping.Photos import start

import argparse

parser = argparse.ArgumentParser(
    prog='Photos', 
    )
parser.add_argument(
    '-i', '--init', type=int,
    help='Initial argument (default 1)',
    default=1
    )
args = parser.parse_args()

start(args.init)