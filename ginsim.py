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
import random
import tempfile
import time

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

class Card:
    ###
    # Not a lot of overhead here because the use of __slots__ 
    # creates a class with no dict element.
    ###
    __slots__ = ('rank', 'suit')

    def __init__(self, rank:int, suit:str) -> None:
        self.rank = rank
        self.suit = suit

    def __str__(self) -> str:
        return f"({self.rank}, {self.suit})"

class OuterLoop(Exception): 
    pass


###
# Stray global.
###
deck = tuple(Card(rank, suit) for rank in tuple(range(1,14)) for suit in 'SHDC')

def hasrun() -> None:

    global deals
    runs = 0

    for deal in deals:
        try:
            deal_dict = defaultdict(set)

            # group the cards by suit, and keep the ranks
            # of the cards in a set.
            for card in deal:
                deal_dict[card.suit].add(card.rank)
            
            for k, v in deal_dict.items():
                if len(v) < 3: continue
                for i in v:
                    if (i+1) in v and (i+2) in v:
                        runs += 1
                        raise OuterLoop

        except OuterLoop:
            continue
        
        write_results(f"runs,{runs},{len(deals)-runs}")
        

def pidprint(s:str) -> None:
    global myargs
    myargs.verbose and print(f"{os.getpid()} -> {s}")


def run_sim(n:int) -> None:
    """
    Run a simulation n times.
    """
    global myargs

    pidprint(f"Running {n} simulations.")
    
    for i in range(n):
        start=time.time()
        if myargs.independent:
            deals = tuple(random.sample(deck, 10) for i in range(myargs.size + 1))
        else:
            pairs = tuple(random.sample(deck, 20) for i in range((myargs.size + 1)/2))
            pidprint(f"{len(pairs)=}")
            lefts = tuple(pair[:10] for pair in pairs)
            rights = tuple(pair[10:] for pair in pairs)
            deals = lefts + rights
                
        pidprint(f"Dealt {myargs.size} hands in {time.time()-start} seconds.")

        triplet_fraction()


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


def triplet_fraction() -> None:

    global deals, result_file

    start=time.time()
    triplets = 0
    for deal in deals:
        ranks = Counter(card.rank for card in deal)
        if any(_ > 2 for _ in ranks.values()): triplets += 1

    pidprint(f"Found {triplets} triplets in {time.time()-start} seconds.")
    
    write_results(f"triplet,{triplets},{len(deals)-triplets}\n")


def write_results(s:str) -> None:
    """
    Write one line of a CSV file to be used for later analysis,
    perhaps in pandas.
    """

    global results_file

    try:
        fcntl.lockf(results_file, fcntl.LOCK_EX)
        results_file.write(s)
    finally:
        fcntl.lockf(results_file, fcntl.LOCK_UN)


def ginsim_main(myargs:argparse.Namespace) -> int:

    global deck, deals, num_cores

    
    result_file = tempfile.NamedTemporaryFile('w+')

    ###
    # Work out the multiprocessing parameters.
    ###
    num_processes = min(myargs.num_evals, num_cores*myargs.saturation)
    pidprint(f"{num_processes=} {num_cores=}")
    pids = set()
    
    # Cut the work into suitable size pieces, and let the kids 
    # go to work.
    for chunk in splitter(tuple(range(myargs.num_evals)), num_processes):
        pid = os.fork()
        if pid: 
            pids.add(pid)
            continue

        else:
            try:
                run_sim(len(chunk))
            finally:
                os._exit(os.EX_OK)
            
    while pids:
        pid, status, resources = os.wait3(0)
        pids.remove(pid)
        sys.stderr.write(f"Child {pid} finished.")

    result_file.seek(0)
    print(result_file.readlines())

    return os.EX_OK


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="ginsim", 
        description="What ginsim does, ginsim does best.")


    parser.add_argument('-i', '--independent', action='store_true',
        help="Assume (falsely) that the two players' hands are indepentent of each other.")

    parser.add_argument('-n', '--num-evals', type=int, default=1,
        choices=(1, num_cores),
        help="Number of times to run the simulation.")

    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")

    parser.add_argument('-s', '--saturation', type=float, default=1.0,
        help="Fraction of the available cores to use. Default is 1.0")

    parser.add_argument('-v', '--verbose', action='store_true',
        help="Print a running narrative.")

    parser.add_argument('-z', '--size', type=int, default=100000,
        help="Number of hands to deal.")

    myargs = parser.parse_args()

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")


