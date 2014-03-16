"""
Boolean Function Arrays

Interface Functions:
    exprzeros
    exprones
    exprvars

    bddzeros
    bddones
    bddvars

    ttzeros
    ttones
    ttvars

    uint2array
    int2array

Classes:
    farray
"""

import collections
import functools
import itertools
import operator

from pyeda.boolalg.boolfunc import Variable, Function
from pyeda.boolalg.bdd import BinaryDecisionDiagram, BDDZERO, BDDONE, bddvar
from pyeda.boolalg.expr import Expression, EXPRZERO, EXPRONE, exprvar
from pyeda.boolalg.table import TruthTable, TTZERO, TTONE, ttvar
from pyeda.util import bit_on, cached_property, clog2


_ZEROS = {
    BinaryDecisionDiagram: BDDZERO,
    Expression: EXPRZERO,
    TruthTable: TTZERO,
}
_ONES = {
    BinaryDecisionDiagram: BDDONE,
    Expression: EXPRONE,
    TruthTable: TTONE,
}
_VAR = {
    BinaryDecisionDiagram: bddvar,
    Expression: exprvar,
    TruthTable: ttvar,
}
_CONSTANTS = {
    BinaryDecisionDiagram: (BDDZERO, BDDONE),
    Expression: (EXPRZERO, EXPRONE),
    TruthTable: (TTZERO, TTONE),
}


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
    farray of EXPRZERO with the given shape.
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
    farray of EXPRONE with the given shape.
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
    farray of ExprVariable with the given shape.
    """
    return _vars(name, shape, Expression)

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
    farray of BDDZERO with the given shape.
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
    farray of BDDONE with the given shape.
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
    farray of BDDVariable with the given shape.
    """
    return _vars(name, shape, BinaryDecisionDiagram)

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
    farray of TTZERO with the given shape.
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
    farray of TTONE with the given shape.
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
    farray of TTVariable with the given shape.
    """
    return _vars(name, shape, TruthTable)

def uint2array(num, length=None, ftype=Expression):
    """Convert an unsigned integer to an farray."""
    if num < 0:
        raise ValueError("expected num >= 0")
    else:
        items = _uint2items(num, length, ftype)
        return farray(items)

def int2array(num, length=None, ftype=Expression):
    """Convert a signed integer to an farray."""
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

    return farray(items)


class farray(object):
    """
    Array of Boolean functions
    """
    def __init__(self, objs, shape=None):
        self.items, _shape, self.ftype = _itemize(objs)
        if shape is None:
            self.shape = _shape
        else:
            shape = _readshape(shape)
            if _volume(shape) == len(self.items):
                self.shape = shape
            else:
                raise ValueError("expected shape volume to match items")

    def __iter__(self):
        for i in range(self.shape[0][0], self.shape[0][1]):
            yield self[i]

    def __len__(self):
        return self.shape[0][1] - self.shape[0][0]

    def __getitem__(self, key):
        # Convert the abbreviated input key to its full form
        sls = self._key2sls(key)
        items = [self.items[self._coord2idx(c)] for c in _iter_coords(sls)]
        # Denormalize slices, and drop int dimensions
        shape = tuple(self._denorm_slice(i, sl) for i, sl in enumerate(sls)
                      if type(sl) is slice)
        if shape:
            return self.__class__(items, shape)
        else:
            return items[0]

    @cached_property
    def size(self):
        """Return the size of the array."""
        return _volume(self.shape)

    @cached_property
    def offsets(self):
        """Return a tuple of dimension offsets."""
        return tuple(start for start, _ in self.shape)

    @cached_property
    def ndim(self):
        """Return the number of dimensions."""
        return len(self.shape)

    @property
    def flat(self):
        """Return a 1D iterator over the array."""
        yield from self.items

    def restrict(self, point):
        """
        Return the array that results from applying the 'restrict' method to
        all functions.
        """
        items = [f.restrict(point) for f in self.items]
        return self.__class__(items, self.shape)

    def vrestrict(self, vpoint):
        """Expand all vectors before applying 'restrict'."""
        return self.restrict(_expand_vectors(vpoint))

    def to_uint(self):
        """Convert vector to an unsigned integer, if possible."""
        num = 0
        for i, f in enumerate(self.items):
            if f.is_zero():
                pass
            elif f.is_one():
                num += 1 << i
            else:
                fstr = "expected all functions to be a constant (0 or 1) form"
                raise ValueError(fstr)
        return num

    def to_int(self):
        """Convert vector to an integer, if possible."""
        num = self.to_uint()
        if self.items[-1].unbox():
            return num - (1 << self.size)
        else:
            return num

    # Operators
    def __invert__(self):
        return self.__class__([~x for x in self.items], self.shape)

    def __or__(self, other):
        return self.__class__([x | y for x, y in zip(self.items, other.items)])

    def __and__(self, other):
        return self.__class__([x & y for x, y in zip(self.items, other.items)])

    def __xor__(self, other):
        return self.__class__([x ^ y for x, y in zip(self.items, other.items)])

    def __lshift__(self, obj):
        if type(obj) is tuple and len(obj) == 2:
            return self.lsh(obj[0], obj[1])[0]
        elif type(obj) is int:
            return self.lsh(obj)[0]
        else:
            raise TypeError("expected int or (int, farray)")

    def __rshift__(self, obj):
        if type(obj) is tuple and len(obj) == 2:
            return self.rsh(obj[0], obj[1])[0]
        elif type(obj) is int:
            return self.rsh(obj)[0]
        else:
            raise TypeError("expected int or (int, farray)")

    # Unary operators
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

    # Shift operators
    def lsh(self, num, cin=None):
        """Return the vector left shifted by N places.

        Parameters
        ----------
        num : non-negative int
            Number of places to shift

        cin : farray
            The "carry-in" bit vector

        Returns
        -------
        (farray fs, farray cout)
            V is the shifted vector, and cout is the "carry out".
        """
        if num < 0 or num > self.size:
            raise ValueError("expected 0 <= num <= {0.size}".format(self))
        if cin is None:
            items = [_ZEROS[self.ftype] for _ in range(num)]
            cin = self.__class__(items)
        else:
            if len(cin) != num:
                raise ValueError("expected length of cin to be equal to num")
        if num == 0:
            return self, self.__class__([])
        else:
            fs = self.__class__(cin.items + self.items[:-num])
            cout = self.__class__(self.items[-num:])
            return fs, cout

    def rsh(self, num, cin=None):
        """Return the vector right shifted by N places.

        Parameters
        ----------
        num : non-negative int
            Number of places to shift

        cin : farray
            The "carry-in" bit vector

        Returns
        -------
        (farray fs, farray cout)
            V is the shifted vector, and cout is the "carry out".
        """
        if num < 0 or num > self.size:
            raise ValueError("expected 0 <= num <= {0.size}".format(self))
        if cin is None:
            items = [_ZEROS[self.ftype] for _ in range(num)]
            cin = self.__class__(items)
        else:
            if len(cin) != num:
                raise ValueError("expected length of cin to be equal to num")
        if num == 0:
            return self, self.__class__([])
        else:
            fs = self.__class__(self.items[num:] + cin.items)
            cout = self.__class__(self.items[:num])
            return fs, cout

    def arsh(self, num):
        """Return the vector arithmetically right shifted by N places.

        Parameters
        ----------
        num : non-negative int
            Number of places to shift

        Returns
        -------
        farray
            The shifted vector
        """
        if num < 0 or num > self.size:
            raise ValueError("expected 0 <= num <= {0.size}".format(self))
        if num == 0:
            return self, self.__class__([])
        else:
            sign = self.items[-1]
            fs = self.__class__(self.items[num:] + [sign] * num)
            cout = self.__class__(self.items[:num])
            return fs, cout

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
        items = [functools.reduce(operator.and_,
                                  [f if bit_on(i, j) else ~f
                                   for j, f in enumerate(self.items)])
                 for i in range(2 ** self.size)]
        return self.__class__(items)

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

    def _key2sls(self, key):
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


# Local functions

def _zeros(shape, ftype):
    """Return a new array of given shape and type, filled with zeros."""
    shape = _readshape(shape)
    items = [_ZEROS[ftype] for _ in range(_volume(shape))]
    return farray(items, shape)

def _ones(shape, ftype):
    """Return a new array of given shape and type, filled with ones."""
    shape = _readshape(shape)
    items = [_ONES[ftype] for _ in range(_volume(shape))]
    return farray(items, shape)

def _vars(name, shape, ftype):
    """
    Return a new array of given shape and type, filled with Boolean variables.
    """
    shape = _readshape(shape)
    items = list()
    for indices in itertools.product(*[range(i, j) for i, j in shape]):
        items.append(_VAR[ftype](name, indices))
    return farray(items, shape)

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

def _expand_vectors(vpoint):
    """Expand all vectors in a substitution dict."""
    point = dict()
    for f, val in vpoint.items():
        if isinstance(f, farray):
            if f.size != len(val):
                fstr = ("invalid vector point: "
                        "expected 1:1 mapping from farray => {0, 1}")
                raise ValueError(fstr)
            for i, val in enumerate(val):
                v = f.items[i]
                if not isinstance(v, Variable):
                    fstr = "expected vpoint key to be a Variable"
                    raise TypeError(fstr)
                point[v] = int(val)
        elif isinstance(f, Variable):
            point[f] = int(val)
        else:
            fstr = "expected vpoint key to be a Variable or farray(Variable)"
            raise ValueError(fstr)
    return point

def _itemize(objs):
    """Recursive helper function for farray."""
    if not isinstance(objs, collections.Sequence):
        raise TypeError("expected a sequence of Function")

    isseq = [isinstance(obj, collections.Sequence) for obj in objs]
    if not any(isseq):
        ftype = Function
        for obj in objs:
            if ftype is Function:
                if isinstance(obj, BinaryDecisionDiagram):
                    ftype = BinaryDecisionDiagram
                elif isinstance(obj, Expression):
                    ftype = Expression
                elif isinstance(obj, TruthTable):
                    ftype = TruthTable
                else:
                    raise ValueError("expected valid Function inputs")
            elif not isinstance(obj, ftype):
                raise ValueError("expected uniform Function types")
        return list(objs), ((0, len(objs)), ), ftype
    elif all(isseq):
        items = list()
        shape = None
        ftype = Function
        for obj in objs:
            _items, _shape, _ftype = _itemize(obj)
            if shape is None:
                shape = _shape
            elif shape != _shape:
                raise ValueError("expected uniform array dimensions")
            if ftype is Function:
                ftype = _ftype
            elif ftype != _ftype:
                raise ValueError("expected uniform Function types")
            items += _items
        shape = ((0, len(objs)), ) + shape
        return items, shape, ftype
    else:
        raise ValueError("expected uniform array dimensions")

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
    for coord in itertools.product(*ranges):
        yield coord

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

def _volume(shape):
    """Return the volume of a shape."""
    prod = 1
    for start, stop in shape:
        prod *= stop - start
    return prod

