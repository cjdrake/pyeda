"""
Boolean Function Arrays

Interface Functions:
    bddzeros
    bddones
    bddvars

    exprzeros
    exprones
    exprvars

    ttzeros
    ttones
    ttvars

    uint2bdds
    uint2exprs
    uint2tts
    int2bdds
    int2exprs
    int2tts

    fcat

Classes:
    farray
"""

import collections
import itertools
import operator
from functools import reduce

from pyeda.boolalg import boolfunc
from pyeda.boolalg.bdd import BinaryDecisionDiagram, bddvar
from pyeda.boolalg.expr import Expression, exprvar
from pyeda.boolalg.table import TruthTable, ttvar
from pyeda.util import bit_on, cached_property, clog2


_VAR = {
    BinaryDecisionDiagram: bddvar,
    Expression: exprvar,
    TruthTable: ttvar,
}


def bddzeros(*dims):
    """
    Return a new array of given dimensions, filled with BDDZERO.

    Parameters
    ----------
    dims : sequence of int or (int, int)
        Dimensions of the new array

    Returns
    -------
    farray of BDDZERO with the given dimensions.
    """
    return _zeros(BinaryDecisionDiagram, *dims)

def bddones(*dims):
    """
    Return a new array of given dimensions, filled with BDDONE.

    Parameters
    ----------
    dims : sequence of int or (int, int)
        Dimensions of the new array

    Returns
    -------
    farray of BDDONE with the given dimensions.
    """
    return _ones(BinaryDecisionDiagram, *dims)

def bddvars(name, *dims):
    """
    Return a new array of given dimensions, filled with BDDVariable.

    Parameters
    ----------
    name : str

    dims : sequence of int or (int, int)
        Dimensions of the new array, e.g:

        * ``4`` means [0:4]
        * ``4, 8`` means [4:8]
        * ``4, (3, 8)`` means [0:4][3:8]

    Returns
    -------
    farray of BDDVariable with the given dimensions.
    """
    return _vars(BinaryDecisionDiagram, name, *dims)

def exprzeros(*dims):
    """
    Return a new array of given dimensions, filled with EXPRZERO.

    Parameters
    ----------
    dims : sequence of int or (int, int)
        Dimensions of the new array

    Returns
    -------
    farray of EXPRZERO with the given dimensions.
    """
    return _zeros(Expression, *dims)

def exprones(*dims):
    """
    Return a new array of given dimensions, filled with EXPRONE.

    Parameters
    ----------
    dims : sequence of int or (int, int)
        Dimensions of the new array

    Returns
    -------
    farray of EXPRONE with the given dimensions.
    """
    return _ones(Expression, *dims)

def exprvars(name, *dims):
    """
    Return a new array of given dimensions, filled with ExprVariable.

    Parameters
    ----------
    name : str

    dims : sequence of int or (int, int)
        Dimensions of the new array, e.g:

        * ``4`` means [0:4]
        * ``4, 8`` means [4:8]
        * ``4, (3, 8)`` means [0:4][3:8]

    Returns
    -------
    farray of ExprVariable with the given dimensions.
    """
    return _vars(Expression, name, *dims)

def ttzeros(*dims):
    """
    Return a new array of given dimensions, filled with TTZERO.

    Parameters
    ----------
    dims : sequence of int or (int, int)
        Dimensions of the new array

    Returns
    -------
    farray of TTZERO with the given dimensions.
    """
    return _zeros(TruthTable, *dims)

def ttones(*dims):
    """
    Return a new array of given dimensions, filled with TTONE.

    Parameters
    ----------
    dims : sequence of int or (int, int)
        Dimensions of the new array

    Returns
    -------
    farray of TTONE with the given dimensions.
    """
    return _ones(TruthTable, *dims)

