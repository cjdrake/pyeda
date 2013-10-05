"""
Test logic functions for Sudoku
"""

import os
import random

from pyeda.logic.sudoku import SudokuSolver

SOLVER = SudokuSolver()

cwd, _ = os.path.split(__file__)
top95_txt = os.path.join(cwd, 'top95.txt')
top95_solns_txt = os.path.join(cwd, 'top95_solns.txt')
with open(top95_txt) as fin:
    GRIDS = [line.strip() for line in fin]
with open(top95_solns_txt) as fin:
    SOLNS = [line.strip() for line in fin]

def test_sudoku():
    for i, grid in enumerate(GRIDS):
        assert SOLVER.display_solve(grid) == SOLNS[i]
