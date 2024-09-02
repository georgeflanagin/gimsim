# ginsim

This is a simple simulator for dealing Gin Rummy hands to study the characteristics 
of distribution. 

## What is Gin Rummy?
Gin Rummy is a card game for two players in which the players exchange and draw cards
to attempt to make all of their own cards fit into groups of 3 or 4 cards of the same
rank, or runs to 3 to 10 cards of the same suit. 

## How do you run it?

```bash
usage: ginsim [-h] [-i] [-n NUM_EVALS] [-o OUTPUT] [-z SIZE]

What ginsim does, ginsim does best.

options:
  -h, --help            show this help message and exit
  -i, --independent     Assume (falsely) that the two players' hands are
                        indepentent of each other.
  -n NUM_EVALS, --num-evals NUM_EVALS
                        Number of times to run the simulation.
  -o OUTPUT, --output OUTPUT
                        Output file name
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
