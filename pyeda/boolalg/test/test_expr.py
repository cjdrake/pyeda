"""
Test expression Boolean functions
"""

import sys

from pyeda.boolalg import boolfunc
from pyeda.boolalg.expr import (
    exprvar,
    Expression,
    Not, Or, And, Nor, Nand, Xor, Xnor, Equal, Unequal, Implies, ITE,
    OneHot0, OneHot, Majority,
    EXPRZERO, EXPRONE,
)
from pyeda.boolalg.vexpr import bitvec

import nose

a, b, c, d, e, p, q, s = map(exprvar, 'abcdepqs')

MAJOR = sys.version_info.major
MINOR = sys.version_info.minor

X = bitvec('x', 16)
Y = bitvec('y', 16, 16, 16)

def test_misc():
    f = a * b + a * c + b * c

    assert f.smoothing(a).equivalent(b + c)
    assert f.consensus(a).equivalent(b * c)
    assert f.derivative(a).equivalent(b * -c + -b * c)

def test_unate():
    # c' * (a' + b')
    f = -c * (-a + -b)
    assert f.is_neg_unate([a, b, c])
    assert f.is_neg_unate([a, b])
    assert f.is_neg_unate([a, c])
    assert f.is_neg_unate([b, c])
    assert f.is_neg_unate(a)
    assert f.is_neg_unate(b)
    assert f.is_neg_unate(c)
    assert f.is_neg_unate()

    f = c * (a + b)
    assert f.is_pos_unate([a, b, c])
    assert f.is_pos_unate([a, b])
    assert f.is_pos_unate([a, c])
    assert f.is_pos_unate([b, c])
    assert f.is_pos_unate(a)
    assert f.is_pos_unate(b)
    assert f.is_pos_unate(c)
    assert f.is_pos_unate()

    f = Xor(a, b, c)
    assert f.is_binate([a, b, c])
    assert f.is_binate([a, b])
    assert f.is_binate([a, c])
    assert f.is_binate([b, c])
    assert f.is_binate(a)
    assert f.is_binate(b)
    assert f.is_binate(c)

def test_box():
    assert Expression.box(0) is EXPRZERO
    assert Expression.box('0') is EXPRZERO
    assert Expression.box(1) is EXPRONE
    assert Expression.box('1') is EXPRONE
    assert Expression.box(a) is a
    assert Expression.box(42) is EXPRONE

def test_nor():
    assert Nor() is EXPRONE
    assert Nor(a) is -a

    assert Nor(0, 0) is EXPRONE
    assert Nor(0, 1) is EXPRZERO
    assert Nor(1, 0) is EXPRZERO
    assert Nor(1, 1) is EXPRZERO

    assert Nor(0, 0, 0) is EXPRONE
    assert Nor(0, 0, 1) is EXPRZERO
    assert Nor(0, 1, 0) is EXPRZERO
    assert Nor(0, 1, 1) is EXPRZERO
    assert Nor(1, 0, 0) is EXPRZERO
    assert Nor(1, 0, 1) is EXPRZERO
    assert Nor(1, 1, 0) is EXPRZERO
    assert Nor(1, 1, 1) is EXPRZERO

    assert Nor(a, b).equivalent(-a * -b)

def test_nand():
    assert Nand() is EXPRZERO
    assert Nand(a) is -a

    assert Nand(0, 0) is EXPRONE
    assert Nand(0, 1) is EXPRONE
    assert Nand(1, 0) is EXPRONE
    assert Nand(1, 1) is EXPRZERO

    assert Nand(0, 0, 0) is EXPRONE
    assert Nand(0, 0, 1) is EXPRONE
    assert Nand(0, 1, 0) is EXPRONE
    assert Nand(0, 1, 1) is EXPRONE
    assert Nand(1, 0, 0) is EXPRONE
    assert Nand(1, 0, 1) is EXPRONE
    assert Nand(1, 1, 0) is EXPRONE
    assert Nand(1, 1, 1) is EXPRZERO

    assert Nand(a, b).equivalent(-a + -b)

