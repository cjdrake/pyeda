"""
Test binary decision diagrams
"""

from pyeda.bdd import expr2bdd
from pyeda.expr import var

a, b, c = map(var, 'abc')

def test_expr2bdd():
    f = a * b + a * c + b * c
    bdd_f = expr2bdd(f)
    assert bdd_f.root == a.var
    assert bdd_f.low.root == b.var
    assert bdd_f.high.root == b.var
    assert bdd_f.low.low.root == 0
    assert bdd_f.low.high.root == c.var
    assert bdd_f.high.low.root == c.var
    assert bdd_f.high.high.root == 1
    assert bdd_f.low.high.low.root == 0
    assert bdd_f.high.low.high.root == 1

    assert bdd_f.support == {a.var, b.var, c.var}
    assert bdd_f.inputs == [a.var, b.var, c.var]
