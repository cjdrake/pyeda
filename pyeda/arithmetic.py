"""
Digital Arithmetic Module

Interface Functions:
    ripple_carry_add
    kogge_stone_add
    bin2gray
    gray2bin
"""

from pyeda.common import clog2
from pyeda.expr import Xor
from pyeda.vexpr import BitVector

def ripple_carry_add(A, B, cin=0):
    """Return symbolic logic for an N-bit ripple carry adder."""
    assert len(A) == len(B)
    s, c = list(), list()
    for i, ai in enumerate(A, A.start):
        carry = (cin if i == 0 else c[i-1])
        s.append(Xor(ai, B[i], carry))
        c.append(ai * B[i] + ai * carry + B[i] * carry)
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

def bin2gray(B):
    """Convert a binary-coded vector into a gray-coded vector."""
    items = [Xor(B[i], B[i+1]) for i in range(B.start, B.stop-1)]
    items.append(B[B.stop-1])
    return BitVector(items, B.start)

def gray2bin(G):
    """Convert a gray-coded vector into a binary-coded vector."""
    items = [G[i:].uxor() for i, _ in enumerate(G, G.start)]
    return BitVector(items, G.start)
