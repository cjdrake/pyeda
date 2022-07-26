"""
The :mod:`pyeda.boolalg.bfarray` module implements multi-dimensional arrays
of Boolean functions.

Interface Functions:

* :func:`bddzeros` --- Return a multi-dimensional array of BDD zeros
* :func:`bddones` --- Return a multi-dimensional array of BDD ones
* :func:`bddvars` --- Return a multi-dimensional array of BDD variables

* :func:`exprzeros` --- Return a multi-dimensional array of expression zeros
* :func:`exprones` --- Return a multi-dimensional array of expression ones
* :func:`exprvars` --- Return a multi-dimensional array of expression variables

* :func:`ttzeros` --- Return a multi-dimensional array of truth table zeros
* :func:`ttones` --- Return a multi-dimensional array of truth table ones
* :func:`ttvars` --- Return a multi-dimensional array of truth table variables

* :func:`uint2bdds` --- Convert unsigned *num* to an array of BDDs
* :func:`uint2exprs` --- Convert unsigned *num* to an array of expressions
* :func:`uint2tts` --- Convert unsigned *num* to an array of truth tables
* :func:`int2bdds` --- Convert *num* to an array of BDDs
* :func:`int2exprs` --- Convert *num* to an array of expressions
* :func:`int2tts` --- Convert *num* to an array of truth tables

* :func:`fcat` --- Concatenate a sequence of farrays

Interface Classes:

* :func:`farray`
"""

import collections
import itertools
import operator
from functools import reduce

from pyeda.boolalg import boolfunc
from pyeda.boolalg.bdd import BinaryDecisionDiagram, bddvar
from pyeda.boolalg.expr import Expression, exprvar
from pyeda.boolalg.table import TruthTable, ttvar
from pyeda.util import clog2


_VAR = {
    BinaryDecisionDiagram: bddvar,
    Expression: exprvar,
    TruthTable: ttvar,
}


def bddzeros(*dims):
    """Return a multi-dimensional array of BDD zeros.

    The variadic *dims* input is a sequence of dimension specs.
    A dimension spec is a two-tuple: (start index, stop index).
    If a dimension is given as a single ``int``,
    it will be converted to ``(0, stop)``.

    The dimension starts at index ``start``,
    and increments by one up to, but not including, ``stop``.
    This follows the Python slice convention.

    For example, to create a 4x4 array of BDD zeros::

       >>> zeros = bddzeros(4, 4)
       >>> zeros
       farray([[0, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0]])
    """
    return _zeros(BinaryDecisionDiagram, *dims)


def bddones(*dims):
    """Return a multi-dimensional array of BDD ones.

    The variadic *dims* input is a sequence of dimension specs.
    A dimension spec is a two-tuple: (start index, stop index).
    If a dimension is given as a single ``int``,
    it will be converted to ``(0, stop)``.

    The dimension starts at index ``start``,
    and increments by one up to, but not including, ``stop``.
    This follows the Python slice convention.

    For example, to create a 4x4 array of BDD ones::

       >>> ones = bddones(4, 4)
       >>> ones
       farray([[1, 1, 1, 1],
               [1, 1, 1, 1],
               [1, 1, 1, 1],
               [1, 1, 1, 1]])
    """
    return _ones(BinaryDecisionDiagram, *dims)


def bddvars(name, *dims):
    """Return a multi-dimensional array of BDD variables.

    The *name* argument is passed directly to the
    :func:`pyeda.boolalg.bdd.bddvar` function,
    and may be either a ``str`` or tuple of ``str``.

    The variadic *dims* input is a sequence of dimension specs.
    A dimension spec is a two-tuple: (start index, stop index).
    If a dimension is given as a single ``int``,
    it will be converted to ``(0, stop)``.

    The dimension starts at index ``start``,
    and increments by one up to, but not including, ``stop``.
    This follows the Python slice convention.

    For example, to create a 4x4 array of BDD variables::

       >>> vs = bddvars('a', 4, 4)
       >>> vs
       farray([[a[0,0], a[0,1], a[0,2], a[0,3]],
               [a[1,0], a[1,1], a[1,2], a[1,3]],
               [a[2,0], a[2,1], a[2,2], a[2,3]],
               [a[3,0], a[3,1], a[3,2], a[3,3]]])
    """
    return _vars(BinaryDecisionDiagram, name, *dims)