def test_onehot0():
    assert OneHot0(0, 0, 0) is EXPRONE
    assert OneHot0(0, 0, 1) is EXPRONE
    assert OneHot0(0, 1, 0) is EXPRONE
    assert OneHot0(0, 1, 1) is EXPRZERO
    assert OneHot0(1, 0, 0) is EXPRONE
    assert OneHot0(1, 0, 1) is EXPRZERO
    assert OneHot0(1, 1, 0) is EXPRZERO
    assert OneHot0(1, 1, 1) is EXPRZERO
    assert OneHot0(a, b, c).equivalent((-a + -b) * (-a + -c) * (-b + -c))

def test_onehot():
    assert OneHot(0, 0, 0) is EXPRZERO
    assert OneHot(0, 0, 1) is EXPRONE
    assert OneHot(0, 1, 0) is EXPRONE
    assert OneHot(0, 1, 1) is EXPRZERO
    assert OneHot(1, 0, 0) is EXPRONE
    assert OneHot(1, 0, 1) is EXPRZERO
    assert OneHot(1, 1, 0) is EXPRZERO
    assert OneHot(1, 1, 1) is EXPRZERO
    assert OneHot(a, b, c).equivalent((-a + -b) * (-a + -c) * (-b + -c) * (a + b + c))

def test_majority():
    assert Majority(0, 0, 0) is EXPRZERO
    assert Majority(0, 0, 1) is EXPRZERO
    assert Majority(0, 1, 0) is EXPRZERO
    assert Majority(0, 1, 1) is EXPRONE
    assert Majority(1, 0, 0) is EXPRZERO
    assert Majority(1, 0, 1) is EXPRONE
    assert Majority(1, 1, 0) is EXPRONE
    assert Majority(1, 1, 1) is EXPRONE
    assert Majority(a, b, c).equivalent(a * b + a * c + b * c)

def test_ops():
    # __sub__, __rsub__
    assert (a - 0) is EXPRONE
    assert (0 - a) == -a
    assert (a - 1) == a
    assert (1 - a) is EXPRONE
    assert (a - b).equivalent(a + -b)
    # xor
    assert a.xor(b).equivalent(a * -b + -a * b)
    # ite
    assert a >> 0 == -a
    assert 0 >> a is EXPRONE
    assert a >> 1 is EXPRONE
    assert 1 >> a == a
    assert (a >> b).equivalent(-a + b)
    assert s.ite(a, b).equivalent(s * a + -s * b)

def test_const():
    if MAJOR >= 3:
        assert bool(EXPRZERO) is False
        assert bool(EXPRONE) is True
    assert int(EXPRZERO) == 0
    assert int(EXPRONE) == 1
    assert str(EXPRZERO) == '0'
    assert str(EXPRONE) == '1'

    assert not EXPRZERO.support
    assert not EXPRONE.support

    assert EXPRZERO.top is None
    assert EXPRONE.top is None

    assert EXPRZERO.restrict({a: 0, b: 1, c: 0, d: 1}) is EXPRZERO
    assert EXPRONE.restrict({a: 0, b: 1, c: 0, d: 1}) is EXPRONE

    assert EXPRZERO.compose({a: 0, b: 1, c: 0, d: 1}) is EXPRZERO
    assert EXPRONE.compose({a: 0, b: 1, c: 0, d: 1}) is EXPRONE

    assert EXPRZERO.simplify() is EXPRZERO
    assert EXPRONE.simplify() is EXPRONE
    assert EXPRZERO.factor() is EXPRZERO
    assert EXPRONE.factor() is EXPRONE

    assert EXPRZERO.depth == 0
    assert EXPRONE.depth == 0

