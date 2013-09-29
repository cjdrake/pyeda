"""
Logic functions for gray code

Interface Functions:
    bin2gray
    gray2bin
"""

# Disable "invalid variable name"
# pylint: disable=C0103

from pyeda.boolalg.expr import Xor
from pyeda.boolalg.vexpr import BitVector

def bin2gray(B):
    """Convert a binary-coded vector into a gray-coded vector."""
    items = [Xor(B[i], B[i+1]) for i in range(B.start, B.stop-1)]
    items.append(B[B.stop-1])
    return BitVector(items, B.start)

def gray2bin(G):
    """Convert a gray-coded vector into a binary-coded vector."""
    items = [G[i:].uxor() for i, _ in enumerate(G, G.start)]
    return BitVector(items, G.start)
