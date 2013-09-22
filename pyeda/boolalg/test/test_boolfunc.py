"""
Test Boolean functions
"""

from pyeda.boolalg.boolfunc import (
    num2point,
    num2upoint,
    num2term,
    point2upoint,
    point2term,
)
from pyeda.boolalg.expr import exprvar

a, b, c, d = map(exprvar, 'abcd')

def test_num2point():
    assert num2point(0x0, [a, b, c, d]) == {a: 0, b: 0, c: 0, d: 0}
    assert num2point(0x1, [a, b, c, d]) == {a: 1, b: 0, c: 0, d: 0}
    assert num2point(0x2, [a, b, c, d]) == {a: 0, b: 1, c: 0, d: 0}
    assert num2point(0x3, [a, b, c, d]) == {a: 1, b: 1, c: 0, d: 0}
    assert num2point(0x4, [a, b, c, d]) == {a: 0, b: 0, c: 1, d: 0}
    assert num2point(0x5, [a, b, c, d]) == {a: 1, b: 0, c: 1, d: 0}
    assert num2point(0x6, [a, b, c, d]) == {a: 0, b: 1, c: 1, d: 0}
    assert num2point(0x7, [a, b, c, d]) == {a: 1, b: 1, c: 1, d: 0}
    assert num2point(0x8, [a, b, c, d]) == {a: 0, b: 0, c: 0, d: 1}
    assert num2point(0x9, [a, b, c, d]) == {a: 1, b: 0, c: 0, d: 1}
    assert num2point(0xA, [a, b, c, d]) == {a: 0, b: 1, c: 0, d: 1}
    assert num2point(0xB, [a, b, c, d]) == {a: 1, b: 1, c: 0, d: 1}
    assert num2point(0xC, [a, b, c, d]) == {a: 0, b: 0, c: 1, d: 1}
    assert num2point(0xD, [a, b, c, d]) == {a: 1, b: 0, c: 1, d: 1}
    assert num2point(0xE, [a, b, c, d]) == {a: 0, b: 1, c: 1, d: 1}
    assert num2point(0xF, [a, b, c, d]) == {a: 1, b: 1, c: 1, d: 1}

def test_num2upoint():
    assert num2upoint(0x0, [a, b, c, d]) == ({a.uniqid, b.uniqid, c.uniqid, d.uniqid}, set()       )
    #assert num2upoint(0x1, [a, b, c, d]) == ({   2, 3, 4}, {1         })
    #assert num2upoint(0x2, [a, b, c, d]) == ({1,    3, 4}, {   2      })
    #assert num2upoint(0x3, [a, b, c, d]) == ({      3, 4}, {1, 2      })
    #assert num2upoint(0x4, [a, b, c, d]) == ({1, 2,    4}, {      3   })
    assert num2upoint(0x5, [a, b, c, d]) == ({   b.uniqid,    d.uniqid}, {a.uniqid,    c.uniqid   })
    #assert num2upoint(0x6, [a, b, c, d]) == ({1,       4}, {   2, 3   })
    #assert num2upoint(0x7, [a, b, c, d]) == ({         4}, {1, 2, 3   })
    #assert num2upoint(0x8, [a, b, c, d]) == ({1, 2, 3   }, {         4})
    #assert num2upoint(0x9, [a, b, c, d]) == ({   2, 3   }, {1,       4})
    assert num2upoint(0xA, [a, b, c, d]) == ({a.uniqid,    c.uniqid   }, {   b.uniqid,    d.uniqid})
    #assert num2upoint(0xB, [a, b, c, d]) == ({      3   }, {1, 2,    4})
    #assert num2upoint(0xC, [a, b, c, d]) == ({1, 2      }, {      3, 4})
    #assert num2upoint(0xD, [a, b, c, d]) == ({   2      }, {1,    3, 4})
    #assert num2upoint(0xE, [a, b, c, d]) == ({1         }, {   2, 3, 4})
    assert num2upoint(0xF, [a, b, c, d]) == (set()       , {a.uniqid, b.uniqid, c.uniqid, d.uniqid})