def test_var():
    # Function
    assert a.support == {a}

    assert a.restrict({a: 0}) is EXPRZERO
    assert a.restrict({a: 1}) is EXPRONE
    assert a.restrict({b: 0}) == a

    assert a.compose({a: b}) == b
    assert a.compose({b: c}) == a

    # Expression
    assert str(a) == 'a'
    assert str(X[10]) == 'x[10]'
    assert str(Y[1][2][3]) == 'y[1][2][3]'

    assert a.simplify() == a
    assert a.factor() == a
    assert a.depth == 0
    assert a.is_cnf()

    assert a.minterm_index == 1
    assert a.maxterm_index == 0

def test_comp():
    # Function
    assert (-a).support == {a}

    assert (-a).restrict({a: 0}) is EXPRONE
    assert (-a).restrict({a: 1}) is EXPRZERO
    assert (-a).restrict({b: 0}) == -a

    assert (-a).compose({a: b}) == -b
    assert (-a).compose({b: c}) == -a

    # Expression
    assert (-a).simplify() == -a
    assert (-a).factor() == -a
    assert (-a).depth == 0
    assert (-a).is_cnf()

    assert (-a).minterm_index == 0
    assert (-a).maxterm_index == 1

def test_order():
    assert EXPRZERO < EXPRONE < -a < a < -b < b

    assert EXPRZERO < EXPRONE
    assert not EXPRONE < EXPRZERO
    assert EXPRZERO < a
    assert not a < EXPRZERO
    assert EXPRZERO < -a
    assert not -a < EXPRZERO
    assert EXPRZERO < (a + b)
    assert not (a + b) < EXPRZERO
    assert EXPRONE < (a * b)
    assert not (a * b) < EXPRONE

    assert a < a + b
    assert b < a + b
    assert -a < a + b
    assert -b < a + b

    assert a + b < a + -b
    assert a + b < -a + b
    assert a + b < -a + -b
    assert a + -b < -a + b
    assert a + -b < -a + -b
    assert -a + b < -a + -b

    assert -a * -b < -a * b
    assert -a * -b < a * -b
    assert -a * -b < a * b
    assert -a * b < a * -b
    assert -a * b < a * b
    assert a * -b < a * b

    assert a * b < a * b * c

    assert X[0] < X[1] < X[10]

def test_not():
    # Function
    assert Not(-a + b).support == {a, b}

    # Expression
    assert Not(0) is EXPRONE
    assert Not(1) is EXPRZERO
    assert Not(a) == -a
    assert Not(-a) == a

    assert -(-a) == a
    assert -(-(-a)) == -a
    assert -(-(-(-a))) == a

    assert Not(a + -a) is EXPRZERO
    assert Not(a * -a) is EXPRONE

def test_or():
    # Function
    assert (-a + b).support == {a, b}

    f = -a * b * c + a * -b * c + a * b * -c
    assert f.restrict({a: 0}).equivalent(b * c)
    assert f.restrict({a: 1}).equivalent(b * -c + -b * c)
    assert f.restrict({a: 0, b: 0}) is EXPRZERO
    assert f.restrict({a: 0, b: 1}) == c
    assert f.restrict({a: 1, b: 0}) == c
    assert f.restrict({a: 1, b: 1}) == -c
    assert f.compose({a: d, b: c}).equivalent(-d * c)

    # Expression
    assert Or() is EXPRZERO
    assert Or(a) == a

    assert Or(0, 0) is EXPRZERO
    assert Or(0, 1) is EXPRONE
    assert Or(1, 0) is EXPRONE
    assert Or(1, 1) is EXPRONE

    assert Or(0, 0, 0) is EXPRZERO
    assert Or(0, 0, 1) is EXPRONE
    assert Or(0, 1, 0) is EXPRONE
    assert Or(0, 1, 1) is EXPRONE
    assert Or(1, 0, 0) is EXPRONE
    assert Or(1, 0, 1) is EXPRONE
    assert Or(1, 1, 0) is EXPRONE
    assert Or(1, 1, 1) is EXPRONE

    assert 0 + a == a
    assert a + 0 == a
    assert 1 + a is EXPRONE
    assert a + 1 is EXPRONE

    assert (0 + a + b).equivalent(a + b)
    assert (a + b + 0).equivalent(a + b)
    assert (1 + a + b) is EXPRONE
    assert (a + b + 1) is EXPRONE

    assert str(Or(a, 0, simplify=False)) == "0 + a"

    # associative
    assert str((a + b) + c + d) == "a + b + c + d"
    assert str(a + (b + c) + d) == "a + b + c + d"
    assert str(a + b + (c + d)) == "a + b + c + d"
    assert str((a + b) + (c + d)) == "a + b + c + d"
    assert str((a + b + c) + d) == "a + b + c + d"
    assert str(a + (b + c + d)) == "a + b + c + d"
    assert str(a + (b + (c + d))) == "a + b + c + d"
    assert str(((a + b) + c) + d) == "a + b + c + d"

    # idempotent
    assert a + a == a
    assert a + a + a == a
    assert a + a + a + a == a
    assert (a + a) + (a + a) == a

    # inverse
    assert -a + a is EXPRONE
    assert a + -a is EXPRONE