def exprzeros(*dims):
    """Return a multi-dimensional array of expression zeros.

    The variadic *dims* input is a sequence of dimension specs.
    A dimension spec is a two-tuple: (start index, stop index).
    If a dimension is given as a single ``int``,
    it will be converted to ``(0, stop)``.

    The dimension starts at index ``start``,
    and increments by one up to, but not including, ``stop``.
    This follows the Python slice convention.

    For example, to create a 4x4 array of expression zeros::

       >>> zeros = exprzeros(4, 4)
       >>> zeros
       farray([[0, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0]])
    """
    return _zeros(Expression, *dims)


def exprones(*dims):
    """Return a multi-dimensional array of expression ones.

    The variadic *dims* input is a sequence of dimension specs.
    A dimension spec is a two-tuple: (start index, stop index).
    If a dimension is given as a single ``int``,
    it will be converted to ``(0, stop)``.

    The dimension starts at index ``start``,
    and increments by one up to, but not including, ``stop``.
    This follows the Python slice convention.

    For example, to create a 4x4 array of expression ones::

       >>> ones = exprones(4, 4)
       >>> ones
       farray([[1, 1, 1, 1],
               [1, 1, 1, 1],
               [1, 1, 1, 1],
               [1, 1, 1, 1]])
    """
    return _ones(Expression, *dims)


def exprvars(name, *dims):
    """Return a multi-dimensional array of expression variables.

    The *name* argument is passed directly to the
    :func:`pyeda.boolalg.expr.exprvar` function,
    and may be either a ``str`` or tuple of ``str``.

    The variadic *dims* input is a sequence of dimension specs.
    A dimension spec is a two-tuple: (start index, stop index).
    If a dimension is given as a single ``int``,
    it will be converted to ``(0, stop)``.

    The dimension starts at index ``start``,
    and increments by one up to, but not including, ``stop``.
    This follows the Python slice convention.

    For example, to create a 4x4 array of expression variables::

       >>> vs = exprvars('a', 4, 4)
       >>> vs
       farray([[a[0,0], a[0,1], a[0,2], a[0,3]],
               [a[1,0], a[1,1], a[1,2], a[1,3]],
               [a[2,0], a[2,1], a[2,2], a[2,3]],
               [a[3,0], a[3,1], a[3,2], a[3,3]]])
    """
    return _vars(Expression, name, *dims)


def ttzeros(*dims):
    """Return a multi-dimensional array of truth table zeros.

    The variadic *dims* input is a sequence of dimension specs.
    A dimension spec is a two-tuple: (start index, stop index).
    If a dimension is given as a single ``int``,
    it will be converted to ``(0, stop)``.

    The dimension starts at index ``start``,
    and increments by one up to, but not including, ``stop``.
    This follows the Python slice convention.

    For example, to create a 4x4 array of truth table zeros::

       >>> zeros = ttzeros(4, 4)
       >>> zeros
       farray([[0, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0]])
    """
    return _zeros(TruthTable, *dims)


def ttones(*dims):
    """Return a multi-dimensional array of truth table ones.

    The variadic *dims* input is a sequence of dimension specs.
    A dimension spec is a two-tuple: (start index, stop index).
    If a dimension is given as a single ``int``,
    it will be converted to ``(0, stop)``.

    The dimension starts at index ``start``,
    and increments by one up to, but not including, ``stop``.
    This follows the Python slice convention.

    For example, to create a 4x4 array of truth table ones::

       >>> ones = ttones(4, 4)
       >>> ones
       farray([[1, 1, 1, 1],
               [1, 1, 1, 1],
               [1, 1, 1, 1],
               [1, 1, 1, 1]])
    """
    return _ones(TruthTable, *dims)


def ttvars(name, *dims):
    """Return a multi-dimensional array of truth table variables.

    The *name* argument is passed directly to the
    :func:`pyeda.boolalg.table.ttvar` function,
    and may be either a ``str`` or tuple of ``str``.

    The variadic *dims* input is a sequence of dimension specs.
    A dimension spec is a two-tuple: (start index, stop index).
    If a dimension is given as a single ``int``,
    it will be converted to ``(0, stop)``.

    The dimension starts at index ``start``,
    and increments by one up to, but not including, ``stop``.
    This follows the Python slice convention.

    For example, to create a 4x4 array of truth table variables::

       >>> vs = ttvars('a', 4, 4)
       >>> vs
       farray([[a[0,0], a[0,1], a[0,2], a[0,3]],
               [a[1,0], a[1,1], a[1,2], a[1,3]],
               [a[2,0], a[2,1], a[2,2], a[2,3]],
               [a[3,0], a[3,1], a[3,2], a[3,3]]])
    """
    return _vars(TruthTable, name, *dims)


