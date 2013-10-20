"""
Logic functions for addition

Interface Functions:
    ripple_carry_add
    kogge_stone_add
"""

# Disable "invalid variable name"
# pylint: disable=C0103

from pyeda.boolalg.expr import Xor, Majority
from pyeda.boolalg.vexpr import BitVector
from pyeda.util import clog2

def ripple_carry_add(A, B, cin=0):
    """Return symbolic logic for an N-bit ripple carry adder."""
    assert len(A) == len(B)
    s, c = list(), list()
    for i, ai in enumerate(A, A.start):
        carry = (cin if i == 0 else c[i-1])
        s.append(Xor(ai, B[i], carry))
        c.append(Majority(ai, B[i], carry))
    return BitVector(s), BitVector(c)

def kogge_stone_add(A, B, cin=0):
    """Return symbolic logic for an N-bit Kogge-Stone adder."""
    assert len(A) == len(B)
    stop = len(A)
    # generate/propagate logic
    g = [A[i] * B[i] for i in range(stop)]
    p = [Xor(A[i], B[i]) for i in range(stop)]
    for i in range(clog2(stop)):
        start = 1 << i
        for j in range(start, stop):
            g[j] = g[j] + p[j] * g[j-start]
            p[j] = p[j] * p[j-start]
    # sum logic
    s = [Xor(A[i], B[i], (cin if i == 0 else g[i-1])) for i in range(stop)]
    return BitVector(s), BitVector(g)
