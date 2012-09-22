"""
=================================
  Abusing PyEDA to solve Sudoku
=================================

According to Peter Norvig in his `classic essay <http://norvig.com/sudoku.html>`_
on solving every Sudoku puzzle using Python, security expert
`Ben Laurie <http://en.wikipedia.org/wiki/Ben_Laurie>`_ once stated that
"Sudoku is a denial of service attack on human intellect." I can personally
attest to that.

In this example, I will explain how to misuse/abuse PyEDA's Boolean expressions
and satisfiability engine to create a general-purpose Sudoku solver.

First, let's get a few ground rules straight:

1. There are lots of Sudoku solvers on the Internet; I make no claims of novelty.
2. PyEDA is unlikely to win any speed competitions.
3. Let's face it--this is a pretty awesome waste of time :).
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from pyeda import *

#>>> grid = "002980010 016327000 390006040 800030095 000070000 640050002 080200054 000761920 060045700"
#>>> soln = solve(grid)
#>>> display(soln)
#752|984|316
#416|327|589
#398|516|247
#---+---+---
#871|632|495
#925|478|163
#643|159|872
#---+---+---
#187|293|654
#534|761|928
#269|845|731

#>>> grid = "8........ ..36..... .7..9.2.. .5...7... ....457.. ...1...3. ..1....68 ..85...1. .9....4.."
#>>> soln = solve(grid)
#>>> display(soln)
#812|753|649
#943|682|175
#675|491|283
#---+---+---
#154|237|896
#369|845|721
#287|169|534
#---+---+---
#521|974|368
#438|526|917
#796|318|452
#"""

DIGITS = "123456789"

X = [ [ [ var("x", r, c, v) for v in range(3 * 3) ]
                            for c in range(3 * 3) ]
                            for r in range(3 * 3) ]

# Value constraints
V = And(*[
        And(*[
            OneHot(*[ X[r][c][v]
                for v in range(3 * 3) ])
                for c in range(3 * 3) ])
                for r in range(3 * 3) ])

# Row constraints
R = And(*[
        And(*[
            OneHot(*[ X[r][c][v]
                for c in range(3 * 3) ])
                for v in range(3 * 3) ])
                for r in range(3 * 3) ])

# Column constraints
C = And(*[
        And(*[
            OneHot(*[ X[r][c][v]
                for r in range(3 * 3) ])
                for v in range(3 * 3) ])
                for c in range(3 * 3) ])

# Box constraints
B = And(*[
        And(*[
            OneHot(*[ X[3*br+r][3*bc+c][v]
                for r in range(3) for c in range(3) ])
                for v in range(3 * 3) ])
                for br in range(3) for bc in range(3) ])

S = CNF_AND(V, R, C, B)

def parse_grid(grid):
    chars = [c for c in grid if c in DIGITS or c in "0."]
    assert len(chars) == (3 * 3) ** 2
    I = And(*[ X[i//(3*3)][i%(3*3)][int(c)-1]
               for i, c in enumerate(chars) if c in DIGITS ])
    return expr2cnf(I)

def solve(grid):
    I = parse_grid(grid)
    return (I * S).satisfy_one()

def _get_val(point, r, c):
    for v in range(3 * 3):
        if point[X[r][c][v]]:
            return DIGITS[v]
    return "X"

def soln2str(point):
    """Return the string representation of a Sudoku solution."""
    chars = list()
    for r in range(3 * 3):
        for c in range(3 * 3):
            if c != 0 and c % 3 == 0:
                chars.append("|")
            chars.append(_get_val(point, r, c))
        if r != (3 * 3 - 1):
            chars.append("\n")
            if r % 3 == (3 - 1):
                chars.append("+".join(["-" * 3] * 3) + "\n")
    return "".join(chars)

def display(point):
    print(soln2str(point))