def test_and():
    # Function
    assert (-a * b).support == {a, b}

    f = (-a + b + c) * (a + -b + c) * (a + b + -c)
    assert f.restrict({a: 0}).equivalent(b * c + -b * -c)
    assert f.restrict({a: 1}).equivalent(b + c)
    assert f.restrict({a: 0, b: 0}) == -c
    assert f.restrict({a: 0, b: 1}) == c
    assert f.restrict({a: 1, b: 0}) == c
    assert f.restrict({a: 1, b: 1}) is EXPRONE
    assert f.compose({a: d, b: c}).equivalent(-d + c)

    # Expression
    assert And() is EXPRONE
    assert And(a) == a

    assert And(0, 0) is EXPRZERO
    assert And(0, 1) is EXPRZERO
    assert And(1, 0) is EXPRZERO
    assert And(1, 1) is EXPRONE

    assert And(0, 0, 0) is EXPRZERO
    assert And(0, 0, 1) is EXPRZERO
    assert And(0, 1, 0) is EXPRZERO
    assert And(0, 1, 1) is EXPRZERO
    assert And(1, 0, 0) is EXPRZERO
    assert And(1, 0, 1) is EXPRZERO
    assert And(1, 1, 0) is EXPRZERO
    assert And(1, 1, 1) is EXPRONE

    assert 0 * a is EXPRZERO
    assert a * 0 is EXPRZERO
    assert 1 * a == a
    assert a * 1 == a

    assert (0 * a * b) is EXPRZERO
    assert (a * b * 0) is EXPRZERO
    assert (1 * a * b).equivalent(a * b)
    assert (a * b * 1).equivalent(a * b)

    assert str(And(a, 1, simplify=False)) == "1 * a"

    # associative
    assert str((a * b) * c * d) == "a * b * c * d"
    assert str(a * (b * c) * d) == "a * b * c * d"
    assert str(a * b * (c * d)) == "a * b * c * d"
    assert str((a * b) * (c * d)) == "a * b * c * d"
    assert str((a * b * c) * d) == "a * b * c * d"
    assert str(a * (b * c * d)) == "a * b * c * d"
    assert str(a * (b * (c * d))) == "a * b * c * d"
    assert str(((a * b) * c) * d) == "a * b * c * d"

    # idempotent
    assert a * a == a
    assert a * a * a == a
    assert a * a * a * a == a
    assert (a * a) + (a * a) == a

    # inverse
    assert -a * a is EXPRZERO
    assert a * -a is EXPRZERO

