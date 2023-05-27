"""
Test Boolean Function arrays
"""


# Allow access to protected class members
# pylint: disable=W0212


import pytest

from pyeda.boolalg.bdd import BinaryDecisionDiagram, bddvar
from pyeda.boolalg.bfarray import (exprvars, exprzeros, farray, fcat,
                                   int2exprs, uint2exprs)
from pyeda.boolalg.expr import Expression, exprvar

X = exprvars("x", 4)
Y = exprvars("y", 4)
a, b, c, d, w, x, y, z = map(exprvar, "abcdwxyz")


def test_fcat():
    # expected Function or farray
    with pytest.raises(TypeError):
        fcat(X, Y, 0)
    assert str(fcat(X[0], X[2:], Y[3], Y[:-2])) == "farray([x[0], x[2], x[3], y[3], y[0], y[1]])"


def test_farray():
    # expected shape volume to match items
    with pytest.raises(ValueError):
        farray([X[0], X[1]], shape=((0, 42), ))
    # could not determine ftype parameter
    with pytest.raises(ValueError):
        farray([])
    # expected ftype to be a type
    with pytest.raises(TypeError):
        farray([X[0], X[1]], ftype=42)
    # expected ftype to match items
    with pytest.raises(ValueError):
        farray([X[0], X[1]], ftype=BinaryDecisionDiagram)
    # expected ftype to be a property subclass of Function
    with pytest.raises(TypeError):
        farray([], ftype=int)
    # expected a sequence of Function
    with pytest.raises(TypeError):
        farray(42)
    with pytest.raises(TypeError):
        farray([1, 2, 3, 4])
    # expected uniform dimensions
    with pytest.raises(ValueError):
        farray([[a, b], [w, x, y, z], 42])
    with pytest.raises(ValueError):
        farray([[a, b], [w, x, y, z]])
    # expected uniform types
    with pytest.raises(ValueError):
        farray([[a, b], [c, bddvar("d")]])
    with pytest.raises(ValueError):
        farray([[a, b], [bddvar("c"), bddvar("d")]])
    # _check_shape errors
    with pytest.raises(ValueError):
        farray([a, b, c, d], shape=((-1, 3), ))
    with pytest.raises(ValueError):
        farray([a, b, c, d], shape=((3, -1), ))
    with pytest.raises(ValueError):
        farray([a, b, c, d], shape=((5, 1), ))
    with pytest.raises(TypeError):
        farray([a, b, c, d], shape=(("foo", "bar"), ))
    with pytest.raises(TypeError):
        farray([a, b, c, d], shape=42)

    temp = farray([[a, b], [c, d]])
    assert str(temp) == """\
farray([[a, b],
        [c, d]])\
"""

    # __str__
    Z = exprvars("z", 2, 2, 2)
    assert str(Z) == """\
farray([[[z[0,0,0], z[0,0,1]],
         [z[0,1,0], z[0,1,1]]],

        [[z[1,0,0], z[1,0,1]],
         [z[1,1,0], z[1,1,1]]]])\
"""

    assert str(farray([], ftype=Expression)) == "farray([])"

    # __getitem__
    # expected <= M slice dimensions, got N
    with pytest.raises(ValueError):
        X.__getitem__((2, 2))
    sel = exprvars("s", 2)
    assert X[sel].equivalent(~sel[0] & ~sel[1] & X[0] | sel[0] & ~sel[1] & X[1] | ~sel[0] & sel[1] & X[2] | sel[0] & sel[1] & X[3])
    assert X[:2][sel[0]].equivalent(~sel[0] & X[0] | sel[0] & X[1])
    # expected clog2(N) bits
    with pytest.raises(ValueError):
        X.__getitem__(sel[0])
    # slice step not supported
    with pytest.raises(ValueError):
        X.__getitem__(slice(None, None, 2))
    # type error
    with pytest.raises(TypeError):
        X.__getitem__("foo")
    # norm_index
    assert X[-1] is X[3]
    with pytest.raises(IndexError):
        X.__getitem__(42)
    # norm_indices
    assert X[-3:-1]._items == [X[-3], X[-2]]
    assert not X[-8:-10]._items
    assert not X[-10:-8]._items
    assert not X[8:10]._items
    assert not X[10:8]._items
    assert not X[3:1]._items

    # __setitem__
    Z = exprzeros(4, 4)
    Z[0,0] = X[0]
    assert Z._items[0] is X[0]
    # expected item to be a Function
    with pytest.raises(TypeError):
        Z.__setitem__((0, 0), 42)
    Z[0,:] = X[:4]
    assert Z._items[0:4] == [X[0], X[1], X[2], X[3]]
    # expected item to be an farray
    with pytest.raises(TypeError):
        Z.__setitem__((0, slice(None, None, None)), 42)
    # expected item.size = ...
    with pytest.raises(ValueError):
        Z.__setitem__(..., X[:2])
    # slice step not supported
    with pytest.raises(ValueError):
        X.__setitem__(slice(None, None, 2), 42)
    # type error
    with pytest.raises(TypeError):
        X.__setitem__("foo", 42)

    # __add__
    assert (0 + X)._items[0].is_zero()
    assert (X + 0)._items[4].is_zero()
    assert (Y[0] + X)._items[0] is Y[0]
    assert (X + Y[0])._items[4] is Y[0]
    assert (X[:2] + Y[2:])._items == [X[0], X[1], Y[2], Y[3]]
    # expected Function or farray
    with pytest.raises(TypeError):
        X.__add__(42)
    with pytest.raises(TypeError):
        X.__radd__(42)

    A = exprvars("a", 2, 5, 6)
    B = exprvars("b", 2, 5, 6)
    C = exprvars("c", (1, 3), 5, 6)
    # regular MDA will retain shape
    assert (A+B).shape == ((0, 4), (0, 5), (0, 6))
    # irregular MDA will not
    assert (A+C).shape == ((0, 4*5*6), )

    # regular MDA will retain shape
    assert (A*2).shape == ((0, 4), (0, 5), (0, 6))
    # irregular MDA will not
    assert (C*2).shape == ((0, 4*5*6), )

    # __mul__
    # expected multiplier to be an int
    with pytest.raises(TypeError):
        X.__mul__("foo")
    # expected multiplier to be non-negative
    with pytest.raises(ValueError):
        X.__mul__(-2)
    assert (X[:2] * 2)._items == [X[0], X[1], X[0], X[1]]
    assert (2 * X[:2])._items == [X[0], X[1], X[0], X[1]]

    # offsets
    Z = exprzeros((1, 5), (17, 21))
    assert Z.offsets == (1, 17)

    # reshape
    assert Z.reshape(4, 4).shape == ((0, 4), (0, 4))
    # expected shape with equal volume
    with pytest.raises(ValueError):
        Z.reshape(42, 42)

    # restrict
    assert str(X.vrestrict({X: "0101"})) == "farray([0, 1, 0, 1])"

    # compose
    assert X.compose({X[0]: Y[0]})._items[0] == Y[0]

    # to_uint / to_int
    assert uint2exprs(42).to_uint() == 42
    assert uint2exprs(42, 8).to_uint() == 42
    # expected all functions to be a constant (0 or 1) form
    with pytest.raises(ValueError):
        X.to_uint()
    # expected num >= 0
    with pytest.raises(ValueError):
        uint2exprs(-1)
    # overflow
    with pytest.raises(ValueError):
        uint2exprs(42, 2)
    with pytest.raises(ValueError):
        int2exprs(42, 2)
    assert int2exprs(-42).to_int() == -42
    assert int2exprs(-42, 8).to_int() == -42
    assert int2exprs(42).to_int() == 42
    assert int2exprs(42, 8).to_int() == 42

    # zext, sext
    assert X.zext(1)[4].is_zero()
    assert X.sext(1)[4] is X[3]

    # __invert__, __or__, __and__, __xor__
    assert str(~X) == "farray([~x[0], ~x[1], ~x[2], ~x[3]])"
    assert str(X | Y) == "farray([Or(x[0], y[0]), Or(x[1], y[1]), Or(x[2], y[2]), Or(x[3], y[3])])"
    assert str(X & Y) == "farray([And(x[0], y[0]), And(x[1], y[1]), And(x[2], y[2]), And(x[3], y[3])])"
    assert str(X ^ Y) == "farray([Xor(x[0], y[0]), Xor(x[1], y[1]), Xor(x[2], y[2]), Xor(x[3], y[3])])"
    # _op_shape
    # expected farray input
    with pytest.raises(TypeError):
        X.__or__(42)
    Z = exprvars("z", 2, 2)
    assert str(X | Z) == "farray([Or(x[0], z[0,0]), Or(x[1], z[0,1]), Or(x[2], z[1,0]), Or(x[3], z[1,1])])"
    Z = exprvars("z", 2, 3)
    # expected operand sizes to match
    with pytest.raises(ValueError):
        X.__or__(Z)

    # lsh, rsh
    assert str(X.lsh(0)) == "(farray([x[0], x[1], x[2], x[3]]), farray([]))"
    assert str(X << 0) == "farray([x[0], x[1], x[2], x[3]])"
    assert str(X.lsh(2)) == "(farray([0, 0, x[0], x[1]]), farray([x[2], x[3]]))"
    assert str(X << 2) == "farray([0, 0, x[0], x[1]])"
    assert str(X << (2, Y[:2])) == "farray([y[0], y[1], x[0], x[1]])"
    assert str(X.rsh(0)) == "(farray([x[0], x[1], x[2], x[3]]), farray([]))"
    assert str(X >> 0) == "farray([x[0], x[1], x[2], x[3]])"
    assert str(X.rsh(2)) == "(farray([x[2], x[3], 0, 0]), farray([x[0], x[1]]))"
    assert str(X >> 2) == "farray([x[2], x[3], 0, 0])"
    assert str(X >> (2, Y[:2])) == "farray([x[2], x[3], y[0], y[1]])"
    with pytest.raises(TypeError):
        X.__lshift__("foo")
    with pytest.raises(ValueError):
        X.__lshift__(-1)
    with pytest.raises(ValueError):
        X.__lshift__((2, Y))
    with pytest.raises(TypeError):
        X.__rshift__("foo")
    with pytest.raises(ValueError):
        X.__rshift__(-1)
    with pytest.raises(ValueError):
        X.__rshift__((2, Y))

    # arsh
    assert str(X.arsh(0)) == "(farray([x[0], x[1], x[2], x[3]]), farray([]))"
    assert str(X.arsh(2)) == "(farray([x[2], x[3], x[3], x[3]]), farray([x[0], x[1]]))"
    with pytest.raises(ValueError):
        X.arsh(-1)

    # unary ops
    assert X.uor().equivalent(X[0] | X[1] | X[2] | X[3])
    assert X.unor().equivalent(~(X[0] | X[1] | X[2] | X[3]))
    assert X.uand().equivalent(X[0] & X[1] & X[2] & X[3])
    assert X.unand().equivalent(~(X[0] & X[1] & X[2] & X[3]))
    assert X.uxor().equivalent(X[0] ^ X[1] ^ X[2] ^ X[3])
    assert X.uxnor().equivalent(~(X[0] ^ X[1] ^ X[2] ^ X[3]))

    # decode
    assert str(farray([], ftype=Expression).decode()) == "farray([1])"
    parts = X[:2].decode()
    assert parts[0].equivalent(~X[0] & ~X[1])
    assert parts[1].equivalent(X[0] & ~X[1])
    assert parts[2].equivalent(~X[0] & X[1])
    assert parts[3].equivalent(X[0] & X[1])


def test_dims2shape():
    with pytest.raises(ValueError):
        exprzeros()
    with pytest.raises(ValueError):
        exprzeros(-1)
    with pytest.raises(ValueError):
        exprzeros((-1, 0))
    with pytest.raises(ValueError):
        exprzeros((0, -1))
    with pytest.raises(ValueError):
        exprzeros((1, 0))
    with pytest.raises(TypeError):
        exprzeros("foo")
