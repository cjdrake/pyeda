"""
Test expressions
"""

from pyeda.expr import (
    factor, simplify,
    var,
    Or, And, Not, Xor, Xnor, Equal, Implies, ITE,
    Nor, Nand, OneHot0, OneHot,
    f_not, f_or, f_and, f_xor, f_xnor, f_equal, f_implies, f_ite
)

a, b, c, d, e, s = map(var, 'abcdes')

def test_ops():
    # __sub__, __rsub__
    assert (a - 0) == 1
    assert (0 - a) == -a
    assert (a - 1) == a
    assert (1 - a) == 1
    assert (a - b).equivalent(a + -b)
    # xor, equal, ite
    assert a.xor(b, c).equivalent(-a * -b * c + -a * b * -c + a * -b * -c + a * b * c)
    assert a.equal(b, c).equivalent(-a * -b * -c + a * b * c)
    assert s.ite(a, b).equivalent(s * a + -s * b)

def test_simplify():
    f1 = And(a, And(b, And(c, 0, simplify=False), simplify=False), simplify=False)
    f2 = Or(a, Or(b, Or(c, 1, simplify=False), simplify=False), simplify=False)
    assert str(f1) == "a * b * c * 0"
    assert str(f2) == "a + b + c + 1"
    assert simplify(f1) == 0
    assert simplify(f2) == 1

def test_onehot0():
    assert OneHot0(0, 0, 0) == 1
    assert OneHot0(0, 0, 1) == 1
    assert OneHot0(0, 1, 0) == 1
    assert OneHot0(0, 1, 1) == 0
    assert OneHot0(1, 0, 0) == 1
    assert OneHot0(1, 0, 1) == 0
    assert OneHot0(1, 1, 0) == 0
    assert OneHot0(1, 1, 1) == 0

    assert OneHot0(a, b, c).equivalent((-a + -b) * (-a + -c) * (-b + -c))

def test_onehot():
    assert OneHot(0, 0, 0) == 0
    assert OneHot(0, 0, 1) == 1
    assert OneHot(0, 1, 0) == 1
    assert OneHot(0, 1, 1) == 0
    assert OneHot(1, 0, 0) == 1
    assert OneHot(1, 0, 1) == 0
    assert OneHot(1, 1, 0) == 0
    assert OneHot(1, 1, 1) == 0

    assert OneHot(a, b, c).equivalent((-a + -b) * (-a + -c) * (-b + -c) * (a + b + c))

def test_var():
    # Function
    assert a.support == {a}

    assert a.restrict({a: 0}) == 0
    assert a.restrict({a: 1}) == 1
    assert a.restrict({b: 0}) == a

    assert a.compose({a: b}) == b
    assert a.compose({b: c}) == a

    # Expression
    assert a.depth == 0
    assert a.factor() == a
    assert a.is_dnf()
    assert a.is_cnf()
    assert a.invert() == -a

def test_comp():
    # Function
    assert (-a).support == {a}

    assert (-a).restrict({a: 0}) == 1
    assert (-a).restrict({a: 1}) == 0
    assert (-a).restrict({b: 0}) == -a

    assert (-a).compose({a: b}) == -b
    assert (-a).compose({b: c}) == -a

    # Expression
    assert (-a).depth == 0
    assert (-a).factor() == -a
    assert (-a).is_dnf()
    assert (-a).is_cnf()
    assert (-a).invert() == a

def test_var_order():
    assert -a < a < -b < b
    assert a < a + b
    assert b < a + b
    assert -a < a + b
    assert -b < a + b

def test_or():
    assert Or() == 0
    assert Or(a) == a

    assert Or(0, 0) == 0
    assert Or(0, 1) == 1
    assert Or(1, 0) == 1
    assert Or(1, 1) == 1

    assert Or(0, 0, 0) == 0
    assert Or(0, 0, 1) == 1
    assert Or(0, 1, 0) == 1
    assert Or(0, 1, 1) == 1
    assert Or(1, 0, 0) == 1
    assert Or(1, 0, 1) == 1
    assert Or(1, 1, 0) == 1
    assert Or(1, 1, 1) == 1

    assert 0 + a == a
    assert a + 0 == a
    assert 1 + a == 1
    assert a + 1 == 1

    assert (0 + a + b).equivalent(a + b)
    assert (a + b + 0).equivalent(a + b)
    assert (1 + a + b) == 1
    assert (a + b + 1) == 1

    assert -a + a == 1
    assert a + -a == 1

    assert f_or(a >> b, c >> d).equivalent(-a + b + -c + d)

