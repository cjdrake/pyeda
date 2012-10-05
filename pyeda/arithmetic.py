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
    S, C = list(), list()
    for i, ai in enumerate(A):
        carry = (cin if i == 0 else C[i-1])
        S.append(Xor(ai, B.getifz(i), carry))
        C.append(ai * B.getifz(i) + ai * carry + B.getifz(i) * carry)
    return BitVector(S), BitVector(C)
