"""
Sudoku Puzzle

>>> grid = "002980010 016327000 390006040 800030095 000070000 640050002 080200054 000761920 060045700"
>>> soln = solve(grid)
>>> print(soln2str(soln))
752|984|316
416|327|589
398|516|247
---+---+---
871|632|495
925|478|163
643|159|872
---+---+---
187|293|654
534|761|928
269|845|731

>>> grid = "8........ ..36..... .7..9.2.. .5...7... ....457.. ...1...3. ..1....68 ..85...1. .9....4.."
>>> soln = solve(grid)
>>> print(soln2str(soln))
812|753|649
943|682|175
675|491|283
---+---+---
154|237|896
369|845|721
287|169|534
---+---+---
521|974|368
438|526|917
796|318|452
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from pyeda.expr import var, And, OneHot
from pyeda.cnf import expr2cnf, CNF_AND

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
