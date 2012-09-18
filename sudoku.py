"""
Sudoku Puzzle

>>> S = Sudoku()
>>> GIVEN =  ["002980010", "016327000", "390006040"]
>>> GIVEN += ["800030095", "000070000", "640050002"]
>>> GIVEN += ["080200054", "000761920", "060045700"]
>>> soln = S.solve(GIVEN)
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
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from pyeda.expr import var, And, OneHot
from pyeda.cnf import expr2cnf

class Sudoku:
    def __init__(self, N=3):
        self.N = N
        N2 = N * N
        self.N2 = N2

        X = [ [ [ var("x", r, c, v) for v in range(N2) ]
                                    for c in range(N2) ]
                                    for r in range(N2) ]
        self.X = X

        # Value constraints
        V = And(*[
                And(*[
                    OneHot(*[ X[r][c][v]
                        for v in range(N2) ])
                        for c in range(N2) ])
                        for r in range(N2) ])
        V = expr2cnf(V)

        # Row constraints
        R = And(*[
                And(*[
                    OneHot(*[ X[r][c][v]
                        for c in range(N2) ])
                        for v in range(N2) ])
                        for r in range(N2) ])
        R = expr2cnf(R)

        # Column constraints
        C = And(*[
                And(*[
                    OneHot(*[ X[r][c][v]
                        for r in range(N2) ])
                        for v in range(N2) ])
                        for c in range(N2) ])
        C = expr2cnf(C)

        # Box constraints
        B = And(*[
                And(*[
                    OneHot(*[ X[N*br+r][N*bc+c][v]
                        for r in range(N) for c in range(N) ])
                        for v in range(N2) ])
                        for br in range(N) for bc in range(N) ])
        B = expr2cnf(B)

        self.cnf = V * R * C * B

    def _specify(self, given):
        cnf = self.cnf.copy()
        nonzero = [str(n) for n in range(1, self.N2 + 1)]
        for r in range(self.N2):
            for c in range(self.N2):
                str_val = given[r][c]
                if str_val == "0":
                    pass
                elif str_val in nonzero:
                    int_val = int(str_val) - 1
                    for v in range(self.N2):
                        if v == int_val:
                            cnf *= self.X[r][c][v]
                else:
                    raise ValueError("invalid given")
        return cnf

    def _get_rows(self, point):
        rows = []
        for r in range(self.N2):
            row = []
            for c in range(self.N2):
                for v in range(self.N2):
                    if self.X[r][c][v] in point and point[self.X[r][c][v]] == 1:
                        row.append(str(v+1))
                        break
                else:
                    row.append("X")
            rows.append("".join(row))
        return rows

    def solve(self, given):
        cnf = self._specify(given)
        # FIXME -- use satisfy_one
        point, _ = cnf.bcp()
        rows = self._get_rows(point)
        return rows

def pretty_soln(rows, N=3):
    chars = list()
    for i, row in enumerate(rows):
        for j, col in enumerate(row):
            if j != 0 and j % N == 0:
                chars.append("|")
            chars.append(col)
        if i != (N * N - 1):
            chars.append("\n")
            if i % N == (N - 1):
                chars.append("---+---+---\n")
    return "".join(chars)
