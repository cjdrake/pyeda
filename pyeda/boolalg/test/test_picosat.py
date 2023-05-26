"""
Test the PicoSAT interface
"""


import pytest

from pyeda.boolalg import picosat
from pyeda.boolalg.expr import expr, expr2dimacscnf


def test_basic():
    assert picosat.COPYRIGHT == "Copyright (c) 2006 - 2014 Armin Biere JKU Linz"
    assert picosat.VERSION == "960"


def test_satisfy_one_errors():
    with pytest.raises(TypeError):
        picosat.satisfy_one(6, ((1, -2, "bad_lit"), (-4, 5, -6)))
    with pytest.raises(ValueError):
        picosat.satisfy_one(5, ((1, -2, 3), (-4, 5, -6)))


def test_satisfy_one():
    _, cnf = expr2dimacscnf(expr("And(a, b, c)"))
    assert picosat.satisfy_one(cnf.nvars, cnf.clauses) == (1, 1, 1)
    assert list(picosat.satisfy_all(cnf.nvars, cnf.clauses)) == [(1, 1, 1)]
