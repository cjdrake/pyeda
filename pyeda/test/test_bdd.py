"""
Test binary decision diagrams
"""

from pyeda.bdd import expr2bdd, BDDVARIABLES
from pyeda.expr import var

a, b, c = map(var, 'abc')

def test_expr2bdd():
    f = expr2bdd(a * b + a * c + b * c)

    aa = BDDVARIABLES[a.uniqid]
    bb = BDDVARIABLES[b.uniqid]
    cc = BDDVARIABLES[c.uniqid]

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
