"""
Logic functions for addition

Interface Functions:
    ripple_carry_add
    kogge_stone_add
    brent_kung_add
"""


# Disable 'invalid-name', b/c 'logic' package uses unconventional names
# pylint: disable=C0103


from math import floor, log

from pyeda.boolalg.bfarray import farray
from pyeda.util import clog2


def ripple_carry_add(A, B, cin=0):
    """Return symbolic logic for an N-bit ripple carry adder."""
    if len(A) != len(B):
        raise ValueError("expected A and B to be equal length")
    ss, cs = [], []
    for i, a in enumerate(A):
        c = (cin if i == 0 else cs[i-1])
        ss.append(a ^ B[i] ^ c)
        cs.append(a & B[i] | a & c | B[i] & c)
    return farray(ss), farray(cs)


def kogge_stone_add(A, B, cin=0):
    """Return symbolic logic for an N-bit Kogge-Stone adder."""
    if len(A) != len(B):
        raise ValueError("expected A and B to be equal length")
    N = len(A)
    # generate/propagate logic
    gs = [A[i] & B[i] for i in range(N)]
    ps = [A[i] ^ B[i] for i in range(N)]
    for i in range(clog2(N)):
        start = 1 << i
        for j in range(start, N):
            gs[j] = gs[j] | ps[j] & gs[j-start]
            ps[j] = ps[j] & ps[j-start]
    # sum logic
    ss = [A[0] ^ B[0] ^ cin]
    ss += [A[i] ^ B[i] ^ gs[i-1] for i in range(1, N)]
    return farray(ss), farray(gs)


def brent_kung_add(A, B, cin=0):
    """Return symbolic logic for an N-bit Brent-Kung adder."""
    if len(A) != len(B):
        raise ValueError("expected A and B to be equal length")
    N = len(A)
    # generate/propagate logic
    gs = [A[i] & B[i] for i in range(N)]
    ps = [A[i] ^ B[i] for i in range(N)]
    # carry tree
    for i in range(floor(log(N, 2))):
        step = 2**i
        for start in range(2**(i+1)-1, N, 2**(i+1)):
            gs[start] = gs[start] | ps[start] & gs[start-step]
            ps[start] = ps[start] & ps[start-step]
    # inverse carry tree
    for i in range(floor(log(N, 2))-2, -1, -1):
        start = 2**(i+1)-1
        step = 2**i
        while start + step < N:
            gs[start+step] = gs[start+step] | ps[start+step] & gs[start]
            ps[start+step] = ps[start+step] & ps[start]
            start += step
    # sum logic
    ss = [A[0] ^ B[0] ^ cin]
    ss += [A[i] ^ B[i] ^ gs[i-1] for i in range(1, N)]
    return farray(ss), farray(gs)
