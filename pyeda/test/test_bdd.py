"""
Test binary decision diagrams
"""

from pyeda.alphas import *
from pyeda.bdd import (
    bddvar, expr2bdd, bdd2expr,
    BinaryDecisionDiagram,
    BDDZERO, BDDONE
)
from pyeda.expr import Xor

aa, bb, cc, dd = map(bddvar, 'abcd')

def test_bddvar():
    assert aa.name == 'a'
    assert aa.indices == tuple()
    assert aa.namespace == tuple()

def test_expr2bdd():
    assert expr2bdd(a) == aa

    assert expr2bdd(-a * -b + a * -b + -a * b + a * b) == 1
    assert expr2bdd(-(-a * -b + a * -b + -a * b + a * b)) == 0

    ff = expr2bdd(a * b + a * c + b * c)
    gg = expr2bdd(a * b + a * c + b * c)

    assert ff == gg

    assert ff.node.root == a.uniqid
    assert ff.node.low.root == b.uniqid
    assert ff.node.high.root == b.uniqid
    assert ff.node.low.low == BDDZERO
    assert ff.node.low.high.root == c.uniqid
    assert ff.node.high.low.root == c.uniqid
    assert ff.node.high.high == BDDONE
    assert ff.node.low.high.low == BDDZERO
    assert ff.node.high.low.high == BDDONE

    assert ff.support == {aa, bb, cc}
    assert ff.inputs == (aa, bb, cc)

def test_bdd2expr():
    f = a * b + a * c + b * c
    zero = BinaryDecisionDiagram(BDDZERO)
    one = BinaryDecisionDiagram(BDDONE)
    assert bdd2expr(zero) == 0
    assert bdd2expr(one) == 1
    assert bdd2expr(expr2bdd(f)).equivalent(f)
    assert bdd2expr(expr2bdd(f), conj=True).equivalent(f)

def test_traverse():
    ff = expr2bdd(a * b + a * c + b * c)
    path = [node.root for node in ff.traverse()]
    # 0, 1, c, b(0, c), b(c, 1), a
    assert path == [-2, -1, 3, 2, 2, 1]

def test_equivalent():
    ff = expr2bdd(a * -b + -a * b)
    gg = expr2bdd((-a + -b) * (a + b))
    assert ff.equivalent(ff)
    assert gg.equivalent(ff)

def test_restrict():
    ff = expr2bdd(a * b + a * c + b * c)

    assert ff.restrict({}).equivalent(ff)

    assert ff.restrict({aa: 0}).equivalent(expr2bdd(b * c))
    assert ff.restrict({aa: 1}).equivalent(expr2bdd(b + c))
    assert ff.restrict({bb: 0}).equivalent(expr2bdd(a * c))
    assert ff.restrict({bb: 1}).equivalent(expr2bdd(a + c))
    assert ff.restrict({cc: 0}).equivalent(expr2bdd(a * b))
    assert ff.restrict({cc: 1}).equivalent(expr2bdd(a + b))

    assert ff.restrict({aa: 0, bb: 0}) == 0
    assert ff.restrict({aa: 0, bb: 1}) == cc
    assert ff.restrict({aa: 1, bb: 0}) == cc
    assert ff.restrict({aa: 1, bb: 1}) == 1

    assert ff.restrict({aa: 0, cc: 0}) == 0
    assert ff.restrict({aa: 0, cc: 1}) == bb
    assert ff.restrict({aa: 1, cc: 0}) == bb
    assert ff.restrict({aa: 1, cc: 1}) == 1

    assert ff.restrict({bb: 0, cc: 0}) == 0
    assert ff.restrict({bb: 0, cc: 1}) == aa
    assert ff.restrict({bb: 1, cc: 0}) == aa
    assert ff.restrict({bb: 1, cc: 1}) == 1

    assert ff.restrict({aa: 0, bb: 0, cc: 0}) == 0
    assert ff.restrict({aa: 0, bb: 0, cc: 1}) == 0
    assert ff.restrict({aa: 0, bb: 1, cc: 0}) == 0
    assert ff.restrict({aa: 0, bb: 1, cc: 1}) == 1
    assert ff.restrict({aa: 1, bb: 0, cc: 0}) == 0
    assert ff.restrict({aa: 1, bb: 0, cc: 1}) == 1
    assert ff.restrict({aa: 1, bb: 1, cc: 0}) == 1
    assert ff.restrict({aa: 1, bb: 1, cc: 1}) == 1

def test_ops():
    assert aa + 0 == aa
    assert aa + 1 == 1
    assert 0 + aa == aa
    assert 1 + aa == 1

    assert aa - 0 == 1
    assert aa - 1 == aa
    assert 0 - aa == -aa
    assert 1 - aa == 1

    assert aa * 0 == 0
    assert aa * 1 == aa
    assert 0 * aa == 0
    assert 1 * aa == aa

    assert aa.xor(0) == aa
    assert aa.xor(1) == -aa

    assert bdd2expr(-aa * bb + aa * -bb).equivalent(-a * b + a * -b)
    assert bdd2expr(aa - bb).equivalent(a - b)
    assert bdd2expr(aa.xor(bb)).equivalent(Xor(a, b))

def test_negate():
    f = a * b + a * c + b * c
    ff = expr2bdd(f)
    assert bdd2expr(-ff).equivalent(-f)

def test_satisfy():
    f = a * b + a * c + b * c
    ff = expr2bdd(f)
    assert [p for p in ff.satisfy_all()] == [{aa: 0, bb: 1, cc: 1}, {aa: 1, bb: 0, cc: 1}, {aa: 1, bb: 1}]
    assert ff.satisfy_count() == 3
    assert ff.satisfy_one() == {aa: 0, bb: 1, cc: 1}

def test_misc():
    f = a * b + a * c + b * c
    ff = expr2bdd(f)
    assert ff.reduce() == ff
    assert ff.smoothing(aa).equivalent(bb + cc)
    assert ff.consensus(aa).equivalent(bb * cc)
    assert ff.derivative(aa).equivalent(bb.xor(cc))

    zero = BinaryDecisionDiagram(BDDZERO)
    assert zero.satisfy_one() is None
