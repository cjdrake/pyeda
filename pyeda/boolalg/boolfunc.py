"""
The :mod:`pyeda.boolalg.boolfunc` module implements the fundamentals of
Boolean space, variables and functions.

Data Types:

point
    A dictionary of ``Variable => {0, 1}`` mappings.
    For example, ``{a: 0, b: 1, c: 0, d: 1}``.
    An N-dimensional *point* corresponds to one vertex of an N-dimensional
    *cube*.

untyped point
    An untyped, immutable representation of a *point*,
    represented as ``(frozenset([int]), frozenset([int]))``.
    The integers are Variable uniqids.
    Index zero contains a frozenset of variables mapped to zero,
    and index one contains a frozenset of variables mapped to one.
    This representation is easier to manipulate than the *point*,
    and it is hashable for caching purposes.

term
    A tuple of :math:`N` Boolean functions,
    intended to be used as the input of either an OR or AND function.
    An OR term is called a *maxterm* (product of sums),
    and an AND term is called a *minterm* (sum of products).

Interface Functions:

* :func:`num2point` --- Convert an integer into a point in an N-dimensional Boolean space
* :func:`num2upoint` --- Convert an integer into an untyped point in an N-dimensional Boolean space.
* :func:`num2term` --- Convert an integer into a min/max term in an N-dimensional Boolean space

* :func:`point2upoint` --- Convert a point into an untyped point
* :func:`point2term` --- Convert a point into a min/max term

* :func:`iter_points` --- Iterate through all points in an N-dimensional Boolean space
* :func:`iter_upoints` --- Iterate through all untyped points in an N-dimensional Boolean space
* :func:`iter_terms` --- Iterate through all min/max terms in an N-dimensional Boolean space

* :func:`vpoint2point` --- Convert a vector point into a point in an N-dimensional Boolean space

Interface Classes:

* :class:`Variable`
* :class:`Function`
"""

import functools
import operator
import re
import threading

from pyeda.util import bit_on, cached_property

VARIABLES = dict()


def var(name, index=None):
    """Return a unique Variable instance.

    .. note::
       Do **NOT** call this function directly.
       Instead, use one of the concrete implementations:

       * :func:`pyeda.boolalg.bdd.bddvar`
       * :func:`pyeda.boolalg.expr.exprvar`,
       * :func:`pyeda.boolalg.table.ttvar`.
    """
    tname = type(name)
    if tname is str:
        names = (name, )
    elif tname is tuple:
        names = name
    else:
        fstr = "expected name to be a str or tuple, got {0.__name__}"
        raise TypeError(fstr.format(tname))

    if not names:
        raise ValueError("expected at least one name")

    for name in names:
        tname = type(name)
        if tname is not str:
            fstr = "expected name to be a str, got {0.__name__}"
            raise TypeError(fstr.format(tname))
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            fstr = "expected name to match [a-zA-Z][a-zA-Z0-9_]*, got {}"
            raise ValueError(fstr.format(name))

    if index is None:
        indices = tuple()
    else:
        tindex = type(index)
        if tindex is int:
            indices = (index, )
        elif tindex is tuple:
            indices = index
        else:
            fstr = "expected index to be an int or tuple, got {0.__name__}"
            raise TypeError(fstr.format(tindex))

    for index in indices:
        tindex = type(index)
        if tindex is not int:
            fstr = "expected index to be an int, got {0.__name__}"
            raise TypeError(fstr.format(tindex))
        if index < 0:
            fstr = "expected index to be >= 0, got {}"
            raise ValueError(fstr.format(index))

    try:
        v = VARIABLES[(names, indices)]
    except KeyError:
        v = Variable(names, indices)
        VARIABLES[(names, indices)] = v
    return v

