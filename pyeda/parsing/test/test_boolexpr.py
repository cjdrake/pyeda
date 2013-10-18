"""
Test Boolean expression parsing
"""

from pyeda.boolalg.expr import (
    exprvar, expr,
    Not, Or, And, Xor, Xnor, Equal, Unequal, Implies, ITE,
    Nor, Nand, OneHot0, OneHot, Majority,
)
from pyeda.parsing.boolexpr import BoolExprParseError

import nose

def test_expr_error():
    # incomplete expression
    nose.tools.assert_raises(BoolExprParseError, expr, "a *")
    # unexpected token
    nose.tools.assert_raises(BoolExprParseError, expr, "a ,")
    nose.tools.assert_raises(BoolExprParseError, expr, "a a")
    nose.tools.assert_raises(BoolExprParseError, expr, "a ? b ,")

def test_basic():
    a, b, c, p, q, s = map(exprvar, 'abcpqs')
    assert expr("a * -b + b * -c").equivalent(a * -b + b * -c)
    assert expr("p => q").equivalent(-p + q)
    assert expr("a <=> b").equivalent(-a * -b + a * b)
    assert expr("s ? a : b").equivalent(s * a + -s * b)
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

def test_misc():
    a, b, c = map(exprvar, 'abc')
    a0 = exprvar('a', 0)
    b0 = exprvar('b', 0)
    assert expr("a * b * c").equivalent(a * b * c)
    assert expr("a + b + c").equivalent(a + b + c)
    assert expr("a * (b + c)").equivalent(a * (b + c))
    assert expr("a + (b * c)").equivalent(a + b * c)
    assert expr("Or()").is_zero()
    assert expr("a[0] + b[0]").equivalent(a0 + b0)
