"""
Boolean Vector Logic Expressions

This module is deprecated.
The functionality has been superceded by the bfarray module.

Interface Functions:
    bitvec
"""

from pyeda.boolalg import expr
from pyeda.boolalg import bfarray

def bitvec(name, *dims):
    """Return a new array of given dimensions, filled with Expressions.

    Parameters
    ----------
    name : str
    dims : (int or (int, int))
        An int N means a slice from [0:N]
        A tuple (M, N) means a slice from [M:N]
    """
    if dims:
        return bfarray.exprvars(name, *dims)
    else:
        return expr.exprvar(name)

