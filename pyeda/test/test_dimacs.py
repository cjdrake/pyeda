
from pyeda.vexpr import bitvec
from pyeda.dimacs import parse_cnf, parse_sat

X = bitvec('x', (1, 10))

F1 = (X[1] + -X[2] + X[3]) * (-X[4] + X[5] + -X[6]) * (X[7] + -X[8] + X[9])

CNF_F1 = \
"""c comment1
c comment2
p cnf 9 3
1 -2 3 0 -4 5 -6 0 7 -8 9
"""

SAT_F1 = \
"""c comment1
c comment2
p sat 9
*( +(1 -2 3) +(-4 5 -6) +(7 -8 9) )
"""

def test_cnf():
    assert parse_cnf(CNF_F1).equivalent(F1)

def test_sat():
    assert parse_sat(SAT_F1).equivalent(F1)