def uint2bdds(num, length=None):
    """Convert unsigned *num* to an array of BDDs.

    The *num* argument is a non-negative integer.

    If no *length* parameter is given,
    the return value will have the minimal required length.
    Otherwise, the return value will be zero-extended to match *length*.

    For example, to convert the byte 42 (binary ``0b00101010``)::

       >>> uint2bdds(42, 8)
       farray([0, 1, 0, 1, 0, 1, 0, 0])
    """
    return _uint2farray(BinaryDecisionDiagram, num, length)


def uint2exprs(num, length=None):
    """Convert unsigned *num* to an array of expressions.

    The *num* argument is a non-negative integer.

    If no *length* parameter is given,
    the return value will have the minimal required length.
    Otherwise, the return value will be zero-extended to match *length*.

    For example, to convert the byte 42 (binary ``0b00101010``)::

       >>> uint2exprs(42, 8)
       farray([0, 1, 0, 1, 0, 1, 0, 0])
    """
    return _uint2farray(Expression, num, length)


def uint2tts(num, length=None):
    """Convert unsigned *num* to an array of truth tables.

    The *num* argument is a non-negative integer.

    If no *length* parameter is given,
    the return value will have the minimal required length.
    Otherwise, the return value will be zero-extended to match *length*.

    For example, to convert the byte 42 (binary ``0b00101010``)::

       >>> uint2tts(42, 8)
       farray([0, 1, 0, 1, 0, 1, 0, 0])
    """
    return _uint2farray(TruthTable, num, length)


def int2bdds(num, length=None):
    """Convert *num* to an array of BDDs.

    The *num* argument is an ``int``.
    Negative numbers will be converted using twos-complement notation.

    If no *length* parameter is given,
    the return value will have the minimal required length.
    Otherwise, the return value will be sign-extended to match *length*.

    For example, to convert the bytes 42 (binary ``0b00101010``),
    and -42 (binary ``0b11010110``)::

       >>> int2bdds(42, 8)
       farray([0, 1, 0, 1, 0, 1, 0, 0])
       >>> int2bdds(-42, 8)
       farray([0, 1, 1, 0, 1, 0, 1, 1])
    """
    return _int2farray(BinaryDecisionDiagram, num, length)


def int2exprs(num, length=None):
    """Convert *num* to an array of expressions.

    The *num* argument is an ``int``.
    Negative numbers will be converted using twos-complement notation.

    If no *length* parameter is given,
    the return value will have the minimal required length.
    Otherwise, the return value will be sign-extended to match *length*.

    For example, to convert the bytes 42 (binary ``0b00101010``),
    and -42 (binary ``0b11010110``)::

       >>> int2exprs(42, 8)
       farray([0, 1, 0, 1, 0, 1, 0, 0])
       >>> int2exprs(-42, 8)
       farray([0, 1, 1, 0, 1, 0, 1, 1])
    """
    return _int2farray(Expression, num, length)


def int2tts(num, length=None):
    """Convert *num* to an array of truth tables.

    The *num* argument is an ``int``.
    Negative numbers will be converted using twos-complement notation.

    If no *length* parameter is given,
    the return value will have the minimal required length.
    Otherwise, the return value will be sign-extended to match *length*.

    For example, to convert the bytes 42 (binary ``0b00101010``),
    and -42 (binary ``0b11010110``)::

       >>> int2tts(42, 8)
       farray([0, 1, 0, 1, 0, 1, 0, 0])
       >>> int2tts(-42, 8)
       farray([0, 1, 1, 0, 1, 0, 1, 1])
    """
    return _int2farray(TruthTable, num, length)


# FIXME: Should this function allow {0, 1} inputs?
def fcat(*fs):
    """Concatenate a sequence of farrays.

    The variadic *fs* input is a homogeneous sequence of functions or arrays.
    """
    items = list()
    for f in fs:
        if isinstance(f, boolfunc.Function):
            items.append(f)
        elif isinstance(f, farray):
            items.extend(f.flat)
        else:
            raise TypeError("expected Function or farray")
    return farray(items)


