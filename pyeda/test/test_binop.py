"""
Test binary operators
"""

from pyeda.binop import *
from pyeda.expr import var

def test_all_ops():
    a, b = map(var, 'ab')
    assert apply2(OP_ZERO, a, b) == 0
    assert apply2(OP_AND, a, b).equivalent(a * b)
    assert apply2(OP_GT, a, b).equivalent(a * -b)
    assert apply2(OP_FST, a, b).equivalent(a)
    assert apply2(OP_LT, a, b).equivalent(-a * b)
    assert apply2(OP_SND, a, b).equivalent(b)
    assert apply2(OP_XOR, a, b).equivalent(-a * b + a * -b)
    assert apply2(OP_OR, a, b).equivalent(a + b)
    assert apply2(OP_NOR, a, b).equivalent(-(a + b))
    assert apply2(OP_XNOR, a, b).equivalent(-a * -b + a * b)
    assert apply2(OP_NSND, a, b).equivalent(-b)
    assert apply2(OP_GTE, a, b).equivalent(a + -b)
    assert apply2(OP_NFST, a, b).equivalent(-a)
    assert apply2(OP_LTE, a, b).equivalent(-a + b)
    assert apply2(OP_NAND, a, b).equivalent(-(a * b))
    assert apply2(OP_ONE, a, b) == 1