def ttvars(name, *dims):
    """
    Return a new array of given dimensions, filled with TTVariable.

    Parameters
    ----------
    name : str

    dims : sequence of int or (int, int)
        Dimensions of the new array, e.g:

        * ``4`` means [0:4]
        * ``4, 8`` means [4:8]
        * ``4, (3, 8)`` means [0:4][3:8]

    Returns
    -------
    farray of TTVariable with the given dimensions.
    """
    return _vars(TruthTable, name, *dims)

def uint2bdds(num, length=None):
    """Convert an unsigned integer to an farray of BDDs."""
    return _uint2farray(BinaryDecisionDiagram, num, length)

def uint2exprs(num, length=None):
    """Convert an unsigned integer to an farray of Expressions."""
    return _uint2farray(Expression, num, length)

def uint2tts(num, length=None):
    """Convert an unsigned integer to an farray of TruthTables."""
    return _uint2farray(TruthTable, num, length)

def int2bdds(num, length=None):
    """Convert a signed integer to an farray of BDDs."""
    return _int2farray(BinaryDecisionDiagram, num, length)

def int2exprs(num, length=None):
    """Convert a signed integer to an farray of Expressions."""
    return _int2farray(Expression, num, length)

def int2tts(num, length=None):
    """Convert a signed integer to an farray of TruthTables."""
    return _int2farray(TruthTable, num, length)

