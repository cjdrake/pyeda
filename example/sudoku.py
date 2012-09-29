"""
Sudoku Example

>>> with open("example/top95.txt") as fin:
...     grids = {i: grid for i, grid in enumerate(fin)}

>>> display(solve(grids[10]))
614|382|579
953|764|812
827|591|436
---+---+---
742|635|198
168|279|354
395|418|627
---+---+---
286|157|943
579|843|261
431|926|785

>>> display(solve(grids[30]))
385|621|497
179|584|326
426|739|518
---+---+---
762|395|841
534|812|769
891|476|253
---+---+---
917|253|684
243|168|975
658|947|132
"""

from pyeda import *

DIGITS = "123456789"

X = [[[ var("x", r, c, v) for v in range(3 * 3) ]
                          for c in range(3 * 3) ]
                          for r in range(3 * 3) ]

V = And(*[
        And(*[
            OneHot(*[ X[r][c][v]
                for v in range(3 * 3) ])
            for c in range(3 * 3) ])
        for r in range(3 * 3) ])

R = And(*[
        And(*[
            OneHot(*[ X[r][c][v]
                for c in range(3 * 3) ])
            for v in range(3 * 3) ])
        for r in range(3 * 3) ])

C = And(*[
        And(*[
            OneHot(*[ X[r][c][v]
                for r in range(3 * 3) ])
            for v in range(3 * 3) ])
        for c in range(3 * 3) ])

B = And(*[
        And(*[
            OneHot(*[ X[3*br+r][3*bc+c][v]
                for r in range(3) for c in range(3) ])
            for v in range(3 * 3) ])
        for br in range(3) for bc in range(3) ])

S = CNF_And(V, R, C, B)

def parse_grid(grid):
    chars = [c for c in grid if c in DIGITS or c in "0."]
    assert len(chars) == (3 * 3) ** 2
    I = And(*[ X[i // (3 * 3)][i % (3 * 3)][int(c) - 1]
               for i, c in enumerate(chars) if c in DIGITS ])
    return expr2cnf(I)

def get_val(point, r, c):
    for v in range(3 * 3):
        if point[X[r][c][v]]:
            return DIGITS[v]
    return "X"

def display(point):
    chars = list()
    for r in range(3 * 3):
        for c in range(3 * 3):
            if c != 0 and c % 3 == 0:
                chars.append("|")
            chars.append(get_val(point, r, c))
        if r != (3 * 3 - 1):
            chars.append("\n")
            if r % 3 == (3 - 1):
                chars.append("+".join(["-" * 3] * 3) + "\n")
    print("".join(chars))

def solve(grid):
    I = parse_grid(grid)
    cnf = I * S
    return cnf.satisfy_one()
