"""
Test expressions
"""

from pyeda.expr import (
    var,
    Or, And, Not, Xor, Xnor, Equal, Implies,
    Nor, Nand, OneHot0, OneHot,
    f_xor, f_xnor, f_equal, f_implies,
)

def test_xor():
    a, b, c = map(var, 'abc')

    assert Xor() == 0
    assert Xor(a).equivalent(a)

    assert Xor(0, 0) == 0
    assert Xor(0, 1) == 1
    assert Xor(1, 0) == 1
    assert Xor(1, 1) == 0

    assert Xor(0, a).equivalent(a)
    assert Xor(a, 0).equivalent(a)
    assert Xor(1, a).equivalent(-a)
    assert Xor(a, 1).equivalent(-a)

    assert Xor(a, a) == 0
    assert Xor(a, -a) == 1
    assert Xor(-a, a) == 1

    assert f_xor(a, b).equivalent(-a * b + a * -b)
    assert f_xor(a, b, c).equivalent(-a * -b * c + -a * b * -c + a * -b * -c + a * b * c)

def test_xnor():
    a, b, c = map(var, 'abc')

    assert Xnor() == 1
    assert Xnor(a).equivalent(-a)

    assert Xnor(0, 0) == 1
    assert Xnor(0, 1) == 0
    assert Xnor(1, 0) == 0
    assert Xnor(1, 1) == 1

    assert Xnor(0, a).equivalent(-a)
    assert Xnor(a, 0).equivalent(-a)
    assert Xnor(1, a).equivalent(a)
    assert Xnor(a, 1).equivalent(a)

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

    assert Equal(0, a).equivalent(-a)
    assert Equal(a, 0).equivalent(-a)
    assert Equal(1, a).equivalent(a)
    assert Equal(a, 1).equivalent(a)

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
    assert (1 >> a).equivalent(a)
    assert (a >> 0).equivalent(-a)
    assert (a >> 1) == 1

    assert (a >> a) == 1
    assert (a >> -a).equivalent(-a)
    assert (-a >> a).equivalent(a)

    assert f_implies(a, b).equivalent(-a + b)
