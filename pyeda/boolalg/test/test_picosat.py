# Filename: test_picosat.py

from pyeda.boolalg.expr import expr, DimacsCNF

from pyeda.boolalg import _picosat
from pyeda.boolalg import picosat

from nose.tools import assert_raises

def test_basic():
    assert _picosat.__doc__ == "Python bindings to PicoSAT"
    assert _picosat.PICOSAT_COPYRIGHT == "Copyright (c) 2006 - 2012 Armin Biere JKU Linz"
    assert _picosat.PICOSAT_VERSION == "957"

def test_solve_errors():
    assert_raises(TypeError, _picosat.solve, 6, ((1, -2, 'bad_lit'), (-4, 5, -6)))
    assert_raises(ValueError, _picosat.solve, 5, ((1, -2, 3), (-4, 5, -6)))

def test_solve():
    a, b, c = map(expr, 'abc')
    cnf = DimacsCNF(a * b * c)
    assert picosat.solve(cnf) == {a: 1, b: 1, c: 1}
