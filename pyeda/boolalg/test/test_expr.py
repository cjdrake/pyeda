"""
Test expression Boolean functions
"""


import pytest

from pyeda.boolalg.bfarray import exprvars
from pyeda.boolalg.expr import (ITE, AchillesHeel, And, Equal, Expression,
                                Implies, Majority, Mux, Nand, NHot, Nor, Not,
                                One, OneHot, OneHot0, Or, Unequal, Xnor, Xor,
                                Zero, expr, expr2dimacssat, exprvar)

a, b, c, d, e, p, q, s = map(exprvar, "abcdepqs")

X = exprvars("x", 16)
Y = exprvars("y", 16, 16, 16)


def test_misc():
    f = a & b | a & c | b & c

    assert f.smoothing(a).equivalent(b | c)
    assert f.consensus(a).equivalent(b & c)
    assert f.derivative(a).equivalent(b & ~c | ~b & c)


def test_issue81():
    # Or(x) = x
    assert str(Or(Or(a, b))) == "Or(a, b)"
    assert str(Or(And(a, b))) == "And(a, b)"
    assert str(Or(Nor(a, b))) == "Not(Or(a, b))"
    assert str(Or(Nand(a, b))) == "Not(And(a, b))"
    assert str(Or(Xor(a, b))) == "Xor(a, b)"
    assert str(Or(Xnor(a, b))) == "Not(Xor(a, b))"
    # And(x) = x
    assert str(And(Or(a, b))) == "Or(a, b)"
    assert str(And(And(a, b))) == "And(a, b)"
    assert str(And(Nor(a, b))) == "Not(Or(a, b))"
    assert str(And(Nand(a, b))) == "Not(And(a, b))"
    assert str(And(Xor(a, b))) == "Xor(a, b)"
    assert str(And(Xnor(a, b))) == "Not(Xor(a, b))"
    # Nor(x) = ~x
    assert str(Nor(Or(a, b))) == "Not(Or(a, b))"
    assert str(Nor(And(a, b))) == "Not(And(a, b))"
    assert str(Nor(Nor(a, b))) == "Or(a, b)"
    assert str(Nor(Nand(a, b))) == "And(a, b)"
    assert str(Nor(Xor(a, b))) == "Not(Xor(a, b))"
    assert str(Nor(Xnor(a, b))) == "Xor(a, b)"
    # Nand(x) = ~x
    assert str(Nand(Or(a, b))) == "Not(Or(a, b))"
    assert str(Nand(And(a, b))) == "Not(And(a, b))"
    assert str(Nand(Nor(a, b))) == "Or(a, b)"
    assert str(Nand(Nand(a, b))) == "And(a, b)"
    assert str(Nand(Xor(a, b))) == "Not(Xor(a, b))"
    assert str(Nand(Xnor(a, b))) == "Xor(a, b)"
    # Xor(x) = x
    assert str(Xor(Or(a, b))) == "Or(a, b)"
    assert str(Xor(And(a, b))) == "And(a, b)"
    assert str(Xor(Nor(a, b))) == "Not(Or(a, b))"
    assert str(Xor(Nand(a, b))) == "Not(And(a, b))"
    assert str(Xor(Xor(a, b))) == "Xor(a, b)"
    assert str(Xor(Xnor(a, b))) == "Not(Xor(a, b))"
    # Xnor(x) = ~x
    assert str(Xnor(Or(a, b))) == "Not(Or(a, b))"
    assert str(Xnor(And(a, b))) == "Not(And(a, b))"
    assert str(Xnor(Nor(a, b))) == "Or(a, b)"
    assert str(Xnor(Nand(a, b))) == "And(a, b)"
    assert str(Xnor(Xor(a, b))) == "Not(Xor(a, b))"
    assert str(Xnor(Xnor(a, b))) == "Xor(a, b)"


