"""
Test logic functions for gray code
"""

from pyeda.boolalg.vexpr import bitvec, uint2vec
from pyeda.logic.graycode import bin2gray, gray2bin

def test_bin2gray():
    B = bitvec('B', 4)
    G = bin2gray(B)
    gnums = [G.vrestrict({B: uint2vec(i, 4)}).to_uint() for i in range(16)]
    assert gnums == [0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8]

def test_gray2bin():
    G = bitvec('G', 4)
    B = gray2bin(G)
    gnums = [0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8]
    bnums = [B.vrestrict({G: uint2vec(i, 4)}).to_uint() for i in gnums]
    assert bnums == list(range(16))