class farray:
    """Multi-dimensional array of Boolean functions

    The *objs* argument is a nested sequence of homogeneous Boolean functions.
    That is, both [a, b, c, d] and [[a, b], [c, d]] are valid inputs.

    The optional *shape* parameter is a tuple of dimension specs,
    which are ``(int, int)`` tuples.
    It must match the volume of *objs*.
    The shape can always be automatically determined from *objs*,
    but you can supply it to automatically reshape a flat input.

    The optional *ftype* parameter is a proper subclass of ``Function``.
    It must match the homogeneous type of *objs*.
    In most cases, *ftype* can automatically be determined from *objs*.
    The one exception is that you must provide *ftype* for ``objs=[]``
    (an empty array).
    """
    def __init__(self, objs, shape=None, ftype=None):
        self._items, autoshape, autoftype = _itemize(objs)
        if shape is None:
            self.shape = autoshape
        else:
            _check_shape(shape)
            if _volume(shape) != len(self._items):
                raise ValueError("expected shape volume to match items")
            self.shape = shape
        if ftype is None:
            if autoftype is None:
                raise ValueError("could not determine ftype parameter")
            self.ftype = autoftype
        else:
            if not isinstance(ftype, type):
                raise TypeError("expected ftype to be a type")
            if not (autoftype is None or ftype is autoftype):
                raise ValueError("expected ftype to match items")
            if (not issubclass(ftype, boolfunc.Function) or
                    ftype is boolfunc.Function):
                fstr = "expected ftype to be a proper subclass of Function"
                raise TypeError(fstr)
            self.ftype = ftype

    def __str__(self):
        pre, post = "farray(", ")"
        indent = " " * len(pre) + " "
        return pre + self._str(indent) + post

    def _str(self, indent=""):
        """Helper function for __str__"""
        if self.ndim <= 1:
            return "[" + ", ".join(str(x) for x in self) + "]"
        elif self.ndim == 2:
            sep = ",\n" + indent
            return "[" + sep.join(x._str(indent + " ") for x in self) + "]"
        else:
            sep = ",\n\n" + indent
            return "[" + sep.join(x._str(indent + " ") for x in self) + "]"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        for i in range(self.shape[0][0], self.shape[0][1]):
            yield self[i]

    def __len__(self):
        return self.shape[0][1] - self.shape[0][0]

    def __getitem__(self, key):
        # Process input key
        sls = self._keys2sls(key, _get_key2sl)

        # Normalize input slices
        fsls = self._fill_slices(sls)
        nsls = self._norm_slices(fsls)

        if all(isinstance(nsl, int) for nsl in nsls):
            # Speed hack for coordinates
            return self._items[self._coord2offset(nsls)]
        else:
            # Filter through all dimensions (right to left)
            items, shape = self._items[:], self.shape[:]
            for dim in range(self.ndim - 1, -1, -1):
                items, shape = _filtdim(items, shape, dim, nsls[dim])

        if shape:
            return self.__class__(items, shape, self.ftype)
        else:
            return items[0]

    def __setitem__(self, key, item):
        # Process input key
        sls = self._keys2sls(key, _set_key2sl)

        # Normalize input slices
        fsls = self._fill_slices(sls)
        nsls = self._norm_slices(fsls)

        if all(isinstance(nsl, int) for nsl in nsls):
            if not isinstance(item, boolfunc.Function):
                raise TypeError("expected item to be a Function")
            self._items[self._coord2offset(nsls)] = item
        else:
            if not isinstance(item, farray):
                raise TypeError("expected item to be an farray")
            coords = list(_iter_coords(nsls))
            if item.size != len(coords):
                fstr = "expected item.size = {}, got {}"
                raise ValueError(fstr.format(len(coords), item.size))
            it = item.flat
            for coord in coords:
                self._items[self._coord2offset(coord)] = next(it)

    # Operators
    def __invert__(self):
        """Bit-wise NOT operator"""
        return self.__class__([~x for x in self._items], self.shape, self.ftype)

    def __or__(self, other):
        """Bit-wise OR operator"""
        shape = self._op_shape(other)
        items = [x | y for x, y in zip(self.flat, other.flat)]
        return self.__class__(items, shape, self.ftype)

    def __and__(self, other):
        """Bit-wise AND operator"""
        shape = self._op_shape(other)
        items = [x & y for x, y in zip(self.flat, other.flat)]
        return self.__class__(items, shape, self.ftype)

    def __xor__(self, other):
        """Bit-wise XOR operator"""
        shape = self._op_shape(other)
        items = [x ^ y for x, y in zip(self.flat, other.flat)]
        return self.__class__(items, shape, self.ftype)

    def __lshift__(self, obj):
        """Left shift operator

        The *obj* argument may either be an ``int``, or ``(int, farray)``.
        The ``int`` argument is *num*, and the ``farray`` argument is *cin*.

        .. seealso:: :meth:`lsh`
        """
        if isinstance(obj, tuple) and len(obj) == 2:
            return self.lsh(obj[0], obj[1])[0]
        elif isinstance(obj, int):
            return self.lsh(obj)[0]
        else:
            raise TypeError("expected int or (int, farray)")

    def __rshift__(self, obj):
        """Right shift operator

        The *obj* argument may either be an ``int``, or ``(int, farray)``.
        The ``int`` argument is *num*, and the ``farray`` argument is *cin*.

        .. seealso:: :meth:`rsh`
        """
        if isinstance(obj, tuple) and len(obj) == 2:
            return self.rsh(obj[0], obj[1])[0]
        elif isinstance(obj, int):
            return self.rsh(obj)[0]
        else:
            raise TypeError("expected int or (int, farray)")

    def __add__(self, other):
        """Concatenation operator

        The *other* argument may be a Function or farray.
        """
        if other in {0, 1}:
            other = farray([self.ftype.box(other)])
        elif isinstance(other, boolfunc.Function):
            other = farray([other])
        elif not isinstance(other, farray):
            raise TypeError("expected Function or farray")

        items = self._items + list(other.flat)
        shape = None
        # Multi-dimensional arrays
        if (self.ndim == other.ndim > 1 and
                self.shape[1:] == other.shape[1:]):
            # (0,x), ... + (0,y), ... = (0,x+y), ...
            if self.shape[0][0] == other.shape[0][0] == 0:
                shape0 = ((0, self.shape[0][1] + other.shape[0][1]), )
                shape = shape0 + self.shape[1:]
        return self.__class__(items, shape, self.ftype)

    def __radd__(self, other):
        if other in {0, 1}:
            return self.__class__([self.ftype.box(other)] + self._items,
                                  ftype=self.ftype)
        else:
            raise TypeError("expected Function or farray")

    def __mul__(self, num):
        """Repetition operator"""
        if not isinstance(num, int):
            raise TypeError("expected multiplier to be an int")
        if num < 0:
            raise ValueError("expected multiplier to be non-negative")

        items = self._items * num
        shape = None
        # Multi-dimensional arrays
        if self.ndim > 1:
            # (0,x), ... * N = (0,N*x), ...
            if self.shape[0][0] == 0:
                shape0 = ((0, self.shape[0][1] * num), )
                shape = shape0 + self.shape[1:]
        return self.__class__(items, shape, self.ftype)

    def __rmul__(self, num):
        return self.__mul__(num)

    # Function stuff
    def restrict(self, point):
        """Apply the ``restrict`` method to all functions.

        Returns a new farray.
        """
        items = [f.restrict(point) for f in self._items]
        return self.__class__(items, self.shape, self.ftype)

    def vrestrict(self, vpoint):
        """Expand all vectors in *vpoint* before applying ``restrict``."""
        return self.restrict(boolfunc.vpoint2point(vpoint))

    def compose(self, mapping):
        """Apply the ``compose`` method to all functions.

        Returns a new farray.
        """
        items = [f.compose(mapping) for f in self._items]
        return self.__class__(items, self.shape, self.ftype)

    # farray stuff
    @property
    def size(self):
        """Return the size of the array.

        The *size* of a multi-dimensional array is the product of the sizes
        of its dimensions.
        """
        return _volume(self.shape)

    @property
    def offsets(self):
        """Return a tuple of dimension offsets."""
        return tuple(start for start, _ in self.shape)

    @property
    def ndim(self):
        """Return the number of dimensions."""
        return len(self.shape)

    def reshape(self, *dims):
        """Return an equivalent farray with a modified shape."""
        shape = _dims2shape(*dims)
        if _volume(shape) != self.size:
            raise ValueError("expected shape with equal volume")
        return self.__class__(self._items, shape, self.ftype)

    @property
    def flat(self):
        """Return a 1D iterator over the farray."""
        yield from self._items

    def to_uint(self):
        """Convert vector to an unsigned integer, if possible.

        This is only useful for arrays filled with zero/one entries.
        """
        num = 0
        for i, f in enumerate(self._items):
            if f.is_zero():
                pass
            elif f.is_one():
                num += 1 << i
            else:
                fstr = "expected all functions to be a constant (0 or 1) form"
                raise ValueError(fstr)
        return num

    def to_int(self):
        """Convert vector to an integer, if possible.

        This is only useful for arrays filled with zero/one entries.
        """
        num = self.to_uint()
        if num and self._items[-1].unbox():
            return num - (1 << self.size)
        else:
            return num

    def zext(self, num):
        """Zero-extend this farray by *num* bits.

        Returns a new farray.
        """
        zero = self.ftype.box(0)
        return self.__class__(self._items + [zero] * num, ftype=self.ftype)

    def sext(self, num):
        """Sign-extend this farray by *num* bits.

        Returns a new farray.
        """
        sign = self._items[-1]
        return self.__class__(self._items + [sign] * num, ftype=self.ftype)

    # Unary operators
    def uor(self):
        """Unary OR reduction operator"""
        return reduce(operator.or_, self._items, self.ftype.box(0))

    def unor(self):
        """Unary NOR reduction operator"""
        return ~self.uor()

    def uand(self):
        """Unary AND reduction operator"""
        return reduce(operator.and_, self._items, self.ftype.box(1))

    def unand(self):
        """Unary NAND reduction operator"""
        return ~self.uand()

    def uxor(self):
        """Unary XOR reduction operator"""
        return reduce(operator.xor, self._items, self.ftype.box(0))

    def uxnor(self):
        """Unary XNOR reduction operator"""
        return ~self.uxor()

    # Shift operators
    def lsh(self, num, cin=None):
        """Left shift the farray by *num* places.

        The *num* argument must be a non-negative ``int``.

        If the *cin* farray is provided, it will be shifted in.
        Otherwise, the carry-in is zero.

        Returns a two-tuple (farray fs, farray cout),
        where *fs* is the shifted vector, and *cout* is the "carry out".

        Returns a new farray.
        """
        if num < 0 or num > self.size:
            raise ValueError("expected 0 <= num <= {0.size}".format(self))
        if cin is None:
            items = [self.ftype.box(0) for _ in range(num)]
            cin = self.__class__(items, ftype=self.ftype)
        else:
            if len(cin) != num:
                raise ValueError("expected length of cin to be equal to num")
        if num == 0:
            return self, self.__class__([], ftype=self.ftype)
        else:
            fs = self.__class__(cin._items + self._items[:-num],
                                ftype=self.ftype)
            cout = self.__class__(self._items[-num:], ftype=self.ftype)
            return fs, cout

    def rsh(self, num, cin=None):
        """Right shift the farray by *num* places.

        The *num* argument must be a non-negative ``int``.

        If the *cin* farray is provided, it will be shifted in.
        Otherwise, the carry-in is zero.

        Returns a two-tuple (farray fs, farray cout),
        where *fs* is the shifted vector, and *cout* is the "carry out".

        Returns a new farray.
        """
        if num < 0 or num > self.size:
            raise ValueError("expected 0 <= num <= {0.size}".format(self))
        if cin is None:
            items = [self.ftype.box(0) for _ in range(num)]
            cin = self.__class__(items, ftype=self.ftype)
        else:
            if len(cin) != num:
                raise ValueError("expected length of cin to be equal to num")
        if num == 0:
            return self, self.__class__([], ftype=self.ftype)
        else:
            fs = self.__class__(self._items[num:] + cin._items,
                                ftype=self.ftype)
            cout = self.__class__(self._items[:num], ftype=self.ftype)
            return fs, cout

    def arsh(self, num):
        """Arithmetically right shift the farray by *num* places.

        The *num* argument must be a non-negative ``int``.

        The carry-in will be the value of the most significant bit.

        Returns a new farray.
        """
        if num < 0 or num > self.size:
            raise ValueError("expected 0 <= num <= {0.size}".format(self))
        if num == 0:
            return self, self.__class__([], ftype=self.ftype)
        else:
            sign = self._items[-1]
            fs = self.__class__(self._items[num:] + [sign] * num,
                                ftype=self.ftype)
            cout = self.__class__(self._items[:num], ftype=self.ftype)
            return fs, cout

    # Other logic
    def decode(self):
        r"""Return a :math:`N \rightarrow 2^N` decoder.

        Example Truth Table for a 2:4 decoder:

        .. csv-table::
           :header: :math:`A_1`, :math:`A_0`, \
                    :math:`D_3`, :math:`D_2`, :math:`D_1`, :math:`D_0`
           :stub-columns: 2

           0, 0, 0, 0, 0, 1
           0, 1, 0, 0, 1, 0
           1, 0, 0, 1, 0, 0
           1, 1, 1, 0, 0, 0
        """
        items = [reduce(operator.and_, boolfunc.num2term(i, self._items),
                        self.ftype.box(1))
                 for i in range(2 ** self.size)]

        return self.__class__(items, ftype=self.ftype)

    # Subroutines of __getitem__/__setitem__
    def _keys2sls(self, keys, key2sl):
        """Convert an input key to a list of slices."""
        sls = list()
        if isinstance(keys, tuple):
            for key in keys:
                sls.append(key2sl(key))
        else:
            sls.append(key2sl(keys))
        if len(sls) > self.ndim:
            fstr = "expected <= {0.ndim} slice dimensions, got {1}"
            raise ValueError(fstr.format(self, len(sls)))
        return sls

    def _fill_slices(self, sls):
        """Fill all '...' and ':' slice entries."""
        # Fill '...' entries with ':'
        nfill = self.ndim - len(sls)
        fsls = list()
        for sl in sls:
            if sl is Ellipsis:
                while nfill:
                    fsls.append(slice(None, None))
                    nfill -= 1
                fsls.append(slice(None, None))
            else:
                fsls.append(sl)

        # Append ':' to the end
        for _ in range(self.ndim - len(fsls)):
            fsls.append(slice(None, None))

        return fsls

    def _norm_slices(self, fsls):
        """Convert slices to a normalized tuple of int/slice/farray."""
        # Normalize indices, and fill empty slice entries
        nsls = list()
        for i, fsl in enumerate(fsls):
            fsl_type = type(fsl)
            if fsl_type is int:
                nsls.append(_norm_index(i, fsl, *self.shape[i]))
            elif fsl_type is slice:
                nsls.append(_norm_slice(fsl, *self.shape[i]))
            # farray
            else:
                nsls.append(fsl)

        return nsls

    def _coord2offset(self, coord):
        """Convert a normalized coordinate to an item offset."""
        size = self.size
        offset = 0
        for dim, index in enumerate(coord):
            size //= self._normshape[dim]
            offset += size * index
        return offset

    @property
    def _normshape(self):
        """Return the shape normalized to zero offsets."""
        return tuple(stop - start for start, stop in self.shape)

    def _op_shape(self, other):
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


