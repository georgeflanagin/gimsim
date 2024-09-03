# ginsim

This is a simple simulator for dealing Gin Rummy hands to study the characteristics 
of distribution. 

## What is Gin Rummy?
Gin Rummy is a card game for two players in which the players exchange and draw cards
to attempt to make all of their own cards fit into groups of 3 or 4 cards of the same
rank, or runs to 3 to 10 cards of the same suit. 

## How do you run it?

```bash
usage: ginsim [-h] [-i] [-n {1,24}] [-o OUTPUT] [-s SATURATION] [-z SIZE]

What ginsim does, ginsim does best.

options:
  -h, --help            show this help message and exit
  -i, --independent     Assume (falsely) that the two players' hands are
                        indepentent of each other.
  -n {1,24}, --num-evals {1,24}
                        Number of times to run the simulation.
  -o OUTPUT, --output OUTPUT
                        Output file name
  -s SATURATION, --saturation SATURATION
                        Fraction of the available cores to use. Default is 1.0
  -z SIZE, --size SIZE  Number of hands to deal.
```

## How does it work?
The code is not too complicated, but everyone says that about their own code, right?

The program constructs a `deck` of cards, where each `card` is an ordered pair of .. (rank, suit).
The properties of the standard deck of cards are hard coded into the program, so it is the
usual cards you find in your 52 friends at the poker, bridge, gin, or blackjack game.

The Python builtin, `random.sample` is used to select hands of ten cards from the deck.
If `--independent` is chosen for the option, the code loops through and pulls ten cards
at a time from the deck and calls it a hand. If you run the simulation more realistically,
`random.sample` pulls twenty cards from the deck, and then divides them into two piles of
ten. 

In both cases, a bigger data structure named `deals` is created as a `tuple` with
each element representing one dealt hand of ten cards.

If you choose to run the simulation multiple times and sum the results, a separate
process is forked for each run, and the data are summed at the end.

## What does it evaluate?
Gin players often wonder what the probability is that they get a hand with no triplets,
or no runs, or all four cards of one rank, and various combinations of these factors of 
chance that affect one's probability of winning before any information is exchanged during
play. Most of the combinatorics are hard to directly calculate because they involve
studying the large numbers of permutations of hands. This program uses a Monte Carlo 
simulation.
