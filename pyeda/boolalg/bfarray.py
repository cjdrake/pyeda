"""
Boolean Function Arrays

Interface Functions:
    exprarray
    exprzeros
    exprones
    exprvars

    bddarray
    bddzeros
    bddones
    bddvars

    ttarray
    ttzeros
    ttones
    ttvars

    uint2array
    int2array

Classes:
    FunctionArray
"""

import collections
import functools
import itertools
import operator

from pyeda.boolalg.bdd import BinaryDecisionDiagram, BDDZERO, BDDONE, bddvar
from pyeda.boolalg.expr import Expression, EXPRZERO, EXPRONE, exprvar
from pyeda.boolalg.table import TruthTable, TTZERO, TTONE, ttvar
from pyeda.util import cached_property, clog2


_ZEROS = {
    Expression: EXPRZERO,
    BinaryDecisionDiagram: BDDZERO,
    TruthTable: TTZERO,
}
_ONES = {
    Expression: EXPRONE,
    BinaryDecisionDiagram: BDDONE,
    TruthTable: TTONE,
}
_VAR = {
    Expression: exprvar,
    BinaryDecisionDiagram: bddvar,
    TruthTable: ttvar,
}
_CONSTANTS = {
    Expression: (EXPRZERO, EXPRONE),
    BinaryDecisionDiagram: (BDDZERO, BDDONE),
    TruthTable: (TTZERO, TTONE),
}


def _array(obj, ftype):
    """Return an array of Boolean functions."""
    items, shape = _itemize(obj, ftype)
    return FunctionArray(items, shape)

def _itemize(obj, ftype):
    """Recursive helper function for array."""
    isseq = [isinstance(item, collections.Sequence) for item in obj]
    if not any(isseq):
        return [ftype.box(x) for x in obj], ((0, len(obj)), )
    elif all(isseq):
        items = list()
        shape = None
        for item in obj:
            _items, _shape = _itemize(item, ftype)
            if shape is None:
                shape = _shape
            elif shape != _shape:
                raise ValueError("expected uniform array dimensions")
            items += _items
        return items, ((0, len(obj)), ) + shape
    else:
        raise ValueError("expected uniform array dimensions")

def _volume(shape):
    """Return the volume of a shape."""
    prod = 1
    for start, stop in shape:
        prod *= stop - start
    return prod

def _readshape(shape):
    """Read and verify an input shape, and return a tuple((int, int))."""
    if type(shape) is int:
        return ((0, shape), )
    elif isinstance(shape, collections.Sequence):
        parts = list()
        for part in shape:
            if type(part) is int:
                start, stop = 0, part
            elif type(part) is tuple and len(part) == 2:
                start, stop = part
            parts.append((start, stop))
        return tuple(parts)
    else:
        raise TypeError("expected int or sequence of int | (int, int)")

def _zeros(shape, ftype):
    """
    Return a new array of given shape and type, filled with zeros.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g., ``(2, 3)`` or ``2``.
    ftype : Function type, optional
        The desired Function type for the array. Default is Expression.

    Returns
    -------
    FunctionArray of zeros with the given shape.
    """
    shape = _readshape(shape)
    zero = _ZEROS[ftype]
    items = [zero for _ in range(_volume(shape))]
    return FunctionArray(items, shape)

def _ones(shape, ftype):
    """
    Return a new array of given shape and type, filled with ones.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g., ``(2, 3)`` or ``2``.
    ftype : Function type, optional
        The desired Function type for the array. Default is Expression.

    Returns
    -------
    FunctionArray of ones with the given shape.
    """
    shape = _readshape(shape)
    one = _ONES[ftype]
    items = [one for _ in range(_volume(shape))]
    return FunctionArray(items, shape)

def _vars(name, shape, ftype):
    """
    Return a new array of given shape and type, filled with Boolean variables.
    """
    shape = _readshape(shape)
    var = _VAR[ftype]
    items = list()
    for indices in itertools.product(*[range(i, j) for i, j in shape]):
        items.append(var(name, indices))
    return FunctionArray(items, shape)

def exprarray(obj):
    """Return an array of Expression."""
    return _array(obj, Expression)

def exprzeros(shape):
    """
    Return a new array of given shape and type, filled with EXPRZERO.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g., ``(2, 3)`` or ``2``.
    ftype : Function type, optional
        The desired Function type for the array. Default is Expression.

    Returns
    -------
    FunctionArray of EXPRZERO with the given shape.
    """
    return _zeros(shape, Expression)

def exprones(shape):
    """
    Return a new array of given shape and type, filled with EXPRONE.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g., ``(2, 3)`` or ``2``.

    Returns
    -------
    FunctionArray of EXPRONE with the given shape.
    """
    return _ones(shape, Expression)