def num2point(num, vs):
    """Convert *num* into a point in an N-dimensional Boolean space.

    The *vs* argument is a sequence of :math:`N` Boolean variables.
    There are :math:`2^N` points in the corresponding Boolean space.
    The dimension number of each variable is its index in the sequence.

    The *num* argument is an int in range :math:`[0, 2^N)`.

    For example, consider the 3-dimensional space formed by variables
    :math:`a`, :math:`b`, :math:`c`.
    Each vertex corresponds to a 3-dimensional point as summarized by the
    table::

                6-----------7  ===== ======= =================
               /|          /|   num   a b c        point
              / |         / |  ===== ======= =================
             /  |        /  |    0    0 0 0   {a:0, b:0, c:0}
            4-----------5   |    1    1 0 0   {a:1, b:0, c:0}
            |   |       |   |    2    0 1 0   {a:0, b:1, c:0}
            |   |       |   |    3    1 1 0   {a:1, b:1, c:0}
            |   2-------|---3    4    0 0 1   {a:0, b:0, c:1}
            |  /        |  /     5    1 0 1   {a:1, b:0, c:1}
       c b  | /         | /      6    0 1 1   {a:0, b:1, c:1}
       |/   |/          |/       7    1 1 1   {a:1, b:1, c:1}
       +-a  0-----------1      ===== ======= =================

    .. note::
       The ``a b c`` column is the binary representation of *num*
       written in little-endian order.
    """
    if type(num) is not int:
        fstr = "expected num to be an int, got {0.__name__}"
        raise TypeError(fstr.format(type(num)))
    N = len(vs)
    if not 0 <= num < 2**N:
        fstr = "expected num to be in range [0, {}), got {}"
        raise ValueError(fstr.format(2**N, num))

    return {v: bit_on(num, i) for i, v in enumerate(vs)}

def num2upoint(num, vs):
    """Convert *num* into an untyped point in an N-dimensional Boolean space.

    The *vs* argument is a sequence of :math:`N` Boolean variables.
    There are :math:`2^N` points in the corresponding Boolean space.
    The dimension number of each variable is its index in the sequence.

    The *num* argument is an int in range :math:`[0, 2^N)`.

    See :func:`num2point` for a description of how *num* maps onto an
    N-dimensional point.
    This function merely converts the output to an immutable (untyped) form.
    """
    return point2upoint(num2point(num, vs))

def num2term(num, fs, conj=False):
    """Convert *num* into a min/max term in an N-dimensional Boolean space.

    The *fs* argument is a sequence of :math:`N` Boolean functions.
    There are :math:`2^N` points in the corresponding Boolean space.
    The dimension number of each function is its index in the sequence.

    The *num* argument is an int in range :math:`[0, 2^N)`.

    If *conj* is ``False``, return a minterm.
    Otherwise, return a maxterm.

    For example, consider the 3-dimensional space formed by functions
    :math:`f`, :math:`g`, :math:`h`.
    Each vertex corresponds to a min/max term as summarized by the table::

                6-----------7  ===== ======= ========== ==========
               /|          /|   num   f g h    minterm    maxterm
              / |         / |  ===== ======= ========== ==========
             /  |        /  |    0    0 0 0   f' g' h'   f  g  h
            4-----------5   |    1    1 0 0   f  g' h'   f' g  h
            |   |       |   |    2    0 1 0   f' g  h'   f  g' h
            |   |       |   |    3    1 1 0   f  g  h'   f' g' h
            |   2-------|---3    4    0 0 1   f' g' h    f  g  h'
            |  /        |  /     5    1 0 1   f  g' h    f' g  h'
       h g  | /         | /      6    0 1 1   f' g  h    f  g' h'
       |/   |/          |/       7    1 1 1   f  g  h    f' g' h'
       +-f  0-----------1      ===== ======= ========= ===========

    .. note::
       The ``f g h`` column is the binary representation of *num*
       written in little-endian order.
    """
    if type(num) is not int:
        fstr = "expected num to be an int, got {0.__name__}"
        raise TypeError(fstr.format(type(num)))
    N = len(fs)
    if not 0 <= num < 2**N:
        fstr = "expected num to be in range [0, {}), got {}"
        raise ValueError(fstr.format(2**N, num))

    if conj:
        return tuple(~f if bit_on(num, i) else f for i, f in enumerate(fs))
    else:
        return tuple(f if bit_on(num, i) else ~f for i, f in enumerate(fs))

