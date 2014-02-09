"""
Boolean Vector Logic Expressions

Interface Functions:
    bitvec
    uint2bv
    int2bv

Interface Classes:
    BitVector
"""

import functools
import operator

from pyeda.boolalg.boolfunc import Slicer, VectorFunction
from pyeda.boolalg.expr import exprvar, CONSTANTS
from pyeda.util import clog2, bit_on

def bitvec(name, *slices):
    """Return a BitVector with an arbitrary number of slices.

    Parameters
    ----------
    name : str
    slices : (int or (int, int))
        An int N means a slice from [0:N]
        A tuple (M, N) means a slice from [M:N]
    """
    if not slices:
        return exprvar(name)

    sls = list()
    for sl in slices:
        if type(sl) is int:
            sls.append(slice(0, sl))
        elif type(sl) is tuple and len(sl) == 2:
            if sl[0] < sl[1]:
                sls.append(slice(sl[0], sl[1]))
            else:
                sls.append(slice(sl[1], sl[0]))
        else:
            fstr = "expected slice to be an int or (int, int), got {0.__name__}"
            raise TypeError(fstr.format(type(sl)))
    return _bitvec(name, sls, tuple())

def _bitvec(name, slices, indices):
    """Return a BitVector with an arbitrary number of slices.

    NOTE: This is a recursive helper function for 'bitvec'.
          Do not invoke this function directly.
    """
    fst, rst = slices[0], slices[1:]
    if rst:
        items = [_bitvec(name, rst, indices + (i, ))
                 for i in range(fst.start, fst.stop)]
        return Slicer(items, fst.start)
    else:
        vs = [exprvar(name, indices + (i, ))
              for i in range(fst.start, fst.stop)]
        return BitVector(vs, fst.start)

def _uint2items(num, length=None):
    """Convert an unsigned integer to a list of constant expressions."""
    if num == 0:
        items = [CONSTANTS[0]]
    else:
        _num = num
        items = list()
        while _num != 0:
            items.append(CONSTANTS[_num & 1])
            _num >>= 1

    if length:
        if length < len(items):
            fstr = "overflow: num = {} requires length >= {}, got length = {}"
            raise ValueError(fstr.format(num, len(items), length))
        else:
            while len(items) < length:
                items.append(CONSTANTS[0])

    return items

def uint2bv(num, length=None):
    """Convert an unsigned integer to a BitVector."""
    if num < 0:
        raise ValueError("expected num >= 0")
    else:
        return BitVector(_uint2items(num, length))

def int2bv(num, length=None):
    """Convert a signed integer to a BitVector."""
    if num < 0:
        req_length = clog2(abs(num)) + 1
        items = _uint2items(2**req_length + num)
    else:
        req_length = clog2(num + 1) + 1
        items = _uint2items(num, req_length)

    if length:
        if length < req_length:
            fstr = "overflow: num = {} requires length >= {}, got length = {}"
            raise ValueError(fstr.format(num, req_length, length))
        else:
            sign = items[-1]
            items += [sign] * (length - req_length)

    return BitVector(items)


class BitVector(VectorFunction):
    """Vector Expression with logical functions."""

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.items)

    def __add__(self, other):
        return BitVector(self.items + other.items, start=self.start)

    # Operators
    def uor(self):
        """Return the unary OR of a vector of expressions."""
        return functools.reduce(operator.or_, self)

    def unor(self):
        """Return the unary NOR of a vector of expressions."""
        return ~functools.reduce(operator.or_, self)

    def uand(self):
        """Return the unary AND of a vector of expressions."""
        return functools.reduce(operator.and_, self)

    def unand(self):
        """Return the unary NAND of a vector of expressions."""
        return ~functools.reduce(operator.and_, self)

    def uxor(self):
        """Return the unary XOR of a vector of expressions."""
        return functools.reduce(operator.xor, self)

    def uxnor(self):
        """Return the unary XNOR of a vector of expressions."""
        return ~functools.reduce(operator.xor, self)

    def __invert__(self):
        return self.__class__(map(operator.invert, self), self.start)

    def __or__(self, other):
        return self.__class__(x | y for x, y in zip(self, other))

    def __and__(self, other):
        return self.__class__(x & y for x, y in zip(self, other))

    def __xor__(self, other):
        return self.__class__(x ^ y for x, y in zip(self, other))

    def __lshift__(self, arg):
        if type(arg) is tuple and len(arg) == 2:
            return self.lsh(arg[0], arg[1])[0]
        elif type(arg) is int:
            return self.lsh(arg)[0]
        else:
            raise TypeError("expected int or (int, bitvec)")

    def __rshift__(self, arg):
        if type(arg) is tuple and len(arg) == 2:
            return self.rsh(arg[0], arg[1])[0]
        elif type(arg) is int:
            return self.rsh(arg)[0]
        else:
            raise TypeError("expected in or (int, bitvec)")

    # Shift operators
    def lsh(self, num, cin=None):
        """Return the vector left shifted by N places.

        Parameters
        ----------
        num : non-negative int
            Number of places to shift

        cin : bitvec
            The "carry-in" bit vector

        Returns
        -------
        (bitvec V, bitvec cout)
            V is the shifted vector, and cout is the "carry out".
        """
        if num < 0 or num > self.__len__():
            raise ValueError("expected 0 <= num <= {}".format(self.__len__()))
        if cin is None:
            cin = BitVector([CONSTANTS[0] for i in range(num)])
        else:
            if len(cin) != num:
                raise ValueError("expected length of cin to be equal to num")
        if num == 0:
            return self, BitVector([])
        else:
            return (BitVector(cin.items + self.items[:-num]),
                    BitVector(self.items[-num:]))

    def rsh(self, num, cin=None):
        """Return the vector right shifted by N places.

        Parameters
        ----------
        num : non-negative int
            Number of places to shift

        cin : bitvec
            The "carry-in" bit vector

        Returns
        -------
        (bitvec V, bitvec cout)
            V is the shifted vector, and cout is the "carry out".
        """
        if num < 0 or num > self.__len__():
            raise ValueError("expected 0 <= num <= {}".format(self.__len__()))
        if cin is None:
            cin = BitVector([CONSTANTS[0] for i in range(num)])
        else:
            if len(cin) != num:
                raise ValueError("expected length of cin to be equal to num")
        if num == 0:
            return self, BitVector([])
        else:
            return (BitVector(self.items[num:] + cin.items),
                    BitVector(self.items[:num]))

    def arsh(self, num):
        """Return the vector arithmetically right shifted by N places.

        Parameters
        ----------
        num : non-negative int
            Number of places to shift

        Returns
        -------
        bitvec
            The shifted vector
        """
        if num < 0 or num > self.__len__():
            raise ValueError("expected 0 <= num <= {}".format(self.__len__()))
        if num == 0:
            return self, BitVector([])
        else:
            sign = self.items[-1]
            return (BitVector(self.items[num:] + (sign, ) * num),
                    BitVector(self.items[:num]))

    # Other logic
    def decode(self):
        """Return symbolic logic for an N-2^N binary decoder.

        Example Truth Table for a 2:4 decoder:

            +===========+=====================+
            | A[1] A[0] | D[3] D[2] D[1] D[0] |
            +===========+=====================+
            |   0    0  |   0    0    0    1  |
            |   0    1  |   0    0    1    0  |
            |   1    0  |   0    1    0    0  |
            |   1    1  |   1    0    0    0  |
            +===========+=====================+
        """
        items = [functools.reduce(operator.and_, [f if bit_on(i, j) else ~f
                                                  for j, f in enumerate(self)])
                 for i in range(2 ** self.__len__())]
        return self.__class__(items)

