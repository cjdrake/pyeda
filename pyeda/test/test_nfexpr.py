"""
Test normal form expressions
"""

from pyeda.expr import var

from pyeda.nfexpr import (
    expr2dnf, expr2cnf, dnf2expr, cnf2expr,
    DisjNormalForm, ConjNormalForm
)

import nose

a, b, c, d, e, p, q, s = map(var, 'abcdepqs')

def test_conversion():
    f = -a * b + a * -b
    g = (a + b) * (-a + -b)

    nose.tools.assert_raises(TypeError, expr2dnf, g)
    nose.tools.assert_raises(TypeError, expr2cnf, f)

    dnf2expr(expr2dnf(f)).equivalent(f)
    cnf2expr(expr2cnf(g)).equivalent(g)

def test_basic():
    assert DisjNormalForm(dict(), set()) == 0
    assert ConjNormalForm(dict(), set()) == 1

    f = -a * b + a * -b
    g = (a + b) * (-a + -b)
    dnf = expr2dnf(f)
    cnf = expr2cnf(g)

    assert str(dnf) == "a' * b + a * b'"
    assert str(cnf) == "(a + b) * (a' + b')"

    assert repr(dnf) == "a' * b + a * b'"
    assert repr(cnf) == "(a + b) * (a' + b')"

    assert dnf.support == {a, b}
    assert cnf.support == {a, b}
    assert dnf.inputs == [a, b]
    assert cnf.inputs == [a, b]

    assert isinstance(-dnf, ConjNormalForm)
    assert cnf2expr(-dnf).equivalent(-f)

    assert isinstance(-cnf, DisjNormalForm)
    assert dnf2expr(-cnf).equivalent(-g)
