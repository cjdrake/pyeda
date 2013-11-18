"""
Logic functions for addition

Interface Functions:
    ripple_carry_add
    kogge_stone_add
    brent_kung_add
"""

# Disable "invalid variable name"
# pylint: disable=C0103

from math import floor, log

from pyeda.boolalg.expr import Xor, Majority
from pyeda.boolalg.vexpr import BitVector
from pyeda.util import clog2

def ripple_carry_add(A, B, cin=0):
    """Return symbolic logic for an N-bit ripple carry adder."""
    if len(A) != len(B):
        raise ValueError("expected A and B to be equal length")
    s, c = list(), list()
    for i, ai in enumerate(A, A.start):
        carry = (cin if i == 0 else c[i-1])
        s.append(Xor(ai, B[i], carry))
        c.append(Majority(ai, B[i], carry))
    return BitVector(s), BitVector(c)

def kogge_stone_add(A, B, cin=0):
    """Return symbolic logic for an N-bit Kogge-Stone adder."""
    if len(A) != len(B):
        raise ValueError("expected A and B to be equal length")
    N = len(A)
    # generate/propagate logic
    g = [A[i] * B[i] for i in range(N)]
    p = [Xor(A[i], B[i]) for i in range(N)]
    for i in range(clog2(N)):
        start = 1 << i
        for j in range(start, N):
            g[j] = g[j] + p[j] * g[j-start]
            p[j] = p[j] * p[j-start]
    # sum logic
    s = [Xor(A[i], B[i], (cin if i == 0 else g[i-1])) for i in range(N)]
    return BitVector(s), BitVector(g)

def brent_kung_add(A, B, cin=0):
    """Return symbolic logic for an N-bit Brent-Kung adder."""
    if len(A) != len(B):
        raise ValueError("expected A and B to be equal length")
    N = len(A)
    # generate/propagate logic
    g = [A[i] * B[i] for i in range(N)]
    p = [Xor(A[i], B[i]) for i in range(N)]
    # carry tree
    for i in range(floor(log(N, 2))):
        step = 2**i
        for start in range(2**(i+1)-1, N, 2**(i+1)):
            g[start] = g[start] + p[start] * g[start-step]
            p[start] = p[start] * p[start-step]
    # inverse carry tree
    for i in range(floor(log(N, 2))-2, -1, -1):
        start = 2**(i+1)-1
        step = 2**i
        while start + step < N:
            g[start+step] = g[start+step] + p[start+step] * g[start]
            p[start+step] = p[start+step] * p[start]
            start += step
    # sum logic
    s = [Xor(A[i], B[i], (cin if i == 0 else g[i-1])) for i in range(N)]
    return BitVector(s), BitVector(g)