def fcat(*fs):
    """Concatenate a sequence of farrays."""
    items = list()
    for f in fs:
        if isinstance(f, boolfunc.Function):
            items.append(f)
        elif isinstance(f, farray):
            items.extend(f.flat)
        else:
            raise TypeError("expected Function or farray")
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
            _check_shape(shape)
            if _volume(shape) == len(self.items):
                self.shape = shape
            else:
                raise ValueError("expected shape volume to match items")

    def __str__(self):
        return str(self.items)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        if self.shape:
            for i in range(self.shape[0][0], self.shape[0][1]):
                yield self[i]

    def __len__(self):
        if self.shape:
            return self.shape[0][1] - self.shape[0][0]
        else:
            return 0

    def __getitem__(self, key):
        # Convert the abbreviated input key to its full form
        sls = self._key2sls(key)
        items = [self.items[self._coord2index(c)] for c in _iter_coords(sls)]
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

    def reshape(self, *dims):
        """Return an equivalent farray with modified dimensions."""
        shape = _dims2shape(*dims)
        if _volume(shape) != self.size:
            raise ValueError("expected shape with equal volume")
        return self.__class__(self.items, shape)

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
        return self.restrict(boolfunc.vpoint2point(vpoint))

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

    def zext(self, num):
        """Return a flat copy of this array, zero-extended by N bits."""
        zero = self.ftype.box(0)
        return self.__class__(self.items + [zero] * num)

    def sext(self, num):
        """Return a flat copy of this array, sign-extended by N bits."""
        sign = self.items[-1]
        return self.__class__(self.items + [sign] * num)

    # Operators
    def __invert__(self):
        return self.__class__([~x for x in self.items], self.shape)

    def __or__(self, other):
        shape = self._get_op_shape(other)
        items = [x | y for x, y in zip(self.flat, other.flat)]
        return self.__class__(items, shape)

    def __and__(self, other):
        shape = self._get_op_shape(other)
        items = [x & y for x, y in zip(self.flat, other.flat)]
        return self.__class__(items, shape)

    def __xor__(self, other):
        shape = self._get_op_shape(other)
        items = [x ^ y for x, y in zip(self.flat, other.flat)]
        return self.__class__(items, shape)

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
        return reduce(operator.or_, self.items)

    def unor(self):
        """Return the unary NOR of a array of functions."""
        return ~reduce(operator.or_, self.items)

    def uand(self):
        """Return the unary AND of a array of functions."""
        return reduce(operator.and_, self.items)

    def unand(self):
        """Return the unary NAND of a array of functions."""
        return ~reduce(operator.and_, self.items)

    def uxor(self):
        """Return the unary XOR of a array of functions."""
        return reduce(operator.xor, self.items)

    def uxnor(self):
        """Return the unary XNOR of a array of functions."""
        return ~reduce(operator.xor, self.items)

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
            items = [self.ftype.box(0) for _ in range(num)]
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
            items = [self.ftype.box(0) for _ in range(num)]
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
        items = [reduce(operator.and_,
                        [f if bit_on(i, j) else ~f
                         for j, f in enumerate(self.items)])
                 for i in range(2 ** self.size)]
        return self.__class__(items)

    @cached_property
    def _normshape(self):
        """Return the shape normalized to zero start indices."""
        return tuple(stop - start for start, stop in self.shape)

    def _dimsize(self, i):
        """Return the size of the i'th dimension."""
        return self.size // reduce(operator.mul, self._normshape[:i+1])

    def _coord2index(self, coord):
        """Convert a coordinate to an item index."""
        return sum(v * self._dimsize(i) for i, v in enumerate(coord))

    def _key2sls(self, key):
        """Convert a slice key to a normalized list of int or slice."""
        # Convert all input keys to a tuple
        if type(key) in {int, slice} or key is Ellipsis:
            key = (key, )
        elif type(key) is not tuple:
            raise TypeError("invalid slice input type")
        keylen = len(key)
        if keylen > self.ndim:
            fstr = "expected <= {} slice dimensions, got {}"
            raise ValueError(fstr.format(self.ndim, keylen))

        # Forbid slice steps
        for k in key:
            if type(k) is slice and k.step is not None:
                raise ValueError("farray slice step is not supported")

        # Fill '...' entries with ':'
        nfill = self.ndim - keylen
        fkeys = list()
        for k in key:
            if k is Ellipsis:
                while nfill:
                    fkeys.append(slice(None, None))
                    nfill -= 1
                fkeys.append(slice(None, None))
            else:
                fkeys.append(k)
        # Append ':' to the end
        for _ in range(self.ndim - len(fkeys)):
            fkeys.append(slice(None, None))

        # Normalize indices, and fill empty slice entries
        sls = list()
        for i, fkey in enumerate(fkeys):
            nkey = self._norm_key(i, fkey)
            if type(nkey) is int:
                sls.append(nkey)
            else:
                start = 0 if nkey.start is None else nkey.start
                stop = self._normshape[i] if nkey.stop is None else nkey.stop
                sls.append(slice(start, stop))

        return sls

    def _norm_key(self, i, key):
        """Return a key normalized to a zero-based index."""
        if type(key) is int:
            return _norm_index(key, *self.shape[i])
        elif type(key) is slice:
            return _norm_slice(key, *self.shape[i])
        else:
            raise TypeError("invalid slice input type")

    def _denorm_slice(self, i, sl):
        """Return a slice denormalized to dimension offsets."""
        return (sl.start + self.offsets[i], sl.stop + self.offsets[i])

    def _get_op_shape(self, other):
        """Return shape that will be used by farray constructor."""
        if isinstance(other, farray):
            if self.shape == other.shape:
                return self.shape
            elif self.size == other.size:
                return None
            else:
                raise ValueError("expected operand sizes to match")
        else:
            raise TypeError("expected farray input")


# Local functions

def _zeros(ftype, *dims):
    """Return a new array filled with zeros."""
    shape = _dims2shape(*dims)
    objs = [ftype.box(0) for _ in range(_volume(shape))]
    return farray(objs, shape)

def _ones(ftype, *dims):
    """Return a new array filled with ones."""
    shape = _dims2shape(*dims)
    objs = [ftype.box(1) for _ in range(_volume(shape))]
    return farray(objs, shape)

def _vars(ftype, name, *dims):
    """Return a new array filled with Boolean variables."""
    shape = _dims2shape(*dims)
    objs = list()
    if shape:
        for indices in itertools.product(*[range(i, j) for i, j in shape]):
            objs.append(_VAR[ftype](name, indices))
    return farray(objs, shape)

