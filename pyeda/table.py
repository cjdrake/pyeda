"""
Boolean Tables

Interface Functions:
    expr2truthtable
    truthtable2expr

Interface Classes:
    TruthTable
    PCTable
"""

import functools

from pyeda import boolfunc
from pyeda.common import (
    boolify, pcify, cached_property,
    PC_VOID, PC_ONE, PC_ZERO, PC_DC
)
from pyeda.expr import Or, And

PC2STR = {
    PC_VOID : '?',
    PC_ZERO : '0',
    PC_ONE  : '1',
    PC_DC   : '-'
}

NIBBLE2PC = {
    0b0000: 0b10101010,
    0b0001: 0b10101001,
    0b0010: 0b10100110,
    0b0011: 0b10100101,
    0b0100: 0b10011010,
    0b0101: 0b10011001,
    0b0110: 0b10010110,
    0b0111: 0b10010101,
    0b1000: 0b01101010,
    0b1001: 0b01101001,
    0b1010: 0b01100110,
    0b1011: 0b01100101,
    0b1100: 0b01011010,
    0b1101: 0b01011001,
    0b1110: 0b01010110,
    0b1111: 0b01010101,
}

def expr2truthtable(expr):
    """Convert an expression into a truth table."""
    return TruthTable(expr.inputs, expr.iter_image())

def truthtable2expr(tt, conj=False):
    """Convert a truth table into an expression."""
    if conj:
        outer, inner = (And, Or)
        points = tt.iter_zeros()
    else:
        outer, inner = (Or, And)
        points = tt.iter_ones()
    terms = [boolfunc.point2term(point, conj) for point in points]
    return outer(*[inner(*term) for term in terms])


class _BaseTruthTable(boolfunc.Function):
    """Base class for TruthTable and PCTable"""

    def __new__(cls, inputs, outputs):
        inputs = tuple(inputs)
        data = bytearray()

        pos = n = 0
        for output in outputs:
            output = cls.param2output(output)
            if pos == 0:
                data.append(0)
            data[-1] += (output << pos)
            pos = (pos + cls.WIDTH) & 7
            n += 1
        assert n == (1 << len(inputs))

        if len(inputs) == 0:
            return output
        else:
            self = super(_BaseTruthTable, cls).__new__(cls)
            self._inputs = inputs
            self.data = data
            return self

    def __str__(self):
        parts = ["inputs: "]
        parts.append(" ".join(str(v) for v in reversed(self._inputs)))
        parts.append("\n")
        n = q = 0
        while n < self.cardinality:
            byte = self.data[q]
            r = 0
            while r < 8 and n < self.cardinality:
                parts.append(_bin_zext(n, self.degree))
                parts.append(" ")
                output = (byte >> r) & self.MASK
                parts.append(self.output2str(output))
                parts.append("\n")
                r += self.WIDTH
                n += 1
            q += 1
        return "".join(parts)

    def __repr__(self):
        return self.__str__()

    # Operators
    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if other == 0:
            return 1
        elif other == 1:
            return self
        else:
            return self.__add__(-other)

    def __rsub__(self, other):
        return self.__neg__().__add__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    # From Function
    @cached_property
    def support(self):
        return frozenset(self._inputs)

    @property
    def inputs(self):
        return self._inputs

    def reduce(self):
        return self

    def compose(self, mapping):
        raise NotImplementedError()

    def satisfy_all(self):
        for point in self.iter_ones():
            yield point

    def satisfy_count(self):
        return sum(1 for _ in self.satisfy_all())

    def is_neg_unate(self, vs=None):
        raise NotImplementedError()

    def is_pos_unate(self, vs=None):
        raise NotImplementedError()

    def smoothing(self, vs=None):
        return functools.reduce(self.__class__.__add__, self.cofactors(vs))

    def consensus(self, vs=None):
        return functools.reduce(self.__class__.__mul__, self.cofactors(vs))

    def derivative(self, vs=None):
        return functools.reduce(self.__class__.xor, self.cofactors(vs))

    # Helper methods
    def _iter_restrict(self, point):
        inputs = list(self.inputs)
        unmapped = dict()
        for i, v in enumerate(self.inputs):
            if v in point:
                inputs[i] = point[v]
            else:
                unmapped[v] = i

        vs = sorted(unmapped.keys())
        for n in range(1 << len(vs)):
            for v, val in boolfunc.num2point(n, vs).items():
                inputs[unmapped[v]] = val
            index = sum((val << i) for i, val in enumerate(inputs))
            q, r = divmod(index * self.WIDTH, 8)
            yield (self.data[q] >> r) & self.MASK


