"""
Arithmetic Module
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved."

# pyeda
from pyeda.expr import Xor
from pyeda.vexpr import BitVector

def ripple_carry_add(A, B, cin=0):
    """Return symbolic logic for an N-bit ripple carry adder.

    >>> import random
    >>> from pyeda import *
    >>> A, B = bitvec("A", 8), bitvec("B", 8)
    >>> S, C = ripple_carry_add(A, B)
    >>> S.append(C[7])
    >>> for i in range(64):
    ...     ra = random.randint(0, 2**8-1)
    ...     rb = random.randint(0, 2**8-1)
    ...     d = {A: uint2vec(ra, 8), B: uint2vec(rb, 8)}
    ...     assert S.vrestrict(d).to_uint() == ra + rb
    >>> S, C = ripple_carry_add(A, B)
    >>> for i in range(64):
    ...     ra = random.randint(-2**6, 2**6-1)
    ...     rb = random.randint(-2**6, 2**6-1)
    ...     d = {A: int2vec(ra, 8), B: int2vec(rb, 8)}
    ...     assert S.vrestrict(d).to_int() == ra + rb
    """
    assert len(A) == len(B)
    s, c = list(), list()
    for i, ai in enumerate(A, A.start):
        carry = (cin if i == 0 else c[i-1])
        s.append(Xor(ai, B[i], carry))
        c.append(ai * B[i] + ai * carry + B[i] * carry)
    return BitVector(s), BitVector(c)

def bin2gray(B):
    """Convert a binary-coded vector into a gray-coded vector.

    >>> from pyeda import bitvec, uint2vec
    >>> B = bitvec("B", 3)
    >>> G = bin2gray(B)
    >>> gnums = [G.vrestrict({B: uint2vec(i, 3)}).to_uint() for i in range(8)]
    >>> print(gnums)
    [0, 1, 3, 2, 6, 7, 5, 4]
    """
    items = [Xor(B[i], B[i+1]) for i in range(B.start, B.stop-1)]
    items.append(B[B.stop-1])
    return BitVector(items, B.start)

def gray2bin(G):
    """Convert a gray-coded vector into a binary-coded vector.

    >>> from pyeda import bitvec, uint2vec
    >>> G = bitvec("G", 3)
    >>> B = gray2bin(G)
    >>> gnums = [0, 1, 3, 2, 6, 7, 5, 4]
    >>> bnums = [B.vrestrict({G: uint2vec(i, 3)}).to_uint() for i in gnums ]
    >>> print(bnums)
    [0, 1, 2, 3, 4, 5, 6, 7]
    """
    items = [G[i:].uxor() for i, _ in enumerate(G, G.start)]
    return BitVector(items, G.start)
