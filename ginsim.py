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
from   collections import Counter, defaultdict
import contextlib
import fcntl
import logging
import random
import tempfile
import time

###
# from hpclib
###
import urlogger
from   urlogger import URLogger

from   urdecorators import trap

###
# Globals.
###
deals = tuple()
num_cores = len(os.sched_getaffinity(0))
result_file = None

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

###
# DECK and SUITS are capitalized to draw attention
# to the fact that they are constant globals.
###
SUITS = 'CDHS'
DECK = tuple(range(52))
CARDS_PER_SUIT = len(DECK)//len(SUITS)

def a_deal() -> list:
    """
    deal 20 cards, and return them as two disjoint sets of 10.
    """
    _ = random.sample(range(52), 20)
    return _[:10], _[10:]


def bucketize(cards:Iterable, size:int) -> dict:
    """
    Efficiently group cards of the same rank.
    """
    buckets = defaultdict(list)
    for card in cards:
        idx = card // size
        buckets[idx].append(card)

    return buckets


def card_to_int(card:tuple) -> int:
    """
    This is the inverse function of int_to_card. Must be
    for testing, because I cannot find a use for it.
    """
    return card[0]*len(SUITS) + SUITS.find(card[1])


def int_to_card(i:int) -> tuple:
    """
    Mainly for debugging, this converts an ordinal into a card name
    that can be printed. It is written this way so that we can use
    the same code with decks other than the 52 standard cards.
    """
    rank, suit = divmod(i, len(SUITS))
    return rank, SUITS[suit]


@trap
def run_sim(n:int) -> None:
    """
    Deal n times.
    """
    global myargs, DECK, logger

    logger.debug(f"Dealing {n} hands.")

    deals = tuple(hand for hand in a_deal() for i in range(n//2)) 

    logger.debug(f"Dealt {n} hands.")

    triplet_fraction(deals)
    sequence_fraction(deals)


@trap
def sequence_fraction(deals:tuple) -> None:
    global result_file, DECK, logger

    start=time.time()
    sequences = 0
    for cards in deals:

        # Whatever the two highest cards are, they cannot be
        # the base of a sequence of three cards in ascending value.
        for i in sorted(cards[:-2]):
            if i+4 in cards and i+8 in cards:
                sequences += 1
                continue
        
    logger.debug(f"Found {sequences} hands with a 3-card sequence.")
    # write_results(f"sequence,{sequences},{len(deals)-sequences}\n")


def splitter(group:Iterable, num_chunks:int) -> Iterable:
    """
    Generator to divide a collection into num_chunks pieces.
    It works with str, tuple, list, and dict, and the return
    value is of the same type as the first argument.

    group      -- str, tuple, list, or dict.
    num_chunks -- how many pieces you want to have.

    Use:
        for chunk in splitter(group, num_chunks):
            ... do something with chunk ...

    """
    quotient, remainder = divmod(len(group), num_chunks)
    is_dict = isinstance(group, dict)
    if is_dict: 
        group = tuple(kvpair for kvpair in group.items())

    for i in range(num_chunks):
        lower = i*quotient + min(i, remainder)
        upper = (i+1)*quotient + min(i+1, remainder)

        if is_dict:
            yield {k:v for (k,v) in group[lower:upper]}
        else:
            yield group[lower:upper]


@trap
def triplet_fraction(deals:tuple) -> None:

    global result_file, DECK, logger

    start=time.time()
    triplets = 0
    for deal in deals:
        if any(len(rank) > 2 for rank in bucketize(deal, 4)): triplets += 1

    logger.debug(f"Found {triplets} triplets in {time.time()-start} seconds.")
    
    # write_results(f"triplet,{triplets},{len(deals)-triplets}\n")

@trap
def write_results(s:str) -> None:
    """
    Write one line of a CSV file to be used for later analysis,
    perhaps in pandas.
    """

    global result_file

    try:
        fcntl.lockf(result_file.fileno(), fcntl.LOCK_EX)
        result_file.write(s)
    finally:
        fcntl.lockf(result_file.fileno(), fcntl.LOCK_UN)


@trap
def ginsim_main(myargs:argparse.Namespace) -> int:

    global DECK, deals, num_cores, logger, result_file

    
    result_file = tempfile.NamedTemporaryFile('w+')

    ###
    # Work out the multiprocessing parameters.
    ###
    num_processes = min(myargs.num_procs, num_cores*myargs.saturation)
    logger.debug(f"Beginning with {num_processes=}, {num_cores=}")
    pids = set()
    
    # Cut the work into suitable size pieces, and let the kids 
    # go to work.
    for j in range(num_processes):
        
        pid = os.fork()
        if pid: 
            pids.add(pid)
            continue

        try:
            run_sim(myargs.size//num_processes)
        finally:
            os._exit(os.EX_OK)
            
    while pids:
        pid, status, resources = os.wait3(0)
        pids.remove(pid)
        sys.stderr.write(f"Child {pid} finished.\n")

    result_file.seek(0)
    print(result_file.readlines())

    return os.EX_OK


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="ginsim", 
        description="What ginsim does, ginsim does best.")


    parser.add_argument('-n', '--num-procs', type=int, default=1,
        choices=range(1, num_cores+1),
        help="Number of processes for the simulation.")

    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")

    parser.add_argument('-s', '--saturation', type=float, default=1.0,
        help="Fraction of the available cores to use. Default is 1.0")

    parser.add_argument('-z', '--size', type=int, default=100000,
        help="Number of hands to deal.")

    myargs = parser.parse_args()

    try:
        os.unlink('ginsim.log')
    except:
        pass

    logger=URLogger(logfile='ginsim.log', level=logging.DEBUG)

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")


