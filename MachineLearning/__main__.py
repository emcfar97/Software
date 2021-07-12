import argparse

parser = argparse.ArgumentParser(
    prog='Machine Learning', 
    description='Command line interface for common ML operations and projects'
    )
parser.add_argument(
    '-n', '--num', type=int,
    help='Number of streams', default=2
    )
args = parser.parse_args()