def test_num2term():
    assert num2term(0x0, [a, b, c, d], conj=False) == (-a, -b, -c, -d)
    assert num2term(0x1, [a, b, c, d], conj=False) == ( a, -b, -c, -d)
    assert num2term(0x2, [a, b, c, d], conj=False) == (-a,  b, -c, -d)
    assert num2term(0x3, [a, b, c, d], conj=False) == ( a,  b, -c, -d)
    assert num2term(0x4, [a, b, c, d], conj=False) == (-a, -b,  c, -d)
    assert num2term(0x5, [a, b, c, d], conj=False) == ( a, -b,  c, -d)
    assert num2term(0x6, [a, b, c, d], conj=False) == (-a,  b,  c, -d)
    assert num2term(0x7, [a, b, c, d], conj=False) == ( a,  b,  c, -d)
    assert num2term(0x8, [a, b, c, d], conj=False) == (-a, -b, -c,  d)
    assert num2term(0x9, [a, b, c, d], conj=False) == ( a, -b, -c,  d)
    assert num2term(0xA, [a, b, c, d], conj=False) == (-a,  b, -c,  d)
    assert num2term(0xB, [a, b, c, d], conj=False) == ( a,  b, -c,  d)
    assert num2term(0xC, [a, b, c, d], conj=False) == (-a, -b,  c,  d)
    assert num2term(0xD, [a, b, c, d], conj=False) == ( a, -b,  c,  d)
    assert num2term(0xE, [a, b, c, d], conj=False) == (-a,  b,  c,  d)
    assert num2term(0xF, [a, b, c, d], conj=False) == ( a,  b,  c,  d)

    assert num2term(0x0, [a, b, c, d], conj=True) == ( a,  b,  c,  d)
    assert num2term(0x1, [a, b, c, d], conj=True) == (-a,  b,  c,  d)
    assert num2term(0x2, [a, b, c, d], conj=True) == ( a, -b,  c,  d)
    assert num2term(0x3, [a, b, c, d], conj=True) == (-a, -b,  c,  d)
    assert num2term(0x4, [a, b, c, d], conj=True) == ( a,  b, -c,  d)
    assert num2term(0x5, [a, b, c, d], conj=True) == (-a,  b, -c,  d)
    assert num2term(0x6, [a, b, c, d], conj=True) == ( a, -b, -c,  d)
    assert num2term(0x7, [a, b, c, d], conj=True) == (-a, -b, -c,  d)
    assert num2term(0x8, [a, b, c, d], conj=True) == ( a,  b,  c, -d)
    assert num2term(0x9, [a, b, c, d], conj=True) == (-a,  b,  c, -d)
    assert num2term(0xA, [a, b, c, d], conj=True) == ( a, -b,  c, -d)
    assert num2term(0xB, [a, b, c, d], conj=True) == (-a, -b,  c, -d)
    assert num2term(0xC, [a, b, c, d], conj=True) == ( a,  b, -c, -d)
    assert num2term(0xD, [a, b, c, d], conj=True) == (-a,  b, -c, -d)
    assert num2term(0xE, [a, b, c, d], conj=True) == ( a, -b, -c, -d)
    assert num2term(0xF, [a, b, c, d], conj=True) == (-a, -b, -c, -d)

def test_point2upoint():
    assert point2upoint({a: 0, b: 0, c: 0, d: 0}) == ({a.uniqid, b.uniqid, c.uniqid, d.uniqid}, set()       )
    #assert point2upoint({a: 1, b: 0, c: 0, d: 0}) == ({   2, 3, 4}, {1         })
    #assert point2upoint({a: 0, b: 1, c: 0, d: 0}) == ({1,    3, 4}, {   2      })
    #assert point2upoint({a: 1, b: 1, c: 0, d: 0}) == ({      3, 4}, {1, 2      })
    #assert point2upoint({a: 0, b: 0, c: 1, d: 0}) == ({1, 2,    4}, {      3   })
    assert point2upoint({a: 1, b: 0, c: 1, d: 0}) == ({   b.uniqid,    d.uniqid}, {a.uniqid,    c.uniqid   })
    #assert point2upoint({a: 0, b: 1, c: 1, d: 0}) == ({1,       4}, {   2, 3   })
    #assert point2upoint({a: 1, b: 1, c: 1, d: 0}) == ({         4}, {1, 2, 3   })
    #assert point2upoint({a: 0, b: 0, c: 0, d: 1}) == ({1, 2, 3   }, {         4})
    #assert point2upoint({a: 1, b: 0, c: 0, d: 1}) == ({   2, 3   }, {1,       4})
    assert point2upoint({a: 0, b: 1, c: 0, d: 1}) == ({a.uniqid,    c.uniqid   }, {   b.uniqid,    d.uniqid})
    #assert point2upoint({a: 1, b: 1, c: 0, d: 1}) == ({      3   }, {1, 2,    4})
    #assert point2upoint({a: 0, b: 0, c: 1, d: 1}) == ({1, 2      }, {      3, 4})
    #assert point2upoint({a: 1, b: 0, c: 1, d: 1}) == ({   2      }, {1,    3, 4})
    #assert point2upoint({a: 0, b: 1, c: 1, d: 1}) == ({1         }, {   2, 3, 4})
    assert point2upoint({a: 1, b: 1, c: 1, d: 1}) == (set()       , {a.uniqid, b.uniqid, c.uniqid, d.uniqid})

