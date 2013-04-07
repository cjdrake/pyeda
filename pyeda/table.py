"""
Boolean Tables

Interface Functions:
    expr2truthtable
    truthtable2expr

Interface Classes:
    TruthTable
"""

from pyeda.common import (
    bit_on, boolify, pcify, cached_property,
    PC_VOID, PC_ONE, PC_ZERO, PC_DC
)
from pyeda.boolfunc import iter_points, index2term, Function
from pyeda.expr import Or, And

PC_STR = {
    PC_VOID : '?',
    PC_ZERO : '0',
    PC_ONE  : '1',
    PC_DC   : 'X'
}

COUNT_ONES = {n: sum(bit_on(n, i) for i in range(8))
              for n in range(256)}

PC_COUNT_ONES = {n: sum((n >> i) & 3 == PC_ONE for i in range(0, 8, 2))
                 for n in range(256)}

def expr2truthtable(expr):
    """Convert an expression into a truth table."""
    return TruthTable(expr.inputs, expr.iter_image())

def truthtable2expr(tt, conj=False):
    """Convert a truth table into an expression."""
    terms = list()
    for n in range(tt.cardinality):
        q, r = divmod(n * tt.width, 8)
        byte = tt.data[q]
        output = (byte >> r) & tt.mask
        if conj:
            if (not tt.pc and output == 0) or (tt.pc and output == PC_ZERO):
                terms.append(index2term(n, tt.inputs, True))
        else:
            if (not tt.pc and output == 1) or (tt.pc and output == PC_ONE):
                terms.append(index2term(n, tt.inputs, False))
    if conj:
        return And(*[Or(*term) for term in terms])
    else:
        return Or(*[And(*term) for term in terms])


class TruthTable(Function):

    def __new__(cls, inputs, outputs, pc=False):
        inputs = tuple(inputs)
        data = bytearray()

        width = 2 if pc else 1
        pos = n = 0
        for output in outputs:
            output = pcify(output) if pc else boolify(output)
            if pos == 0:
                data.append(0)
            data[-1] += output << pos
            pos = (pos + width) & 7
            n += 1
        assert n == 1 << len(inputs)

        if len(inputs) == 0:
            return output
        else:
            self = super(TruthTable, cls).__new__(cls)
            self._inputs = inputs
            self.data = data
            self.pc = pc
            return self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        s = ["inputs: "]
        s.append(" ".join(str(v) for v in reversed(self._inputs)))
        s.append("\n")
        for n in range(self.cardinality):
            s.append(_bin_zext(n, self.degree))
            s.append(" ")
            q, r = divmod(n * self.width, 8)
            byte = self.data[q]
            output = (byte >> r) & self.mask
            if self.pc:
                s.append(PC_STR[output])
            else:
                s.append(str(output))
            s.append("\n")
        return "".join(s)

    # From Function
    @cached_property
    def support(self):
        return frozenset(self._inputs)

    @property
    def inputs(self):
        return self._inputs

    def reduce(self):
        return self

    def restrict(self, point):
        intersect = {v: val for v, val in point.items() if v in self.support}
        if intersect:
            inputs = (v for v in self.inputs if v not in point)
            outputs = self._iter_restrict(intersect)
            return TruthTable(inputs, outputs, pc=self.pc)
        else:
            return self

    def _iter_restrict(self, point):
        for n in range(self.cardinality):
            q, r = divmod(n * self.width, 8)
            _point = {v: bit_on(n, i) for i, v in enumerate(self._inputs)
                      if v in point}
            if _point == point:
                byte = self.data[q]
                yield (byte >> r) & self.mask

    def satisfy_count(self):
        if self.pc:
            return sum(PC_COUNT_ONES[byte] for byte in self.data)
        else:
            return sum(COUNT_ONES[byte] for byte in self.data)

    # Specific to TruthTable
    @cached_property
    def width(self):
        return 2 if self.pc else 1

    @cached_property
    def mask(self):
        return (1 << self.width) - 1


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
