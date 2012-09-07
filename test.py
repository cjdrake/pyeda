"""
Test Module
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved."

# standard library
import random

# pyeda
from pyeda.expr import (
    var,
    Not,
    Or, And,
    Xor, Xnor,
    factor
)

from pyeda.vexpr import (
    bitvec, sbitvec,
    int2vec, uint2vec
)

a, b, c, d, e = map(var, "abcde")

def test_truth():
    assert 6 * 9, int("42", 13)

def test_literal():
    c0 = var("c", 0)
    c1 = var("c", 1)
    c2 = var("c", 2)
    c10 = var("c", 10)

    # __str__
    assert str(-a) == "a'"
    assert str(a) == "a"
    assert str(c0) == "c[0]"
    assert str(-c0) == "c[0]'"
    assert str(c1) == "c[1]"
    assert str(-c1) == "c[1]'"

    # __eq__
    assert -a == -a
    assert a != -a
    assert -a != a
    assert a == a

    assert a != b
    assert b != a
    assert c0 != c1
    assert c1 != c0

    # __lt__
    assert -a < a
    assert a < b
    assert c0 < c1
    assert c1 < c10
    assert c2 < c10
    assert a < a + b
    assert b < a + b

    # name
    assert (-a).name == "a"
    assert a.name == "a"

    # index
    assert (-a).index is None
    assert a.index is None
    assert c0.index == 0
    assert c1.index == 1

    # invert
    assert (-a).invert() == a
    assert a.invert() == -a

    # support
    assert (-a).support == {a}
    assert a.support == {a}

    # restrict
    assert a.restrict({a: 0}) == 0
    assert a.restrict({a: 1}) == 1
    assert (-a).restrict({a: 0}) == 1
    assert (-a).restrict({a: 1}) == 0

    # compose
    assert a.compose({a: -b}) == -b
    assert a.compose({a: b}) == b
    assert (-a).compose({a: -b}) == b
    assert (-a).compose({a: b}) == -b

    # factor
    assert (-a).factor() == -a
    assert a.factor() == a

def test_not():
    # __str__
    assert str(-(-a + b)) == "Not(a' + b)"
    assert str(-(a + -b)) == "Not(a + b')"

    # support
    assert Not(-a + b).support == {a, b}

    # restrict
    assert Not(-a + b).restrict({a: 0}) == 0
    assert Not(-a + b).restrict({a: 1}) == -b
    assert str(-(-a + b + c).restrict({a: 1})) == "Not(b + c)"

    # factor
    assert str(Not(-a + b).factor()) == "a * b'"

def test_or():
    # __str__
    assert str(a + b) == "a + b"
    assert str(a + b + c) == "a + b + c"
    assert str(a + b + c + d) == "a + b + c + d"

    # __lt__
    assert -a < a + b
    assert  a < a + b
    assert -b < a + b
    assert  b < a + b

    assert a +  b <  a + -b # 00 < 01
    assert a +  b < -a +  b # 00 < 10
    assert a +  b < -a + -b # 00 < 11
    assert a + -b < -a +  b # 01 < 10
    assert a + -b < -a + -b # 01 < 11
    assert -a + b < -a + -b # 10 < 11

    assert a + b < a + b + c

    # support
    assert (-a + b + (-c * d)).support == {a, b, c, d}

    # restrict
    f = -a * b * c + a * -b * c + a * b * -c
    fa0, fa1 = f.restrict({a: 0}), f.restrict({a: 1})
    assert str(fa0) == "b * c"
    assert str(fa1) == "b' * c + b * c'"

    assert f.restrict({a: 0, b: 0}) == 0
    assert f.restrict({a: 0, b: 1}) == c
    assert f.restrict({a: 1, b: 0}) == c
    assert f.restrict({a: 1, b: 1}) == -c

    # factor
    assert str(factor(a + -(b * c))) == "a + b' + c'"

def test_and():
    # __str__
    assert str(a * b) == "a * b"
    assert str(a * b * c) == "a * b * c"
    assert str(a * b * c * d) == "a * b * c * d"

    # __lt__
    assert -a < a * b
    assert  a < a * b
    assert -b < a * b
    assert  b < a * b

    assert -a * -b < -a * b # 00 < 01
    assert -a * -b < a * -b # 00 < 10
    assert -a * -b < a *  b # 00 < 11
    assert -a *  b < a * -b # 01 < 10
    assert -a *  b < a *  b # 01 < 11
    assert a *  -b < a *  b # 10 < 11

    assert a * b < a * b * c

    # support
    assert (-a * b * (-c + d)).support == {a, b, c, d}

    # restrict
    f = (-a + b + c) * (a + -b + c) * (a + b + -c)
    fa0, fa1 = f.restrict({a: 0}), f.restrict({a: 1})
    assert str(fa0) == "(b + c') * (b' + c)"
    assert str(fa1) == "b + c"

    assert f.restrict({a: 0, b: 0}) == -c
    assert f.restrict({a: 0, b: 1}) == c
    assert f.restrict({a: 1, b: 0}) == c
    assert f.restrict({a: 1, b: 1}) == 1

    # factor
    assert str(factor(a * -(b + c))) == "a * b' * c'"

def test_absorb():
    assert str((a * b + a * b).absorb()) == "a * b"
    assert (a * (a + b)).absorb() == a
    assert ((a + b) * a).absorb() == a
    assert (-a * (-a + b)).absorb() == -a
    assert str((a * b * (a + c)).absorb()) == "a * b"
    assert str((a * b * (a + c) * (a + d)).absorb()) == "a * b"
    assert str((-a * b * (-a + c)).absorb()) == "a' * b"
    assert str((-a * b * (-a + c) * (-a + d)).absorb()) == "a' * b"
    assert str((a * -b + a * -b * c).absorb()) == "a * b'"
    assert str(((a + -b) * (a + -b + c)).absorb()) == "a + b'"
    assert str(((a + -b + c) * (a + -b)).absorb()) == "a + b'"

def test_cofactors():
    f = a * b + a * c + b * c
    assert str(f.cofactors()) == "(a * b + a * c + b * c,)"
    assert str(f.cofactors(a)) == "(b * c, b + c + b * c)"
    assert f.cofactors([a, b]) == (0, c, c, 1)
    assert f.cofactors([a, b, c]) == (0, 0, 0, 1, 0, 1, 1, 1)
    assert str(f.smoothing(a).to_sop()) == "b + c"
    assert str(f.consensus(a).to_sop()) == "b * c"
    assert str(f.derivative(a).to_sop()) == "b' * c + b * c'"

def test_unate():
    f = a + b + -c
    assert not f.is_neg_unate(a)
    assert not f.is_neg_unate(b)
    assert f.is_neg_unate(c)
    assert f.is_pos_unate(a)
    assert f.is_pos_unate(b)
    assert not f.is_pos_unate(c)
    assert not f.is_binate(a)
    assert not f.is_binate(b)
    assert not f.is_binate(c)
    assert f.is_binate()

    g = a * b + a * -c + b * -c
    assert g.is_pos_unate(a)
    assert g.is_pos_unate(b)
    assert g.is_neg_unate(c)

def test_rcadd():
    A, B = bitvec("A", 8), bitvec("B", 8)
    S, C = A.ripple_carry_add(B)
    S.append(C[-1])
    for i in range(64):
        ra = random.randint(0, 2**8-1)
        rb = random.randint(0, 2**8-1)
        d = {A: uint2vec(ra, 8), B: uint2vec(rb, 8)}
        assert int(A.vrestrict(d)) == ra
        assert int(B.vrestrict(d)) == rb
        assert int(S.vrestrict(d)) == ra + rb

    A, B = sbitvec("A", 8), sbitvec("B", 8)
    S, C = A.ripple_carry_add(B)
    for i in range(64):
        ra = random.randint(-2**6, 2**6-1)
        rb = random.randint(-2**6, 2**6-1)
        d = {A: int2vec(ra, 8), B: int2vec(rb, 8)}
        assert int(A.vrestrict(d)) == ra
        assert int(B.vrestrict(d)) == rb
        assert int(S.vrestrict(d)) == ra + rb
