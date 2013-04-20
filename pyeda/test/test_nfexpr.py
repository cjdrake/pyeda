"""
Test normal form expression Boolean functions
"""

from pyeda.expr import var, Xor

from pyeda.nfexpr import (
    expr2nfexpr, nfexpr2expr,
    DisjNormalForm, ConjNormalForm
)

import nose

a, b, c, d, e, p, q, s = map(var, 'abcdepqs')

def test_conversion():
    f = -a * b + a * -b
    g = (a + b) * (-a + -b)

    nose.tools.assert_raises(TypeError, expr2nfexpr, Xor(a, b))
    nose.tools.assert_raises(TypeError, nfexpr2expr, "what?")

    nfexpr2expr(expr2nfexpr(f)).equivalent(f)
    nfexpr2expr(expr2nfexpr(g)).equivalent(g)

def test_basic():
    assert DisjNormalForm(set()) == 0
    assert ConjNormalForm(set()) == 1

    f = -a * b + a * -b
    g = (a + b) * (-a + -b)
    dnf = expr2nfexpr(f)
    cnf = expr2nfexpr(g)

    assert str(dnf) == "a' * b + a * b'"
    assert str(cnf) == "(a + b) * (a' + b')"

    assert repr(dnf) == "a' * b + a * b'"
    assert repr(cnf) == "(a + b) * (a' + b')"

    assert dnf.support == {a.var, b.var}
    assert cnf.support == {a.var, b.var}
    assert dnf.inputs == [a.var, b.var]
    assert cnf.inputs == [a.var, b.var]

    assert isinstance(-dnf, ConjNormalForm)
    assert nfexpr2expr(-dnf).equivalent(-f)

    assert isinstance(-cnf, DisjNormalForm)
    assert nfexpr2expr(-cnf).equivalent(-g)