def _uint2objs(ftype, num, length=None):
    """Convert an unsigned integer to a list of constant expressions."""
    if num == 0:
        objs = [ftype.box(0)]
    else:
        _num = num
        objs = list()
        while _num != 0:
            objs.append(ftype.box(_num & 1))
            _num >>= 1

    if length:
        if length < len(objs):
            fstr = "overflow: num = {} requires length >= {}, got length = {}"
            raise ValueError(fstr.format(num, len(objs), length))
        else:
            while len(objs) < length:
                objs.append(ftype.box(0))

    return objs

def _uint2farray(ftype, num, length=None):
    """Convert an unsigned integer to an farray."""
    if num < 0:
        raise ValueError("expected num >= 0")
    else:
        objs = _uint2objs(ftype, num, length)
        return farray(objs)

def _int2farray(ftype, num, length=None):
    """Convert a signed integer to an farray."""
    if num < 0:
        req_length = clog2(abs(num)) + 1
        objs = _uint2objs(ftype, 2**req_length + num)
    else:
        req_length = clog2(num + 1) + 1
        objs = _uint2objs(ftype, num, req_length)

    if length:
        if length < req_length:
            fstr = "overflow: num = {} requires length >= {}, got length = {}"
            raise ValueError(fstr.format(num, req_length, length))
        else:
            sign = objs[-1]
            objs += [sign] * (length - req_length)

    return farray(objs)

def _itemize(objs):
    """Recursive helper function for farray."""
    if not isinstance(objs, collections.Sequence):
        raise TypeError("expected a sequence of Function")

    isseq = [isinstance(obj, collections.Sequence) for obj in objs]
    if not any(isseq):
        ftype = boolfunc.Function
        for obj in objs:
            if ftype is boolfunc.Function:
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
        ftype = boolfunc.Function
        for obj in objs:
            _items, _shape, _ftype = _itemize(obj)
            if shape is None:
                shape = _shape
            elif shape != _shape:
                raise ValueError("expected uniform array dimensions")
            if ftype is boolfunc.Function:
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
            ranges.append(range(sl.start, sl.stop))
    # Iterate through all matching coordinates
    yield from itertools.product(*ranges)

def _norm_index(i, start, stop):
    """Return an index normalized to an array start index."""
    if i >= start and i < stop:
        index = i - start
    elif i >= -stop and i < -start:
        index = i + stop
    else:
        fstr = "expected index in range [{}, {}]"
        raise IndexError(fstr.format(start, stop))
    return index

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
    return slice(limits['start'], limits['stop'])

def _dims2shape(*dims):
    """Convert input dimensions to a shape."""
    shape = list()
    for dim in dims:
        if type(dim) is int:
            if dim <= 0:
                raise ValueError("expected high dimension to be > 0")
            start, stop = 0, dim
        elif type(dim) is tuple and len(dim) == 2:
            if dim[0] < 0:
                raise ValueError("expected low dimension to be >= 0")
            if dim[1] <= 0:
                raise ValueError("expected high dimension to be > 0")
            if dim[0] >= dim[1]:
                raise ValueError("expected low < high dimensions")
            start, stop = dim
        else:
            raise TypeError("expected dimension to be int or (int, int)")
        shape.append((start, stop))
    return tuple(shape)

def _check_shape(shape):
    """Verify that a shape has the right format."""
    if type(shape) is tuple:
        for dim in shape:
            if (type(dim) is tuple and len(dim) == 2 and
                type(dim[0]) is int and type(dim[1]) is int):
                if dim[0] < 0:
                    raise ValueError("expected low dimension to be >= 0")
                if dim[1] <= 0:
                    raise ValueError("expected high dimension to be > 0")
                if dim[0] >= dim[1]:
                    raise ValueError("expected low < high dimensions")
            else:
                raise TypeError("expected shape dimension to be (int, int)")
    else:
        raise TypeError("expected shape to be tuple of (int, int)")

def _volume(shape):
    """Return the volume of a shape."""
    if shape:
        prod = 1
        for start, stop in shape:
            prod *= stop - start
        return prod
    else:
        return 0

