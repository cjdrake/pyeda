"""
Test logic functions for addition
"""

import random

from pyeda.logic.addition import (
    ripple_carry_add as rca,
    kogge_stone_add as ksa,
    brent_kung_add as bka,
)
from pyeda.boolalg.vexpr import bitvec, uint2vec, int2vec

NVECS = 100

def uadd(S, A, B, aval, bval):
    N = len(A)
    R = S.vrestrict({A: uint2vec(aval, N), B: uint2vec(bval, N)})
    return R.to_uint()

def sadd(S, A, B, aval, bval):
    N = len(A)
    R = S.vrestrict({A: int2vec(aval, N), B: int2vec(bval, N)})
    return R.to_int()

def test_unsigned_add():
    N = 9

    A = bitvec('A', N)
    B = bitvec('B', N)

    for adder in (rca, ksa, bka):
        S, C = adder(A, B)
        S.append(C[N-1])

        # 0 + 0 = 0
        assert uadd(S, A, B, 0, 0) == 0
        # 255 + 255 = 510
        assert uadd(S, A, B, 2**N-1, 2**N-1) == (2**(N+1)-2)
        # 255 + 1 = 256
        assert uadd(S, A, B, 2**N-1, 1) == 2**N

        # unsigned random vectors
        for i in range(NVECS):
            ra = random.randint(0, 2**N-1)
            rb = random.randint(0, 2**N-1)
            assert uadd(S, A, B, ra, rb) == ra + rb

def test_signed_add():
    A = bitvec('A', 8)
    B = bitvec('B', 8)

    for adder in (rca, ksa, bka):
        S, C = adder(A, B)

        # 0 + 0 = 0
        assert sadd(S, A, B, 0, 0) == 0
        # -64 + -64 = -128
        assert sadd(S, A, B, -64, -64) == -128
        # -1 + 1 = 0
        assert sadd(S, A, B, -1, 1) == 0
        # -64 + 64 = 0
        assert sadd(S, A, B, -64, 64) == 0

        # signed random vectors
        for i in range(NVECS):
            ra = random.randint(-2**6, 2**6-1) # -64..63
            rb = random.randint(-2**6, 2**6)   # -64..64
            assert sadd(S, A, B, ra, rb) == ra + rb

        # 64 + 64, overflow
        R = C.vrestrict({A: int2vec(64, 8), B: int2vec(64, 8)})
        assert R[7] != R[6]
        # -65 + -64, overflow
        R = C.vrestrict({A: int2vec(-65, 8), B: int2vec(-64, 8)})
        assert R[7] != R[6]
