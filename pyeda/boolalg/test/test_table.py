"""
Test table Boolean functions
"""

from pyeda.boolalg.table import (
    ttvar, truthtable, expr2truthtable, truthtable2expr
)
from pyeda.boolalg.expr import exprvar, Xor

a, b, c, d, e = map(exprvar, 'abcde')
aa, bb, cc, dd, ee = map(ttvar, 'abcde')

XOR_STR = \
"""inputs: d c b a
0000 0
0001 1
0010 1
0011 0
0100 1
0101 0
0110 0
0111 1
1000 1
1001 0
1010 0
1011 1
1100 0
1101 1
1110 1
1111 0
"""

def test_unate():
    # c' * (a' + b')
    f = truthtable([aa, bb, cc], "11100000")
    assert f.is_neg_unate([aa, bb, cc])
    assert f.is_neg_unate([aa, bb])
    assert f.is_neg_unate([aa, cc])
    assert f.is_neg_unate([bb, cc])
    assert f.is_neg_unate(aa)
    assert f.is_neg_unate(bb)
    assert f.is_neg_unate(cc)
    assert f.is_neg_unate()

    # c * (a + b)
    f = truthtable([a, b, c], "00000111")
    assert f.is_pos_unate([aa, bb, cc])
    assert f.is_pos_unate([aa, bb])
    assert f.is_pos_unate([aa, cc])
    assert f.is_pos_unate([bb, cc])
    assert f.is_pos_unate(aa)
    assert f.is_pos_unate(bb)
    assert f.is_pos_unate(cc)
    assert f.is_pos_unate()

    # Xor(a, b, c)
    f = truthtable([a, b, c], "01101001")
    assert f.is_binate([aa, bb, cc])
    assert f.is_binate([aa, bb])
    assert f.is_binate([aa, cc])
    assert f.is_binate([bb, cc])
    assert f.is_binate(aa)
    assert f.is_binate(bb)
    assert f.is_binate(cc)

def test_ttvar():
    assert aa.name == 'a'
    assert aa.names == ('a', )
    assert aa.indices == tuple()

def test_table():
    assert truthtable([], [0]).is_zero()
    assert truthtable([], [1]).is_one()

    f = Xor(a, b, c, d)
    tt = expr2truthtable(f)
    assert truthtable2expr(tt).equivalent(f)
    assert truthtable2expr(tt, conj=True).equivalent(f)
    assert str(tt) == XOR_STR
    assert repr(tt) == XOR_STR
    assert tt.support == {aa, bb, cc, dd}
    assert tt.inputs == (aa, bb, cc, dd)

    assert truthtable2expr(tt.restrict({a: 0})).equivalent(Xor(b, c, d))
    assert tt.restrict({e: 0}) == tt

    assert tt.satisfy_one() == {aa: 1, bb: 0, cc: 0, dd: 0}
    assert [p for p in tt.satisfy_all()] == [{aa: 1, bb: 0, cc: 0, dd: 0},
                                             {aa: 0, bb: 1, cc: 0, dd: 0},
                                             {aa: 0, bb: 0, cc: 1, dd: 0},
                                             {aa: 1, bb: 1, cc: 1, dd: 0},
                                             {aa: 0, bb: 0, cc: 0, dd: 1},
                                             {aa: 1, bb: 1, cc: 0, dd: 1},
                                             {aa: 1, bb: 0, cc: 1, dd: 1},
                                             {aa: 0, bb: 1, cc: 1, dd: 1}]

    assert tt.satisfy_count() == 8

    assert truthtable((a, b), "0000").satisfy_one() == None

def test_ops():
    f = truthtable([aa, bb], "0001")
    assert str(f) == "inputs: b a\n00 0\n01 0\n10 0\n11 1\n"
    assert str(-f) == "inputs: b a\n00 1\n01 1\n10 1\n11 0\n"

    assert str(f + 0) == "inputs: b a\n00 0\n01 0\n10 0\n11 1\n"
    assert str(f + 1) == "inputs: b a\n00 1\n01 1\n10 1\n11 1\n"
    assert str(0 + f) == "inputs: b a\n00 0\n01 0\n10 0\n11 1\n"
    assert str(1 + f) == "inputs: b a\n00 1\n01 1\n10 1\n11 1\n"

    assert str(f * 0) == "inputs: b a\n00 0\n01 0\n10 0\n11 0\n"
    assert str(f * 1) == "inputs: b a\n00 0\n01 0\n10 0\n11 1\n"
    assert str(0 * f) == "inputs: b a\n00 0\n01 0\n10 0\n11 0\n"
    assert str(1 * f) == "inputs: b a\n00 0\n01 0\n10 0\n11 1\n"

    assert str(f - 0) == "inputs: b a\n00 1\n01 1\n10 1\n11 1\n"
    assert str(f - 1) == "inputs: b a\n00 0\n01 0\n10 0\n11 1\n"
    assert str(0 - f) == "inputs: b a\n00 1\n01 1\n10 1\n11 0\n"
    assert str(1 - f) == "inputs: b a\n00 1\n01 1\n10 1\n11 1\n"

    assert str(f.xor(0)) == "inputs: b a\n00 0\n01 0\n10 0\n11 1\n"
    assert str(f.xor(1)) == "inputs: b a\n00 1\n01 1\n10 1\n11 0\n"

    f = truthtable([aa, bb], "01-0")
    assert str(-f) == "inputs: b a\n00 1\n01 0\n10 -\n11 1\n"

    f = truthtable([aa, bb], "0011")
    g = truthtable([aa, bb], "0101")
    assert str(f + g) == "inputs: b a\n00 0\n01 1\n10 1\n11 1\n"
    assert str(f * g) == "inputs: b a\n00 0\n01 0\n10 0\n11 1\n"
    assert str(f.xor(g)) == "inputs: b a\n00 0\n01 1\n10 1\n11 0\n"

    f = truthtable([a, b, c], "00011-00")
    g = truthtable([a, b, c], "01-1--00")
    assert str(f + g) == "inputs: c b a\n000 0\n001 1\n010 -\n011 1\n100 1\n101 -\n110 0\n111 0\n"
    assert str(f - g) == "inputs: c b a\n000 1\n001 0\n010 -\n011 1\n100 1\n101 -\n110 1\n111 1\n"
    assert str(f * g) == "inputs: c b a\n000 0\n001 0\n010 0\n011 1\n100 -\n101 -\n110 0\n111 0\n"
    assert str(f.xor(g)) == "inputs: c b a\n000 0\n001 1\n010 -\n011 0\n100 -\n101 -\n110 0\n111 0\n"
