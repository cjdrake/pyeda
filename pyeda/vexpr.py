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
        elif type(arg) is slice:
            slices.append(arg)
        else:
            raise ValueError("invalid argument")
    return _rbitvec(name, slices, tuple(), bnr)

def _rbitvec(name, slices, indices, bnr=VF.UNSIGNED):
    fst, rst = slices[0], slices[1:]
    if rst:
        sls = [ _rbitvec(name, rst, indices + (i, ), bnr)
                for i in range(fst.start, fst.stop) ]
        return Slicer(fst.start, sls)
    else:
        bv = BitVector((fst.start, fst.stop), bnr=bnr)
        for i in range(fst.start, fst.stop):
            bv[i] = var(name, *(indices + (i, )))
        return bv

def sbitvec(name, *args):
    """Return a signed vector of variables."""
    return bitvec(name, *args, bnr=VF.TWOS_COMPLEMENT)

def uint2vec(num, length=None):
    """Convert an unsigned integer to a BitVector."""
    assert num >= 0

    logvec = BitVector()
    while num != 0:
        logvec.append(num & 1)
        num >>= 1

    if length:
        if length < len(logvec):
            raise ValueError("overflow: " + str(num))
        else:
            logvec.ext(length - len(logvec))

    return logvec

def int2vec(num, length=None):
    """Convert a signed integer to a BitVector."""
    if num < 0:
        req_length = clog2(abs(num)) + 1
        logvec = uint2vec(2 ** req_length + num)
    else:
        req_length = clog2(num + 1) + 1
        logvec = uint2vec(num)
        logvec.ext(req_length - len(logvec))
    logvec.bnr = VF.TWOS_COMPLEMENT

    if length:
        if length < req_length:
            raise ValueError("overflow: " + str(num))
        else:
            logvec.ext(length - req_length)

    return logvec


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
        bv = self.__class__(self.sl.start)
        for f in self:
            bv.append(Not(f))
        return bv

    def __or__(self, other):
        assert isinstance(other, BitVector) and len(self) == len(other)
        bv = self.__class__()
        for t in zip(self, other):
            bv.append(Or(*t))
        return bv

    def __and__(self, other):
        assert isinstance(other, BitVector) and len(self) == len(other)
        bv = self.__class__()
        for t in zip(self, other):
            bv.append(And(*t))
        return bv

    def __xor__(self, other):
        assert isinstance(other, BitVector) and len(self) == len(other)
        bv = self.__class__()
        for t in zip(self, other):
            bv.append(Xor(*t))
        return bv

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
        """
        bv = BitVector()
        for i in range(2 ** len(self)):
            bv.append( And(*[ f if bit_on(i, j) else -f
                              for j, f in enumerate(self) ]) )
        return bv

    def ripple_carry_add(self, B, ci=0):
        """Return symbolic logic for an N-bit ripple carry adder."""
        assert isinstance(B, BitVector) and len(self) == len(B)
        if self.bnr == VF.TWOS_COMPLEMENT or B.bnr == VF.TWOS_COMPLEMENT:
            sum_bnr = VF.TWOS_COMPLEMENT
        else:
            sum_bnr = VF.UNSIGNED
        S = BitVector(bnr=sum_bnr)
        C = BitVector()
        for i, A in enumerate(self):
            carry = (ci if i == 0 else C[i-1])
            S.append(Xor(A, B.getifz(i), carry))
            C.append(A * B.getifz(i) + A * carry + B.getifz(i) * carry)
        return S, C
