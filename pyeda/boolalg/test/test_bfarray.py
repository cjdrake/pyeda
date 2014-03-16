"""
Test Boolean Function arrays
"""

from pyeda.boolalg.bfarray import (
    _dims2shape,
    bddzeros, exprzeros, ttzeros,
    bddones, exprones, ttones,
    bddvars, exprvars, ttvars,
)

from nose.tools import assert_raises

def test_dims2shape():
    assert_raises(ValueError, exprzeros, -1)
    assert_raises(ValueError, exprzeros, 0)
    assert_raises(ValueError, exprzeros, (-1, 0))
    assert_raises(ValueError, exprzeros, (0, -1))
    assert_raises(ValueError, exprzeros, (1, 0))
    assert_raises(TypeError, exprzeros, 'foo')
    assert _dims2shape(4, (4, 8)) == ((0, 4), (4, 8))

def test_zeros():
    zeros = bddzeros(4)
    assert all(zero.is_zero() for zero in zeros)
    zeros = exprzeros(4)
    assert all(zero.is_zero() for zero in zeros)
    zeros = ttzeros(4)
    assert all(zero.is_zero() for zero in zeros)

def test_ones():
    ones = bddones(4)
    assert all(one.is_one() for one in ones)
    ones = exprones(4)
    assert all(one.is_one() for one in ones)
    ones = ttones(4)
    assert all(one.is_one() for one in ones)

def test_vars():
    xs = bddvars('x', 4)
    assert all(x.name == 'x' and x.indices == (i, ) for i, x in enumerate(xs))
    xs = exprvars('x', 4)
    assert all(x.name == 'x' and x.indices == (i, ) for i, x in enumerate(xs))
    xs = ttvars('x', 4)
    assert all(x.name == 'x' and x.indices == (i, ) for i, x in enumerate(xs))