def exprvars(name, shape):
    """
    Return a new array of given shape and type, filled with ExprVariable.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g:

        * ``4`` means [0:4]
        * ``(4, 8)`` means [4:8]
        * ``(4, (3, 8))`` means [0:4][3:8]

    Returns
    -------
    FunctionArray of ExprVariable with the given shape.
    """
    return _vars(name, shape, Expression)

def bddarray(obj):
    """Return an array of BinaryDecisionDiagram."""
    return _array(obj, BinaryDecisionDiagram)

def bddzeros(shape):
    """
    Return a new array of given shape and type, filled with BDDZERO.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g., ``(2, 3)`` or ``2``.
    ftype : Function type, optional
        The desired Function type for the array. Default is Expression.

    Returns
    -------
    FunctionArray of BDDZERO with the given shape.
    """
    return _zeros(shape, BinaryDecisionDiagram)

def bddones(shape):
    """
    Return a new array of given shape and type, filled with BDDONE.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g., ``(2, 3)`` or ``2``.

    Returns
    -------
    FunctionArray of BDDONE with the given shape.
    """
    return _ones(shape, BinaryDecisionDiagram)

def bddvars(name, shape):
    """
    Return a new array of given shape and type, filled with BDDVariable.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g:

        * ``4`` means [0:4]
        * ``(4, 8)`` means [4:8]
        * ``(4, (3, 8))`` means [0:4][3:8]

    Returns
    -------
    FunctionArray of BDDVariable with the given shape.
    """
    return _vars(name, shape, BinaryDecisionDiagram)

def ttarray(obj):
    """Return an array of TruthTable."""
    return _array(obj, TruthTable)

def ttzeros(shape):
    """
    Return a new array of given shape and type, filled with TTZERO.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g., ``(2, 3)`` or ``2``.
    ftype : Function type, optional
        The desired Function type for the array. Default is Expression.

    Returns
    -------
    FunctionArray of TTZERO with the given shape.
    """
    return _zeros(shape, TruthTable)

def ttones(shape):
    """
    Return a new array of given shape and type, filled with TTONE.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g., ``(2, 3)`` or ``2``.

    Returns
    -------
    FunctionArray of TTONE with the given shape.
    """
    return _ones(shape, TruthTable)

def ttvars(name, shape):
    """
    Return a new array of given shape and type, filled with TTVariable.

    Parameters
    ----------
    shape : int or sequence of ints
        Shape of the new array, e.g:

        * ``4`` means [0:4]
        * ``(4, 8)`` means [4:8]
        * ``(4, (3, 8))`` means [0:4][3:8]

    Returns
    -------
    FunctionArray of TTVariable with the given shape.
    """
    return _vars(name, shape, TruthTable)

def _uint2items(num, length=None, ftype=Expression):
    """Convert an unsigned integer to a list of constant expressions."""
    if num == 0:
        items = [_CONSTANTS[ftype][0]]
    else:
        _num = num
        items = list()
        while _num != 0:
            items.append(_CONSTANTS[ftype][_num & 1])
            _num >>= 1

    if length:
        if length < len(items):
            fstr = "overflow: num = {} requires length >= {}, got length = {}"
            raise ValueError(fstr.format(num, len(items), length))
        else:
            while len(items) < length:
                items.append(_CONSTANTS[ftype][0])

    return items

def uint2array(num, length=None, ftype=Expression):
    """Convert an unsigned integer to a FunctionArray."""
    if num < 0:
        raise ValueError("expected num >= 0")
    else:
        items = _uint2items(num, length, ftype)
        shape = (len(items), )
        return FunctionArray(items, shape)

def int2array(num, length=None, ftype=Expression):
    """Convert a signed integer to a BitVector."""
    if num < 0:
        req_length = clog2(abs(num)) + 1
        items = _uint2items(2**req_length + num, ftype=ftype)
    else:
        req_length = clog2(num + 1) + 1
        items = _uint2items(num, req_length, ftype)

    if length:
        if length < req_length:
            fstr = "overflow: num = {} requires length >= {}, got length = {}"
            raise ValueError(fstr.format(num, req_length, length))
        else:
            sign = items[-1]
            items += [sign] * (length - req_length)

    shape = (len(items), )
    return FunctionArray(items, shape)


