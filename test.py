"""
Test Module
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved."

# pyeda
from pyeda.expr import var

a, b, c, d, e = map(var, "abcde")

def test_cofactors():
    f = a * b + a * c + b * c
    assert str(f.cofactors()) == "(a * b + a * c + b * c,)"
    assert str(f.cofactors(a)) == "(b * c, b + c + b * c)"
    assert f.cofactors([a, b]) == (0, c, c, 1)
    assert f.cofactors([a, b, c]) == (0, 0, 0, 1, 0, 1, 1, 1)
    assert str(f.smoothing(a).to_dnf()) == "b + c"
    assert str(f.consensus(a).to_dnf()) == "b * c"
    assert str(f.derivative(a).to_dnf()) == "b' * c + b * c'"

def test_unate():
    f = a + b + -c
    assert not f.is_neg_unate(a)
    assert not f.is_neg_unate(b)
    assert f.is_neg_unate(c)
    assert f.is_pos_unate(a)
    assert f.is_pos_unate(b)
    assert not f.is_pos_unate(c)
    assert not f.is_binate(a)
    assert not f.is_binate(b)
    assert not f.is_binate(c)
    assert f.is_binate()

    g = a * b + a * -c + b * -c
    assert g.is_pos_unate(a)
    assert g.is_pos_unate(b)
    assert g.is_neg_unate(c)
