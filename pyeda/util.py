"""
The :mod:`pyeda.util` module contains top-level utilities,
such as fundamental functions and decorators.

Interface Functions:

* :func:`bit_on` --- Return the value of a number's bit position
* :func:`clog2` --- Return the ceiling log base two of an integer
* :func:`parity` --- Return the parity of an integer
"""


def bit_on(num: int, bit: int) -> int:
    """Return the value of a number's bit position.

    For example, since :math:`42 = 2^1 + 2^3 + 2^5`,
    this function will return 1 in bit positions 1, 3, 5:

    >>> [bit_on(42, i) for i in range(clog2(42))]
    [0, 1, 0, 1, 0, 1]
    """
    return (num >> bit) & 1


def clog2(num: int) -> int:
    r"""Return the ceiling log base two of an integer :math:`\ge 1`.

    This function tells you the minimum dimension of a Boolean space with at
    least N points.

    For example, here are the values of ``clog2(N)`` for :math:`1 \le N < 18`:

    >>> [clog2(n) for n in range(1, 18)]
    [0, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5]

    This function is undefined for non-positive integers:

    >>> clog2(0)
    Traceback (most recent call last):
        ...
    ValueError: expected num >= 1
    """
    if num < 1:
        raise ValueError("expected num >= 1")
    accum, shifter = 0, 1
    while num > shifter:
        shifter <<= 1
        accum += 1
    return accum


def parity(num: int) -> int:
    """Return the parity of a non-negative integer.

    For example, here are the parities of the first ten integers:

    >>> [parity(n) for n in range(10)]
    [0, 1, 1, 0, 1, 0, 0, 1, 1, 0]

    This function is undefined for negative integers:

    >>> parity(-1)
    Traceback (most recent call last):
        ...
    ValueError: expected num >= 0
    """
    if num < 0:
        raise ValueError("expected num >= 0")
    par = 0
    while num:
        par ^= (num & 1)
        num >>= 1
    return par