class FunctionArray(object):
    """
    banana banana banana
    """
    def __init__(self, items, shape):
        self.items = items
        self.shape = shape

    def __iter__(self):
        for i in range(self.shape[0][0], self.shape[0][1]):
            yield self[i]

    def __len__(self):
        return self.shape[0][1] - self.shape[0][0]

    def __getitem__(self, key):
        # Convert the abbreviated input key to its full form
        sls = self._key2nsls(key)
        items = [self.items[self._coord2idx(c)] for c in _iter_coords(sls)]
        # Denormalize slices, and drop int dimensions
        shape = [self._denorm_slice(i, sl) for i, sl in enumerate(sls)
                 if type(sl) is slice]
        if shape:
            return FunctionArray(items, tuple(shape))
        else:
            return items[0]

    @cached_property
    def size(self):
        return _volume(self.shape)

    @cached_property
    def offsets(self):
        """Return a tuple of dimension offsets."""
        return tuple(start for start, _ in self.shape)

    @cached_property
    def ndim(self):
        """Return the number of dimensions."""
        return len(self.shape)

    def restrict(self, point):
        """
        Return the array that results from applying the 'restrict' method to
        all functions.
        """
        items = [f.restrict(point) for f in self.items]
        return self.__class__(items, self.shape)

    # Operators
    def uor(self):
        """Return the unary OR of a array of functions."""
        return functools.reduce(operator.or_, self.items)

    def unor(self):
        """Return the unary NOR of a array of functions."""
        return ~functools.reduce(operator.or_, self.items)

    def uand(self):
        """Return the unary AND of a array of functions."""
        return functools.reduce(operator.and_, self.items)

    def unand(self):
        """Return the unary NAND of a array of functions."""
        return ~functools.reduce(operator.and_, self.items)

    def uxor(self):
        """Return the unary XOR of a array of functions."""
        return functools.reduce(operator.xor, self.items)

    def uxnor(self):
        """Return the unary XNOR of a array of functions."""
        return ~functools.reduce(operator.xor, self.items)

    @cached_property
    def _normshape(self):
        """Return the shape normalized to zero start indices."""
        return tuple(stop - start for start, stop in self.shape)

    @cached_property
    def _dimsizes(self):
        """Return a list of dimension sizes."""
        prod = len(self.items)
        sizes = list()
        for idx in self._normshape:
            prod //= idx
            sizes.append(prod)
        return sizes

    def _coord2idx(self, vertex):
        """Convert a coordinate to an item index."""
        return sum(v * self._dimsizes[i] for i, v in enumerate(vertex))

    def _key2nsls(self, key):
        """Convert a slice key to a normalized list of int or slice."""
        # Convert all indices to slices
        if type(key) in {int, slice} or key is Ellipsis:
            key = (key, )
        elif type(key) is not tuple:
            raise TypeError("invalid slice input type")
        keylen = len(key)
        if keylen > self.ndim:
            fstr = "expected <= {} slice dimensions, got {}"
            raise ValueError(fstr.format(self.ndim, keylen))

        # Fill '...' entries with ':'
        nfill = self.ndim - keylen
        _key = list()
        for k in key:
            if k is Ellipsis:
                while nfill:
                    _key.append(slice(None, None, None))
                    nfill -= 1
                _key.append(slice(None, None, None))
            else:
                _key.append(k)
        # Append ':' to the end
        for _ in range(self.ndim - len(_key)):
            _key.append(slice(None, None, None))
        # Normalize indices
        keys = [self._norm_key(i, k) for i, k in enumerate(_key)]
        sls = list()
        for i, sl in enumerate(keys):
            if type(sl) is int:
                sls.append(sl)
            else:
                start = 0 if sl.start is None else sl.start
                stop = self._normshape[i] if sl.stop is None else sl.stop
                step = 1 if sl.step is None else sl.step
                sls.append(slice(start, stop, step))

        return sls

    def _norm_key(self, i, key):
        """Return a key normalized to a zero-based index."""
        if type(key) is int:
            return _norm_idx(key, *self.shape[i])
        elif type(key) is slice:
            return _norm_slice(key, *self.shape[i])
        else:
            raise TypeError("invalid slice input type")

    def _denorm_slice(self, i, sl):
        """Return a slice denormalized to dimension offsets."""
        return (sl.start + self.offsets[i], sl.stop + self.offsets[i])


def _norm_idx(i, start, stop):
    """Return an index normalized to an array start index."""
    if i >= start and i < stop:
        idx = i - start
    elif i >= -stop and i < -start:
        idx = i + stop
    else:
        fstr = "expected index in range [{}, {}]"
        raise IndexError(fstr.format(start, stop))
    return idx

def _norm_slice(sl, start, stop):
    """Return a slice normalized to an array start index."""
    limits = {'start': None, 'stop': None}
    for k in limits:
        i = getattr(sl, k)
        if i is not None:
            if i >= start and i <= stop:
                limits[k] = i - start
            elif i >= -stop and i <= -start:
                limits[k] = i + stop
            else:
                fstr = "expected index in range [{}, {}]"
                raise IndexError(fstr.format(start, stop))
    step = getattr(sl, 'step', None)
    return slice(limits['start'], limits['stop'], step)

def _iter_coords(sls):
    """Iterate through all matching coordinates in a sequence of slices."""
    # First convert all slices to ranges
    ranges = list()
    for sl in sls:
        if type(sl) is int:
            ranges.append(range(sl, sl+1))
        else:
            ranges.append(range(sl.start, sl.stop, sl.step))
    # Iterate through all matching coordinates
    yield from itertools.product(*ranges)