def _dims2shape(*dims):
    """Convert input dimensions to a shape."""
    if not dims:
        raise ValueError("expected at least one dimension spec")
    shape = list()
    for dim in dims:
        if isinstance(dim, int):
            dim = (0, dim)
        if isinstance(dim, tuple) and len(dim) == 2:
            if dim[0] < 0:
                raise ValueError("expected low dimension to be >= 0")
            if dim[1] < 0:
                raise ValueError("expected high dimension to be >= 0")
            if dim[0] > dim[1]:
                raise ValueError("expected low <= high dimensions")
            start, stop = dim
        else:
            raise TypeError("expected dimension to be int or (int, int)")
        shape.append((start, stop))
    return tuple(shape)


def _volume(shape):
    """Return the volume of a shape."""
    prod = 1
    for start, stop in shape:
        prod *= stop - start
    return prod


def _zeros(ftype, *dims):
    """Return a new farray filled with zeros."""
    shape = _dims2shape(*dims)
    objs = [ftype.box(0) for _ in range(_volume(shape))]
    return farray(objs, shape, ftype)


def _ones(ftype, *dims):
    """Return a new farray filled with ones."""
    shape = _dims2shape(*dims)
    objs = [ftype.box(1) for _ in range(_volume(shape))]
    return farray(objs, shape, ftype)