class TruthTable(_BaseTruthTable):
    """Boolean function represented by a truth table"""

    WIDTH = 1
    MASK = 1

    @staticmethod
    def param2output(output):
        return boolify(output)

    @staticmethod
    def output2str(output):
        return str(output)

    # Operators
    def __neg__(self):
        obj = super(_BaseTruthTable, self).__new__(TruthTable)
        obj._inputs = self._inputs
        obj.data = bytearray(255 - byte for byte in self.data)
        return obj

    def __add__(self, other):
        if other == 0:
            return self
        elif other == 1:
            return 1
        elif isinstance(other, PCTable):
            return self.to_pctable() + other

        inputs = sorted(self.support | other.support)
        def outputs():
            for point in boolfunc.iter_points(inputs):
                yield self.restrict(point) | other.restrict(point)
        return TruthTable(inputs, outputs())

    def __mul__(self, other):
        if other == 0:
            return 0
        elif other == 1:
            return self
        elif isinstance(other, PCTable):
            return self.to_pctable() * other

        inputs = sorted(self.support | other.support)
        def outputs():
            for point in boolfunc.iter_points(inputs):
                yield self.restrict(point) & other.restrict(point)
        return TruthTable(inputs, outputs())

    def xor(self, other):
        if other == 0:
            return self
        elif other == 1:
            return self.__neg__()
        elif isinstance(other, PCTable):
            return self.to_pctable().xor(other)

        inputs = sorted(self.support | other.support)
        def outputs():
            for point in boolfunc.iter_points(inputs):
                yield self.restrict(point) ^ other.restrict(point)
        return TruthTable(inputs, outputs())

    # From Function
    def iter_zeros(self):
        n = q = 0
        while n < self.cardinality:
            byte = self.data[q]
            if byte != 255:
                r = 0
                while r < 8 and n < self.cardinality:
                    output = (byte >> r) & self.MASK
                    if output == 0:
                        yield boolfunc.num2point(n, self.inputs)
                    r += self.WIDTH
                    n += 1
            else:
                n += 8
            q += 1

    def iter_ones(self):
        n = q = 0
        while n < self.cardinality:
            byte = self.data[q]
            if byte != 0:
                r = 0
                while r < 8 and n < self.cardinality:
                    output = (byte >> r) & self.MASK
                    if output == 1:
                        yield boolfunc.num2point(n, self.inputs)
                    r += self.WIDTH
                    n += 1
            else:
                n += 8
            q += 1

    def restrict(self, point):
        intersect = {v: val for v, val in point.items() if v in self.support}
        if intersect:
            inputs = (v for v in self.inputs if v not in point)
            outputs = self._iter_restrict(intersect)
            return TruthTable(inputs, outputs)
        else:
            return self

    def satisfy_one(self):
        n = q = 0
        while n < self.cardinality:
            byte = self.data[q]
            if byte != 0:
                r = 0
                while r < 8 and n < self.cardinality:
                    output = (byte >> r) & self.MASK
                    if output == 1:
                        return boolfunc.num2point(n, self.inputs)
                    r += self.WIDTH
                    n += 1
            else:
                n += 8
            q += 1
        return None

    # Specific to TruthTable
    def to_pctable(self):
        obj = super(_BaseTruthTable, self).__new__(PCTable)
        obj._inputs = self._inputs
        obj.data = bytearray()
        for byte in self.data:
            obj.data.append(NIBBLE2PC[byte & 0xF])
            obj.data.append(NIBBLE2PC[byte >> 4])
        return obj


