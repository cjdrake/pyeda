"""
Test Module
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved."

# standard library
import random

# pyeda
from pyeda.boolalg import (
    var, vec, svec,
    Zero, One,
    Buf, Not,
    Or, Nor, And, Nand,
    Xor, Xnor,
    Implies,
    factor, simplify, notf, orf, norf, andf, nandf, xorf, xnorf, impliesf,
    cube_sop, cube_pos,
    int2vec, uint2vec
)

a, b, c, d = map(var, "abcd")

def test_truth():
    assert 6 * 9, int("42", 13)

def test_number():
    assert str(Zero) == "0"
    assert str(One) == "1"

    # __eq__
    for val in (Zero, False, 0, 0.0, "0"):
        assert Zero == val
        assert One != val
    for val in (One, True, 1, 1.0, "1"):
        assert Zero != val
        assert One == val

    # __lt__
    assert Zero < One
    assert One > Zero
    assert Zero < a
    assert One < a
    assert Zero < a + b
    assert One < a + b

    # __bool__
    assert bool(Zero) is False
    assert bool(One) is True

    # depth
    assert Zero.depth == 1
    assert One.depth == 1

    # val
    assert Zero.val == 0
    assert One.val == 1

    # get_dual
    assert Zero.get_dual() == One
    assert One.get_dual() == Zero

    # subs
    assert Zero.subs({a: 0, b: 1}) == 0
    assert One.subs({a: 0, b: 1}) == 1

    # factor
    assert Zero.factor() == Zero
    assert One.factor() == One

    # simplify
    assert Zero.simplify() == Zero
    assert One.simplify() == One

def test_literal():
    c0 = var("c", 0)
    c1 = var("c", 1)
    c2 = var("c", 2)
    c10 = var("c", 10)

    # __len__
    assert len(-a) == 1
    assert len(a) == 1

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
    assert Zero < -a
    assert Zero < a
    assert One < -a
    assert One < a
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
    assert (-a).index == -1
    assert a.index == -1
    assert c0.index == 0
    assert c1.index == 1

    # get_dual
    assert (-a).get_dual() == a
    assert a.get_dual() == -a

    # support
    assert (-a).support == {a}
    assert a.support == {a}

    # subs
    assert a.subs({a: 0}) == 0
    assert a.subs({a: 1}) == 1
    assert a.subs({a: -b}) == -b
    assert a.subs({a: b}) == b
    assert (-a).subs({a: 0}) == 1
    assert (-a).subs({a: 1}) == 0
    assert (-a).subs({a: -b}) == b
    assert (-a).subs({a: b}) == -b

    # factor
    assert (-a).factor() == -a
    assert a.factor() == a

    # simplify
    assert (-a).simplify() == -a
    assert a.simplify() == a

def test_buf():
    assert Buf(0) == 0
    assert Buf(1) == 1
    assert Buf(-a) == -a
    assert Buf(a) == a

    assert Buf(Buf(a)) == a
    assert Buf(Buf(Buf(a))) == a
    assert Buf(Buf(Buf(Buf(a)))) == a

    # __str__
    assert str(Buf(-a + b)) == "Buf(a' + b)"
    assert str(Buf(a + -b)) == "Buf(a + b')"

    # support
    assert Buf(-a + b).support == {a, b}

    # subs
    assert Buf(-a + b).subs({a: 0}) == 1
    assert Buf(-a + b).subs({a: 1}) == b
    assert str(Buf(-a + b + c).subs({a: 1})) == "Buf(b + c)"

    # factor
    assert str(Buf(-a + b).factor()) == "a' + b"

    # simplify
    assert simplify(Buf(a + -a)) == 1
    assert simplify(Buf(a * -a)) == 0

def test_not():
    assert Not(0) == 1
    assert Not(1) == 0
    assert Not(-a) == a
    assert Not(a) == -a

    assert -(-a) == a
    assert -(-(-a)) == -a
    assert -(-(-(-a))) == a

    # __str__
    assert str(-(-a + b)) == "Not(a' + b)"
    assert str(-(a + -b)) == "Not(a + b')"

    # support
    assert Not(-a + b).support == {a, b}

    # subs
    assert Not(-a + b).subs({a: 0}) == 0
    assert Not(-a + b).subs({a: 1}) == -b
    assert str(-(-a + b + c).subs({a: 1})) == "Not(b + c)"

    # factor
    assert str(Not(-a + b).factor()) == "a * b'"

    # simplify
    assert simplify(-(a + -a)) == 0
    assert simplify(-(a * -a)) == 1

def test_or():
    assert Or() == 0
    assert Or(a) == a

    assert a + 1 == 1
    assert a + b + 1 == 1
    assert a + 0 == a

    # __len__
    assert len(a + b + c) == 3

    # __str__
    assert str(a + b) == "a + b"
    assert str(a + b + c) == "a + b + c"
    assert str(a + b + c + d) == "a + b + c + d"

    # __lt__
    assert Zero < a + b
    assert One < a + b

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

    # associative
    assert str((a + b) + c + d)   == "a + b + c + d"
    assert str(a + (b + c) + d)   == "a + b + c + d"
    assert str(a + b + (c + d))   == "a + b + c + d"
    assert str((a + b) + (c + d)) == "a + b + c + d"
    assert str((a + b + c) + d)   == "a + b + c + d"
    assert str(a + (b + c + d))   == "a + b + c + d"
    assert str(a + (b + (c + d))) == "a + b + c + d"
    assert str(((a + b) + c) + d) == "a + b + c + d"

    # depth
    assert (a + b).depth == 1
    assert (a + (b * c)).depth == 2
    assert (a + (b * (c + d))).depth == 3

    # get_dual
    assert Or.get_dual() is And

    # support
    assert (-a + b + (-c * d)).support == {a, b, c, d}

    # subs
    f = -a * b * c + a * -b * c + a * b * -c
    fa0, fa1 = f.subs({a: 0}), f.subs({a: 1})
    assert str(fa0) == "b * c"
    assert str(fa1) == "b' * c + b * c'"

    assert f.subs({a: 0, b: 0}) == 0
    assert f.subs({a: 0, b: 1}) == c
    assert f.subs({a: 1, b: 0}) == c
    assert f.subs({a: 1, b: 1}) == -c

    # factor
    assert str(factor(a + -(b * c))) == "a + b' + c'"

    # simplify
    assert simplify(-a + a) == 1
    assert simplify(-a + a + b) == 1

    assert simplify(a + a) == a
    assert simplify(a + a + a) == a
    assert simplify(a + a + a + a) == a
    assert simplify((a + a) + (a + a)) == a

    # to_csop
    f = a * b + a * c + b * c
    assert str(f.to_csop()) == "a' * b * c + a * b' * c + a * b * c' + a * b * c"

def test_and():
    assert And() == One
    assert And(a) == a

    assert a * 0 == 0
    assert a * b * 0 == 0
    assert a * 1 == a

    # __len__
    assert len(a * b * c) == 3

    # __str__
    assert str(a * b) == "a * b"
    assert str(a * b * c) == "a * b * c"
    assert str(a * b * c * d) == "a * b * c * d"

    # __lt__
    assert Zero < a * b
    assert One < a * b

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

    # associative
    assert str((a * b) * c * d)   == "a * b * c * d"
    assert str(a * (b * c) * d)   == "a * b * c * d"
    assert str(a * b * (c * d))   == "a * b * c * d"
    assert str((a * b) * (c * d)) == "a * b * c * d"
    assert str((a * b * c) * d)   == "a * b * c * d"
    assert str(a * (b * c * d))   == "a * b * c * d"
    assert str(a * (b * (c * d))) == "a * b * c * d"
    assert str(((a * b) * c) * d) == "a * b * c * d"

    # depth
    assert (a * b).depth == 1
    assert (a * (b + c)).depth == 2
    assert (a * (b + (c * d))).depth == 3

    # get_dual
    assert And.get_dual() is Or

    # support
    assert (-a * b * (-c + d)).support == {a, b, c, d}

    # subs
    f = (-a + b + c) * (a + -b + c) * (a + b + -c)
    fa0, fa1 = f.subs({a: 0}), f.subs({a: 1})
    assert str(fa0) == "(b + c') * (b' + c)"
    assert str(fa1) == "b + c"

    assert f.subs({a: 0, b: 0}) == -c
    assert f.subs({a: 0, b: 1}) == c
    assert f.subs({a: 1, b: 0}) == c
    assert f.subs({a: 1, b: 1}) == 1

    # factor
    assert str(factor(a * -(b + c))) == "a * b' * c'"

    # simplify
    assert simplify(-a * a) == 0
    assert simplify(-a * a * b) == 0

    assert simplify(a * a) == a
    assert simplify(a * a * a) == a
    assert simplify(a * a * a * a) == a
    assert simplify((a * a) + (a * a)) == a

    # to_cpos
    f = a * b + a * c + b * c
    assert str(f.to_cpos()) == "(a + b + c) * (a + b + c') * (a + b' + c) * (a' + b + c)"


def test_implies():
    assert str(a >> b) == "a => b"
    assert str(-a >> b) == "a' => b"
    assert str(a >> -b) == "a => b'"
    assert str(-a + b >> a + -b) == "a' + b => a + b'"
    assert str((-a >> b) >> (a >> -b)) == "(a' => b) => (a => b')"
    assert simplify(a >> a) == 1
    assert simplify(a >> -a) == -a
    assert simplify(-a >> a) == a
    assert (a >> 0) == -a
    assert (a >> 1) == 1
    assert (Zero >> a) == 1
    assert (One >> a) == a
    assert str(impliesf(a, b)) == "a' + b"
    assert str(factor(a >> b)) == "a' + b"

def test_nops():
    assert str(norf(a, b)) == "a' * b'"
    assert str(norf(a, b, c, d)) == "a' * b' * c' * d'"
    assert str(nandf(a, b)) == "a' + b'"
    assert str(nandf(a, b, c, d)) == "a' + b' + c' + d'"

def test_xor():
    assert Xor() == 0
    assert Xor(a) == a
    assert Xor(0, 0) == 0
    assert Xor(0, 1) == 1
    assert Xor(1, 0) == 1
    #assert Xor(1, 1) == 0
    assert str(Xor(a, b).to_sop())     == "a' * b + a * b'"
    assert str(Xnor(a, b).to_sop())    == "a' * b' + a * b"
    assert str(Xor(a, b, c).to_sop())  == "a' * b' * c + a' * b * c' + a * b' * c' + a * b * c"
    assert str(Xnor(a, b, c).to_sop()) == "a' * b' * c' + a' * b * c + a * b' * c + a * b * c'"

def test_demorgan():
    assert str(notf(a * b))  == "a' + b'"
    assert str(notf(a + b))  == "a' * b'"
    assert str(notf(a * -b)) == "a' + b"
    assert str(notf(a * -b)) == "a' + b"
    assert str(notf(-a * b)) == "a + b'"
    assert str(notf(-a * b)) == "a + b'"

    assert str(notf(a * b * c))  == "a' + b' + c'"
    assert str(notf(a + b + c))  == "a' * b' * c'"
    assert str(notf(-a * b * c)) == "a + b' + c'"
    assert str(notf(-a + b + c)) == "a * b' * c'"
    assert str(notf(a * -b * c)) == "a' + b + c'"
    assert str(notf(a + -b + c)) == "a' * b * c'"
    assert str(notf(a * b * -c)) == "a' + b' + c"
    assert str(notf(a + b + -c)) == "a' * b' * c"

def test_absorb():
    assert str(simplify(a * b + a * b)) == "a * b"
    assert simplify(a * (a + b)) == a
    assert simplify(-a * (-a + b)) == -a
    assert str(simplify(a * b * (a + c))) == "a * b"
    assert str(simplify(a * b * (a + c) * (a + d))) == "a * b"
    assert str(simplify(-a * b * (-a + c))) == "a' * b"
    assert str(simplify(-a * b * (-a + c) * (-a + d))) == "a' * b"
    assert str(simplify(a * -b + a * -b * c)) == "a * b'"
    assert str(simplify((a + -b) * (a + -b + c))) == "a + b'"

def test_cofactors():
    f = a * b + a * c + b * c
    assert str(f.cofactors()) == "[a * b + a * c + b * c]"
    assert str(f.cofactors(a)) == "[b * c, b + c + b * c]"
    assert f.cofactors(a, b) == [0, c, c, 1]
    assert f.cofactors(a, b, c) == [0, 0, 0, 1, 0, 1, 1, 1]
    assert str(f.smoothing(a)) == "b + c + b * c + b * c"
    assert str(f.consensus(a)) == "b * c * (b + c + b * c)"
    assert str(f.derivative(a).to_sop()) == "b' * c + b * c'"

def test_unate():
    f = a + b + -c
    assert f.is_pos_unate(a)
    assert f.is_pos_unate(b)
    assert f.is_neg_unate(c)
    assert not f.is_neg_unate(a)
    assert not f.is_neg_unate(b)
    assert f.is_neg_unate(c)
    assert not f.is_binate(a)
    assert not f.is_binate(b)
    assert not f.is_binate(c)
    assert f.is_binate()
    g = a * b + a * -c + b * -c
    assert f.is_pos_unate(a)
    assert f.is_pos_unate(b)
    assert f.is_neg_unate(c)

def test_cube():
    assert str(cube_sop(a, b, c)) == "a' * b' * c' + a' * b' * c + a' * b * c' + a' * b * c + a * b' * c' + a * b' * c + a * b * c' + a * b * c"
    assert str(cube_pos(a, b, c)) == "(a + b + c) * (a + b + c') * (a + b' + c) * (a + b' + c') * (a' + b + c) * (a' + b + c') * (a' + b' + c) * (a' + b' + c')"

def test_rcadd():
    A, B = vec("A", 8), vec("B", 8)
    S, C = A.ripple_carry_add(B)
    S.append(C[-1])
    for i in range(64):
        ra = random.randint(0, 2**8-1)
        rb = random.randint(0, 2**8-1)
        d = {A: uint2vec(ra, 8), B: uint2vec(rb, 8)}
        assert int(A.vsubs(d)) == ra
        assert int(B.vsubs(d)) == rb
        assert int(S.vsubs(d)) == ra + rb

    A, B = svec("A", 8), svec("B", 8)
    S, C = A.ripple_carry_add(B)
    for i in range(64):
        ra = random.randint(-2**6, 2**6-1)
        rb = random.randint(-2**6, 2**6-1)
        d = {A: int2vec(ra, 8), B: int2vec(rb, 8)}
        assert int(A.vsubs(d)) == ra
        assert int(B.vsubs(d)) == rb
        assert int(S.vsubs(d)) == ra + rb