def _vars(ftype, name, *dims):
    """Return a new farray filled with Boolean variables."""
    shape = _dims2shape(*dims)
    objs = list()
    for indices in itertools.product(*[range(i, j) for i, j in shape]):
        objs.append(_VAR[ftype](name, indices))
    return farray(objs, shape, ftype)


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
    if not isinstance(objs, collections.abc.Sequence):
        raise TypeError("expected a sequence of Function")

    isseq = [isinstance(obj, collections.abc.Sequence) for obj in objs]
    if not any(isseq):
        ftype = None
        for obj in objs:
            if ftype is None:
                if isinstance(obj, BinaryDecisionDiagram):
                    ftype = BinaryDecisionDiagram
                elif isinstance(obj, Expression):
                    ftype = Expression
                elif isinstance(obj, TruthTable):
                    ftype = TruthTable
                else:
                    raise TypeError("expected valid Function inputs")
            elif not isinstance(obj, ftype):
                raise ValueError("expected uniform Function types")
        return list(objs), ((0, len(objs)), ), ftype
    elif all(isseq):
        items = list()
        shape = None
        ftype = None
        for obj in objs:
            _items, _shape, _ftype = _itemize(obj)
            if shape is None:
                shape = _shape
            elif shape != _shape:
                raise ValueError("expected uniform farray dimensions")
            if ftype is None:
                ftype = _ftype
            elif ftype != _ftype:
                raise ValueError("expected uniform Function types")
            items += _items
        shape = ((0, len(objs)), ) + shape
        return items, shape, ftype
    else:
        raise ValueError("expected uniform farray dimensions")


