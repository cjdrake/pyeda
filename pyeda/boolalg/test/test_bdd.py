"""
Test binary decision diagrams
"""

from pyeda.boolalg.bdd import (
    bddvar, _bdd, expr2bdd, bdd2expr,
    BDDNODEZERO, BDDNODEONE, BDDZERO, BDDONE
)
from pyeda.boolalg.expr import exprvar, EXPRZERO, EXPRONE, Xor

a, b, c, d, e = map(exprvar, 'abcde')
aa, bb, cc, dd, ee = map(bddvar, 'abcde')

def test_misc():
    f = a & b | a & c | b & c
    ff = expr2bdd(f)

    assert ff.smoothing(aa).equivalent(bb | cc)
    assert ff.consensus(aa).equivalent(bb & cc)
    assert ff.derivative(aa).equivalent(bb ^ cc)

def test_bddvar():
    assert aa.name == 'a'
    assert aa.names == ('a', )
    assert aa.indices == tuple()

def test_expr2bdd():
    assert expr2bdd(a) is aa

    assert expr2bdd(~a & ~b | a & ~b | ~a & b | a & b).node is BDDNODEONE
    assert expr2bdd(~(~a & ~b | a & ~b | ~a & b | a & b)).node is BDDNODEZERO

    ff = expr2bdd(a & b | a & c | b & c)
    gg = expr2bdd(a & b | a & c | b & c)

    assert ff is gg

    assert ff.node.root == a.uniqid
    assert ff.node.lo.root == b.uniqid
    assert ff.node.hi.root == b.uniqid
    assert ff.node.lo.lo is BDDNODEZERO
    assert ff.node.lo.hi.root == c.uniqid
    assert ff.node.hi.lo.root == c.uniqid
    assert ff.node.hi.hi is BDDNODEONE
    assert ff.node.lo.hi.lo is BDDNODEZERO
    assert ff.node.hi.lo.hi is BDDNODEONE

    assert ff.support == {aa, bb, cc}
    assert ff.inputs == (aa, bb, cc)

def test_bdd2expr():
    f = a & b | a & c | b & c
    zero = _bdd(BDDNODEZERO)
    one = _bdd(BDDNODEONE)
    assert bdd2expr(zero) is EXPRZERO
    assert bdd2expr(one) is EXPRONE
    assert bdd2expr(expr2bdd(f)).equivalent(f)
    assert bdd2expr(expr2bdd(f), conj=True).equivalent(f)

def test_traverse():
    ff = expr2bdd(a & b | a & c | b & c)
    path = [node.root for node in ff.traverse()]
    # 0, 1, c, b(0, c), b(c, 1), a
    assert path == [-2, -1, c.uniqid, b.uniqid, b.uniqid, a.uniqid]

def test_equivalent():
    ff = expr2bdd(a & ~b | ~a & b)
    gg = expr2bdd((~a | ~b) & (a | b))
    assert ff.equivalent(ff)
    assert gg.equivalent(ff)

def test_restrict():
    ff = expr2bdd(a & b | a & c | b & c)

    assert ff.restrict({}).equivalent(ff)

    assert ff.restrict({aa: 0}).equivalent(expr2bdd(b & c))
    assert ff.restrict({aa: 1}).equivalent(expr2bdd(b | c))
    assert ff.restrict({bb: 0}).equivalent(expr2bdd(a & c))
    assert ff.restrict({bb: 1}).equivalent(expr2bdd(a | c))
    assert ff.restrict({cc: 0}).equivalent(expr2bdd(a & b))
    assert ff.restrict({cc: 1}).equivalent(expr2bdd(a | b))

    assert ff.restrict({aa: 0, bb: 0}) is BDDZERO
    assert ff.restrict({aa: 0, bb: 1}) is cc
    assert ff.restrict({aa: 1, bb: 0}) is cc
    assert ff.restrict({aa: 1, bb: 1}) is BDDONE

    assert ff.restrict({aa: 0, cc: 0}) is BDDZERO
    assert ff.restrict({aa: 0, cc: 1}) is bb
    assert ff.restrict({aa: 1, cc: 0}) is bb
    assert ff.restrict({aa: 1, cc: 1}) is BDDONE

    assert ff.restrict({bb: 0, cc: 0}) is BDDZERO
    assert ff.restrict({bb: 0, cc: 1}) is aa
    assert ff.restrict({bb: 1, cc: 0}) is aa
    assert ff.restrict({bb: 1, cc: 1}) is BDDONE

    assert ff.restrict({aa: 0, bb: 0, cc: 0}) is BDDZERO
    assert ff.restrict({aa: 0, bb: 0, cc: 1}) is BDDZERO
    assert ff.restrict({aa: 0, bb: 1, cc: 0}) is BDDZERO
    assert ff.restrict({aa: 0, bb: 1, cc: 1}) is BDDONE
    assert ff.restrict({aa: 1, bb: 0, cc: 0}) is BDDZERO
    assert ff.restrict({aa: 1, bb: 0, cc: 1}) is BDDONE
    assert ff.restrict({aa: 1, bb: 1, cc: 0}) is BDDONE
    assert ff.restrict({aa: 1, bb: 1, cc: 1}) is BDDONE

def test_compose():
    f = a & b | a & c | b & c
    ff = expr2bdd(a & b | a & c | b & c)
    assert ff.compose({aa: bb, cc: dd&ee}).equivalent(expr2bdd(f.compose({a: b, c: d&e})))

def test_negate():
    f = a & b | a & c | b & c
    ff = expr2bdd(f)
    assert bdd2expr(~ff).equivalent(~f)

def test_ops():
    assert aa | 0 is aa
    assert aa | 1 is BDDONE
    assert 0 | aa is aa
    assert 1 | aa is BDDONE

    assert aa & 0 is BDDZERO
    assert aa & 1 is aa
    assert 0 & aa is BDDZERO
    assert 1 & aa is aa

    assert aa ^ 0 is aa
    assert aa ^ 1 is ~aa

    assert bdd2expr(~aa & bb | aa & ~bb).equivalent(~a & b | a & ~b)
    assert bdd2expr(aa ^ bb).equivalent(Xor(a, b))

def test_satisfy():
    f = a & b | a & c | b & c
    ff = expr2bdd(f)
    assert [p for p in ff.satisfy_all()] == [{aa: 0, bb: 1, cc: 1}, {aa: 1, bb: 0, cc: 1}, {aa: 1, bb: 1}]
    assert ff.satisfy_count() == 3
    assert ff.satisfy_one() == {aa: 0, bb: 1, cc: 1}
    assert expr2bdd(EXPRZERO).satisfy_one() is None
    assert expr2bdd(EXPRONE).satisfy_one() == {}