def test_expr():
    assert expr(a) is a
    f = a & ~b | c ^ ~d
    assert expr(f) is f
    assert expr(False) is Zero
    assert expr(0) is Zero
    assert expr("0") is Zero
    assert expr([]) is Zero
    assert expr(True) is One
    assert expr(1) is One
    assert expr("1") is One
    assert expr(["foo", "bar"]) is One
    assert expr("a ^ b").to_nnf().equivalent(~a & b | a & ~b)
    assert str(expr("a ^ 0", simplify=False)) == "Xor(a, 0)"


def test_expr2dimacssat():
    with pytest.raises(ValueError):
        expr2dimacssat(Xor(0, a, simplify=False))
    ret = expr2dimacssat(Xor(a, ~b))
    assert ret in {"p satx 2\nxor(-2 1)", "p satx 2\nxor(1 -2)"}
    ret = expr2dimacssat(Xor(a, Equal(b, ~c)))
    assert ret in {"p satex 3\nxor(=(2 -3) 1)", "p satex 3\nxor(1 =(2 -3))",
                   "p satex 3\nxor(=(-3 2) 1)", "p satex 3\nxor(1 =(-3 2))"}
    ret = expr2dimacssat(Equal(a, ~b))
    assert ret in {"p sate 2\n=(1 -2)", "p sate 2\n=(-2 1)"}
    ret = expr2dimacssat(And(a, ~b))
    assert ret in {"p sat 2\n*(1 -2)", "p sat 2\n*(-2 1)"}
    ret = expr2dimacssat(Or(a, ~b))
    assert ret in {"p sat 2\n+(1 -2)", "p sat 2\n+(-2 1)"}
    ret = expr2dimacssat(Not(a | ~b))
    assert ret in {"p sat 2\n-(+(1 -2))", "p sat 2\n-(+(-2 1))"}


def test_box():
    assert Expression.box(0) is Zero
    assert Expression.box("0") is Zero
    assert Expression.box(1) is One
    assert Expression.box("1") is One
    assert Expression.box(a) is a
    assert Expression.box(42) is One


def test_nor():
    assert Nor() is One
    assert Nor(a) is ~a

    assert Nor(0, 0) is One
    assert Nor(0, 1) is Zero
    assert Nor(1, 0) is Zero
    assert Nor(1, 1) is Zero

    assert Nor(0, 0, 0) is One
    assert Nor(0, 0, 1) is Zero
    assert Nor(0, 1, 0) is Zero
    assert Nor(0, 1, 1) is Zero
    assert Nor(1, 0, 0) is Zero
    assert Nor(1, 0, 1) is Zero
    assert Nor(1, 1, 0) is Zero
    assert Nor(1, 1, 1) is Zero

    assert Nor(a, b).equivalent(~a & ~b)


def test_nand():
    assert Nand() is Zero
    assert Nand(a) is ~a

    assert Nand(0, 0) is One
    assert Nand(0, 1) is One
    assert Nand(1, 0) is One
    assert Nand(1, 1) is Zero

    assert Nand(0, 0, 0) is One
    assert Nand(0, 0, 1) is One
    assert Nand(0, 1, 0) is One
    assert Nand(0, 1, 1) is One
    assert Nand(1, 0, 0) is One
    assert Nand(1, 0, 1) is One
    assert Nand(1, 1, 0) is One
    assert Nand(1, 1, 1) is Zero

    assert Nand(a, b).equivalent(~a | ~b)


def test_onehot0():
    assert OneHot0(0, 0, 0) is One
    assert OneHot0(0, 0, 1) is One
    assert OneHot0(0, 1, 0) is One
    assert OneHot0(0, 1, 1) is Zero
    assert OneHot0(1, 0, 0) is One
    assert OneHot0(1, 0, 1) is Zero
    assert OneHot0(1, 1, 0) is Zero
    assert OneHot0(1, 1, 1) is Zero
    assert OneHot0(a, b, c, conj=False).equivalent((~a | ~b) & (~a | ~c) & (~b | ~c))
    assert OneHot0(a, b, c, conj=True).equivalent((~a | ~b) & (~a | ~c) & (~b | ~c))


