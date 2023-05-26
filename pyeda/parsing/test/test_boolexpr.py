"""
Test Boolean expression parsing
"""


import pytest

from pyeda.boolalg.expr import (
    exprvar, expr,
    Not, Or, And, Xor, Xnor, Equal, Unequal, Implies, ITE,
    Nor, Nand, OneHot0, OneHot, Majority, AchillesHeel,
)
from pyeda.parsing.boolexpr import Error


def test_expr_error():
    # lexical error
    with pytest.raises(Error):
        expr("#a")
    # incomplete expression
    with pytest.raises(Error):
        expr("a &")
    # unexpected token
    with pytest.raises(Error):
        expr("a ,")
    with pytest.raises(Error):
        expr("a a")
    with pytest.raises(Error):
        expr("a ? b ,")
    with pytest.raises(Error):
        expr("a | 42")


def test_basic():
    a, b, c, d, p, q, s = map(exprvar, "abcdpqs")
    assert expr("a & ~b | b & ~c").equivalent(a & ~b | b & ~c)
    assert expr("p => q").equivalent(~p | q)
    assert expr("a <=> b").equivalent(~a & ~b | a & b)
    assert expr("s ? a : b").equivalent(s & a | ~s & b)
    assert expr("Not(a)").equivalent(Not(a))
    assert expr("Or(a, b, c)").equivalent(Or(a, b, c))
    assert expr("And(a, b, c)").equivalent(And(a, b, c))
    assert expr("Xor(a, b, c)").equivalent(Xor(a, b, c))
    assert expr("Xnor(a, b, c)").equivalent(Xnor(a, b, c))
    assert expr("Equal(a, b, c)").equivalent(Equal(a, b, c))
    assert expr("Unequal(a, b, c)").equivalent(Unequal(a, b, c))
    assert expr("Implies(p, q)").equivalent(Implies(p, q))
    assert expr("ITE(s, a, b)").equivalent(ITE(s, a, b))
    assert expr("Nor(a, b, c)").equivalent(Nor(a, b, c))
    assert expr("Nand(a, b, c)").equivalent(Nand(a, b, c))
    assert expr("OneHot0(a, b, c)").equivalent(OneHot0(a, b, c))
    assert expr("OneHot(a, b, c)").equivalent(OneHot(a, b, c))
    assert expr("Majority(a, b, c)").equivalent(Majority(a, b, c))
    assert expr("AchillesHeel(a, b, c, d)").equivalent(AchillesHeel(a, b, c, d))


def test_misc():
    a, b, c = map(exprvar, "abc")
    assert expr("a & b & c").equivalent(a & b & c)
    assert expr("a ^ b ^ c").equivalent(a ^ b ^ c)
    assert expr("a | b | c").equivalent(a | b | c)
    assert expr("a & (b | c)").equivalent(a & (b | c))
    assert expr("a | (b & c)").equivalent(a | b & c)
    assert expr("Or()").is_zero()

    a_0 = exprvar("a", 0)
    b_a = exprvar(("a", "b"))
    a_0_1 = exprvar("a", (0, 1))
    b_a_0_1 = exprvar(("a", "b"), (0, 1))
    assert expr("a[0] | b.a | a[0,1] | b.a[0,1]").equivalent(a_0 | b_a | a_0_1 | b_a_0_1)
