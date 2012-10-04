"""
Boolean Vector Logic Expressions

Interface Functions:
    bitvec
    sbitvec
    uint2vec
    int2vec

Interface Classes:
    BitVector
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from pyeda.common import clog2, bit_on
from pyeda.boolfunc import Slicer, VectorFunction as VF
from pyeda.expr import var, Not, Or, And, Xor, Xnor

def bitvec(name, *args, **kwargs):
    """Return a vector of variables."""
    bnr = kwargs.get("bnr", VF.UNSIGNED)
    slices = list()
    for arg in args:
        if type(arg) is int:
            slices.append(slice(0, arg))
        elif type(arg) is tuple and len(arg) == 2:
            slices.append(slice(*arg))
        else:
            raise ValueError("invalid argument")
    return _rbitvec(name, slices, tuple(), bnr)

def _rbitvec(name, slices, indices, bnr):
    fst, rst = slices[0], slices[1:]
    if rst:
        items = [ _rbitvec(name, rst, indices + (i, ), bnr)
                  for i in range(fst.start, fst.stop) ]
        return Slicer(items, fst.start)
    else:
        vs = [var(name, *(indices + (i, ))) for i in range(fst.start, fst.stop)]
        return BitVector(vs, (fst.start, fst.stop), bnr=bnr)

def sbitvec(name, *args):
    """Return a signed vector of variables."""
    return bitvec(name, *args, bnr=VF.TWOS_COMPLEMENT)

def uint2vec(num, length=None):
    """Convert an unsigned integer to a BitVector."""
    assert num >= 0

    items = list()
    while num != 0:
        items.append(num & 1)
        num >>= 1

    if length:
        if length < len(items):
            raise ValueError("overflow: " + str(num))
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
    bv.bnr = VF.TWOS_COMPLEMENT

    if length:
        if length < req_length:
            raise ValueError("overflow: " + str(num))
        else:
            bv.ext(length - req_length)

    return bv


class BitVector(VF):
    """Vector Expression with logical functions."""

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.items)

    # Operators
    def uor(self):
        return Or(*self)

    def uand(self):
        return And(*self)

    def uxor(self):
        return Xor(*self)

    def __invert__(self):
        items = [Not(f) for f in self]
        return self.__class__(items, bnr=self.bnr)

    def __or__(self, other):
        items = [Or(*t) for t in zip(self, other)]
        return self.__class__(items)

    def __and__(self, other):
        items = [And(*t) for t in zip(self, other)]
        return self.__class__(items)

    def __xor__(self, other):
        items = [Xor(*t) for t in zip(self, other)]
        return self.__class__(items)

    # Common logic
    def eq(self, B):
        """Return symbolic logic for equivalence of two bit vectors."""
        assert isinstance(B, BitVector) and len(self) == len(B)
        return And(*[Xnor(*t) for t in zip(self, B)])

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

        >>> a = bitvec('a', 2)
        >>> d = a.decode()
        >>> d.vrestrict({a: "00"})
        [1, 0, 0, 0]
        >>> d.vrestrict({a: "10"})
        [0, 1, 0, 0]
        >>> d.vrestrict({a: "01"})
        [0, 0, 1, 0]
        >>> d.vrestrict({a: "11"})
        [0, 0, 0, 1]
        """
        items = [ And(*[ f if bit_on(i, j) else -f
                         for j, f in enumerate(self) ])
                  for i in range(2 ** len(self)) ]
        return self.__class__(items)
