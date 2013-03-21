"""
Test the DIMACS parser
"""

from pyeda.vexpr import bitvec
from pyeda.dimacs import parse_cnf, parse_sat
from pyeda.expr import Xor, Equal

import nose

X = bitvec('x', (1, 16))

F1 = (X[1] + -X[2] + X[3]) * (-X[4] + X[5]) * -X[6]
F2 = (-X[1] * X[2] * -X[3]) + (X[4] * -X[5]) + X[6]
F3 = X[1] + Xor(-X[2], X[3], -X[4] * X[5]) + -X[6]
F4 = X[1] + Equal(-X[2], X[3], -X[4] * X[5]) + -X[6]
F5 = X[1] + Xor(-X[2], X[3], Equal(-X[4], X[5])) + -X[6]

CNF_NO_PREAMBLE = \
"""c comment
1 -2 3 0 -4 5 0 -6
"""

CNF_INCORRECT_PREAMBLE_1 = \
"""c comment
p
1 -2 3 0 -4 5 0 -6
"""

CNF_INCORRECT_PREAMBLE_2 = \
"""c comment
p cnf
1 -2 3 0 -4 5 0 -6
"""

CNF_INCORRECT_PREAMBLE_3 = \
"""c comment
p cnf 6
1 -2 3 0 -4 5 0 -6
"""

CNF_INCORRECT_FORMULA_1 = \
"""c comment
p cnf 6
1 -2 3 0 foo -4 5 0 -6
"""

CNF_INCORRECT_FORMULA_2 = \
"""c comment
p cnf 6
1 -2 3 0 - -4 5 0 -6
"""

CNF_F1_1 = \
"""c comment
p cnf 6 3
1 -2 3 0 -4 5 0 -6
"""

CNF_F1_2 = \
"""c comment
p cnf 6 3
1 -2 3 0
-4 5 0
-6
"""

CNF_F1_3 = \
"""c comment
p cnf 6 3
1 -2
3
0 -4
5 0
-6
"""

SAT_INCORRECT_PREAMBLE_1 = \
"""c comment
p
*( +(1 -2 3) +(-4 5) -6 )
"""

SAT_INCORRECT_PREAMBLE_2 = \
"""c comment
p sat
*( +(1 -2 3) +(-4 5) -6 )
"""

SAT_F1_1 = \
"""c comment
p sat 6
*( +(1 -2 3) +(-4 5) -6 *(-6) *() )
"""

SAT_F2_1 = \
"""c comment
p sat 6
+( *(-1 2 -3) *(4 -5) 6 +(6) +() )
"""

SAT_F3_1 = \
"""c comment
p satx 6
+(1 xor(-2 3 *(-4 5)) -6)
"""

SAT_F4_1 = \
"""c comment
p sate 6
+(1 =(-2 3 *(-4 5)) -6)
"""

SAT_F5_1 = \
"""c comment
p satex 6
+(1 xor(-2 3 =(-4 5)) -6)
"""

def test_cnf_errors():
    nose.tools.assert_raises(SyntaxError, parse_cnf, CNF_NO_PREAMBLE)
    nose.tools.assert_raises(SyntaxError, parse_cnf, CNF_INCORRECT_PREAMBLE_1)
    nose.tools.assert_raises(SyntaxError, parse_cnf, CNF_INCORRECT_PREAMBLE_2)
    nose.tools.assert_raises(SyntaxError, parse_cnf, CNF_INCORRECT_PREAMBLE_3)
    nose.tools.assert_raises(SyntaxError, parse_cnf, CNF_INCORRECT_FORMULA_1)
    nose.tools.assert_raises(SyntaxError, parse_cnf, CNF_INCORRECT_FORMULA_2)

def test_cnf():
    assert parse_cnf(CNF_F1_1).equivalent(F1)
    assert parse_cnf(CNF_F1_2).equivalent(F1)
    assert parse_cnf(CNF_F1_3).equivalent(F1)

def test_sat_errors():
    nose.tools.assert_raises(SyntaxError, parse_sat, SAT_INCORRECT_PREAMBLE_1)
    nose.tools.assert_raises(SyntaxError, parse_sat, SAT_INCORRECT_PREAMBLE_2)

def test_sat():
    assert parse_sat(SAT_F1_1).equivalent(F1)
    assert parse_sat(SAT_F2_1).equivalent(F2)

def test_satx():
    assert parse_sat(SAT_F3_1).equivalent(F3)

def test_sate():
    assert parse_sat(SAT_F4_1).equivalent(F4)

def test_satex():
    assert parse_sat(SAT_F5_1).equivalent(F5)
