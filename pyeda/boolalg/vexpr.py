"""
Boolean Vector Logic Expressions

Interface Functions:
    bitvec
    uint2vec
    int2vec

Interface Classes:
    BitVector
"""

from pyeda.boolalg.boolfunc import Slicer, VectorFunction
from pyeda.boolalg.expr import exprvar, Not, Or, And, Xor
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

def uint2vec(num, length=None):
    """Convert an unsigned integer to a BitVector."""
    if num < 0:
        raise ValueError("expected num >= 0")

    _num = num
    items = list()
    while _num != 0:
        items.append(_num & 1)
        _num >>= 1

    if length:
        if length < len(items):
            fstr = "overflow: num = {} requires length >= {}, got length = {}"
            raise ValueError(fstr.format(num, len(items), length))
        else:
            while len(items) < length:
                items.append(0)

    return BitVector(items)

def int2vec(num, length=None):
    """Convert a signed integer to a BitVector."""
    if num < 0:
        req_length = clog2(abs(num)) + 1
        bv = uint2vec(2 ** req_length + num)
    else:
        req_length = clog2(num + 1) + 1
        bv = uint2vec(num, req_length)

    if length:
        if length < req_length:
            fstr = "overflow: num = {} requires length >= {}, got length = {}"
            raise ValueError(fstr.format(num, req_length, length))
        else:
            bv.sext(length - req_length)

    return bv


class BitVector(VectorFunction):
    """Vector Expression with logical functions."""

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.items)

    # Operators
    def uor(self):
        """Return the unary OR of a vector of expressions."""
        return Or(*self)

    def uand(self):
        """Return the unary AND of a vector of expressions."""
        return And(*self)

    def uxor(self):
        """Return the unary XOR of a vector of expressions."""
        return Xor(*self)

    def __invert__(self):
        items = [Not(f) for f in self]
        return self.__class__(items, self.start)

    def __or__(self, other):
        items = [Or(*t) for t in zip(self, other)]
        return self.__class__(items)

    def __and__(self, other):
        items = [And(*t) for t in zip(self, other)]
        return self.__class__(items)

    def __xor__(self, other):
        items = [Xor(*t) for t in zip(self, other)]
        return self.__class__(items)

    # Shift operators
    def lsh(self, num, cin=None):
        """Return the vector left shifted by N places."""
        if num < 0 or num > self.__len__():
            raise ValueError("expected 0 <= num <= {}".format(self.__len__()))
        if cin is None:
            cin = BitVector([0] * num)
        else:
            if len(cin) != num:
                raise ValueError("expected length of cin to be equal to num")
        if num == 0:
            return self, BitVector([])
        else:
            return ( BitVector(cin.items + self.items[:-num], self.start),
                     BitVector(self.items[-num:]) )

    def rsh(self, num, cin=None):
        """Return the vector right shifted by N places."""
        if num < 0 or num > self.__len__():
            raise ValueError("expected 0 <= num <= {}".format(self.__len__()))
        if cin is None:
            cin = BitVector([0] * num)
        else:
            if len(cin) != num:
                raise ValueError("expected length of cin to be equal to num")
        if num == 0:
            return self, BitVector([])
        else:
            return ( BitVector(self.items[num:] + cin.items, self.start),
                     BitVector(self.items[:num]) )

    def arsh(self, num):
        """Return the vector arithmetically right shifted by N places."""
        if num < 0 or num > self.__len__():
            raise ValueError("expected 0 <= num <= {}".format(self.__len__()))
        if num == 0:
            return self, BitVector([])
        else:
            sign = self.items[-1]
            return ( BitVector(self.items[num:] + [sign] * num, self.start),
                     BitVector(self.items[:num]) )

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

        >>> A = bitvec('a', 2)
        >>> d = A.decode()
        >>> d.vrestrict({A: "00"})
        [1, 0, 0, 0]
        >>> d.vrestrict({A: "10"})
        [0, 1, 0, 0]
        >>> d.vrestrict({A: "01"})
        [0, 0, 1, 0]
        >>> d.vrestrict({A: "11"})
        [0, 0, 0, 1]
        """
        items = [ And(*[ f if bit_on(i, j) else -f
                         for j, f in enumerate(self) ])
                  for i in range(2 ** len(self)) ]
        return self.__class__(items)
