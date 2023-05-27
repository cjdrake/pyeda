"""
Test binary decision diagrams
"""


from pyeda.boolalg.bdd import (BDDNODEONE, BDDNODEZERO, BinaryDecisionDiagram,
                               bdd2expr, bddvar, expr2bdd, ite,
                               upoint2bddpoint)
from pyeda.boolalg.expr import AndOp, OrOp, expr

zero = BinaryDecisionDiagram.box(0)
one = BinaryDecisionDiagram.box(1)
a, b, c, d, w, x, y, z = map(bddvar, "abcdwxyz")


def test_expr2bdd():
    assert expr2bdd(expr("a ^ b ^ c")) is a ^ b ^ c

    assert expr2bdd(expr("~a & ~b | a & ~b | ~a & b | a & b")) is one
    assert expr2bdd(expr("~(~a & ~b | a & ~b | ~a & b | a & b)")) is zero

    f = expr2bdd(expr("~a & ~b & c | ~a & b & ~c | a & ~b & ~c | a & b & c"))
    g = expr2bdd(expr("a ^ b ^ c"))

    assert f is g

    assert f.node.root == a.uniqid

    assert f.node.lo.root == b.uniqid
    assert f.node.hi.root == b.uniqid

    assert f.node.lo.lo.root == c.uniqid
    assert f.node.lo.hi.root == c.uniqid
    assert f.node.hi.lo.root == c.uniqid
    assert f.node.hi.hi.root == c.uniqid

    assert f.node.lo.lo.lo == BDDNODEZERO
    assert f.node.lo.lo.hi == BDDNODEONE
    assert f.node.lo.hi.lo == BDDNODEONE
    assert f.node.lo.hi.hi == BDDNODEZERO
    assert f.node.hi.lo.lo == BDDNODEONE
    assert f.node.hi.lo.hi == BDDNODEZERO
    assert f.node.hi.hi.lo == BDDNODEZERO
    assert f.node.hi.hi.hi == BDDNODEONE


def test_bdd2expr():
    ex = bdd2expr(a ^ b ^ c, conj=False)
    assert ex.equivalent(expr("a ^ b ^ c"))
    assert isinstance(ex, OrOp) and ex.depth == 2

    ex = bdd2expr(a ^ b ^ c, conj=True)
    assert ex.equivalent(expr("a ^ b ^ c"))
    assert isinstance(ex, AndOp) and ex.depth == 2


def test_upoint2bddpoint():
    upoint = (frozenset([a.uniqid, c.uniqid]), frozenset([b.uniqid, d.uniqid]))
    assert upoint2bddpoint(upoint) == {a: 0, b: 1, c: 0, d: 1}


def test_ite():
    assert ite(a, b, c) is a & b | ~a & c


def test_const():
    assert bool(zero) is False
    assert bool(one) is True
    assert int(zero) == 0
    assert int(one) == 1
    assert str(zero) == "0"
    assert str(one) == "1"
    assert repr(zero) == "0"
    assert repr(one) == "1"


def test_boolfunc():
    # __invert__, __or__, __and__, __xor__
    f = ~a | b & c ^ d
    assert expr2bdd(expr("~a | b & c ^ d")) is f

    # support, usupport, inputs
    assert f.support == {a, b, c, d}
    assert f.usupport == {a.uniqid, b.uniqid, c.uniqid, d.uniqid}

    # restrict
    assert f.restrict({}) is f
    assert f.restrict({a: 0}) is one
    assert f.restrict({a: 1, b: 1}) is c ^ d
    assert f.restrict({a: 1, b: 1, c: 0}) is d
    assert f.restrict({a: 1, b: 1, c: 0, d: 0}) is zero

    # compose
    assert f.compose({a: w}) is ~w | b & c ^ d
    assert f.compose({a: w, b: x & y, c: y | z, d: x ^ z}) is ~w | x ^ z ^ x & y & (y | z)

    # satisfy_one, satisfy_all
    assert zero.satisfy_one() is None
    assert one.satisfy_one() == {}
    g = a & b | a & c | b & c
    assert list(g.satisfy_all()) == [
               {a: 0, b: 1, c: 1},
               {a: 1, b: 0, c: 1},
               {a: 1, b: 1}
           ]
    assert g.satisfy_count() == 3
    assert g.satisfy_one() == {a: 0, b: 1, c: 1}

    # is_zero, is_one
    assert zero.is_zero()
    assert one.is_one()

    # box, unbox
    assert BinaryDecisionDiagram.box("0") is zero
    assert BinaryDecisionDiagram.box("1") is one
    assert BinaryDecisionDiagram.box("") is zero
    assert BinaryDecisionDiagram.box("foo") is one


def test_traverse():
    f = a & b | a & c | b & c
    path1 = [node.root for node in f.dfs_preorder()]
    path2 = [node.root for node in f.dfs_postorder()]
    path3 = [node.root for node in f.bfs()]
    # a, b(0, c), 0, c, 1, b(c, 1)
    assert path1 == [a.uniqid, b.uniqid, -1, c.uniqid, -2, b.uniqid]
    # 0, 1, c, b(0, c), b(c, 1), a
    assert path2 == [-1, -2, c.uniqid, b.uniqid, b.uniqid, a.uniqid]
    # a, b(0, c), b(c, 1), 0, c, 1
    assert path3 == [a.uniqid, b.uniqid, b.uniqid, -1, c.uniqid, -2]


def test_equivalent():
    f = a & b | ~a & c
    g = (~a | b) & (a | c)
    assert f.equivalent(g)


def test_satisfy():
    f = a & b | a & c | b & c
    assert list(f.satisfy_all()) == [
               {a: 0, b: 1, c: 1},
               {a: 1, b: 0, c: 1},
               {a: 1, b: 1}
           ]
    assert f.satisfy_count() == 3
    assert f.satisfy_one() == {a: 0, b: 1, c: 1}
    assert (a & ~a).satisfy_one() is None
    assert (a | ~a).satisfy_one() == {}
