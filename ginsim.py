# -*- coding: utf-8 -*-
import typing
from   typing import *

min_py = (3, 8)

###
# Standard imports, starting with os and sys
###
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

###
# Other standard distro imports
###
import argparse
from   collections import Counter
import contextlib
import random
import time

###
# Credits
###
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2022'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = ['gflanagin@richmond.edu', 'me@georgeflanagin.com']
__status__ = 'in progress'
__license__ = 'MIT'

class Card:
    __slots__ = ('rank', 'suit')

    def __init__(self, rank:int, suit:str) -> None:
        self.rank = rank
        self.suit = suit

    def __str__(self) -> str:
        return f"({self.rank}, {self.suit})"

deck = tuple(Card(rank, suit) for rank in tuple(range(1,14)) for suit in 'SHDC')

def triplet_fraction(deals:tuple) -> int:

    triplets = 0
    for deal in deals:
        ranks = Counter(card.rank for card in deal)
        if any(_ > 2 for _ in ranks.values()): triplets += 1

    return (triplets, len(deals)-triplets)



def ginsim_main(myargs:argparse.Namespace) -> int:
    global deck

    start = time.time()
    deals = tuple(random.sample(deck, 10) for i in range(myargs.size))
    print(f"{myargs.size} hands in {time.time()-start} seconds.")

    print(triplet_fraction(deals))

    return os.EX_OK


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="ginsim", 
        description="What ginsim does, ginsim does best.")

    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")

    parser.add_argument('-z', '--size', type=int, default=100000,
        help="Number of hands to deal.")

    myargs = parser.parse_args()

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")


