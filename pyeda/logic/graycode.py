"""
Logic functions for gray code

Interface Functions:
    bin2gray
    gray2bin
"""


# Disable 'invalid-name', b/c 'logic' package uses unconventional names
# pylint: disable=C0103


from pyeda.boolalg.bfarray import farray, fcat


def bin2gray(B):
    """Convert a binary-coded vector into a gray-coded vector."""
    return fcat(B[:-1] ^ B[1:], B[-1])


def gray2bin(G):
    """Convert a gray-coded vector into a binary-coded vector."""
    return farray([G[i:].uxor() for i, _ in enumerate(G)])

