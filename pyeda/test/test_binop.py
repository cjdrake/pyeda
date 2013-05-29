"""
Test binary operators
"""

from pyeda.alphas import *
from pyeda.binop import *

def test_all_ops():
    assert apply2(OP_ZERO, 0, 0) == 0
    assert apply2(OP_ZERO, 0, 1) == 0
    assert apply2(OP_ZERO, 1, 0) == 0
    assert apply2(OP_ZERO, 1, 1) == 0
    assert apply2(OP_ZERO, a, 0) == 0
    assert apply2(OP_ZERO, a, 1) == 0
    assert apply2(OP_ZERO, 0, b) == 0
    assert apply2(OP_ZERO, 1, b) == 0
    assert apply2(OP_ZERO, a, b) == 0

    assert apply2(OP_AND, 0, 0) == 0
    assert apply2(OP_AND, 0, 1) == 0
    assert apply2(OP_AND, 1, 0) == 0
    assert apply2(OP_AND, 1, 1) == 1
    assert apply2(OP_AND, a, 0) == 0
    assert apply2(OP_AND, a, 1).equivalent(a)
    assert apply2(OP_AND, 0, b) == 0
    assert apply2(OP_AND, 1, b).equivalent(b)
    assert apply2(OP_AND, a, b).equivalent(a * b)

    assert apply2(OP_GT, 0, 0) == 0
    assert apply2(OP_GT, 0, 1) == 0
    assert apply2(OP_GT, 1, 0) == 1
    assert apply2(OP_GT, 1, 1) == 0
    assert apply2(OP_GT, a, 0).equivalent(a)
    assert apply2(OP_GT, a, 1) == 0
    assert apply2(OP_GT, 0, b) == 0
    assert apply2(OP_GT, 1, b).equivalent(-b)
    assert apply2(OP_GT, a, b).equivalent(a * -b)

    assert apply2(OP_FST, 0, 0) == 0
    assert apply2(OP_FST, 0, 1) == 0
    assert apply2(OP_FST, 1, 0) == 1
    assert apply2(OP_FST, 1, 1) == 1
    assert apply2(OP_FST, a, 0).equivalent(a)
    assert apply2(OP_FST, a, 1).equivalent(a)
    assert apply2(OP_FST, 0, b) == 0
    assert apply2(OP_FST, 1, b) == 1
    assert apply2(OP_FST, a, b).equivalent(a)

    assert apply2(OP_LT, 0, 0) == 0
    assert apply2(OP_LT, 0, 1) == 1
    assert apply2(OP_LT, 1, 0) == 0
    assert apply2(OP_LT, 1, 1) == 0
    assert apply2(OP_LT, a, 0) == 0
    assert apply2(OP_LT, a, 1).equivalent(-a)
    assert apply2(OP_LT, 0, b).equivalent(b)
    assert apply2(OP_LT, 1, b) == 0
    assert apply2(OP_LT, a, b).equivalent(-a * b)

    assert apply2(OP_SND, 0, 0) == 0
    assert apply2(OP_SND, 0, 1) == 1
    assert apply2(OP_SND, 1, 0) == 0
    assert apply2(OP_SND, 1, 1) == 1
    assert apply2(OP_SND, a, 0) == 0
    assert apply2(OP_SND, a, 1) == 1
    assert apply2(OP_SND, 0, b).equivalent(b)
    assert apply2(OP_SND, 1, b).equivalent(b)
    assert apply2(OP_SND, a, b).equivalent(b)

    assert apply2(OP_XOR, 0, 0) == 0
    assert apply2(OP_XOR, 0, 1) == 1
    assert apply2(OP_XOR, 1, 0) == 1
    assert apply2(OP_XOR, 1, 1) == 0
    assert apply2(OP_XOR, a, 0).equivalent(a)
    assert apply2(OP_XOR, a, 1).equivalent(-a)
    assert apply2(OP_XOR, 0, b).equivalent(b)
    assert apply2(OP_XOR, 1, b).equivalent(-b)
    assert apply2(OP_XOR, a, b).equivalent(-a * b + a * -b)

    assert apply2(OP_OR, 0, 0) == 0
    assert apply2(OP_OR, 0, 1) == 1
    assert apply2(OP_OR, 1, 0) == 1
    assert apply2(OP_OR, 1, 1) == 1
    assert apply2(OP_OR, a, 0).equivalent(a)
    assert apply2(OP_OR, a, 1) == 1
    assert apply2(OP_OR, 0, b).equivalent(b)
    assert apply2(OP_OR, 1, b) == 1
    assert apply2(OP_OR, a, b).equivalent(a + b)

    assert apply2(OP_NOR, 0, 0) == 1
    assert apply2(OP_NOR, 0, 1) == 0
    assert apply2(OP_NOR, 1, 0) == 0
    assert apply2(OP_NOR, 1, 1) == 0
    assert apply2(OP_NOR, a, 0).equivalent(-a)
    assert apply2(OP_NOR, a, 1) == 0
    assert apply2(OP_NOR, 0, b).equivalent(-b)
    assert apply2(OP_NOR, 1, b) == 0
    assert apply2(OP_NOR, a, b).equivalent(-a * -b)

    assert apply2(OP_XNOR, 0, 0) == 1
    assert apply2(OP_XNOR, 0, 1) == 0
    assert apply2(OP_XNOR, 1, 0) == 0
    assert apply2(OP_XNOR, 1, 1) == 1
    assert apply2(OP_XNOR, a, 0).equivalent(-a)
    assert apply2(OP_XNOR, a, 1).equivalent(a)
    assert apply2(OP_XNOR, 0, b).equivalent(-b)
    assert apply2(OP_XNOR, 1, b).equivalent(b)
    assert apply2(OP_XNOR, a, b).equivalent(-a * -b + a * b)

    assert apply2(OP_NSND, 0, 0) == 1
    assert apply2(OP_NSND, 0, 1) == 0
    assert apply2(OP_NSND, 1, 0) == 1
    assert apply2(OP_NSND, 1, 1) == 0
    assert apply2(OP_NSND, a, 0) == 1
    assert apply2(OP_NSND, a, 1) == 0
    assert apply2(OP_NSND, 0, b).equivalent(-b)
    assert apply2(OP_NSND, 1, b).equivalent(-b)
    assert apply2(OP_NSND, a, b).equivalent(-b)

    assert apply2(OP_GTE, 0, 0) == 1
    assert apply2(OP_GTE, 0, 1) == 0
    assert apply2(OP_GTE, 1, 0) == 1
    assert apply2(OP_GTE, 1, 1) == 1
    assert apply2(OP_GTE, a, 0) == 1
    assert apply2(OP_GTE, a, 1).equivalent(a)
    assert apply2(OP_GTE, 0, b).equivalent(-b)
    assert apply2(OP_GTE, 1, b) == 1
    assert apply2(OP_GTE, a, b).equivalent(a + -b)

    assert apply2(OP_NFST, 0, 0) == 1
    assert apply2(OP_NFST, 0, 1) == 1
    assert apply2(OP_NFST, 1, 0) == 0
    assert apply2(OP_NFST, 1, 1) == 0
    assert apply2(OP_NFST, a, 0).equivalent(-a)
    assert apply2(OP_NFST, a, 1).equivalent(-a)
    assert apply2(OP_NFST, 0, b) == 1
    assert apply2(OP_NFST, 1, b) == 0
    assert apply2(OP_NFST, a, b).equivalent(-a)

    assert apply2(OP_LTE, 0, 0) == 1
    assert apply2(OP_LTE, 0, 1) == 1
    assert apply2(OP_LTE, 1, 0) == 0
    assert apply2(OP_LTE, 1, 1) == 1
    assert apply2(OP_LTE, a, 0).equivalent(-a)
    assert apply2(OP_LTE, a, 1) == 1
    assert apply2(OP_LTE, 0, b) == 1
    assert apply2(OP_LTE, 1, b).equivalent(b)
    assert apply2(OP_LTE, a, b).equivalent(-a + b)

    assert apply2(OP_NAND, 0, 0) == 1
    assert apply2(OP_NAND, 0, 1) == 1
    assert apply2(OP_NAND, 1, 0) == 1
    assert apply2(OP_NAND, 1, 1) == 0
    assert apply2(OP_NAND, a, 0) == 1
    assert apply2(OP_NAND, a, 1).equivalent(-a)
    assert apply2(OP_NAND, 0, b) == 1
    assert apply2(OP_NAND, 1, b).equivalent(-b)
    assert apply2(OP_NAND, a, b).equivalent(-a + -b)

    assert apply2(OP_ONE, 0, 0) == 1
    assert apply2(OP_ONE, 0, 1) == 1
    assert apply2(OP_ONE, 1, 0) == 1
    assert apply2(OP_ONE, 1, 1) == 1
    assert apply2(OP_ONE, a, 0) == 1
    assert apply2(OP_ONE, a, 1) == 1
    assert apply2(OP_ONE, 0, b) == 1
    assert apply2(OP_ONE, 1, b) == 1
    assert apply2(OP_ONE, a, b) == 1