def test_xor():
    # Function
    assert Xor(-a, b).support == {a, b}

    # Expression
    assert Xor() is EXPRZERO
    assert Xor(a) == a

    assert Xor(0, 0) is EXPRZERO
    assert Xor(0, 1) is EXPRONE
    assert Xor(1, 0) is EXPRONE
    assert Xor(1, 1) is EXPRZERO

    assert Xor(0, 0, 0) is EXPRZERO
    assert Xor(0, 0, 1) is EXPRONE
    assert Xor(0, 1, 0) is EXPRONE
    assert Xor(0, 1, 1) is EXPRZERO
    assert Xor(1, 0, 0) is EXPRONE
    assert Xor(1, 0, 1) is EXPRZERO
    assert Xor(1, 1, 0) is EXPRZERO
    assert Xor(1, 1, 1) is EXPRONE

    assert Xor(0, a) == a
    assert Xor(a, 0) == a
    assert Xor(1, a) == -a
    assert Xor(a, 1) == -a

    assert Xor(a, a) is EXPRZERO
    assert Xor(a, -a) is EXPRONE
    assert Xor(-a, a) is EXPRONE

    assert str(Xor(a, 0, simplify=False)) == "0 \u2295 a"

def test_xnor():
    # Function
    assert Xnor(-a, b).support == {a, b}

    # Expression
    assert Xnor() is EXPRONE
    assert Xnor(a) == -a

    assert Xnor(0, 0) is EXPRONE
    assert Xnor(0, 1) is EXPRZERO
    assert Xnor(1, 0) is EXPRZERO
    assert Xnor(1, 1) is EXPRONE

    assert Xnor(0, 0, 0) is EXPRONE
    assert Xnor(0, 0, 1) is EXPRZERO
    assert Xnor(0, 1, 0) is EXPRZERO
    assert Xnor(0, 1, 1) is EXPRONE
    assert Xnor(1, 0, 0) is EXPRZERO
    assert Xnor(1, 0, 1) is EXPRONE
    assert Xnor(1, 1, 0) is EXPRONE
    assert Xnor(1, 1, 1) is EXPRZERO

    assert Xnor(0, a) == -a
    assert Xnor(a, 0) == -a
    assert Xnor(1, a) == a
    assert Xnor(a, 1) == a

    assert Xnor(a, a) is EXPRONE
    assert Xnor(a, -a) is EXPRZERO
    assert Xnor(-a, a) is EXPRZERO

    assert str(Xnor(a, 0, simplify=False)) == "0 \u2299 a"

def test_equal():
    # Function
    assert Equal(-a, b).support == {a, b}

    # Expression
    assert Equal() is EXPRONE
    assert Equal(a) is EXPRONE

    assert Equal(0, 0) is EXPRONE
    assert Equal(0, 1) is EXPRZERO
    assert Equal(1, 0) is EXPRZERO
    assert Equal(1, 1) is EXPRONE

    assert Equal(0, 0, 0) is EXPRONE
    assert Equal(0, 0, 1) is EXPRZERO
    assert Equal(0, 1, 0) is EXPRZERO
    assert Equal(0, 1, 1) is EXPRZERO
    assert Equal(1, 0, 0) is EXPRZERO
    assert Equal(1, 0, 1) is EXPRZERO
    assert Equal(1, 1, 0) is EXPRZERO
    assert Equal(1, 1, 1) is EXPRONE

    assert Equal(0, a) == -a
    assert Equal(a, 0) == -a
    assert Equal(1, a) == a
    assert Equal(a, 1) == a

    assert Equal(a, a) is EXPRONE
    assert Equal(a, -a) is EXPRZERO
    assert Equal(-a, a) is EXPRZERO

    assert Equal(a, b, c).factor(conj=False).equivalent(-a * -b * -c + a * b * c)
    assert Equal(a, b, c).factor(conj=True).equivalent(-a * -b * -c + a * b * c)