class PCTable(_BaseTruthTable):
    """
    Boolean function represented by a truth table encoded using
    positional cube notation.

    00: VOID
    01: 1
    10: 0
    11: DC
    """

    WIDTH = 2
    MASK = 3

    @staticmethod
    def param2output(output):
        return pcify(output)

    @staticmethod
    def output2str(output):
        return PC2STR[output]

    # Operators
    def __neg__(self):
        obj = super(_BaseTruthTable, self).__new__(PCTable)
        obj._inputs = self._inputs
        obj.data = bytearray(((byte & 0x55) << 1) | ((byte & 0xAA) >> 1)
                             for byte in self.data)
        return obj

    def __add__(self, other):
        if other == 0:
            return self
        elif other == 1:
            return 1
        elif isinstance(other, TruthTable):
            other = other.to_pctable()

        inputs = sorted(self.support | other.support)
        def outputs():
            for point in boolfunc.iter_points(inputs):
                ab = self.restrict(point)
                cd = other.restrict(point)
                # a * c, b + d
                output = (ab & cd) & 2 | (ab | cd) & 1
                yield self.output2str(output)
        return PCTable(inputs, outputs())

    def __mul__(self, other):
        if other == 0:
            return 0
        elif other == 1:
            return self
        elif isinstance(other, TruthTable):
            other = other.to_pctable()

        inputs = sorted(self.support | other.support)
        def outputs():
            for point in boolfunc.iter_points(inputs):
                ab = self.restrict(point)
                cd = other.restrict(point)
                # a + c, b * d
                output = (ab | cd) & 2 | (ab & cd) & 1
                yield self.output2str(output)
        return PCTable(inputs, outputs())

    def xor(self, other):
        if other == 0:
            return self
        elif other == 1:
            return self.__neg__()
        elif isinstance(other, TruthTable):
            other = other.to_pctable()

        inputs = sorted(self.support | other.support)
        def outputs():
            for point in boolfunc.iter_points(inputs):
                ab = self.restrict(point)
                cd = other.restrict(point)
                a, b, c, d = ab >> 1, ab & 1, cd >> 1, cd & 1
                # a * c + b * d, a * d + b * c
                output = ( ((a & c | b & d) << 1) |
                           (a & d | b & c) )
                yield self.output2str(output)
        return TruthTable(inputs, outputs())

    # From Function
    def iter_zeros(self):
        n = q = 0
        while n < self.cardinality:
            byte = self.data[q]
            if byte & 0xAA:
                r = 0
                while r < 8 and n < self.cardinality:
                    output = (byte >> r) & self.MASK
                    if output & 2:
                        yield boolfunc.num2point(n, self.inputs)
                    r += self.WIDTH
                    n += 1
            else:
                n += 8
            q += 1

    def iter_ones(self):
        n = q = 0
        while n < self.cardinality:
            byte = self.data[q]
            if byte & 0x55:
                r = 0
                while r < 8 and n < self.cardinality:
                    output = (byte >> r) & self.MASK
                    if output & 1:
                        yield boolfunc.num2point(n, self.inputs)
                    r += self.WIDTH
                    n += 1
            else:
                n += 8
            q += 1

    def restrict(self, point):
        intersect = {v: val for v, val in point.items() if v in self.support}
        if intersect:
            inputs = (v for v in self.inputs if v not in point)
            outputs = (self.output2str(output)
                       for output in self._iter_restrict(intersect))
            return PCTable(inputs, outputs)
        else:
            return self

    def satisfy_one(self):
        n = q = 0
        while n < self.cardinality:
            byte = self.data[q]
            if byte & 0x55:
                r = 0
                while r < 8 and n < self.cardinality:
                    output = (byte >> r) & self.MASK
                    if output & 1:
                        return boolfunc.num2point(n, self.inputs)
                    r += self.WIDTH
                    n += 1
            else:
                n += 8
            q += 1
        return None


def _bin_zext(num, w=None):
    """Convert a base-10 number to a binary string.

    Parameters
    num: int
    w: int, optional
        Zero-extend the string to this width.
    Examples
    --------

    >>> _bin_zext(42)
    '101010'
    >>> _bin_zext(42, 8)
    '00101010'
    """
    s = bin(num)[2:]
    if w is None:
        return s
    else:
        return "0" * (w - len(s)) + s