def _check_shape(shape):
    """Verify that a shape has the right format."""
    if isinstance(shape, tuple):
        for dim in shape:
            if (isinstance(dim, tuple) and len(dim) == 2 and
                    isinstance(dim[0], int) and isinstance(dim[1], int)):
                if dim[0] < 0:
                    raise ValueError("expected low dimension to be >= 0")
                if dim[1] < 0:
                    raise ValueError("expected high dimension to be >= 0")
                if dim[0] > dim[1]:
                    raise ValueError("expected low <= high dimensions")
            else:
                raise TypeError("expected shape dimension to be (int, int)")
    else:
        raise TypeError("expected shape to be tuple of (int, int)")


def _get_key2sl(key):
    """Convert a key part to a slice part."""
    if isinstance(key, (int, farray)) or key is Ellipsis:
        return key
    elif isinstance(key, slice):
        # Forbid slice steps
        if key.step is not None:
            raise ValueError("farray slice step is not supported")
        return key
    elif isinstance(key, boolfunc.Function):
        return farray([key])
    else:
        raise TypeError("expected int, slice, Function, farray, or ...")


def _set_key2sl(key):
    """Convert a key part to a slice part."""
    if isinstance(key, int) or key is Ellipsis:
        return key
    elif isinstance(key, slice):
        # Forbid slice steps
        if key.step is not None:
            raise ValueError("farray slice step is not supported")
        return key
    else:
        raise TypeError("expected int, slice, or ...")


