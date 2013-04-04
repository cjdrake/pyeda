"""
Test constant Boolean functions
"""

from pyeda.constant import Zero, One
from pyeda.expr import var

a, b = map(var, 'ab')

zero = Zero()
one = One()

zero_a = Zero({a})
zero_ab = Zero({a, b})

one_a = One({a})
one_ab = One({a, b})

def test_zero():
    assert str(zero) == '0'
    assert repr(zero) == '0'
    assert zero.support == set()
    assert zero_a.support == {a}
    assert zero_ab.support == {a, b}
    assert zero.restrict({a: 0, b: 1}) == zero
    assert zero.compose({a: 0, b: 1}) == zero
    assert bool(zero) is False
    assert int(zero) == 0
    assert zero.satisfy_one() is None
    assert not [p for p in zero.satisfy_all()]
    assert zero.satisfy_count() == 0

def test_one():
    assert str(one) == '1'
    assert repr(one) == '1'
    assert one.support == set()
    assert one_a.support == {a}
    assert one_ab.support == {a, b}
    assert one.restrict({a: 0, b: 1}) == one
    assert one.compose({a: 0, b: 1}) == one
    assert bool(one) is True
    assert int(one) == 1
    assert one.satisfy_one() == dict()
    assert [p for p in one.satisfy_all()] == [{}]
    assert [p for p in one_a.satisfy_all()] == [{a: 0}, {a: 1}]
    assert [p for p in one_ab.satisfy_all()] == [
        {a: 0, b: 0}, {a: 1, b: 0}, {a: 0, b: 1}, {a: 1, b: 1}
    ]
    assert one.satisfy_count() == 1
    assert one_a.satisfy_count() == 2
    assert one_ab.satisfy_count() == 4

def test_ops():
    assert str(-zero) == '1'
    assert str(-one) == '0'

    assert str(zero + zero) == '0'
    assert str(zero + one) == '1'
    assert str(one + zero) == '1'
    assert str(one + one) == '1'

    assert str(zero * zero) == '0'
    assert str(zero * one) == '0'
    assert str(one * zero) == '0'
    assert str(one * one) == '1'