def point2upoint(point):
    """Convert *point* into an untyped point."""
    upoint = [set(), set()]
    for v, val in point.items():
        upoint[val].add(v.uniqid)
    upoint[0] = frozenset(upoint[0])
    upoint[1] = frozenset(upoint[1])
    return tuple(upoint)

def point2term(point, conj=False):
    """Convert *point* into a min/max term.

    If *conj* is ``False``, return a minterm.
    Otherwise, return a maxterm.
    """
    if conj:
        return tuple(~v if val else v for v, val in point.items())
    else:
        return tuple(v if val else ~v for v, val in point.items())

def iter_points(vs):
    """Iterate through all points in an N-dimensional Boolean space.

    The *vs* argument is a sequence of :math:`N` Boolean variables.
    """
    for num in range(1 << len(vs)):
        yield num2point(num, vs)

def iter_upoints(vs):
    """Iterate through all untyped points in an N-dimensional Boolean space.

    The *vs* argument is a sequence of :math:`N` Boolean variables.
    """
    for num in range(1 << len(vs)):
        yield num2upoint(num, vs)

def iter_terms(fs, conj=False):
    """Iterate through all min/max terms in an N-dimensional Boolean space.

    The *fs* argument is a sequence of :math:`N` Boolean functions.

    If *conj* is ``False``, yield minterms.
    Otherwise, yield maxterms.
    """
    for num in range(1 << len(fs)):
        yield num2term(num, fs, conj)

def vpoint2point(vpoint):
    """Convert *vpoint* into a point in an N-dimensional Boolean space.

    The *vpoint* argument is a mapping from multi-dimensional arrays of
    variables to matching arrays of :math:`{0, 1}`.
    Elements from the values array will be converted to :math:`{0, 1}` using
    the `int` builtin function.

    For example::

       >>> from pyeda.boolalg.expr import exprvar
       >>> a = exprvar('a')
       >>> b00, b01, b10, b11 = map(exprvar, "b00 b01 b10 b11".split())
       >>> vpoint = {a: 0, ((b00, b01), (b10, b11)): ["01", "01"]}
       >>> point = vpoint2point(vpoint)
       >>> point[a], point[b00], point[b01], point[b10], point[b11]
       (0, 0, 1, 0, 1)

    The vpoint mapping is more concise if ``B`` is an farray::

       >>> from pyeda.boolalg.expr import exprvar
       >>> from pyeda.boolalg.bfarray import exprvars
       >>> a = exprvar('a')
       >>> B = exprvars('b', 2, 2)
       >>> vpoint = {a: 0, B: ["01", "01"]}
       >>> point = vpoint2point(vpoint)
       >>> point[a], point[B[0,0]], point[B[0,1]], point[B[1,0]], point[B[1,1]]
       (0, 0, 1, 0, 1)

    The shape of the array must match the shape of its values::

       >>> from pyeda.boolalg.bfarray import exprvars
       >>> X = exprvars('x', 2, 2)
       >>> vpoint = {X: "0101"}
       >>> point = vpoint2point(vpoint)
       Traceback (most recent call last):
           ...
       ValueError: expected 1:1 mapping from Variable => {0, 1}
    """
    point = dict()
    for v, val in vpoint.items():
        point.update(_flatten(v, val))
    return point

def _flatten(v, val):
    """Recursively flatten vectorized var => {0, 1} mappings."""
    if isinstance(v, Variable):
        yield v, int(val)
    else:
        if len(v) != len(val):
            raise ValueError("expected 1:1 mapping from Variable => {0, 1}")
        for _var, _val in zip(v, val):
            yield from _flatten(_var, _val)


_UNIQIDS = dict()
_COUNT = 1

