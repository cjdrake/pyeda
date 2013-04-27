"""
Test binary decision diagrams
"""

from pyeda.alphas import *
from pyeda.bdd import expr2bdd, BDDVariable

aa, bb, cc, dd = [BDDVariable(v.name) for v in (a, b, c, d)]

def test_expr2bdd():
    f = expr2bdd(a * b + a * c + b * c)

    assert f.node.root == a.uniqid
    assert f.node.low.root == b.uniqid
    assert f.node.high.root == b.uniqid
    assert f.node.low.low.root == -2
    assert f.node.low.high.root == c.uniqid
    assert f.node.high.low.root == c.uniqid
    assert f.node.high.high.root == -1
    assert f.node.low.high.low.root == -2
    assert f.node.high.low.high.root == -1

    assert f.support == {aa, bb, cc}
    assert f.inputs == (aa, bb, cc)

def test_traverse():
    f = expr2bdd(a * b + a * c + b * c)
    path = [node.root for node in f.traverse()]
    # 0, 1, c, b(0, c), b(c, 1), a
    assert path == [-2, -1, 3, 2, 2, 1]

def test_equivalent():
    f = expr2bdd(a * -b + -a * b)
    g = expr2bdd((-a + -b) * (a + b))
    assert f != g
    assert f.equivalent(f)
    assert g.equivalent(f)
