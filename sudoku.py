"""
Sudoku Puzzle

>>> S = Sudoku()
>>> grid = "002980010016327000390006040800030095000070000640050002080200054000761920060045700"
>>> soln = S.solve(grid)
>>> print(pretty_soln(soln))
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
>>> soln = S.solve(grid)
>>> print(pretty_soln(soln))
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
from pyeda.cnf import expr2cnf

DIGITS = "123456789"

class Sudoku:
    def __init__(self):
        X = [ [ [ var("x", r, c, v) for v in range(3 * 3) ]
                                    for c in range(3 * 3) ]
                                    for r in range(3 * 3) ]
        self.X = X

        # Value constraints
        V = And(*[
                And(*[
                    OneHot(*[ X[r][c][v]
                        for v in range(3 * 3) ])
                        for c in range(3 * 3) ])
                        for r in range(3 * 3) ])
        V = expr2cnf(V)

        # Row constraints
        R = And(*[
                And(*[
                    OneHot(*[ X[r][c][v]
                        for c in range(3 * 3) ])
                        for v in range(3 * 3) ])
                        for r in range(3 * 3) ])
        R = expr2cnf(R)

        # Column constraints
        C = And(*[
                And(*[
                    OneHot(*[ X[r][c][v]
                        for r in range(3 * 3) ])
                        for v in range(3 * 3) ])
                        for c in range(3 * 3) ])
        C = expr2cnf(C)

        # Box constraints
        B = And(*[
                And(*[
                    OneHot(*[ X[3*br+r][3*bc+c][v]
                        for r in range(3) for c in range(3) ])
                        for v in range(3 * 3) ])
                        for br in range(3) for bc in range(3) ])
        B = expr2cnf(B)

        self.cnf = V * R * C * B

    def _assign(self, grid):
        chars = [c for c in grid if c in DIGITS or c in "0."]
        assert len(chars) == (3 * 3) ** 2

        cnf = self.cnf.copy()
        for i, c in enumerate(chars):
            if c in DIGITS:
                cnf *= self.X[i//(3*3)][i%(3*3)][int(c)-1]
        return cnf

    def _get_rows(self, point):
        rows = []
        for r in range(3 * 3):
            row = []
            for c in range(3 * 3):
                for v in range(3 * 3):
                    if self.X[r][c][v] in point and point[self.X[r][c][v]] == 1:
                        row.append(str(v+1))
                        break
                else:
                    row.append("X")
            rows.append("".join(row))
        return rows

    def solve(self, grid):
        cnf = self._assign(grid)
        point = cnf.satisfy_one()
        rows = self._get_rows(point)
        return rows

def pretty_soln(rows):
    chars = list()
    for i, row in enumerate(rows):
        for j, col in enumerate(row):
            if j != 0 and j % 3 == 0:
                chars.append("|")
            chars.append(col)
        if i != (3 * 3 - 1):
            chars.append("\n")
            if i % 3 == (3 - 1):
                chars.append("---+---+---\n")
    return "".join(chars)
