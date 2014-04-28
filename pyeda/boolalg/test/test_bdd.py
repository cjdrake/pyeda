"""
Test binary decision diagrams
"""

import re

from pyeda.boolalg.bdd import (
    bddvar, expr2bdd, bdd2expr, upoint2bddpoint,
    BDDNODEZERO, BDDNODEONE,
)
from pyeda.boolalg.expr import expr

a, b, c, d, e = map(bddvar, 'abcde')

def test_const():
    zero = a & []
    one = a | ['foo']
    assert int(zero) == 0
    assert int(one) == 1
    assert bool(zero) is False
    assert bool(one) is True
    assert str(zero) == '0'
    assert str(one) == '1'

def test_misc():
    f = a & b | a & c | b & c
    assert f.smoothing(a) is b | c
    assert f.consensus(a) is b & c
    assert f.derivative(a) is b ^ c

def test_bddvar():
    assert a.name == 'a'
    assert a.names == ('a', )
    assert a.indices == tuple()

def test_expr2bdd():
    assert expr2bdd(expr("a ^ b ^ c")) is a ^ b ^ c

    assert expr2bdd(expr("~a & ~b | a & ~b | ~a & b | a & b")).is_one()
    assert expr2bdd(expr("~(~a & ~b | a & ~b | ~a & b | a & b)")).is_zero()

    f = expr2bdd(expr("a & b | a & c | b & c"))
    g = expr2bdd(expr("Majority(a, b, c)"))

    assert f is g

    assert f.node.root == a.uniqid
    assert f.node.lo.root == b.uniqid
    assert f.node.hi.root == b.uniqid
    assert f.node.lo.lo is BDDNODEZERO
    assert f.node.lo.hi.root == c.uniqid
    assert f.node.hi.lo.root == c.uniqid
    assert f.node.hi.hi is BDDNODEONE
    assert f.node.lo.hi.lo is BDDNODEZERO
    assert f.node.hi.lo.hi is BDDNODEONE

    assert f.support == {a, b, c}
    assert f.inputs == (a, b, c)

def test_bdd2expr():
    assert bdd2expr(a & ~a).is_zero()
    assert bdd2expr(a | ~a).is_one()
    f = a & b | a & c | b & c
    assert bdd2expr(f).equivalent(expr("Majority(a, b, c)"))
    assert bdd2expr(f, conj=True).equivalent(expr("Majority(a, b, c)"))

def test_upoint2bddpoint():
    upoint = (frozenset([a.uniqid, c.uniqid]), frozenset([b.uniqid, d.uniqid]))
    assert upoint2bddpoint(upoint) == {a: 0, b: 1, c: 0, d: 1}

def test_traverse():
    f = a & b | a & c | b & c
    path1 = [node.root for node in f.dfs_preorder()]
    path2 = [node.root for node in f.dfs_postorder()]
    path3 = [node.root for node in f.bfs()]
    # a, b(0, c), 0, c, 1, b(c, 1)
    assert path1 == [a.uniqid, b.uniqid, -2, c.uniqid, -1, b.uniqid]
    # 0, 1, c, b(0, c), b(c, 1), a
    assert path2 == [-2, -1, c.uniqid, b.uniqid, b.uniqid, a.uniqid]
    # a, b(0, c), b(c, 1), 0, c, 1
    assert path3 == [a.uniqid, b.uniqid, b.uniqid, -2, c.uniqid, -1]

def test_equivalent():
    f = a & ~b | ~a & b
    g = (~a | ~b) & (a | b)
    assert f.equivalent(g)

def test_restrict():
    f = a & b | a & c | b & c

    assert f.restrict({}) is f

    assert f.restrict({a: 0}) is b & c
    assert f.restrict({a: 1}) is b | c
    assert f.restrict({b: 0}) is a & c
    assert f.restrict({b: 1}) is a | c
    assert f.restrict({c: 0}) is a & b
    assert f.restrict({c: 1}) is a | b

    assert f.restrict({a: 0, b: 0}).is_zero()
    assert f.restrict({a: 0, b: 1}) is c
    assert f.restrict({a: 1, b: 0}) is c
    assert f.restrict({a: 1, b: 1}).is_one()

    assert f.restrict({a: 0, c: 0}).is_zero()
    assert f.restrict({a: 0, c: 1}) is b
    assert f.restrict({a: 1, c: 0}) is b
    assert f.restrict({a: 1, c: 1}).is_one()

    assert f.restrict({b: 0, c: 0}).is_zero()
    assert f.restrict({b: 0, c: 1}) is a
    assert f.restrict({b: 1, c: 0}) is a
    assert f.restrict({b: 1, c: 1}).is_one()

    assert f.restrict({a: 0, b: 0, c: 0}).is_zero()
    assert f.restrict({a: 0, b: 0, c: 1}).is_zero()
    assert f.restrict({a: 0, b: 1, c: 0}).is_zero()
    assert f.restrict({a: 0, b: 1, c: 1}).is_one()
    assert f.restrict({a: 1, b: 0, c: 0}).is_zero()
    assert f.restrict({a: 1, b: 0, c: 1}).is_one()
    assert f.restrict({a: 1, b: 1, c: 0}).is_one()
    assert f.restrict({a: 1, b: 1, c: 1}).is_one()

def test_compose():
    f = a & b | a & c | b & c
    assert f.compose({a: b, c: d&e}) is (b | b & d & e | b & d & e)

def test_ops():
    f = a & b | a & c | b & c
    assert ~f is (~a & ~b | ~a & ~c | ~b & ~c)

    assert a | 0 is a
    assert (a | 1).is_one()
    assert 0 | a is a
    assert (1 | a).is_one()

    assert (a & 0).is_zero()
    assert a & 1 is a
    assert (0 & a).is_zero()
    assert 1 & a is a

    assert a ^ 0 is a
    assert a ^ 1 is ~a
    assert 0 ^ a is a
    assert 1 ^ a is ~a

    assert a ^ b is ~a & b | a & ~b

def test_satisfy():
    f = a & b | a & c | b & c
    assert [p for p in f.satisfy_all()] == [{a: 0, b: 1, c: 1}, {a: 1, b: 0, c: 1}, {a: 1, b: 1}]
    assert f.satisfy_count() == 3
    assert f.satisfy_one() == {a: 0, b: 1, c: 1}
    assert (a & ~a).satisfy_one() is None
    assert (a | ~a).satisfy_one() == {}