def test_onehot():
    assert OneHot(0, 0, 0) is Zero
    assert OneHot(0, 0, 1) is One
    assert OneHot(0, 1, 0) is One
    assert OneHot(0, 1, 1) is Zero
    assert OneHot(1, 0, 0) is One
    assert OneHot(1, 0, 1) is Zero
    assert OneHot(1, 1, 0) is Zero
    assert OneHot(1, 1, 1) is Zero
    assert OneHot(a, b, c, conj=False).equivalent((~a | ~b) & (~a | ~c) & (~b | ~c) & (a | b | c))
    assert OneHot(a, b, c, conj=True).equivalent((~a | ~b) & (~a | ~c) & (~b | ~c) & (a | b | c))


def test_nhot():
    assert NHot(2, 0, 0, 0) is Zero
    assert NHot(2, 0, 0, 1) is Zero
    assert NHot(2, 0, 1, 0) is Zero
    assert NHot(2, 0, 1, 1) is One
    assert NHot(2, 1, 0, 0) is Zero
    assert NHot(2, 1, 0, 1) is One
    assert NHot(2, 1, 1, 0) is One
    assert NHot(2, 1, 1, 1) is Zero


def test_majority():
    assert Majority(0, 0, 0) is Zero
    assert Majority(0, 0, 1) is Zero
    assert Majority(0, 1, 0) is Zero
    assert Majority(0, 1, 1) is One
    assert Majority(1, 0, 0) is Zero
    assert Majority(1, 0, 1) is One
    assert Majority(1, 1, 0) is One
    assert Majority(1, 1, 1) is One
    assert Majority(a, b, c, conj=False).equivalent(a & b | a & c | b & c)
    assert Majority(a, b, c, conj=True).equivalent(a & b | a & c | b & c)


def test_achilles_heel():
    assert AchillesHeel(a, b).equivalent(a | b)
    assert AchillesHeel(a, b, c, d).equivalent((a | b) & (c | d))
    # expected an even number of arguments
    with pytest.raises(ValueError):
        AchillesHeel(a, b, c)


def test_mux():
    assert Mux([One] * 4, [a,b]).equivalent(One)
    assert Mux([Zero] * 4, [a,b]).equivalent(Zero)
    assert Mux(X[:4], [a,b]).equivalent(~a&~b&X[0] | a&~b&X[1] | ~a&b&X[2] | a&b&X[3])
    assert Mux(X[:2], a).equivalent(~a & X[0] | a & X[1])
    # Expected at least ? select bits
    with pytest.raises(ValueError):
        Mux(X, [a,b])


def test_ops():
    # __xor__
    assert (a ^ b).equivalent(a & ~b | ~a & b)
    # ite
    assert (a >> 0).equivalent(~a)
    assert (0 >> a).equivalent(One)
    assert (a >> 1).equivalent(One)
    assert (1 >> a).equivalent(a)
    assert (a >> b).equivalent(~a | b)


def test_const():
    assert bool(Zero) is False
    assert bool(One) is True
    assert int(Zero) == 0
    assert int(One) == 1
    assert str(Zero) == "0"
    assert str(One) == "1"

    assert not Zero.support
    assert not One.support

    assert Zero.top is None
    assert One.top is None

    assert Zero.restrict({a: 0, b: 1, c: 0, d: 1}) is Zero
    assert One.restrict({a: 0, b: 1, c: 0, d: 1}) is One

    assert Zero.compose({a: 0, b: 1, c: 0, d: 1}) is Zero
    assert One.compose({a: 0, b: 1, c: 0, d: 1}) is One

    assert Zero.simplify() is Zero
    assert One.simplify() is One
    assert Zero.to_nnf() is Zero
    assert One.to_nnf() is One

    assert Zero.depth == 0
    assert One.depth == 0