def test_unequal():
    # Function
    assert Unequal(-a, b).support == {a, b}

    # Expression
    assert Unequal() is EXPRZERO
    assert Unequal(a) is EXPRZERO

    assert Unequal(0, 0) is EXPRZERO
    assert Unequal(0, 1) is EXPRONE
    assert Unequal(1, 0) is EXPRONE
    assert Unequal(1, 1) is EXPRZERO

    assert Unequal(0, 0, 0) is EXPRZERO
    assert Unequal(0, 0, 1) is EXPRONE
    assert Unequal(0, 1, 0) is EXPRONE
    assert Unequal(0, 1, 1) is EXPRONE
    assert Unequal(1, 0, 0) is EXPRONE
    assert Unequal(1, 0, 1) is EXPRONE
    assert Unequal(1, 1, 0) is EXPRONE
    assert Unequal(1, 1, 1) is EXPRZERO

    assert Unequal(0, a) == a
    assert Unequal(a, 0) == a
    assert Unequal(1, a) == -a
    assert Unequal(a, 1) == -a

    assert Unequal(a, a) is EXPRZERO
    assert Unequal(a, -a) is EXPRONE
    assert Unequal(-a, a) is EXPRONE

    assert Unequal(a, b, c).factor(conj=False).equivalent((-a + -b + -c) * (a + b + c))
    assert Unequal(a, b, c).factor(conj=True).equivalent((-a + -b + -c) * (a + b + c))

def test_implies():
    # Function
    assert Implies(-p, q).support == {p, q}

    # Expression
    assert Implies(0, 0) is EXPRONE
    assert Implies(0, 1) is EXPRONE
    assert Implies(1, 0) is EXPRZERO
    assert Implies(1, 1) is EXPRONE

    assert Implies(0, p) is EXPRONE
    assert Implies(1, p) == p
    assert Implies(p, 0) == -p
    assert Implies(p, 1) is EXPRONE

    assert Implies(p, p) is EXPRONE
    assert Implies(p, -p) == -p
    assert Implies(-p, p) == p

    assert str(p >> q) == "p \u21D2 q"
    assert str((a * b) >> (c + d)) == "a * b \u21D2 c + d"

    assert (p >> q).restrict({p: 0}) is EXPRONE
    assert (p >> q).compose({q: a}).equivalent(p >> a)
    assert Not(p >> q).equivalent(p * -q)
    assert ((a * b) >> (c + d)).depth == 2

    f = Implies(p, 1, simplify=False)
    assert str(f) == "p \u21D2 1"

def test_ite():
    # Function
    assert ITE(s, -a, b).support == {s, a, b}

    # Expression
    assert ITE(0, 0, 0) is EXPRZERO
    assert ITE(0, 0, 1) is EXPRONE
    assert ITE(0, 1, 0) is EXPRZERO
    assert ITE(0, 1, 1) is EXPRONE
    assert ITE(1, 0, 0) is EXPRZERO
    assert ITE(1, 0, 1) is EXPRZERO
    assert ITE(1, 1, 0) is EXPRONE
    assert ITE(1, 1, 1) is EXPRONE

    assert ITE(0, 0, b) == b
    assert ITE(0, a, 0) is EXPRZERO
    assert ITE(0, 1, b) == b
    assert ITE(0, a, 1) is EXPRONE
    assert ITE(1, 0, b) is EXPRZERO
    assert ITE(1, a, 0) == a
    assert ITE(1, 1, b) is EXPRONE
    assert ITE(1, a, 1) == a

    assert ITE(s, 0, 0) is EXPRZERO
    assert ITE(s, 0, 1) == -s
    assert ITE(s, 1, 0) == s
    assert ITE(s, 1, 1) is EXPRONE
    assert ITE(s, 0, b).equivalent(-s * b)
    assert ITE(s, a, 0).equivalent(s * a)
    assert ITE(s, 1, b).equivalent(s + b)
    assert ITE(s, a, 1).equivalent(-s + a)

    assert ITE(s, -a, -a) == -a
    assert ITE(s, a, a) == a

    assert str(ITE(s, a, b)) == "s ? a : b"
    assert str(ITE(s, a * b, c + d)) == "s ? a * b : c + d"

    assert ITE(s, a, b).restrict({a: 1, b: 1}) is EXPRONE
    assert ITE(s, a, b).compose({a: b, b: a}).equivalent(s * b + -s * a)
    assert ITE(s, a * b, c + d).depth == 3

    f = ITE(s, 1, 1, simplify=False)
    assert str(f) == "s ? 1 : 1"

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

