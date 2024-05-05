from Webscraping.Favorites import main

import argparse

parser = argparse.ArgumentParser(
    prog='favorites', 
    )
parser.add_argument(
    '-i', '--init', type=int,
    help='Initial argument (default 1)',
    default=1
    )
parser.add_argument(
    '-d', '--depth', type=int,
    help='Depth argument (default 0)',
    default=0
    )

args = parser.parse_args()

main(args.init, args.depth)