"""
Boolean Tables

Globals:
    TTVARIABLES

Interface Functions:
    ttvar
    expr2truthtable
    truthtable2expr

Interface Classes:
    TruthTable
    TTVariable
"""

import array
import functools

from pyeda import boolfunc
from pyeda.common import (
    pcify, cached_property,
    PC_VOID, PC_ONE, PC_ZERO, PC_DC
)
from pyeda.expr import EXPRVARIABLES, Or, And

# existing TTVariable references
TTVARIABLES = dict()

_PC2STR = {
    PC_VOID : '?',
    PC_ZERO : '0',
    PC_ONE  : '1',
    PC_DC   : '-'
}

_PC2NUM = {
    PC_ZERO: 0,
    PC_ONE: 1,
    PC_DC: 1,
}

def ttvar(name, indices=None, namespace=None):
    """Return a TruthTable variable.

    Parameters
    ----------
    name : str
        The variable's identifier string.
    indices : int or tuple[int], optional
        One or more integer suffixes for variables that are part of a
        multi-dimensional bit-vector, eg x[1], x[1][2][3]
    namespace : str or tuple[str], optional
        A container for a set of variables. Since a Variable instance is global,
        a namespace can be used for local scoping.
    """
    return TTVariable(name, indices, namespace)

def expr2truthtable(expr):
    """Convert an expression into a truth table."""
    inputs = [TTVariable(v.name, v.indices, v.namespace) for v in expr.inputs]
    return TruthTable(inputs, expr.iter_image())

def truthtable2expr(tt, conj=False):
    """Convert a truth table into an expression."""
    if conj:
        outer, inner = (And, Or)
        points = tt.iter_zeros()
    else:
        outer, inner = (Or, And)
        points = tt.iter_ones()
    points = ({EXPRVARIABLES[v.uniqid]: val for v, val in point.items()}
              for point in points)
    terms = [boolfunc.point2term(point, conj) for point in points]
    return outer(*[inner(*term) for term in terms])


class PCData(object):
    """
    Positional cube data.

    This class packs PC data items into a Python stdlib array.
    The 2^N indices cover a Boolean space of dimension N.
    """

    _NEG = {
        PC_VOID : PC_VOID,
        PC_ONE  : PC_ZERO,
        PC_ZERO : PC_ONE,
        PC_DC   : PC_DC,
    }

    def __init__(self, items):
        data = array.array('L')
        width = data.itemsize << 3

        pos = num = 0
        for item in items:
            if pos == 0:
                data.append(0)
            data[-1] += (item << pos)
            pos = (pos + 2) % width
            num += 1

        self.data = data
        self.width = width
        self._len = num

    def __len__(self):
        return self._len

    def __iter__(self):
        num = quotient = 0
        while num < self._len:
            chunk = self.data[quotient]
            remainder = 0
            while remainder < self.width and num < self._len:
                item = (chunk >> remainder) & 3
                yield item
                remainder += 2
                num += 1
            quotient += 1

    def __neg__(self):
        return PCData(self._NEG[item] for item in self)

    def __getitem__(self, num):
        quotient, remainder = divmod(num, (self.width >> 1))
        return (self.data[quotient] >> (remainder << 1)) & 3

    @cached_property
    def zero_mask(self):
        """Return a mask to determine whether an array chunk has any zeros."""
        accum = 0
        for i in range(self.data.itemsize):
            accum += (0xAA << (i << 3))
        return accum

    @cached_property
    def one_mask(self):
        """Return a mask to determine whether an array chunk has any ones."""
        accum = 0
        for i in range(self.data.itemsize):
            accum += (0x55 << (i << 3))
        return accum

    def iter_zeros(self):
        """Iterate through the indices of all zero items."""
        num = quotient = 0
        while num < self._len:
            chunk = self.data[quotient]
            if chunk & self.zero_mask:
                remainder = 0
                while remainder < self.width and num < self._len:
                    item = (chunk >> remainder) & 3
                    if item & 2:
                        yield num
                    remainder += 2
                    num += 1
            else:
                num += (self.width >> 1)
            quotient += 1

    def find_one(self):
        """
        Return the first index of an entry that is either one or DC.
        If no item is found, return None.
        """
        num = quotient = 0
        while num < self._len:
            chunk = self.data[quotient]
            if chunk & self.one_mask:
                remainder = 0
                while remainder < self.width and num < self._len:
                    item = (chunk >> remainder) & 3
                    if item & 1:
                        return num
                    remainder += 2
                    num += 1
            else:
                num += (self.width >> 1)
            quotient += 1
        return None

    def iter_ones(self):
        """Iterate through all items that are either one or DC."""
        num = quotient = 0
        while num < self._len:
            chunk = self.data[quotient]
            if chunk & self.one_mask:
                remainder = 0
                while remainder < self.width and num < self._len:
                    item = (chunk >> remainder) & 3
                    if item & 1:
                        yield num
                    remainder += 2
                    num += 1
            else:
                num += (self.width >> 1)
            quotient += 1


