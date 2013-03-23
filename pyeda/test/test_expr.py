"""
Test expressions
"""

from pyeda.expr import (
    var,
    Or, And, Not, Xor, Xnor, Equal, Implies, ITE,
    Nor, Nand, OneHot0, OneHot,
    f_xor, f_xnor, f_equal, f_implies, f_ite
)

def test_xor():
    a, b, c = map(var, 'abc')

    assert Xor() == 0
    assert Xor(a) == a

    assert Xor(0, 0) == 0
    assert Xor(0, 1) == 1
    assert Xor(1, 0) == 1
    assert Xor(1, 1) == 0

    assert Xor(0, a) == a
    assert Xor(a, 0) == a
    assert Xor(1, a) == -a
    assert Xor(a, 1) == -a

    assert Xor(a, a) == 0
    assert Xor(a, -a) == 1
    assert Xor(-a, a) == 1

    assert f_xor(a, b).equivalent(-a * b + a * -b)
    assert f_xor(a, b, c).equivalent(-a * -b * c + -a * b * -c + a * -b * -c + a * b * c)

def test_xnor():
    a, b, c = map(var, 'abc')

    assert Xnor() == 1
    assert Xnor(a) == -a

    assert Xnor(0, 0) == 1
    assert Xnor(0, 1) == 0
    assert Xnor(1, 0) == 0
    assert Xnor(1, 1) == 1

    assert Xnor(0, a) == -a
    assert Xnor(a, 0) == -a
    assert Xnor(1, a) == a
    assert Xnor(a, 1) == a

    assert Xnor(a, a) == 1
    assert Xnor(a, -a) == 0
    assert Xnor(-a, a) == 0

    assert f_xnor(a, b).equivalent(-a * -b + a * b)
    assert f_xnor(a, b, c).equivalent(-a * -b * -c + -a * b * c + a * -b * c + a * b * -c)

def test_equal():
    a, b, c = map(var, 'abc')

    assert Equal() == 1
    assert Equal(a) == 1

    assert Equal(0, 0) == 1
    assert Equal(0, 1) == 0
    assert Equal(1, 0) == 0
    assert Equal(1, 1) == 1

    assert Equal(0, a) == -a
    assert Equal(a, 0) == -a
    assert Equal(1, a) == a
    assert Equal(a, 1) == a

    assert Equal(a, a) == 1
    assert Equal(a, -a) == 0
    assert Equal(-a, a) == 0

    assert f_equal(a, b).equivalent(-a * -b + a * b)
    assert f_equal(a, b, c).equivalent(-a * -b * -c + a * b * c)

def test_implies():
    a, b = map(var, 'ab')

    assert Implies(0, 0) == 1
    assert Implies(0, 1) == 1
    assert Implies(1, 0) == 0
    assert Implies(1, 1) == 1

    assert (0 >> a) == 1
    assert (1 >> a) == a
    assert (a >> 0) == -a
    assert (a >> 1) == 1

    assert (a >> a) == 1
    assert (a >> -a) == -a
    assert (-a >> a) == a

    assert f_implies(a, b).equivalent(-a + b)

def test_ite():
    s, a, b = map(var, 'sab')

    assert ITE(0, 0, 0) == 0
    assert ITE(0, 0, 1) == 1
    assert ITE(0, 1, 0) == 0
    assert ITE(0, 1, 1) == 1
    assert ITE(1, 0, 0) == 0
    assert ITE(1, 0, 1) == 0
    assert ITE(1, 1, 0) == 1
    assert ITE(1, 1, 1) == 1

    assert ITE(0, 0, b) == b
    assert ITE(0, a, 0) == 0
    assert ITE(0, 1, b) == b
    assert ITE(0, a, 1) == 1
    assert ITE(1, 0, b) == 0
    assert ITE(1, a, 0) == a
    assert ITE(1, 1, b) == 1
    assert ITE(1, a, 1) == a

    assert ITE(s, 0, b).equivalent(-s * b)
    assert ITE(s, a, 0).equivalent(s * a)
    assert ITE(s, 1, b).equivalent(s * b)
    assert ITE(s, a, 1).equivalent(-s * a)

    assert ITE(s, -a, -a) == -a
    assert ITE(s, a, a) == a

    assert f_ite(s, a, b).equivalent(s * a + -s * b)