class Variable:
    r"""
    Base class for a symbolic Boolean variable.

    A Boolean *variable* is an abstract numerical quantity that may assume any
    value in the set :math:`B = \{0, 1\}`.

    .. note::
       Do **NOT** instantiate a ``Variable`` directly.
       Instead, use one of the concrete implementations:
       :func:`pyeda.boolalg.bdd.bddvar` :func:`pyeda.boolalg.expr.exprvar`,
       :func:`pyeda.boolalg.table.ttvar`.

    A variable is defined by one or more *names*,
    and zero or more *indices*.
    Multiple names establish hierarchical namespaces,
    and multiple indices group several related variables.

    Each variable has a unique, positive integer called the *uniqid*.
    This integer may be used to identify a variable that is represented by
    more than one data structure.
    For example, ``bddvar('a', 0)`` and ``exprvar('a', 0)`` will refer to two
    different Variable instances, but both will share the same uniqid.

    All variables are implicitly ordered.
    If two variable names are identical, compare their indices.
    Otherwise, do a string comparison of their names.
    This is only useful where variable order matters,
    and is not meaningful in any algebraic sense.

    For example, the following statements are true:

    * ``a == a``
    * ``a < b``
    * ``a[0] < a[1]``
    * ``a[0][1] < a[0][2]``
    """
    def __init__(self, names, indices):
        global _UNIQIDS, _COUNT

        with threading.Lock():
            try:
                uniqid = _UNIQIDS[(names, indices)]
            except KeyError:
                uniqid = _COUNT
                _COUNT += 1
                _UNIQIDS[(names, indices)] = uniqid

        self.names = names
        self.indices = indices
        self.uniqid = uniqid

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.indices:
            suffix = "[" + ",".join(str(idx) for idx in self.indices) + "]"
            return self.qualname + suffix
        else:
            return self.qualname

    def __lt__(self, other):
        if self.names == other.names:
            return self.indices < other.indices
        else:
            return self.names < other.names

    @property
    def name(self):
        """Return the innermost variable name."""
        return self.names[0]

    @property
    def qualname(self):
        """Return the fully qualified name."""
        return ".".join(reversed(self.names))