def test_and():
    assert And() == 1
    assert And(a) == a

    assert And(0, 0) == 0
    assert And(0, 1) == 0
    assert And(1, 0) == 0
    assert And(1, 1) == 1

    assert And(0, 0, 0) == 0
    assert And(0, 0, 1) == 0
    assert And(0, 1, 0) == 0
    assert And(0, 1, 1) == 0
    assert And(1, 0, 0) == 0
    assert And(1, 0, 1) == 0
    assert And(1, 1, 0) == 0
    assert And(1, 1, 1) == 1

    assert 0 * a == 0
    assert a * 0 == 0
    assert 1 * a == a
    assert a * 1 == a

    assert (0 * a * b) == 0
    assert (a * b * 0) == 0
    assert (1 * a * b).equivalent(a * b)
    assert (a * b * 1).equivalent(a * b)

    assert -a * a == 0
    assert a * -a == 0

    assert f_and(a >> b, c >> d).equivalent((-a + b) * (-c + d))

def test_not():
    assert f_not(-a * b * -c * d).equivalent(a + -b + c + -d)
    assert f_not(-a + b + -c + d).equivalent(a * -b * c * -d)

def test_xor():
    assert Xor() == 0
    assert Xor(a) == a

    assert Xor(0, 0) == 0
    assert Xor(0, 1) == 1
    assert Xor(1, 0) == 1
    assert Xor(1, 1) == 0

    assert Xor(0, 0, 0) == 0
    assert Xor(0, 0, 1) == 1
    assert Xor(0, 1, 0) == 1
    assert Xor(0, 1, 1) == 0
    assert Xor(1, 0, 0) == 1
    assert Xor(1, 0, 1) == 0
    assert Xor(1, 1, 0) == 0
    assert Xor(1, 1, 1) == 1

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
    assert Xnor() == 1
    assert Xnor(a) == -a

    assert Xnor(0, 0) == 1
    assert Xnor(0, 1) == 0
    assert Xnor(1, 0) == 0
    assert Xnor(1, 1) == 1

    assert Xnor(0, 0, 0) == 1
    assert Xnor(0, 0, 1) == 0
    assert Xnor(0, 1, 0) == 0
    assert Xnor(0, 1, 1) == 1
    assert Xnor(1, 0, 0) == 0
    assert Xnor(1, 0, 1) == 1
    assert Xnor(1, 1, 0) == 1
    assert Xnor(1, 1, 1) == 0

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
    assert Equal() == 1
    assert Equal(a) == 1

    assert Equal(0, 0) == 1
    assert Equal(0, 1) == 0
    assert Equal(1, 0) == 0
    assert Equal(1, 1) == 1

    assert Equal(0, 0, 0) == 1
    assert Equal(0, 0, 1) == 0
    assert Equal(0, 1, 0) == 0
    assert Equal(0, 1, 1) == 0
    assert Equal(1, 0, 0) == 0
    assert Equal(1, 0, 1) == 0
    assert Equal(1, 1, 0) == 0
    assert Equal(1, 1, 1) == 1

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
    assert ITE(s, 1, b).equivalent(s + b)
    assert ITE(s, a, 1).equivalent(-s + a)

    assert ITE(s, -a, -a) == -a
    assert ITE(s, a, a) == a

    assert f_ite(s, a, b).equivalent(s * a + -s * b)

def test_absorb():
    assert (a * b + a * b).absorb().equivalent(a * b)
    assert (a * (a + b)).absorb() == a
    assert ((a + b) * a).absorb() == a
    assert (-a * (-a + b)).absorb() == -a
    assert (a * b * (a + c)).absorb().equivalent(a * b)
    assert (a * b * (a + c) * (a + d)).absorb().equivalent(a * b)
    assert (-a * b * (-a + c)).absorb().equivalent(-a * b)
    assert (-a * b * (-a + c) * (-a + d)).absorb().equivalent(-a * b)
    assert (a * -b + a * -b * c).absorb().equivalent(a * -b)
    assert ((a + -b) * (a + -b + c)).absorb().equivalent(a + -b)
    assert ((a + -b + c) * (a + -b)).absorb().equivalent(a + -b)
