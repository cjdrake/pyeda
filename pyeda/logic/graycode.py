"""
Logic functions for gray code

Interface Functions:
    bin2gray
    gray2bin
"""

# Disable "invalid variable name"
# pylint: disable=C0103

from pyeda.boolalg.bfarray import cat, farray

def bin2gray(B):
    """Convert a binary-coded vector into a gray-coded vector."""
    return cat(B[:-1] ^ B[1:], B[-1])

def gray2bin(G):
    """Convert a gray-coded vector into a binary-coded vector."""
    return farray([G[i:].uxor() for i, _ in enumerate(G)])