class TruthTable(boolfunc.Function):
    """Boolean function represented by a truth table."""

    def __new__(cls, inputs, outputs):
        inputs = tuple(inputs)
        pcdata = PCData(pcify(output) for output in outputs)
        assert len(pcdata) == (1 << len(inputs))

        if len(inputs) == 0:
            return _PC2NUM[pcdata[0]]
        else:
            self = super(TruthTable, cls).__new__(cls)
            self._inputs = inputs
            self.pcdata = pcdata
            return self

    def __str__(self):
        parts = ["inputs: "]
        parts.append(" ".join(str(v) for v in reversed(self._inputs)))
        parts.append("\n")
        for num, item in enumerate(self.pcdata):
            parts += [_bin_zfill(num, self.degree), " ", _PC2STR[item], "\n"]
        return "".join(parts)

    def __repr__(self):
        return self.__str__()

    # Operators
    def __neg__(self):
        obj = super(TruthTable, self).__new__(TruthTable)
        obj._inputs = self._inputs
        obj.pcdata = -self.pcdata
        return obj

    def __add__(self, other):
        if other == 0:
            return self
        elif other == 1:
            return 1

        inputs = sorted(self.support | other.support)
        def outputs():
            for upoint in boolfunc.iter_upoints(inputs):
                a_b = self._urestrict(upoint).pcdata[0]
                c_d = other._urestrict(upoint).pcdata[0]
                # a * c, b + d
                yield ((a_b & c_d) & 2) | ((a_b | c_d) & 1)

        obj = super(TruthTable, self).__new__(TruthTable)
        obj._inputs = inputs
        obj.pcdata = PCData(outputs())
        return obj

    def __sub__(self, other):
        if other == 0:
            return 1
        elif other == 1:
            return self
        else:
            return self.__add__(other.__neg__())

    def __mul__(self, other):
        if other == 0:
            return 0
        elif other == 1:
            return self

        inputs = sorted(self.support | other.support)
        def outputs():
            for upoint in boolfunc.iter_upoints(inputs):
                a_b = self._urestrict(upoint).pcdata[0]
                c_d = other._urestrict(upoint).pcdata[0]
                # a + c, b * d
                yield ((a_b | c_d) & 2) | ((a_b & c_d) & 1)

        obj = super(TruthTable, self).__new__(TruthTable)
        obj._inputs = inputs
        obj.pcdata = PCData(outputs())
        return obj

    def xor(self, other):
        if other == 0:
            return self
        elif other == 1:
            return self.__neg__()

        inputs = sorted(self.support | other.support)
        def outputs():
            for upoint in boolfunc.iter_upoints(inputs):
                a_b = self._urestrict(upoint).pcdata[0]
                c_d = other._urestrict(upoint).pcdata[0]
                # a * c + b * d, a * d + b * c
                a, b, c, d = a_b >> 1, a_b & 1, c_d >> 1, c_d & 1
                yield (((a & c | b & d) << 1) | (a & d | b & c))

        obj = super(TruthTable, self).__new__(TruthTable)
        obj._inputs = inputs
        obj.pcdata = PCData(outputs())
        return obj

    # From Function
    @cached_property
    def support(self):
        return frozenset(self._inputs)

    @property
    def inputs(self):
        return self._inputs

    def iter_zeros(self):
        for num in self.pcdata.iter_zeros():
            yield boolfunc.num2point(num, self.inputs)

    def iter_ones(self):
        for num in self.pcdata.iter_ones():
            yield boolfunc.num2point(num, self.inputs)

    def reduce(self):
        return self

    def urestrict(self, upoint):
        obj = self._urestrict(upoint)
        if len(obj.inputs) == 0:
            return _PC2NUM[obj.pcdata[0]]
        else:
            return obj

    def _urestrict(self, upoint):
        usupport = {v.uniqid for v in self.support}
        zeros = usupport & upoint[0]
        ones = usupport & upoint[1]
        others = usupport - upoint[0] - upoint[1]
        if zeros or ones:
            obj = super(TruthTable, self).__new__(TruthTable)
            obj._inputs = sorted(TTVARIABLES[uniqid] for uniqid in others)
            gen = (self.pcdata[i] for i in self._iter_restrict(zeros, ones))
            obj.pcdata = PCData(gen)
            return obj
        else:
            return self

    def compose(self, mapping):
        raise NotImplementedError()

    def satisfy_one(self):
        num = self.pcdata.find_one()
        if num is None:
            return None
        else:
            return boolfunc.num2point(num, self.inputs)

    def satisfy_all(self):
        for num in self.pcdata.iter_ones():
            yield boolfunc.num2point(num, self.inputs)

    def satisfy_count(self):
        return sum(1 for _ in self.satisfy_all())

    #def is_neg_unate(self, vs=None):
    #    raise NotImplementedError()

    #def is_pos_unate(self, vs=None):
    #    raise NotImplementedError()

    def smoothing(self, vs=None):
        return functools.reduce(self.__class__.__add__, self.cofactors(vs))

    def consensus(self, vs=None):
        return functools.reduce(self.__class__.__mul__, self.cofactors(vs))

    def derivative(self, vs=None):
        return functools.reduce(self.__class__.xor, self.cofactors(vs))

    # Specific to TruthTable
    def _iter_restrict(self, zeros, ones):
        inputs = list(self.inputs)
        unmapped = dict()
        for i, v in enumerate(self.inputs):
            if v.uniqid in zeros:
                inputs[i] = 0
            elif v.uniqid in ones:
                inputs[i] = 1
            else:
                unmapped[v] = i
        vs = sorted(unmapped.keys())
        for num in range(1 << len(vs)):
            for v, val in boolfunc.num2point(num, vs).items():
                inputs[unmapped[v]] = val
            yield sum((val << i) for i, val in enumerate(inputs))


class TTVariable(boolfunc.Variable, TruthTable):
    """Boolean truth table variable"""

    def __new__(cls, name, indices=None, namespace=None):
        _var = boolfunc.Variable(name, indices, namespace)
        uniqid = _var.uniqid
        try:
            self = TTVARIABLES[uniqid]
        except KeyError:
            self = boolfunc.Function.__new__(cls)
            self._inputs = [self]
            self.data = array.array('L', [0b0110])
            self._var = _var
            TTVARIABLES[uniqid] = self
        return self

    # From Variable
    @property
    def uniqid(self):
        return self._var.uniqid

    @property
    def namespace(self):
        return self._var.namespace

    @property
    def name(self):
        return self._var.name

    @property
    def indices(self):
        return self._var.indices


def _bin_zfill(num, width=None):
    """Convert a base-10 number to a binary string.

    Parameters
    num: int
    width: int, optional
        Zero-extend the string to this width.
    Examples
    --------

    >>> _bin_zfill(42)
    '101010'
    >>> _bin_zfill(42, 8)
    '00101010'
    """
    s = bin(num)[2:]
    return s if width is None else s.zfill(width)