def test_var():
    # Function
    assert a.support == {a}

    assert a.restrict({a: 0}) is Zero
    assert a.restrict({a: 1}) is One
    assert a.restrict({b: 0}) == a

    assert a.compose({a: b}) == b
    assert a.compose({b: c}) == a

    # Expression
    assert str(a) == "a"
    assert str(X[10]) == "x[10]"
    assert str(Y[1,2,3]) == "y[1,2,3]"
    assert str(Y[1][2][3]) == "y[1,2,3]"

    assert a.simplify() == a
    assert a.to_nnf() == a
    assert a.depth == 0
    assert a.is_cnf()


def test_comp():
    # Function
    assert (~a).support == {a}

    assert (~a).restrict({a: 0}) is One
    assert (~a).restrict({a: 1}) is Zero
    assert (~a).restrict({b: 0}) == ~a

    assert (~a).compose({a: b}) == ~b
    assert (~a).compose({b: c}) == ~a

    # Expression
    assert (~a).simplify() == ~a
    assert (~a).to_nnf() == ~a
    assert (~a).depth == 0
    assert (~a).is_cnf()


def test_not():
    # Function
    assert Not(~a | b).support == {a, b}

    # Expression
    assert Not(0) is One
    assert Not(1) is Zero
    assert Not(a) is ~a
    assert Not(~a) is a

    assert ~(~a) is a
    assert ~(~(~a)) is ~a
    assert ~(~(~(~a))) is a

    assert Not(a | ~a) is Zero
    assert Not(a & ~a) is One


def test_or():
    # Function
    assert (~a | b).support == {a, b}

    f = ~a & b & c | a & ~b & c | a & b & ~c
    assert f.restrict({a: 0}).equivalent(b & c)
    assert f.restrict({a: 1}).equivalent(b & ~c | ~b & c)
    assert f.restrict({a: 0, b: 0}) is Zero
    assert f.restrict({a: 0, b: 1}) is c
    assert f.restrict({a: 1, b: 0}) is c
    assert f.restrict({a: 1, b: 1}) is ~c
    assert f.compose({a: d, b: c}).equivalent(~d & c)

    # Expression
    assert Or() is Zero
    assert Or(a) is a

    assert Or(0, 0) is Zero
    assert Or(0, 1) is One
    assert Or(1, 0) is One
    assert Or(1, 1) is One

    assert Or(0, 0, 0) is Zero
    assert Or(0, 0, 1) is One
    assert Or(0, 1, 0) is One
    assert Or(0, 1, 1) is One
    assert Or(1, 0, 0) is One
    assert Or(1, 0, 1) is One
    assert Or(1, 1, 0) is One
    assert Or(1, 1, 1) is One

    assert (0 | a).equivalent(a)
    assert (a | 0).equivalent(a)
    assert (1 | a).equivalent(One)
    assert (a | 1).equivalent(One)

    assert (0 | a | b).equivalent(a | b)
    assert (a | b | 0).equivalent(a | b)
    assert (1 | a | b).equivalent(One)
    assert (a | b | 1).equivalent(One)

    assert str(Or(a, 0, simplify=False)) == "Or(a, 0)"

    # associative
    assert ((a | b) | c | d).equivalent(Or(a, b, c, d))
    assert (a | (b | c) | d).equivalent(Or(a, b, c, d))
    assert (a | b | (c | d)).equivalent(Or(a, b, c, d))
    assert ((a | b) | (c | d)).equivalent(Or(a, b, c, d))
    assert ((a | b | c) | d).equivalent(Or(a, b, c, d))
    assert (a | (b | c | d)).equivalent(Or(a, b, c, d))
    assert (a | (b | (c | d))).equivalent(Or(a, b, c, d))
    assert (((a | b) | c) | d).equivalent(Or(a, b, c, d))

    # idempotent
    assert (a | a).equivalent(a)
    assert (a | a | a).equivalent(a)
    assert (a | a | a | a).equivalent(a)
    assert ((a | a) | (a | a)).equivalent(a)

    # inverse
    assert (~a | a).equivalent(One)
    assert (a | ~a).equivalent(One)