def test_point2term():
    assert sorted(point2term({a: 0, b: 0, c: 0, d: 0}, conj=False)) == [-a, -b, -c, -d]
    assert sorted(point2term({a: 1, b: 0, c: 0, d: 0}, conj=False)) == [ a, -b, -c, -d]
    assert sorted(point2term({a: 0, b: 1, c: 0, d: 0}, conj=False)) == [-a,  b, -c, -d]
    assert sorted(point2term({a: 1, b: 1, c: 0, d: 0}, conj=False)) == [ a,  b, -c, -d]
    assert sorted(point2term({a: 0, b: 0, c: 1, d: 0}, conj=False)) == [-a, -b,  c, -d]
    assert sorted(point2term({a: 1, b: 0, c: 1, d: 0}, conj=False)) == [ a, -b,  c, -d]
    assert sorted(point2term({a: 0, b: 1, c: 1, d: 0}, conj=False)) == [-a,  b,  c, -d]
    assert sorted(point2term({a: 1, b: 1, c: 1, d: 0}, conj=False)) == [ a,  b,  c, -d]
    assert sorted(point2term({a: 0, b: 0, c: 0, d: 1}, conj=False)) == [-a, -b, -c,  d]
    assert sorted(point2term({a: 1, b: 0, c: 0, d: 1}, conj=False)) == [ a, -b, -c,  d]
    assert sorted(point2term({a: 0, b: 1, c: 0, d: 1}, conj=False)) == [-a,  b, -c,  d]
    assert sorted(point2term({a: 1, b: 1, c: 0, d: 1}, conj=False)) == [ a,  b, -c,  d]
    assert sorted(point2term({a: 0, b: 0, c: 1, d: 1}, conj=False)) == [-a, -b,  c,  d]
    assert sorted(point2term({a: 1, b: 0, c: 1, d: 1}, conj=False)) == [ a, -b,  c,  d]
    assert sorted(point2term({a: 0, b: 1, c: 1, d: 1}, conj=False)) == [-a,  b,  c,  d]
    assert sorted(point2term({a: 1, b: 1, c: 1, d: 1}, conj=False)) == [ a,  b,  c,  d]

    assert sorted(point2term({a: 0, b: 0, c: 0, d: 0}, conj=True)) == [ a,  b,  c,  d]
    assert sorted(point2term({a: 1, b: 0, c: 0, d: 0}, conj=True)) == [-a,  b,  c,  d]
    assert sorted(point2term({a: 0, b: 1, c: 0, d: 0}, conj=True)) == [ a, -b,  c,  d]
    assert sorted(point2term({a: 1, b: 1, c: 0, d: 0}, conj=True)) == [-a, -b,  c,  d]
    assert sorted(point2term({a: 0, b: 0, c: 1, d: 0}, conj=True)) == [ a,  b, -c,  d]
    assert sorted(point2term({a: 1, b: 0, c: 1, d: 0}, conj=True)) == [-a,  b, -c,  d]
    assert sorted(point2term({a: 0, b: 1, c: 1, d: 0}, conj=True)) == [ a, -b, -c,  d]
    assert sorted(point2term({a: 1, b: 1, c: 1, d: 0}, conj=True)) == [-a, -b, -c,  d]
    assert sorted(point2term({a: 0, b: 0, c: 0, d: 1}, conj=True)) == [ a,  b,  c, -d]
    assert sorted(point2term({a: 1, b: 0, c: 0, d: 1}, conj=True)) == [-a,  b,  c, -d]
    assert sorted(point2term({a: 0, b: 1, c: 0, d: 1}, conj=True)) == [ a, -b,  c, -d]
    assert sorted(point2term({a: 1, b: 1, c: 0, d: 1}, conj=True)) == [-a, -b,  c, -d]
    assert sorted(point2term({a: 0, b: 0, c: 1, d: 1}, conj=True)) == [ a,  b, -c, -d]
    assert sorted(point2term({a: 1, b: 0, c: 1, d: 1}, conj=True)) == [-a,  b, -c, -d]
    assert sorted(point2term({a: 0, b: 1, c: 1, d: 1}, conj=True)) == [ a, -b, -c, -d]
    assert sorted(point2term({a: 1, b: 1, c: 1, d: 1}, conj=True)) == [-a, -b, -c, -d]