def _norm_index(dim, index, start, stop):
    """Return an index normalized to an farray start index."""
    length = stop - start
    if -length <= index < 0:
        normindex = index + length
    elif start <= index < stop:
        normindex = index - start
    else:
        fstr = "expected dim {} index in range [{}, {})"
        raise IndexError(fstr.format(dim, start, stop))
    return normindex


def _norm_slice(sl, start, stop):
    """Return a slice normalized to an farray start index."""
    length = stop - start
    if sl.start is None:
        normstart = 0
    else:
        if sl.start < 0:
            if sl.start < -length:
                normstart = 0
            else:
                normstart = sl.start + length
        else:
            if sl.start > stop:
                normstart = length
            else:
                normstart = sl.start - start
    if sl.stop is None:
        normstop = length
    else:
        if sl.stop < 0:
            if sl.stop < -length:
                normstop = 0
            else:
                normstop = sl.stop + length
        else:
            if sl.stop > stop:
                normstop = length
            else:
                normstop = sl.stop - start
    if normstop < normstart:
        normstop = normstart
    return slice(normstart, normstop)


def _filtdim(items, shape, dim, nsl):
    """Return items, shape filtered by a dimension slice."""
    normshape = tuple(stop - start for start, stop in shape)
    nsl_type = type(nsl)
    newitems = list()
    # Number of groups
    num = reduce(operator.mul, normshape[:dim+1])
    # Size of each group
    size = len(items) // num
    # Size of the dimension
    n = normshape[dim]
    if nsl_type is int:
        for i in range(num):
            if i % n == nsl:
                newitems += items[size*i:size*(i+1)]
        # Collapse dimension
        newshape = shape[:dim] + shape[dim+1:]
    elif nsl_type is slice:
        for i in range(num):
            if nsl.start <= (i % n) < nsl.stop:
                newitems += items[size*i:size*(i+1)]
        # Reshape dimension
        offset = shape[dim][0]
        redim = (offset + nsl.start, offset + nsl.stop)
        newshape = shape[:dim] + (redim, ) + shape[dim+1:]
    # farray
    else:
        if nsl.size < clog2(n):
            fstr = "expected dim {} select to have >= {} bits, got {}"
            raise ValueError(fstr.format(dim, clog2(n), nsl.size))
        groups = [list() for _ in range(n)]
        for i in range(num):
            groups[i % n] += items[size*i:size*(i+1)]
        for muxins in zip(*groups):
            it = boolfunc.iter_terms(nsl._items)
            xs = [reduce(operator.and_, (muxin, ) + next(it))
                  for muxin in muxins]
            newitems.append(reduce(operator.or_, xs))
        # Collapse dimension
        newshape = shape[:dim] + shape[dim+1:]
    return newitems, newshape


def _iter_coords(nsls):
    """Iterate through all matching coordinates in a sequence of slices."""
    # First convert all slices to ranges
    ranges = list()
    for nsl in nsls:
        if isinstance(nsl, int):
            ranges.append(range(nsl, nsl+1))
        else:
            ranges.append(range(nsl.start, nsl.stop))
    # Iterate through all matching coordinates
    yield from itertools.product(*ranges)

