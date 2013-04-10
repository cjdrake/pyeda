"""
Test table Boolean functions
"""

from pyeda.expr import var, Xor
from pyeda.table import (
    expr2truthtable, truthtable2expr,
    TruthTable, PCTable
)

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
    tt = PCTable((a, b, c, d), "0110100110010110")
    assert str(tt) == XOR_STR
    assert tt.satisfy_count() == 8

    tt = PCTable((a, b), "100-")
    assert len(tt.data) == 1
    assert str(tt) == "inputs: b a\n00 1\n01 0\n10 0\n11 -\n"

def test_ops():
    f = TruthTable([a, b], "0001")
    assert str(-f) == "inputs: b a\n00 1\n01 1\n10 1\n11 0\n"

    assert f + 0 == f
    assert f + 1 == 1
    assert 0 + f == f
    assert 1 + f == 1

    assert f * 0 == 0
    assert f * 1 == f
    assert 0 * f == 0
    assert 1 * f == f

    assert f - 0 == 1
    assert f - 1 == f
    assert str(0 - f) == "inputs: b a\n00 1\n01 1\n10 1\n11 0\n"
    assert 1 - f == 1

    f = PCTable([a, b], "01-0")
    assert str(-f) == "inputs: b a\n00 1\n01 0\n10 -\n11 1\n"

    f = TruthTable([a, b], "0011")
    g = TruthTable([a, b], "0101")
    assert str(f + g) == "inputs: b a\n00 0\n01 1\n10 1\n11 1\n"

    f = TruthTable([a, b], "0011")
    g = TruthTable([a, b], "0101")
    assert str(f * g) == "inputs: b a\n00 0\n01 0\n10 0\n11 1\n"

    f = PCTable([a, b, c], "00011-00")
    g = PCTable([a, b, c], "01-1--00")
    assert str(f + g) == "inputs: c b a\n000 0\n001 1\n010 -\n011 1\n100 1\n101 -\n110 0\n111 0\n"

    f = PCTable([a, b, c], "00011-00")
    g = PCTable([a, b, c], "10-0--11")
    assert str(f - g) == "inputs: c b a\n000 0\n001 1\n010 -\n011 1\n100 1\n101 -\n110 0\n111 0\n"

    f = PCTable([a, b, c], "00011-00")
    g = PCTable([a, b, c], "01-1--00")
    assert str(f * g) == "inputs: c b a\n000 0\n001 0\n010 0\n011 1\n100 -\n101 -\n110 0\n111 0\n"

    f = TruthTable([a, b, c], "00011100")
    g = PCTable([a, b, c], "01-01-00")
    assert str(f + g) == "inputs: c b a\n000 0\n001 1\n010 -\n011 1\n100 1\n101 1\n110 0\n111 0\n"

    f = PCTable([a, b, c], "0011--00")
    g = TruthTable([a, b, c], "01010100")
    assert str(f + g) == "inputs: c b a\n000 0\n001 1\n010 1\n011 1\n100 -\n101 1\n110 0\n111 0\n"

    f = PCTable([a, b, c], "0011--00")
    g = TruthTable([a, b, c], "01010100")
    assert str(f * g) == "inputs: c b a\n000 0\n001 0\n010 0\n011 1\n100 0\n101 -\n110 0\n111 0\n"

    f = TruthTable([a, b, c], "00011100")
    g = PCTable([a, b, c], "01-01-00")
    assert str(f * g) == "inputs: c b a\n000 0\n001 0\n010 0\n011 0\n100 1\n101 -\n110 0\n111 0\n"