def test_and():
    # Function
    assert (~a & b).support == {a, b}

    f = (~a | b | c) & (a | ~b | c) & (a | b | ~c)
    assert f.restrict({a: 0}).equivalent(b & c | ~b & ~c)
    assert f.restrict({a: 1}).equivalent(b | c)
    assert f.restrict({a: 0, b: 0}) == ~c
    assert f.restrict({a: 0, b: 1}) == c
    assert f.restrict({a: 1, b: 0}) == c
    assert f.restrict({a: 1, b: 1}) is One
    assert f.compose({a: d, b: c}).equivalent(~d | c)

    # Expression
    assert And() is One
    assert And(a) is a

    assert And(0, 0) is Zero
    assert And(0, 1) is Zero
    assert And(1, 0) is Zero
    assert And(1, 1) is One

    assert And(0, 0, 0) is Zero
    assert And(0, 0, 1) is Zero
    assert And(0, 1, 0) is Zero
    assert And(0, 1, 1) is Zero
    assert And(1, 0, 0) is Zero
    assert And(1, 0, 1) is Zero
    assert And(1, 1, 0) is Zero
    assert And(1, 1, 1) is One

    assert (0 & a).equivalent(Zero)
    assert (a & 0).equivalent(Zero)
    assert (1 & a).equivalent(a)
    assert (a & 1).equivalent(a)

    assert (0 & a & b).equivalent(Zero)
    assert (a & b & 0).equivalent(Zero)
    assert (1 & a & b).equivalent(a & b)
    assert (a & b & 1).equivalent(a & b)

    assert str(And(a, 1, simplify=False)) == "And(a, 1)"

    # associative
    assert ((a & b) & c & d).equivalent(And(a, b, c, d))
    assert (a & (b & c) & d).equivalent(And(a, b, c, d))
    assert (a & b & (c & d)).equivalent(And(a, b, c, d))
    assert ((a & b) & (c & d)).equivalent(And(a, b, c, d))
    assert ((a & b & c) & d).equivalent(And(a, b, c, d))
    assert (a & (b & c & d)).equivalent(And(a, b, c, d))
    assert (a & (b & (c & d))).equivalent(And(a, b, c, d))
    assert (((a & b) & c) & d).equivalent(And(a, b, c, d))

    # idempotent
    assert (a & a).equivalent(a)
    assert (a & a & a).equivalent(a)
    assert (a & a & a & a).equivalent(a)
    assert ((a & a) | (a & a)).equivalent(a)

    # inverse
    assert (~a & a).equivalent(Zero)
    assert (a & ~a).equivalent(Zero)


