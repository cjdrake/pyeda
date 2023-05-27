"""
Test expression Boolean functions

NOTE: This was from some miscellaneous work a while ago.
      Needs to be reorganized.
"""


import pytest

from pyeda.boolalg import exprnode
from pyeda.boolalg.bfarray import exprvars
from pyeda.boolalg.expr import (ITE, And, Equal, Expression, Implies, Not, One,
                                Or, Xor, Zero, expr, exprvar)

# Common variables
a, b, c, d, e, p, q, s, w, x, y, z = map(exprvar, "abcdepqswxyz")
d1, d0 = map(exprvar, ("d1", "d0"))

xs = exprvars("x", 16)
ys = exprvars("y", 16, 16, 16)


def test_exprnode_constants():
    """Test exprnode constants"""
    assert exprnode.ZERO == 0x0
    assert exprnode.ONE == 0x1

    assert exprnode.COMP == 0x4
    assert exprnode.VAR == 0x5

    assert exprnode.OP_OR == 0x8
    assert exprnode.OP_AND == 0x9
    assert exprnode.OP_XOR == 0xA
    assert exprnode.OP_EQ == 0xB

    assert exprnode.OP_NOT == 0xC
    assert exprnode.OP_IMPL == 0xD
    assert exprnode.OP_ITE == 0xE


def test_exprnode_errors():
    """Test exprnode errors."""
    with pytest.raises(TypeError):
        exprnode.lit("invalid input")
    with pytest.raises(ValueError):
        exprnode.lit(0)
    with pytest.raises(TypeError):
        exprnode.not_("invalid input")
    with pytest.raises(TypeError):
        exprnode.or_("invalid input", b.node)
    with pytest.raises(TypeError):
        exprnode.or_(a.node, "invalid input")
    with pytest.raises(TypeError):
        exprnode.and_("invalid input", b.node)
    with pytest.raises(TypeError):
        exprnode.and_(a.node, "invalid input")
    with pytest.raises(TypeError):
        exprnode.xor("invalid input", b.node)
    with pytest.raises(TypeError):
        exprnode.xor(a.node, "invalid input")
    with pytest.raises(TypeError):
        exprnode.eq("invalid input", b.node)
    with pytest.raises(TypeError):
        exprnode.eq(a.node, "invalid input")
    with pytest.raises(TypeError):
        exprnode.impl("invalid input", q.node)
    with pytest.raises(TypeError):
        exprnode.impl(p.node, "invalid input")
    with pytest.raises(TypeError):
        exprnode.ite("invalid input", d1.node, d0.node)
    with pytest.raises(TypeError):
        exprnode.ite(s.node, "invalid input", d0.node)
    with pytest.raises(TypeError):
        exprnode.ite(s.node, d1.node, "invalid input")


def test_expr():
    f = a & ~b | c ^ ~d

    assert expr(Zero) is Zero
    assert expr(a) is a
    assert expr(f) is f

    assert expr(False) is Zero
    assert expr(True) is One

    assert expr(0) is Zero
    assert expr(1) is One

    assert expr("0") is Zero
    assert expr("1") is One

    assert expr([]) is Zero
    assert expr(["foo", "bar"]) is One

    assert str(expr("a & ~b | c ^ ~d")) == "Or(And(a, ~b), Xor(c, ~d))"
    assert str(expr("a & 0 | 1 ^ ~d", simplify=False)) == "Or(And(a, 0), Xor(1, ~d))"


def test_to_ast():
    """Test exprnode.to_ast()."""
    f = (~a | b & ~c ^ d).eq(~(0 & p) >> (~q ^ 1))
    assert f.to_ast() == \
        ("eq",
            ("or",
                ("lit", -a.uniqid),
                ("xor",
                    ("and", ("lit", b.uniqid),
                            ("lit", -c.uniqid)),
                    ("lit", d.uniqid))),
            ("impl",
                ("not",
                    ("and",
                        ("lit", p.uniqid),
                        ("const", 0))),
                ("xor",
                    ("lit", -q.uniqid),
                    ("const", 1))))


def test_not():
    assert Not(0) is One
    assert Not(1) is Zero
    assert Not(~a) is a
    assert Not(a) is ~a
    assert Not(~a | a) is Zero
    assert Not(~a & a) is One

    assert str(Not(~a | b)) == "Not(Or(~a, b))"
    assert str(Not(~a | b | 0, simplify=False)) == "Not(Or(Or(~a, b), 0))"

    assert ~~a is a
    assert ~~~a is ~a
    assert ~~~~a is a


def test_or():
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

    assert Or(a, 0) is a
    assert Or(1, a) is One
    assert Or(~a, a) is One

    assert str(Or(a, 0, simplify=False)) == "Or(a, 0)"
    assert str(Or(1, a, simplify=False)) == "Or(1, a)"
    assert str(Or(~a, a, simplify=False)) == "Or(~a, a)"


def test_and():
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

    assert And(a, 0) is Zero
    assert And(1, a) is a
    assert And(~a, a) is Zero

    assert str(And(a, 0, simplify=False)) == "And(a, 0)"
    assert str(And(1, a, simplify=False)) == "And(1, a)"
    assert str(And(~a, a, simplify=False)) == "And(~a, a)"


def test_xor():
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

    assert Xor(a, 0) is a
    assert Xor(1, a) is ~a
    assert Xor(~a, a) is One

    assert str(Xor(a, 0, simplify=False)) == "Xor(a, 0)"
    assert str(Xor(1, a, simplify=False)) == "Xor(1, a)"
    assert str(Xor(~a, a, simplify=False)) == "Xor(~a, a)"


def test_equal():
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

    assert Equal(a, 0) is ~a
    assert Equal(1, a) is a
    assert Equal(~a, a) is Zero

    assert str(Equal(a, 0, simplify=False)) == "Equal(a, 0)"
    assert str(Equal(1, a, simplify=False)) == "Equal(1, a)"
    assert str(Equal(~a, a, simplify=False)) == "Equal(~a, a)"


def test_implies():
    assert Implies(0, 0) is One
    assert Implies(0, 1) is One
    assert Implies(1, 0) is Zero
    assert Implies(1, 1) is One

    assert Implies(a, 0) is ~a
    assert Implies(1, a) is a
    assert Implies(~a, a) is a

    assert str(Implies(a, 0, simplify=False)) == "Implies(a, 0)"
    assert str(Implies(1, a, simplify=False)) == "Implies(1, a)"
    assert str(Implies(~a, a, simplify=False)) == "Implies(~a, a)"


def test_ite():
    assert ITE(0, 0, 0) is Zero
    assert ITE(0, 0, 1) is One
    assert ITE(0, 1, 0) is Zero
    assert ITE(0, 1, 1) is One
    assert ITE(1, 0, 0) is Zero
    assert ITE(1, 0, 1) is Zero
    assert ITE(1, 1, 0) is One
    assert ITE(1, 1, 1) is One


def test_is_zero_one():
    assert Zero.is_zero()
    assert not One.is_zero()
    assert not a.is_zero()
    assert not (~a | b).is_zero()

    assert One.is_one()
    assert not Zero.is_one()
    assert not a.is_one()
    assert not (~a | b).is_one()


def test_box():
    assert Expression.box(a) is a

    assert Expression.box(0) is Zero
    assert Expression.box(1) is One

    assert Expression.box("0") is Zero
    assert Expression.box("1") is One

    assert Expression.box([]) is Zero
    assert Expression.box(42) is One