def test_expand():
    assert a.expand() == a

    f = a.expand(b)
    assert len(f.args) == 2 and f.equivalent(a)

    f = a.expand([b, c])
    assert len(f.args) == 4 and f.equivalent(a)

    assert a.expand(conj=True) == a

    f = a.expand(b, conj=True)
    assert len(f.args) == 2 and f.equivalent(a)

    f = a.expand([b, c], conj=True)
    assert len(f.args) == 4 and f.equivalent(a)

def test_satisfy():
    # Typical cases
    f = a * -b * c * -d
    assert EXPRZERO.satisfy_one() is None
    assert EXPRONE.satisfy_one() == {}
    assert f.satisfy_one() == {a: 1, b: 0, c: 1, d: 0}
    assert f.satisfy_one() == {a: 1, b: 0, c: 1, d: 0}

    # PLE solution
    f = (a + b + c) * (-a + -b + c)
    assert f.satisfy_one() == {a: 0, b: 0, c: 1}

    points = [p for p in Xor(a, b, c).satisfy_all()]
    assert points == [
        {a: 0, b: 0, c: 1},
        {a: 0, b: 1, c: 0},
        {a: 1, b: 0, c: 0},
        {a: 1, b: 1, c: 1},
    ]
    assert Xor(a, b, c).satisfy_count() == 4

def test_depth():
    assert (a + b).depth == 1
    assert (a + (b * c)).depth == 2
    assert (a + (b * (c + d))).depth == 3

    assert (a * b).depth == 1
    assert (a * (b + c)).depth == 2
    assert (a * (b + (c * d))).depth == 3

    assert Not(a + b).depth == 1
    assert Not(a + (b * c)).depth == 2
    assert Not(a + (b * (c + d))).depth == 3

    assert Xor(a, b, c).depth == 2
    assert Xor(a, b, c + d).depth == 3
    assert Xor(a, b, c + Xor(d, e)).depth == 5

    assert Equal(a, b, c).depth == 2
    assert Equal(a, b, c + d).depth == 3
    assert Equal(a, b, c + Xor(d, e)).depth == 5

    assert Implies(p, q).depth == 1
    assert Implies(p, a + b).depth == 2
    assert Implies(p, Xor(a, b)).depth == 3

    assert ITE(s, a, b).depth == 2
    assert ITE(s, a + b, b).depth == 3
    assert ITE(s, a + b, Xor(a, b)).depth == 4

def test_nf():
    f = Xor(a, b, c)
    g = a * b + a * c + b * c

    assert str(f.to_dnf()) == "a' * b' * c + a' * b * c' + a * b' * c' + a * b * c"
    assert str(f.to_cnf()) == "(a + b + c) * (a + b' + c') * (a' + b + c') * (a' + b' + c)"

    assert str(g.to_cdnf()) == "a' * b * c + a * b' * c + a * b * c' + a * b * c"
    assert str(g.to_ccnf()) == "(a + b + c) * (a + b + c') * (a + b' + c) * (a' + b + c)"

def test_is_nf():
    assert (a * b * c).is_cnf()
    assert (a * (b + c) * (c + d)).is_cnf()
    assert not ((a + b) * (b + c * d)).is_cnf()

def test_dpllif():
    assert a.bcp() == (frozenset(), frozenset([a.uniqid]))
    assert a.ple() == (frozenset(), frozenset([a.uniqid]))
    assert (-a).bcp() == (frozenset([a.uniqid]), frozenset())
    assert (-a).ple() == (frozenset([a.uniqid]), frozenset())

def test_complete_sum():
    v, w, x, y, z = map(exprvar, 'vwxyz')
    f = -v*x*y*z + -v*-w*x + -v*-x*-z + -v*w*x*z + -w*y*-z + v*-w*z + v*w*-x*z
    cs = -v*-w*x + v*-w*y + -v*-w*-z + v*-w*z + -v*-x*-z + -v*x*z + v*-x*z + -w*x*y + -w*x*z + -w*y*-z
    assert str(f.complete_sum()) == str(cs)
