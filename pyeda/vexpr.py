"""
Boolean Vector Logic Expressions

Interface Functions:
    bitvec
    sbitvec
    uint2vec
    int2vec

Interface Classes:
    VectorExpression
        BitVector
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from pyeda.common import clog2, bit_on
from pyeda.boolfunc import VectorFunction as VF
from pyeda.expr import var, Not, Or, And, Xor, Xnor

def bitvec(name, *args, bnr=VF.UNSIGNED):
    """Return a vector of variables."""
    if len(args) == 0:
        raise TypeError("bitvec() expected at least two argument")
    elif len(args) == 1:
        start, stop = 0, args[0]
    elif len(args) == 2:
        start, stop = args
    else:
        raise TypeError("bitvec() expected at most three arguments")
    if not (0 <= start < stop):
        raise ValueError("invalid range: [{}:{}]".format(start, stop))
    fs = [var(name, i) for i in range(start, stop)]
    return BitVector(*fs, start=start, bnr=bnr)

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


class VectorExpression(VF):
    """Vector Boolean function"""

    def __str__(self):
        return str(self.fs)

    # Operators
    def uor(self):
        return Or(*self.fs)

    def uand(self):
        return And(*self.fs)

    def uxor(self):
        return Xor(*self.fs)

    def __invert__(self):
        fs = [Not(v) for v in self.fs]
        return self.__class__(*fs, start=self._start, bnr=self._bnr)

    def __or__(self, other):
        assert isinstance(other, VectorExpression) and len(self) == len(other)
        return self.__class__(*[Or(*t) for t in zip(self.fs, other.fs)])

    def __and__(self, other):
        assert isinstance(other, VectorExpression) and len(self) == len(other)
        return self.__class__(*[And(*t) for t in zip(self.fs, other.fs)])

    def __xor__(self, other):
        assert isinstance(other, VectorExpression) and len(self) == len(other)
        return self.__class__(*[Xor(*t) for t in zip(self.fs, other.fs)])


class BitVector(VectorExpression):
    """Vector Expression with logical functions."""

    def eq(self, B):
        """Return symbolic logic for equivalence of two bit vectors."""
        assert isinstance(B, BitVector) and len(self) == len(B)
        return And(*[Xnor(*t) for t in zip(self.fs, B.fs)])

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
        fs = [ And(*[ f if bit_on(i, j) else -f
                      for j, f in enumerate(self.fs) ])
               for i in range(2 ** len(self)) ]
        return BitVector(*fs)

    def ripple_carry_add(self, B, ci=0):
        """Return symbolic logic for an N-bit ripple carry adder."""
        assert isinstance(B, BitVector) and len(self) == len(B)
        if self.bnr == VF.TWOS_COMPLEMENT or B.bnr == VF.TWOS_COMPLEMENT:
            sum_bnr = VF.TWOS_COMPLEMENT
        else:
            sum_bnr = VF.UNSIGNED
        S = BitVector(bnr=sum_bnr)
        C = BitVector()
        for i, A in enumerate(self.fs):
            carry = (ci if i == 0 else C[i-1])
            S.append(Xor(A, B.getifz(i), carry))
            C.append(A * B.getifz(i) + A * carry + B.getifz(i) * carry)
        return S, C