def test_xor():
    # Function
    assert Xor(~a, b).support == {a, b}

    # Expression
    assert Xor() is Zero
    assert Xor(a) is a

    assert Xor(0, 0) is Zero
    assert Xor(0, 1) is One
    assert Xor(1, 0) is One
    assert Xor(1, 1) is Zero

    assert Xor(0, 0, 0) is Zero
    assert Xor(0, 0, 1) is One
    assert Xor(0, 1, 0) is One
    assert Xor(0, 1, 1) is Zero
    assert Xor(1, 0, 0) is One
    assert Xor(1, 0, 1) is Zero
    assert Xor(1, 1, 0) is Zero
    assert Xor(1, 1, 1) is One

    assert (0 ^ a).equivalent(a)
    assert (a ^ 0).equivalent(a)
    assert (1 ^ a).equivalent(~a)
    assert (a ^ 1).equivalent(~a)

    # associative
    assert ((a ^ b) ^ c ^ d).equivalent(Xor(a, b, c, d))
    assert (a ^ (b ^ c) ^ d).equivalent(Xor(a, b, c, d))
    assert (a ^ b ^ (c ^ d)).equivalent(Xor(a, b, c, d))
    assert ((a ^ b) ^ (c ^ d)).equivalent(Xor(a, b, c, d))
    assert ((a ^ b ^ c) ^ d).equivalent(Xor(a, b, c, d))
    assert (a ^ (b ^ c ^ d)).equivalent(Xor(a, b, c, d))
    assert (a ^ (b ^ (c ^ d))).equivalent(Xor(a, b, c, d))
    assert (((a ^ b) ^ c) ^ d).equivalent(Xor(a, b, c, d))

    assert (a ^ a).equivalent(Zero)
    assert (a ^ a ^ a).equivalent(a)
    assert (a ^ a ^ a ^ a).equivalent(Zero)

    assert (a ^ ~a).equivalent(One)
    assert (~a ^ a).equivalent(One)

    assert str(Xor(a, 0, simplify=False)) == "Xor(a, 0)"


def test_xnor():
    # Function
    assert Xnor(~a, b).support == {a, b}

    # Expression
    assert Xnor() is One
    assert Xnor(a) is ~a

    assert Xnor(0, 0) is One
    assert Xnor(0, 1) is Zero
    assert Xnor(1, 0) is Zero
    assert Xnor(1, 1) is One

    assert Xnor(0, 0, 0) is One
    assert Xnor(0, 0, 1) is Zero
    assert Xnor(0, 1, 0) is Zero
    assert Xnor(0, 1, 1) is One
    assert Xnor(1, 0, 0) is Zero
    assert Xnor(1, 0, 1) is One
    assert Xnor(1, 1, 0) is One
    assert Xnor(1, 1, 1) is Zero

    assert Xnor(0, a) is ~a
    assert Xnor(a, 0) is ~a
    assert Xnor(1, a) is a
    assert Xnor(a, 1) is a

    assert Xnor(a, a) is One
    assert Xnor(a, ~a) is Zero
    assert Xnor(~a, a) is Zero

    assert str(Xnor(a, 0, simplify=False)) == "Not(Xor(a, 0))"


def test_equal():
    # Function
    assert Equal(~a, b).support == {a, b}

    # Expression
    assert Equal() is One
    assert Equal(a) is One

    assert Equal(0, 0) is One
    assert Equal(0, 1) is Zero
    assert Equal(1, 0) is Zero
    assert Equal(1, 1) is One

    assert Equal(0, 0, 0) is One
    assert Equal(0, 0, 1) is Zero
    assert Equal(0, 1, 0) is Zero
    assert Equal(0, 1, 1) is Zero
    assert Equal(1, 0, 0) is Zero
    assert Equal(1, 0, 1) is Zero
    assert Equal(1, 1, 0) is Zero
    assert Equal(1, 1, 1) is One

    assert Equal(0, a) == ~a
    assert Equal(a, 0) is ~a
    assert Equal(1, a) is a
    assert Equal(a, 1) is a

    assert Equal(a, a) is One
    assert Equal(a, ~a) is Zero
    assert Equal(~a, a) is Zero

    assert Equal(a, b, c).to_nnf().equivalent(~a & ~b & ~c | a & b & c)


def test_unequal():
    # Function
    assert Unequal(~a, b).support == {a, b}

    # Expression
    assert Unequal() is Zero
    assert Unequal(a) is Zero

    assert Unequal(0, 0) is Zero
    assert Unequal(0, 1) is One
    assert Unequal(1, 0) is One
    assert Unequal(1, 1) is Zero

    assert Unequal(0, 0, 0) is Zero
    assert Unequal(0, 0, 1) is One
    assert Unequal(0, 1, 0) is One
    assert Unequal(0, 1, 1) is One
    assert Unequal(1, 0, 0) is One
    assert Unequal(1, 0, 1) is One
    assert Unequal(1, 1, 0) is One
    assert Unequal(1, 1, 1) is Zero

    assert Unequal(0, a) is a
    assert Unequal(a, 0) is a
    assert Unequal(1, a) is ~a
    assert Unequal(a, 1) is ~a

    assert Unequal(a, a) is Zero
    assert Unequal(a, ~a) is One
    assert Unequal(~a, a) is One

    assert Unequal(a, b, c).to_nnf().equivalent((~a | ~b | ~c) & (a | b | c))


