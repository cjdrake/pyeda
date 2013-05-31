"""
Boolean Tables

Globals:
    TTVARIABLES

Interface Functions:
    ttvar
    truthtable
    expr2truthtable
    truthtable2expr

Interface Classes:
    TruthTable
    TTConstant
    TTVariable
"""

import array

from pyeda import boolfunc
from pyeda import PC_VOID, PC_ONE, PC_ZERO, PC_DC
from pyeda.common import cached_property
from pyeda.expr import EXPRVARIABLES, Or, And

# existing TTVariable references
TTVARIABLES = dict()

_PC2STR = {
    PC_VOID : '?',
    PC_ZERO : '0',
    PC_ONE  : '1',
    PC_DC   : '-'
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
    bvar = boolfunc.var(name, indices, namespace)
    try:
        var = TTVARIABLES[bvar.uniqid]
    except KeyError:
        var = TTVARIABLES[bvar.uniqid] = TTVariable(bvar)
    return var

def truthtable(inputs, outputs):
    """Return a truth table."""
    def items():
        """Convert all outputs to PC notation."""
        for output in outputs:
            if isinstance(output, boolfunc.Function):
                output = output.unbox()
            if output in (0, '0'):
                yield PC_ZERO
            elif output in (1, '1'):
                yield PC_ONE
            elif output in "-xX":
                yield PC_DC
            else:
                raise ValueError("invalid output: " + str(output))
    inputs = [ttvar(v.name, v.indices, v.namespace) for v in inputs]
    pcdata = PCData(items())
    assert len(pcdata) == (1 << len(inputs))
    return _truthtable(inputs, pcdata)

def _truthtable(inputs, pcdata):
    """Return a truth table."""
    if len(inputs) == 0:
        return {
            PC_ZERO: TTZERO,
            PC_ONE: TTONE,
            PC_DC: TTDC
        }[pcdata[0]]
    elif len(inputs) == 1 and pcdata[0] == PC_ZERO and pcdata[1] == PC_ONE:
        return inputs[0]
    else:
        return TruthTable(inputs, pcdata)

def expr2truthtable(expr):
    """Convert an expression into a truth table."""
    inputs = [ttvar(v.name, v.indices, v.namespace) for v in expr.inputs]
    return truthtable(inputs, expr.iter_image())

def truthtable2expr(tt, conj=False):
    """Convert a truth table into an expression."""
    if conj:
        outer, inner = (And, Or)
        nums = tt.pcdata.iter_zeros()
    else:
        outer, inner = (Or, And)
        nums = tt.pcdata.iter_ones()
    inputs = [EXPRVARIABLES[v.uniqid] for v in tt.inputs]
    terms = [boolfunc.num2term(num, inputs, conj) for num in nums]
    return outer(*[inner(*term) for term in terms])


class PCData(object):
    """
    Positional cube data.

    This class packs PC data items into a Python stdlib array.
    The 2^N indices cover a Boolean space of dimension N.
    """
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

    def __init__(self, inputs, pcdata):
        self._inputs = tuple(inputs)
        self.pcdata = pcdata

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
        def items():
            """Iterate through negated items."""
            sub = {PC_ZERO: PC_ONE, PC_ONE: PC_ZERO, PC_DC: PC_DC}
            for item in self.pcdata:
                yield sub[item]
        pcdata = PCData(items())
        return _truthtable(self._inputs, pcdata)

    def __add__(self, other):
        other = self.box(other)
        inputs = sorted(self.support | other.support)
        def items():
            """Iterate through OR'ed items."""
            for upoint in boolfunc.iter_upoints(inputs):
                a_b = self.urestrict(upoint).pcdata[0]
                c_d = other.urestrict(upoint).pcdata[0]
                # a * c, b + d
                yield ((a_b & c_d) & 2) | ((a_b | c_d) & 1)
        pcdata = PCData(items())
        return _truthtable(inputs, pcdata)

    def __sub__(self, other):
        other = self.box(other)
        return self.__add__(other.__neg__())

    def __mul__(self, other):
        other = self.box(other)
        inputs = sorted(self.support | other.support)
        def items():
            """Iterate through AND'ed items."""
            for upoint in boolfunc.iter_upoints(inputs):
                a_b = self.urestrict(upoint).pcdata[0]
                c_d = other.urestrict(upoint).pcdata[0]
                # a + c, b * d
                yield ((a_b | c_d) & 2) | ((a_b & c_d) & 1)
        pcdata = PCData(items())
        return _truthtable(inputs, pcdata)

    def xor(self, other):
        other = self.box(other)
        inputs = sorted(self.support | other.support)
        def items():
            """Iterate through XOR'ed items."""
            # pylint: disable=C0103
            for upoint in boolfunc.iter_upoints(inputs):
                a_b = self.urestrict(upoint).pcdata[0]
                c_d = other.urestrict(upoint).pcdata[0]
                # a * c + b * d, a * d + b * c
                a, b, c, d = a_b >> 1, a_b & 1, c_d >> 1, c_d & 1
                yield ((a & c | b & d) << 1) | (a & d | b & c)
        pcdata = PCData(items())
        return _truthtable(inputs, pcdata)

    # From Function
    @cached_property
    def support(self):
        return frozenset(self._inputs)

    @property
    def inputs(self):
        return self._inputs

    def urestrict(self, upoint):
        usupport = {v.uniqid for v in self.support}
        zeros = usupport & upoint[0]
        ones = usupport & upoint[1]
        others = usupport - upoint[0] - upoint[1]
        if zeros or ones:
            inputs = sorted(TTVARIABLES[uniqid] for uniqid in others)
            def items():
                """Iterate through restricted outputs."""
                for i in self._iter_restrict(zeros, ones):
                    yield self.pcdata[i]
            pcdata = PCData(items())
            return _truthtable(inputs, pcdata)
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

    def is_neg_unate(self, vs=None):
        raise NotImplementedError()

    def is_pos_unate(self, vs=None):
        raise NotImplementedError()

    def is_zero(self):
        return not self._inputs and self.pcdata[0] == PC_ZERO

    def is_one(self):
        return not self._inputs and self.pcdata[0] == PC_ONE

    @staticmethod
    def box(arg):
        if isinstance(arg, TruthTable):
            return arg
        elif arg == 0 or arg == '0':
            return TTZERO
        elif arg == 1 or arg == '1':
            return TTONE
        else:
            fstr = "argument cannot be converted to a TruthTable: " + str(arg)
            raise TypeError(fstr)

    # Specific to TruthTable
    def _iter_restrict(self, zeros, ones):
        """Iterate through indices of all table entries that vary."""
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


class TTConstant(TruthTable):
    """Truth table constant"""

    def __init__(self):
        super(TTConstant, self).__init__([], PCData([self.PCVAL]))

    def __str__(self):
        return _PC2STR[self.PCVAL]

    PCVAL = NotImplemented


class _TTZero(TTConstant):
    """
    Truth table zero

    .. NOTE:: Never use this class. Use TTZERO instead.
    """
    PCVAL = PC_ZERO

class _TTOne(TTConstant):
    """
    Truth table one

    .. NOTE:: Never use this class. Use TTONE instead.
    """
    PCVAL = PC_ONE

class _TTDontCare(TTConstant):
    """
    Truth table "don't care".

    .. NOTE:: Never use this class. Use TTDC instead.
    """
    PCVAL = PC_DC

TTZERO = _TTZero()
TTONE = _TTOne()
TTDC = _TTDontCare()


class TTVariable(boolfunc.Variable, TruthTable):
    """Truth table variable"""

    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.namespace, bvar.name,
                                   bvar.indices)
        pcdata = PCData((PC_ZERO, PC_ONE))
        TruthTable.__init__(self, [self], pcdata)


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
