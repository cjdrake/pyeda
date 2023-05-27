"""
Test table Boolean functions
"""


from pyeda.boolalg.expr import Xor, exprvar
from pyeda.boolalg.table import (expr2truthtable, truthtable, truthtable2expr,
                                 ttvar)

a, b, c, d, e = map(exprvar, "abcde")
aa, bb, cc, dd, ee = map(ttvar, "abcde")

XOR_STR = """\
d c b a
0 0 0 0 : 0
0 0 0 1 : 1
0 0 1 0 : 1
0 0 1 1 : 0
0 1 0 0 : 1
0 1 0 1 : 0
0 1 1 0 : 0
0 1 1 1 : 1
1 0 0 0 : 1
1 0 0 1 : 0
1 0 1 0 : 0
1 0 1 1 : 1
1 1 0 0 : 0
1 1 0 1 : 1
1 1 1 0 : 1
1 1 1 1 : 0
"""


def test_unate():
    # ~c & (~a | ~b)
    f = truthtable([aa, bb, cc], "11100000")
    assert f.is_neg_unate([aa, bb, cc])
    assert f.is_neg_unate([aa, bb])
    assert f.is_neg_unate([aa, cc])
    assert f.is_neg_unate([bb, cc])
    assert f.is_neg_unate(aa)
    assert f.is_neg_unate(bb)
    assert f.is_neg_unate(cc)
    assert f.is_neg_unate()

    # c & (a | b)
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
    assert aa.name == "a"
    assert aa.names == ("a", )
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

    assert truthtable2expr(tt.restrict({aa: 0})).equivalent(Xor(b, c, d))
    assert tt.restrict({ee: 0}) == tt

    assert tt.satisfy_one() == {aa: 1, bb: 0, cc: 0, dd: 0}
    assert list(tt.satisfy_all()) == [{aa: 1, bb: 0, cc: 0, dd: 0},
                                      {aa: 0, bb: 1, cc: 0, dd: 0},
                                      {aa: 0, bb: 0, cc: 1, dd: 0},
                                      {aa: 1, bb: 1, cc: 1, dd: 0},
                                      {aa: 0, bb: 0, cc: 0, dd: 1},
                                      {aa: 1, bb: 1, cc: 0, dd: 1},
                                      {aa: 1, bb: 0, cc: 1, dd: 1},
                                      {aa: 0, bb: 1, cc: 1, dd: 1}]

    assert tt.satisfy_count() == 8

    assert truthtable((a, b), "0000").satisfy_one() is None


def test_ops():
    f = truthtable([aa, bb], "0001")
    assert str(f) == "b a\n0 0 : 0\n0 1 : 0\n1 0 : 0\n1 1 : 1\n"
    assert str(~f) == "b a\n0 0 : 1\n0 1 : 1\n1 0 : 1\n1 1 : 0\n"

    assert str(f | 0) == "b a\n0 0 : 0\n0 1 : 0\n1 0 : 0\n1 1 : 1\n"
    assert str(f | 1) == "b a\n0 0 : 1\n0 1 : 1\n1 0 : 1\n1 1 : 1\n"
    assert str(0 | f) == "b a\n0 0 : 0\n0 1 : 0\n1 0 : 0\n1 1 : 1\n"
    assert str(1 | f) == "b a\n0 0 : 1\n0 1 : 1\n1 0 : 1\n1 1 : 1\n"

    assert str(f & 0) == "b a\n0 0 : 0\n0 1 : 0\n1 0 : 0\n1 1 : 0\n"
    assert str(f & 1) == "b a\n0 0 : 0\n0 1 : 0\n1 0 : 0\n1 1 : 1\n"
    assert str(0 & f) == "b a\n0 0 : 0\n0 1 : 0\n1 0 : 0\n1 1 : 0\n"
    assert str(1 & f) == "b a\n0 0 : 0\n0 1 : 0\n1 0 : 0\n1 1 : 1\n"

    assert str(f ^ 0) == "b a\n0 0 : 0\n0 1 : 0\n1 0 : 0\n1 1 : 1\n"
    assert str(f ^ 1) == "b a\n0 0 : 1\n0 1 : 1\n1 0 : 1\n1 1 : 0\n"

    f = truthtable([aa, bb], "01-0")
    assert str(~f) == "b a\n0 0 : 1\n0 1 : 0\n1 0 : -\n1 1 : 1\n"

    f = truthtable([aa, bb], "0011")
    g = truthtable([aa, bb], "0101")
    assert str(f | g) == "b a\n0 0 : 0\n0 1 : 1\n1 0 : 1\n1 1 : 1\n"
    assert str(f & g) == "b a\n0 0 : 0\n0 1 : 0\n1 0 : 0\n1 1 : 1\n"
    assert str(f ^ g) == "b a\n0 0 : 0\n0 1 : 1\n1 0 : 1\n1 1 : 0\n"

    f = truthtable([a, b, c], "00011-00")
    g = truthtable([a, b, c], "01-1--00")
    assert str(f | g) == "c b a\n0 0 0 : 0\n0 0 1 : 1\n0 1 0 : -\n0 1 1 : 1\n1 0 0 : 1\n1 0 1 : -\n1 1 0 : 0\n1 1 1 : 0\n"
    assert str(f & g) == "c b a\n0 0 0 : 0\n0 0 1 : 0\n0 1 0 : 0\n0 1 1 : 1\n1 0 0 : -\n1 0 1 : -\n1 1 0 : 0\n1 1 1 : 0\n"
    assert str(f ^ g) == "c b a\n0 0 0 : 0\n0 0 1 : 1\n0 1 0 : -\n0 1 1 : 0\n1 0 0 : -\n1 0 1 : -\n1 1 0 : 0\n1 1 1 : 0\n"
