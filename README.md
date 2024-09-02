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
  -i, --independent     Assume (falsely) that the two players' hands are indepentent of each other.
  -n NUM_EVALS, --num-evals NUM_EVALS
                        Number of times to run the simulation.
  -o OUTPUT, --output OUTPUT
                        Output file name
  -z SIZE, --size SIZE  Number of hands to deal.
```