def test_implies():
    # Function
    assert Implies(~p, q).support == {p, q}

    # Expression
    assert Implies(0, 0) is One
    assert Implies(0, 1) is One
    assert Implies(1, 0) is Zero
    assert Implies(1, 1) is One

    assert Implies(0, p) is One
    assert Implies(1, p) is p
    assert Implies(p, 0) is ~p
    assert Implies(p, 1) is One

    assert Implies(p, p) is One
    assert Implies(p, ~p) == ~p
    assert Implies(~p, p) == p

    assert str(p >> q) == "Implies(p, q)"
    assert str((a & b) >> (c | d)) == "Implies(And(a, b), Or(c, d))"

    assert (p >> q).restrict({p: 0}) is One
    assert (p >> q).compose({q: a}).equivalent(p >> a)
    assert Not(p >> q).equivalent(p & ~q)
    assert ((a & b) >> (c | d)).depth == 2

    f = Implies(p, 1, simplify=False)
    assert str(f) == "Implies(p, 1)"

    assert Implies(p, q).to_nnf().equivalent(~p | q)


def test_ite():
    # Function
    assert ITE(s, ~a, b).support == {s, a, b}

    # Expression
    assert ITE(0, 0, 0) is Zero
    assert ITE(0, 0, 1) is One
    assert ITE(0, 1, 0) is Zero
    assert ITE(0, 1, 1) is One
    assert ITE(1, 0, 0) is Zero
    assert ITE(1, 0, 1) is Zero
    assert ITE(1, 1, 0) is One
    assert ITE(1, 1, 1) is One

    assert ITE(0, 0, b) is b
    assert ITE(0, a, 0) is Zero
    assert ITE(0, 1, b) is b
    assert ITE(0, a, 1) is One
    assert ITE(1, 0, b) is Zero
    assert ITE(1, a, 0) is a
    assert ITE(1, 1, b) is One
    assert ITE(1, a, 1) is a

    assert ITE(s, 0, 0) is Zero
    assert ITE(s, 0, 1) is ~s
    assert ITE(s, 1, 0) is s
    assert ITE(s, 1, 1) is One
    assert ITE(s, 0, b).equivalent(~s & b)
    assert ITE(s, a, 0).equivalent(s & a)
    assert ITE(s, 1, b).equivalent(s | b)
    assert ITE(s, a, 1).equivalent(~s | a)

    assert ITE(s, ~a, ~a) is ~a
    assert ITE(s, a, a) is a

    assert str(ITE(s, a, b)) == "ITE(s, a, b)"
    assert str(ITE(s, a & b, c | d)) == "ITE(s, And(a, b), Or(c, d))"

    assert ITE(s, a, b).restrict({a: 1, b: 1}) is One
    assert ITE(s, a, b).compose({a: b, b: a}).equivalent(s & b | ~s & a)
    assert ITE(s, a & b, c | d).depth == 2

    f = ITE(s, 1, 1, simplify=False)
    assert str(f) == "ITE(s, 1, 1)"


def test_expand():
    assert a.expand() is a

    f = a.expand(b)
    assert len(f.xs) == 2 and f.equivalent(a)

    f = a.expand([b, c])
    assert len(f.xs) == 4 and f.equivalent(a)

    assert a.expand(conj=True) == a

    f = a.expand(b, conj=True)
    assert len(f.xs) == 2 and f.equivalent(a)

    f = a.expand([b, c], conj=True)
    assert len(f.xs) == 4 and f.equivalent(a)


