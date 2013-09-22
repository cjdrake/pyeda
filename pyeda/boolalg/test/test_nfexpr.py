"""
Test normal form expression Boolean functions
"""

from pyeda.boolalg.expr import exprvar, EXPRZERO, EXPRONE

from pyeda.boolalg.nfexpr import (
    expr2dnf, expr2cnf, nf2expr,
    upoint2nfpoint,
    DisjNormalForm, ConjNormalForm
)

import nose

a, b, c, d = map(exprvar, 'abcd')

def test_misc():
    nose.tools.assert_raises(TypeError, nf2expr, "foo")

def test_expr2dnf():
    nose.tools.assert_raises(TypeError, expr2dnf, "foo")
    assert expr2dnf(EXPRZERO).is_zero()
    nose.tools.assert_raises(ValueError, expr2dnf, EXPRONE)
    assert nf2expr(expr2dnf(a)) == a
    assert nf2expr(expr2dnf(-a)) == -a
    assert nf2expr(expr2dnf(a + -b)).equivalent(a + -b)
    assert nf2expr(expr2dnf(a * -b)).equivalent(a * -b)
    assert nf2expr(expr2dnf(a + -b + (c * -d))).equivalent(a + -b + (c * -d))

def test_expr2cnf():
    nose.tools.assert_raises(TypeError, expr2cnf, "foo")
    assert expr2cnf(EXPRONE).is_one()
    nose.tools.assert_raises(ValueError, expr2cnf, EXPRZERO)
    assert nf2expr(expr2cnf(a)) == a
    assert nf2expr(expr2cnf(-a)) == -a
    assert nf2expr(expr2cnf(a + -b)).equivalent(a + -b)
    assert nf2expr(expr2cnf(a * -b)).equivalent(a * -b)
    assert nf2expr(expr2cnf(a * -b * (c + -d))).equivalent(a * -b * (c + -d))

def test_upoint2point():
    upoint = frozenset([a.uniqid, c.uniqid]), frozenset([b.uniqid, d.uniqid])
    assert upoint2nfpoint(upoint) == {a: 0, b: 1, c: 0, d: 1}

def test_basic():
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
    assert nf2expr(-dnf).equivalent(-f)

    assert isinstance(-cnf, DisjNormalForm)
    assert nf2expr(-cnf).equivalent(-g)
