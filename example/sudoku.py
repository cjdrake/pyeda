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

X = bitvec("x", (1, 10), (1, 10), (1, 10))

V = And(*[
        And(*[
            OneHot(*[ X[r][c][v]
                for v in range(1, 10) ])
            for c in range(1, 10) ])
        for r in range(1, 10) ])

R = And(*[
        And(*[
            OneHot(*[ X[r][c][v]
                for c in range(1, 10) ])
            for v in range(1, 10) ])
        for r in range(1, 10) ])

C = And(*[
        And(*[
            OneHot(*[ X[r][c][v]
                for r in range(1, 10) ])
            for v in range(1, 10) ])
        for c in range(1, 10) ])

B = And(*[
        And(*[
            OneHot(*[ X[3*br+r][3*bc+c][v]
                for r in range(1, 4) for c in range(1, 4) ])
            for v in range(1, 10) ])
        for br in range(3) for bc in range(3) ])

S = CNF_And(V, R, C, B)

def parse_grid(grid):
    chars = [c for c in grid if c in DIGITS or c in "0."]
    assert len(chars) == 9 ** 2
    I = And(*[ X[i // 9 + 1][i % 9 + 1][int(c)]
               for i, c in enumerate(chars) if c in DIGITS ])
    return expr2cnf(I)

def get_val(point, r, c):
    for v in range(1, 10):
        if point[X[r][c][v]]:
            return DIGITS[v-1]
    return "X"

def display(point):
    chars = list()
    for r in range(1, 10):
        for c in range(1, 10):
            if c in (4, 7):
                chars.append("|")
            chars.append(get_val(point, r, c))
        if r != 9:
            chars.append("\n")
            if r in (3, 6):
                chars.append("---+---+---\n")
    print("".join(chars))

def solve(grid):
    I = parse_grid(grid)
    cnf = I * S
    return cnf.satisfy_one()