class Function:
    """
    Abstract base class that defines an interface for a symbolic Boolean
    function of :math:`N` variables.
    """
    # Operators
    def __invert__(self):
        """Boolean negation operator

        +-----------+------------+
        | :math:`f` | :math:`f'` |
        +===========+============+
        |         0 |          1 |
        +-----------+------------+
        |         1 |          0 |
        +-----------+------------+
        """
        raise NotImplementedError()

    def __or__(self, g):
        """Boolean disjunction (sum, OR) operator

        +-----------+-----------+---------------+
        | :math:`f` | :math:`g` | :math:`f + g` |
        +===========+===========+===============+
        |         0 |         0 |             0 |
        +-----------+-----------+---------------+
        |         0 |         1 |             1 |
        +-----------+-----------+---------------+
        |         1 |         0 |             1 |
        +-----------+-----------+---------------+
        |         1 |         1 |             1 |
        +-----------+-----------+---------------+
        """
        raise NotImplementedError()

    def __ror__(self, g):
        return self.__or__(g)

    def __and__(self, g):
        r"""Boolean conjunction (product, AND) operator

        +-----------+-----------+-------------------+
        | :math:`f` | :math:`g` | :math:`f \cdot g` |
        +===========+===========+===================+
        |         0 |         0 |                 0 |
        +-----------+-----------+-------------------+
        |         0 |         1 |                 0 |
        +-----------+-----------+-------------------+
        |         1 |         0 |                 0 |
        +-----------+-----------+-------------------+
        |         1 |         1 |                 1 |
        +-----------+-----------+-------------------+
        """
        raise NotImplementedError()

    def __rand__(self, g):
        return self.__and__(g)

    def __xor__(self, g):
        r"""Boolean exclusive or (XOR) operator

        +-----------+-----------+--------------------+
        | :math:`f` | :math:`g` | :math:`f \oplus g` |
        +===========+===========+====================+
        |         0 |         0 |                  0 |
        +-----------+-----------+--------------------+
        |         0 |         1 |                  1 |
        +-----------+-----------+--------------------+
        |         1 |         0 |                  1 |
        +-----------+-----------+--------------------+
        |         1 |         1 |                  0 |
        +-----------+-----------+--------------------+
        """
        raise NotImplementedError()

    def __rxor__(self, g):
        return self.__xor__(g)

    def __add__(self, other):
        """Concatenation operator

        The *other* argument may be a Function or an farray.
        """
        from pyeda.boolalg.bfarray import farray
        if other in {0, 1}:
            return farray([self] + [self.box(other)])
        elif isinstance(other, Function):
            return farray([self] + [other])
        elif isinstance(other, farray):
            return farray([self] + list(other.flat))
        else:
            raise TypeError("expected Function or farray")

    def __radd__(self, other):
        from pyeda.boolalg.bfarray import farray
        if other in {0, 1}:
            return farray([self.box(other)] + [self])
        else:
            raise TypeError("expected Function or farray")

    def __mul__(self, num):
        """Repetition operator"""
        from pyeda.boolalg.bfarray import farray
        if type(num) is not int:
            raise TypeError("expected multiplier to be an int")
        if num < 0:
            raise ValueError("expected multiplier to be non-negative")
        return farray([self] * num)

    def __rmul__(self, num):
        return self.__mul__(num)

    @property
    def support(self):
        r"""Return the support set of a function.

        Let :math:`f(x_1, x_2, \dots, x_n)` be a Boolean function of :math:`N`
        variables.

        The unordered set :math:`\{x_1, x_2, \dots, x_n\}` is called the
        *support* of the function.
        """
        raise NotImplementedError()

    @cached_property
    def usupport(self):
        """Return the untyped support set of a function."""
        return frozenset(v.uniqid for v in self.support)

    @property
    def inputs(self):
        """Return the support set in name/index order."""
        raise NotImplementedError()

    @property
    def top(self):
        """Return the first variable in the ordered support set."""
        if self.inputs:
            return self.inputs[0]
        else:
            return None

    @property
    def degree(self):
        r"""Return the degree of a function.

        A function from :math:`B^{N} \Rightarrow B` is called a Boolean
        function of *degree* :math:`N`.
        """
        return len(self.support)

    @property
    def cardinality(self):
        r"""Return the cardinality of the relation :math:`B^{N} \Rightarrow B`.

        Always equal to :math:`2^{N}`.
        """
        return 1 << self.degree

    def iter_domain(self):
        """Iterate through all points in the domain."""
        yield from iter_points(self.inputs)

    def iter_image(self):
        """Iterate through all elements in the image."""
        for point in iter_points(self.inputs):
            yield self.restrict(point)

    def iter_relation(self):
        """Iterate through all (point, element) pairs in the relation."""
        for point in iter_points(self.inputs):
            yield (point, self.restrict(point))

    def restrict(self, point):
        r"""
        Restrict a subset of support variables to :math:`\{0, 1\}`.

        Returns a new function: :math:`f(x_i, \ldots)`

        :math:`f \: | \: x_i = b`
        """
        return self.urestrict(point2upoint(point))

    def urestrict(self, upoint):
        """Implementation of restrict that requires an untyped point."""
        raise NotImplementedError()

    def vrestrict(self, vpoint):
        """Expand all vectors in *vpoint* before applying ``restrict``."""
        return self.restrict(vpoint2point(vpoint))

    def compose(self, mapping):
        r"""
        Substitute a subset of support variables with other Boolean functions.

        Returns a new function: :math:`f(g_i, \ldots)`

        :math:`f_1 \: | \: x_i = f_2`
        """
        raise NotImplementedError()

    def satisfy_one(self):
        """
        If this function is satisfiable, return a satisfying input point. A
        tautology *may* return a zero-dimensional point; a contradiction *must*
        return None.
        """
        raise NotImplementedError()

    def satisfy_all(self):
        """Iterate through all satisfying input points."""
        raise NotImplementedError()

    def satisfy_count(self):
        """Return the cardinality of the set of all satisfying input points."""
        return sum(1 for _ in self.satisfy_all())

    def iter_cofactors(self, vs=None):
        r"""Iterate through the cofactors of a function over N variables.

        The *vs* argument is a sequence of :math:`N` Boolean variables.

        The *cofactor* of :math:`f(x_1, x_2, \dots, x_i, \dots, x_n)`
        with respect to variable :math:`x_i` is:
        :math:`f_{x_i} = f(x_1, x_2, \dots, 1, \dots, x_n)`

        The *cofactor* of :math:`f(x_1, x_2, \dots, x_i, \dots, x_n)`
        with respect to variable :math:`x_i'` is:
        :math:`f_{x_i'} = f(x_1, x_2, \dots, 0, \dots, x_n)`
        """
        vs = self._expect_vars(vs)
        for upoint in iter_upoints(vs):
            yield self.urestrict(upoint)

    def cofactors(self, vs=None):
        r"""Return a tuple of the cofactors of a function over N variables.

        The *vs* argument is a sequence of :math:`N` Boolean variables.

        The *cofactor* of :math:`f(x_1, x_2, \dots, x_i, \dots, x_n)`
        with respect to variable :math:`x_i` is:
        :math:`f_{x_i} = f(x_1, x_2, \dots, 1, \dots, x_n)`

        The *cofactor* of :math:`f(x_1, x_2, \dots, x_i, \dots, x_n)`
        with respect to variable :math:`x_i'` is:
        :math:`f_{x_i'} = f(x_1, x_2, \dots, 0, \dots, x_n)`
        """
        return tuple(cf for cf in self.iter_cofactors(vs))

    def smoothing(self, vs=None):
        r"""Return the smoothing of a function over a sequence of N variables.

        The *vs* argument is a sequence of :math:`N` Boolean variables.

        The *smoothing* of :math:`f(x_1, x_2, \dots, x_i, \dots, x_n)` with
        respect to variable :math:`x_i` is:
        :math:`S_{x_i}(f) = f_{x_i} + f_{x_i'}`

        This is the same as the existential quantification operator:
        :math:`\exists \{x_1, x_2, \dots\} \: f`
        """
        return functools.reduce(operator.or_, self.iter_cofactors(vs))

    def consensus(self, vs=None):
        r"""Return the consensus of a function over a sequence of N variables.

        The *vs* argument is a sequence of :math:`N` Boolean variables.

        The *consensus* of :math:`f(x_1, x_2, \dots, x_i, \dots, x_n)` with
        respect to variable :math:`x_i` is:
        :math:`C_{x_i}(f) = f_{x_i} \cdot f_{x_i'}`

        This is the same as the universal quantification operator:
        :math:`\forall \{x_1, x_2, \dots\} \: f`
        """
        return functools.reduce(operator.and_, self.iter_cofactors(vs))

    def derivative(self, vs=None):
        r"""Return the derivative of a function over a sequence of N variables.

        The *vs* argument is a sequence of :math:`N` Boolean variables.

        The *derivative* of :math:`f(x_1, x_2, \dots, x_i, \dots, x_n)` with
        respect to variable :math:`x_i` is:
        :math:`\frac{\partial}{\partial x_i} f = f_{x_i} \oplus f_{x_i'}`

        This is also known as the Boolean *difference*.
        """
        return functools.reduce(operator.xor, self.iter_cofactors(vs))

    def is_zero(self):
        """Return whether this function is zero.

        .. note::
           This method will only look for a particular "zero form",
           and will **NOT** do a full search for a contradiction.
        """
        raise NotImplementedError()

    def is_one(self):
        """Return whether this function is one.

        .. note::
           This method will only look for a particular "one form",
           and will **NOT** do a full search for a tautology.
        """
        raise NotImplementedError()

    @staticmethod
    def box(obj):
        """Convert primitive types to a Function."""
        raise NotImplementedError()

    def unbox(self):
        """Return integer 0 or 1 if possible, otherwise return the Function."""
        if self.is_zero():
            return 0
        elif self.is_one():
            return 1
        else:
            return self

    @staticmethod
    def _expect_vars(vs=None):
        """Verify the input type and return a list of Variables."""
        if vs is None:
            return list()
        elif isinstance(vs, Variable):
            return [vs]
        else:
            checked = list()
            # Will raise TypeError if vs is not iterable
            for v in vs:
                if isinstance(v, Variable):
                    checked.append(v)
                else:
                    fstr = "expected Variable, got {0.__name__}"
                    raise TypeError(fstr.format(type(v)))
            return checked

