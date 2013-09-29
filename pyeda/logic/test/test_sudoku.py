"""
Test logic functions for Sudoku
"""

import os

from pyeda.logic.sudoku import SudokuSolver

SOLN_10 = """\
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
431|926|785"""

SOLN_20 = """\
498|716|523
257|839|461
136|425|987
---+---+---
971|382|654
684|157|392
523|694|718
---+---+---
765|241|839
319|578|246
842|963|175"""

SOLN_30 = """\
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
658|947|132"""


SOLVER = SudokuSolver()

cwd, _ = os.path.split(__file__)
top95_txt = os.path.join(cwd, 'top95.txt')
with open(top95_txt) as fin:
    GRIDS = fin.readlines()

def test_sudoku_grid10():
    assert SOLVER.display_solve(GRIDS[10]) == SOLN_10

#def test_sudoku_grid20():
#    assert SOLVER.display_solve(GRIDS[20]) == SOLN_20

#def test_sudoku_grid30():
#    assert SOLVER.display_solve(GRIDS[30]) == SOLN_30