def test_satisfy():
    # Typical cases
    f = a & ~b & c & ~d
    assert Zero.satisfy_one() is None
    assert One.satisfy_one() == {}
    assert f.satisfy_one() == {a: 1, b: 0, c: 1, d: 0}

    # PLE solution
    f = (a | b | c) & (~a | ~b | c)
    assert f.satisfy_one() == {a: 0, b: 0, c: 1}

    points = list(Xor(a, b, c).satisfy_all())
    assert points == [
        {a: 0, b: 0, c: 1},
        {a: 0, b: 1, c: 0},
        {a: 1, b: 0, c: 0},
        {a: 1, b: 1, c: 1},
    ]
    assert Xor(a, b, c).satisfy_count() == 4

    # CNF SAT UNSAT
    sat = Majority(a, b, c, conj=True)
    unsat = Zero.expand([a, b, c], conj=True)
    assert unsat.satisfy_one() is None
    assert not list(unsat.satisfy_all())
    assert list(sat.satisfy_all())

    # Assumptions
    f = OneHot(a, b, c)
    g = Xor(a, b, c)
    with a, ~b:
        assert f.satisfy_one() == {a: 1, b: 0, c: 0}
        assert g.satisfy_one() == {a: 1, b: 0, c: 0}
    with a & ~b:
        assert f.satisfy_one() == {a: 1, b: 0, c: 0}
        assert g.satisfy_one() == {a: 1, b: 0, c: 0}


def test_depth():
    assert (a | b).depth == 1
    assert (a | (b & c)).depth == 2
    assert (a | (b & (c | d))).depth == 3

    assert (a & b).depth == 1
    assert (a & (b | c)).depth == 2
    assert (a & (b | (c & d))).depth == 3

    assert Not(a | b).depth == 2
    assert Not(a | (b & c)).depth == 3
    assert Not(a | (b & (c | d))).depth == 4

    assert Xor(a, b, c).depth == 1
    assert Xor(a, b, c | d).depth == 2
    assert Xor(a, b, c | Xor(d, e)).depth == 3

    assert Equal(a, b, c).depth == 1
    assert Equal(a, b, c | d).depth == 2
    assert Equal(a, b, c | Xor(d, e)).depth == 3

    assert Implies(p, q).depth == 1
    assert Implies(p, a | b).depth == 2
    assert Implies(p, Xor(a, b)).depth == 2

    assert ITE(s, a, b).depth == 1
    assert ITE(s, a | b, b).depth == 2
    assert ITE(s, a | b, Xor(a, b)).depth == 2


def test_nf():
    f = a ^ b ^ c
    #g = a & b | a & c | b & c

    f_dnf = f.to_dnf()
    f_cnf = f.to_cnf()

    assert f_dnf.equivalent(Or(And(~a, ~b, c), And(~a, b, ~c), And(a, ~b, ~c), And(a, b, c)))
    assert f_cnf.equivalent(And(Or(a, b, c), Or(a, ~b, ~c), Or(~a, b, ~c), Or(~a, ~b, c)))


def test_is_nf():
    assert And(a, b, c).is_cnf()
    assert And(a, (b | c), (c | d)).is_cnf()
    assert not And((a | b), (b | c & d)).is_cnf()


def test_complete_sum():
    v, w, x, y, z = map(exprvar, "vwxyz")
    f = ~v&x&y&z | ~v&~w&x | ~v&~x&~z | ~v&w&x&z | ~w&y&~z | v&~w&z | v&w&~x&z
    cs = ~v&~w&x | v&~w&y | ~v&~w&~z | v&~w&z | ~v&~x&~z | ~v&x&z | v&~x&z | ~w&x&y | ~w&x&z | ~w&y&~z
    assert f.complete_sum().equivalent(cs)
