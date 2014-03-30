"""
Test vector Boolean functions
"""

from pyeda.boolalg.vexpr import bitvec
from pyeda.boolalg.bfarray import uint2exprs, int2exprs

from nose.tools import assert_raises

def test_bitvec():
    assert_raises(TypeError, bitvec, 'x', "foo")
    X = bitvec('x')
    assert X.name == 'x'
    X = bitvec('x', 4)
    assert X.shape[0][0] == 0 and X.shape[0][1] == 4 and len(X.items) == 4
    X = bitvec('x', (4, 8))
    assert X.shape[0][0] == 4 and X.shape[0][1] == 8 and len(X.items) == 4
    # FIXME: should we support this?
    #X = bitvec('x', (8, 4))
    #assert X.shape[0][0] == 4 and X.shape[0][1] == 8 and len(X.items) == 4

def test_uint2exprs():
    assert_raises(ValueError, uint2exprs, -1)
    assert_raises(ValueError, uint2exprs, 42, 4)
    assert str(uint2exprs(0)) == "[0]"
    assert str(uint2exprs(1)) == "[1]"
    assert str(uint2exprs(2)) == "[0, 1]"
    assert str(uint2exprs(3)) == "[1, 1]"
    assert str(uint2exprs(4)) == "[0, 0, 1]"
    assert str(uint2exprs(4, 4)) == "[0, 0, 1, 0]"

def test_int2exprs():
    assert_raises(ValueError, int2exprs, 42, 4)
    assert str(int2exprs(-4)) == "[0, 0, 1]"
    assert str(int2exprs(-3)) == "[1, 0, 1]"
    assert str(int2exprs(-2)) == "[0, 1]"
    assert str(int2exprs(-1)) == "[1]"
    assert str(int2exprs(0)) == "[0]"
    assert str(int2exprs(1)) == "[1, 0]"
    assert str(int2exprs(2)) == "[0, 1, 0]"
    assert str(int2exprs(3)) == "[1, 1, 0]"
    assert str(int2exprs(3, 4)) == "[1, 1, 0, 0]"

def test_ops():
    X = bitvec('x', 4)
    Y = bitvec('y', 4)

    assert X.uor().equivalent(X[3] | X[2] | X[1] | X[0])
    assert X.unor().equivalent(~(X[3] | X[2] | X[1] | X[0]))
    assert X.uand().equivalent(X[3] & X[2] & X[1] & X[0])
    assert X.unand().equivalent(~(X[3] & X[2] & X[1] & X[0]))
    assert X.uxor().equivalent(X[3] ^ X[2] ^ X[1] ^ X[0])
    assert X.uxnor().equivalent(~(X[3] ^ X[2] ^ X[1] ^ X[0]))

    assert str(~X) == "[~x[0], ~x[1], ~x[2], ~x[3]]"
    assert str(X | Y) == "[Or(x[0], y[0]), Or(x[1], y[1]), Or(x[2], y[2]), Or(x[3], y[3])]"
    assert str(X & Y) == "[And(x[0], y[0]), And(x[1], y[1]), And(x[2], y[2]), And(x[3], y[3])]"
    assert str(X ^ Y) == "[Xor(x[0], y[0]), Xor(x[1], y[1]), Xor(x[2], y[2]), Xor(x[3], y[3])]"

def test_shift():
    X = bitvec('x', 8)
    Y = bitvec('y', 4)

    # left shift
    assert_raises(ValueError, X.lsh, -1)
    assert_raises(ValueError, X.lsh, 9)
    assert_raises(ValueError, X.lsh, 2, Y)
    a, b = X.lsh(4)
    assert str(a) == "[0, 0, 0, 0, x[0], x[1], x[2], x[3]]"
    assert str(b) == "[x[4], x[5], x[6], x[7]]"
    a, b = X.lsh(4, Y)
    assert str(a) == "[y[0], y[1], y[2], y[3], x[0], x[1], x[2], x[3]]"
    assert str(b) == "[x[4], x[5], x[6], x[7]]"
    a, b = X.lsh(0)
    assert str(a) == "[x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]]"
    assert not b
    assert_raises(TypeError, X.__lshift__, "foo")
    assert str(X << 4) == "[0, 0, 0, 0, x[0], x[1], x[2], x[3]]"
    assert str(X << (4, Y)) == "[y[0], y[1], y[2], y[3], x[0], x[1], x[2], x[3]]"

    # right shift
    assert_raises(ValueError, X.rsh, -1)
    assert_raises(ValueError, X.rsh, 9)
    assert_raises(ValueError, X.rsh, 2, Y)
    a, b = X.rsh(4)
    assert str(a) == "[x[4], x[5], x[6], x[7], 0, 0, 0, 0]"
    assert str(b) == "[x[0], x[1], x[2], x[3]]"
    a, b = X.rsh(4, Y)
    assert str(a) == "[x[4], x[5], x[6], x[7], y[0], y[1], y[2], y[3]]"
    assert str(b) == "[x[0], x[1], x[2], x[3]]"
    a, b = X.rsh(0)
    assert str(a) == "[x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]]"
    assert not b
    assert_raises(TypeError, X.__rshift__, "foo")
    assert str(X >> 4) == "[x[4], x[5], x[6], x[7], 0, 0, 0, 0]"
    assert str(X >> (4, Y)) == "[x[4], x[5], x[6], x[7], y[0], y[1], y[2], y[3]]"

    # arithmetic right shift
    assert_raises(ValueError, X.arsh, -1)
    assert_raises(ValueError, X.arsh, 9)
    a, b = X.arsh(4)
    assert str(a) == "[x[4], x[5], x[6], x[7], x[7], x[7], x[7], x[7]]"
    assert str(b) == "[x[0], x[1], x[2], x[3]]"
    a, b = X.arsh(0)
    assert str(a) == "[x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]]"
    assert not b

def test_decode():
    A = bitvec('a', 2)
    d = A.decode()
    d.vrestrict({A: "00"}) == [1, 0, 0, 0]
    d.vrestrict({A: "10"}) == [0, 1, 0, 0]
    d.vrestrict({A: "01"}) == [0, 0, 1, 0]
    d.vrestrict({A: "11"}) == [0, 0, 0, 1]

