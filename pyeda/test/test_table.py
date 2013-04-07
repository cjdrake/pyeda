"""
Test table Boolean functions
"""

from pyeda.expr import var, Xor
from pyeda.table import expr2truthtable, truthtable2expr, TruthTable

a, b, c, d, e = map(var, 'abcde')

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

def test_table():
    assert TruthTable([], [0]) == 0
    assert TruthTable([], [1]) == 1

    f = Xor(a, b, c, d)
    tt = expr2truthtable(f)
    assert len(tt.data) == 2
    assert truthtable2expr(tt).equivalent(f)
    assert truthtable2expr(tt, conj=True).equivalent(f)
    assert str(tt) == XOR_STR
    assert repr(tt) == XOR_STR
    assert tt.support == {a, b, c, d}
    assert tt.inputs == (a, b, c, d)

    assert tt.reduce() == tt
    assert truthtable2expr(tt.restrict({a: 0})).equivalent(Xor(b, c, d))
    assert tt.restrict({e: 0}) == tt

    assert [p for p in tt.iter_zeros()] == [{a: 0, b: 0, c: 0, d: 0},
                                            {a: 1, b: 1, c: 0, d: 0},
                                            {a: 1, b: 0, c: 1, d: 0},
                                            {a: 0, b: 1, c: 1, d: 0},
                                            {a: 1, b: 0, c: 0, d: 1},
                                            {a: 0, b: 1, c: 0, d: 1},
                                            {a: 0, b: 0, c: 1, d: 1},
                                            {a: 1, b: 1, c: 1, d: 1}]

    assert tt.satisfy_one() == {a: 1, b: 0, c: 0, d: 0}
    assert [p for p in tt.satisfy_all()] == [{a: 1, b: 0, c: 0, d: 0},
                                             {a: 0, b: 1, c: 0, d: 0},
                                             {a: 0, b: 0, c: 1, d: 0},
                                             {a: 1, b: 1, c: 1, d: 0},
                                             {a: 0, b: 0, c: 0, d: 1},
                                             {a: 1, b: 1, c: 0, d: 1},
                                             {a: 1, b: 0, c: 1, d: 1},
                                             {a: 0, b: 1, c: 1, d: 1}]

    assert tt.satisfy_count() == 8

    assert TruthTable((a, b), "0000").satisfy_one() == None

def test_pc_table():
    tt = TruthTable((a, b, c, d), "0110100110010110", pc=True)
    assert str(tt) == XOR_STR
    assert tt.satisfy_count() == 8

    tt = TruthTable((a, b), "100-", pc=True)
    assert len(tt.data) == 1
    assert str(tt) == "inputs: b a\n00 1\n01 0\n10 0\n11 -\n"

def test_negate():
    tt = TruthTable((a, b, c), "00010111", pc=False)
    assert str(-tt) == "inputs: c b a\n000 1\n001 1\n010 1\n011 0\n100 1\n101 0\n110 0\n111 0\n"

    tt = TruthTable((a, b, c), "0001011-", pc=True)
    assert str(-tt) == "inputs: c b a\n000 1\n001 1\n010 1\n011 0\n100 1\n101 0\n110 0\n111 -\n"
