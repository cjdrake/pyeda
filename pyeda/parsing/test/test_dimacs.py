"""
Test DIMACS load/dump methods
"""

from pyeda.vexpr import bitvec
from pyeda.parsing.lex import LexError
from pyeda.parsing.dimacs import (
    DIMACSError,
    load_cnf, dump_cnf, load_sat, dump_sat,
)
from pyeda.expr import Not, Xor, Equal, Implies

import nose

X = bitvec('x', (1, 16))

def test_cnf_errors():
    # unexpected token
    nose.tools.assert_raises(DIMACSError, load_cnf, "p cnf cnf 0 0\n")
    # formula has fewer clauses than specified
    nose.tools.assert_raises(DIMACSError, load_cnf, "p cnf 0 1\n")
    # formula has more clauses than specified
    nose.tools.assert_raises(DIMACSError, load_cnf, "p cnf 0 0\n0")
    # formula literal too large
    nose.tools.assert_raises(DIMACSError, load_cnf, "p cnf 0 1\n1 0")
    nose.tools.assert_raises(DIMACSError, load_cnf, "p cnf 0 1\n-1 0")
    # incomplete clause
    nose.tools.assert_raises(DIMACSError, load_cnf, "p cnf 1 1\n1")

def test_load_cnf():
    # Empty formula corner cases
    assert load_cnf("p cnf 0 0\n").is_one()
    assert load_cnf("p cnf 1 0\n").is_one()

    # Empty clause corner cases
    assert load_cnf("p cnf 0 1\n0").is_zero()
    assert load_cnf("p cnf 1 2\n0 0").is_zero()

    assert load_cnf("p cnf 2 2\n-1 2 0 1 -2 0").equivalent((-X[1] + X[2]) * (X[1] + -X[2]))

def test_dump_cnf():
    # input is not an expression
    nose.tools.assert_raises(ValueError, dump_cnf, 42)
    # expression is not a CNF
    nose.tools.assert_raises(ValueError, dump_cnf, X[1] * X[2] + X[3] * X[4])
    assert load_cnf(dump_cnf((-X[1] + X[2]) * (X[1] + -X[2]))).equivalent((-X[1] + X[2]) * (X[1] + -X[2]))

def test_sat_errors():
    nose.tools.assert_raises(DIMACSError, load_sat, "p sat 0\n")
    nose.tools.assert_raises(DIMACSError, load_sat, "p sat 2\n0")
    nose.tools.assert_raises(DIMACSError, load_sat, "p sat 2\n3")
    nose.tools.assert_raises(DIMACSError, load_sat, "p sat 2\n-3")
    nose.tools.assert_raises(DIMACSError, load_sat, "p sat 2\n-(0)")
    nose.tools.assert_raises(DIMACSError, load_sat, "p sat 2\n-(3)")

def test_load_sat():
    assert load_sat("p sat 2\n-(+(*(-1 2) *(1 -2)))").equivalent((X[1] + -X[2]) * (-X[1] + X[2]))
    assert load_sat("p satx 2\nxor(-1 2)").equivalent(Xor(-X[1], X[2]))
    assert load_sat("p sate 2\n=(-1 2)").equivalent(Equal(-X[1], X[2]))
    assert load_sat("p satex 2\n+(xor(-1 2) =(-1 2))").equivalent(Xor(-X[1], X[2]) + Equal(-X[1], X[2]))

def test_dump_sat():
    # input is not an expression
    nose.tools.assert_raises(ValueError, dump_sat, 42)
    nose.tools.assert_raises(ValueError, dump_sat, Implies(X[1], -X[2]))
    assert load_sat(dump_sat(Not(-X[1] * X[2] + X[1] * -X[2]))).equivalent((X[1] + -X[2]) * (-X[1] + X[2]))
    assert load_sat(dump_sat(Xor(-X[1], X[2]))).equivalent(Xor(-X[1], X[2]))
    assert load_sat(dump_sat(Equal(-X[1], X[2]))).equivalent(Equal(-X[1], X[2]))
    assert load_sat(dump_sat(Xor(-X[1], X[2]) + Equal(-X[1], X[2]))).equivalent(Xor(-X[1], X[2]) + Equal(-X[1], X[2]))
