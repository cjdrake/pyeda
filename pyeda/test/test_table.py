"""
Test tables
"""

from pyeda.expr import var, Xor
from pyeda.table import expr2truthtable, TruthTable

a, b, c, d, = map(var, 'abcd')

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
    f = expr2truthtable(Xor(a, b, c, d))
    assert str(f) == XOR_STR
    assert f.support == {a, b, c, d}
    assert f.inputs == (a, b, c, d)
    assert f.reduce() == f
    #assert f.satisfy_one() == {a: 1, b: 0, c: 0, d: 0}
    #assert [p for p in f.satisfy_all()] == [{a: 1, b: 0, c: 0, d: 0},
    #                                        {a: 0, b: 1, c: 0, d: 0},
    #                                        {a: 0, b: 0, c: 1, d: 0},
    #                                        {a: 1, b: 1, c: 1, d: 0},
    #                                        {a: 0, b: 0, c: 0, d: 1},
    #                                        {a: 1, b: 1, c: 0, d: 1},
    #                                        {a: 1, b: 0, c: 1, d: 1},
    #                                        {a: 0, b: 1, c: 1, d: 1}]
    assert f.satisfy_count() == 8

def test_pc_table():
    f = TruthTable((a, b, c, d), "0110100110010110", pc=True)
    assert str(f) == XOR_STR
