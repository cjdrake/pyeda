"""
Boolean Functions

Interface Functions:
    num2point
    num2upoint
    num2term

    point2upoint
    point2term

    iter_points
    iter_upoints
    iter_terms

Interface Classes:
    Variable
    Function
    Slicer
    VectorFunction
"""

import collections
import functools

from pyeda.util import bit_on, boolify, cached_property

VARIABLES = dict()


def var(name, index=None):
    """Return a unique Variable instance.

    .. NOTE:: Do NOT call this function directly. It should only be used by
              concrete Variable implementations, eg ExprVariable.
    """
    if type(name) is str:
        names = (name, )
    else:
        names = name
    if index is None:
        indices = tuple()
    elif type(index) is int:
        indices = (index, )
    else:
        indices = index

    # Check input types
    assert type(names) is tuple and len(names) > 0
    assert all(type(name) is str for name in names)
    assert type(indices) is tuple
    assert all(type(index) is int for index in indices)

    try:
        v = VARIABLES[(names, indices)]
    except KeyError:
        v = Variable(names, indices)
        VARIABLES[(names, indices)] = v
    return v

def num2point(num, vs):
    """Convert a number into a point in an N-dimensional space.

    Parameters
    ----------
    num : int
    vs : [Variable]
    """
    return {v: bit_on(num, i) for i, v in enumerate(vs)}

def num2upoint(num, vs):
    """Convert a number into an untyped point in an N-dimensional space.

    Parameters
    ----------
    num : int
    vs : [Variable]
    """
    upoint = [set(), set()]
    for i, v in enumerate(vs):
        upoint[bit_on(num, i)].add(v.uniqid)
    return frozenset(upoint[0]), frozenset(upoint[1])

def num2term(num, vs, conj=False):
    """Convert a number into a min/max term.

    Parameters
    ----------
    num : int
    vs : [Variable]
    conj : bool
        conj=False for minterms, conj=True for maxterms

    Examples
    --------

    Table of min/max terms for Boolean space {a, b, c}

    +-----+----------+----------+
    | num |  minterm |  maxterm |
    +=====+==========+==========+
    | 0   | a' b' c' | a  b  c  |
    | 1   | a  b' c' | a' b  c  |
    | 2   | a' b  c' | a  b' c  |
    | 3   | a  b  c' | a' b' c  |
    | 4   | a' b' c  | a  b  c' |
    | 5   | a  b' c  | a' b  c' |
    | 6   | a' b  c  | a  b' c' |
    | 7   | a  b  c  | a' b' c' |
    +-------+----------+----------+
    """
    if conj:
        return tuple(-v if bit_on(num, i) else v for i, v in enumerate(vs))
    else:
        return tuple(v if bit_on(num, i) else -v for i, v in enumerate(vs))

def point2upoint(point):
    """Convert a point into an untyped point.

    Parameters
    ----------
    point : {Variable: int}
    """
    upoint = [set(), set()]
    for v, val in point.items():
        upoint[val].add(v.uniqid)
    upoint[0] = frozenset(upoint[0])
    upoint[1] = frozenset(upoint[1])
    return tuple(upoint)

def point2term(point, conj=False):
    """Convert a point in an N-dimension space into a min/max term.

    Parameters
    ----------
    point : {Variable: int}
    """
    if conj:
        return tuple(-v if val else v for v, val in point.items())
    else:
        return tuple(v if val else -v for v, val in point.items())

def iter_points(vs):
    """Iterate through all points in an N-dimensional space.

    Parameters
    ----------
    vs : [Variable]
    """
    for num in range(1 << len(vs)):
        yield num2point(num, vs)

def iter_upoints(vs):
    """Iterate through all untyped points in an N-dimensional space.

    Parameters
    ----------
    vs : [Variable]
    """
    for num in range(1 << len(vs)):
        yield num2upoint(num, vs)

def iter_terms(vs, conj=False):
    """Iterate through all min/max terms in an N-dimensional space.

    Parameters
    ----------
    vs: [Variable]
    """
    for num in range(1 << len(vs)):
        yield num2term(num, vs, conj)


_UNIQIDS = dict()
_CNT = 1

class Variable(object):
    """
    Abstract base class that defines an interface for a Boolean variable.

    A Boolean variable is a numerical quantity that may assume any value in the
    set B = {0, 1}.

    This implementation includes optional indices, nonnegative integers that
    can be used to construct multi-dimensional bit vectors.
    """
    def __init__(self, names, indices):
        global _UNIQIDS, _CNT
        try:
            uniqid = _UNIQIDS[(names, indices)]
        except KeyError:
            uniqid = _CNT
            _CNT += 1
            _UNIQIDS[(names, indices)] = uniqid

        self.names = names
        self.indices = indices
        self.uniqid = uniqid

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        suffix = "".join("[{}]".format(idx) for idx in self.indices)
        return self.qualname + suffix

    def __lt__(self, other):
        if self.names == other.names:
            return self.indices < other.indices
        else:
            return self.names < other.names

    @property
    def name(self):
        """Return the variable name."""
        return self.names[0]

    @property
    def qualname(self):
        """Return the fully qualified name."""
        return ".".join(reversed(self.names))


class Function(object):
    """
    Abstract base class that defines an interface for a scalar Boolean function
    of :math:`N` variables.
    """

    # Operators
    def __neg__(self):
        """Boolean negation operator

        +-----------+------------+
        | :math:`f` | :math:`-f` |
        +===========+============+
        |         0 |          1 |
        +-----------+------------+
        |         1 |          0 |
        +-----------+------------+
        """
        raise NotImplementedError()

    def __add__(self, other):
        """Boolean disjunction (addition, OR) operator

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

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        """Alias: a - b <=> a + -b"""
        raise NotImplementedError()

    def __rsub__(self, other):
        return self.__neg__().__add__(other)

    def __mul__(self, other):
        r"""Boolean conjunction (multiplication, AND) operator

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

    def __rmul__(self, other):
        return self.__mul__(other)

    def xor(self, other):
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

    @property
    def support(self):
        r"""Return the support set of a function.

        Let :math:`f(x_1, x_2, ..., x_n)` be a Boolean function of :math:`N`
        variables.

        The unordered set :math:`\{x_1, x_2, ..., x_n\}` is called the *support*
        of the function.
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
        for point in iter_points(self.inputs):
            yield point

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
        Return the Boolean function that results after restricting a subset of
        its input variables to :math:`\{0, 1\}`.

        :math:`g = f \: | \: x_i = b`
        """
        return self.urestrict(point2upoint(point))

    def urestrict(self, upoint):
        """Implementation of restrict that requires an untyped point."""
        raise NotImplementedError()

    def vrestrict(self, vpoint):
        """Expand all vectors before applying 'restrict'."""
        return self.restrict(_expand_vectors(vpoint))

    def compose(self, mapping):
        r"""
        Return the Boolean function that results after substituting a subset of
        its input variables for other Boolean functions.

        :math:`g = f_1 \: | \: x_i = f2`
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
        raise NotImplementedError()

    def iter_cofactors(self, vs=None):
        """Iterate through the cofactors of N variables.

        The *cofactor* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)`
        with respect to variable :math:`x_i` is
        :math:`f_{x_i} = f(x_1, x_2, ..., 1, ..., x_n)`

        The *cofactor* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)`
        with respect to variable :math:`x_i'` is
        :math:`f_{x_i'} = f(x_1, x_2, ..., 0, ..., x_n)`
        """
        vs = self._expect_vars(vs)
        for upoint in iter_upoints(vs):
            yield self.urestrict(upoint)

    def cofactors(self, vs=None):
        """Return a tuple of cofactors of N variables.

        The *cofactor* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)`
        with respect to variable :math:`x_i` is
        :math:`f_{x_i} = f(x_1, x_2, ..., 1, ..., x_n)`

        The *cofactor* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)`
        with respect to variable :math:`x_i'` is
        :math:`f_{x_i'} = f(x_1, x_2, ..., 0, ..., x_n)`
        """
        return tuple(cf for cf in self.iter_cofactors(vs))

    def is_neg_unate(self, vs=None):
        r"""Return whether a function is negative unate.

        A function :math:`f(x_1, x_2, ..., x_i, ..., x_n)` is *negative unate*
        in variable :math:`x_i` if :math:`f_{x_i'} \geq f_{xi}`.
        """
        raise NotImplementedError()

    def is_pos_unate(self, vs=None):
        r"""Return whether a function is positive unate.

        A function :math:`f(x_1, x_2, ..., x_i, ..., x_n)` is *positive unate*
        in variable :math:`x_i` if :math:`f_{x_i} \geq f_{x_i'}`.
        """
        raise NotImplementedError()

    def is_binate(self, vs=None):
        """Return whether a function is binate.

        A function :math:`f(x_1, x_2, ..., x_i, ..., x_n)` is *binate* in
        variable :math:`x_i` if it is neither negative nor positive unate in
        :math:`x_i`.
        """
        return not (self.is_neg_unate(vs) or self.is_pos_unate(vs))

    def smoothing(self, vs=None):
        """Return the smoothing of a function.

        The *smoothing* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)` with respect
        to variable :math:`x_i` is :math:`S_{x_i}(f) = f_{x_i} + f_{x_i'}`.
        """
        return functools.reduce(self.__class__.__add__, self.iter_cofactors(vs))

    def consensus(self, vs=None):
        r"""Return the consensus of a function.

        The *consensus* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)` with respect
        to variable :math:`x_i` is :math:`C_{x_i}(f) = f_{x_i} \cdot f_{x_i'}`.
        """
        return functools.reduce(self.__class__.__mul__, self.iter_cofactors(vs))

    def derivative(self, vs=None):
        r"""Return the derivative of a function.

        The *derivative* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)` with respect
        to variable :math:`x_i` is
        :math:`\frac{\partial}{\partial x_i} f = f_{x_i} \oplus f_{x_i'}`.
        """
        return functools.reduce(self.__class__.xor, self.iter_cofactors(vs))

    def is_zero(self):
        """Return whether this function is zero.

        .. NOTE:: This method will only look for a particular "zero form",
                  and will **NOT** do a full search for a contradiction.
        """
        raise NotImplementedError()

    def is_one(self):
        """Return whether this function is one.

        .. NOTE:: This method will only look for a particular "one form",
                  and will **NOT** do a full search for a tautology.
        """
        raise NotImplementedError()

    @staticmethod
    def box(arg):
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
        """Verify the input type and return an iterable of Variables."""
        if vs is None:
            return list()
        elif isinstance(vs, Variable):
            return [vs]
        else:
            if (isinstance(vs, collections.Iterable) and
                all(isinstance(v, Variable) for v in vs)):
                return vs
            else:
                raise TypeError("expected iter of Variable")


class Slicer(object):
    """Interface for vector objects that supports non-zero start index.

    Similar to a Python list, this class can be used to support arbitrarily
    nested vectors. Unlike Python lists, you can use a Slicer object to
    instantiate a vector with arbitrary start, stop indices.

    NOTE: This is a general-purpose utility class, but for the purposes of
          creating and manipulating BitVectors, we recommend using the
          BitVector class from pyeda.vexpr, or the 'bitvec' convenience
          function.
    """

    def __init__(self, items, start=0):
        self.items = items
        self.start = start

    @property
    def stop(self):
        """Return the stop index."""
        return self.start + self.__len__()

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def getifz(self, i):
        """Get item from zero-based index."""
        return self.__getitem__(i + self.start)

    def __getitem__(self, sl):
        if isinstance(sl, int):
            return self.items[self._norm_idx(sl)]
        else:
            items = self.items[self._norm_slice(sl)]
            return self.__class__(items, sl.start)

    def __setitem__(self, sl, item):
        if isinstance(sl, int):
            self.items[self._norm_idx(sl)] = item
        else:
            self.items[self._norm_slice(sl)] = item

    def __delitem__(self, sl):
        if isinstance(sl, int):
            del self.items[self._norm_idx(sl)]
        else:
            del self.items[self._norm_slice(sl)]

    def _norm_idx(self, i):
        """Return an index normalized to vector start index."""
        if i >= self.start and i < self.stop:
            idx = i - self.start
        elif i >= -self.stop and i < -self.start:
            idx = i + self.stop
        else:
            raise IndexError("list index out of range")
        return idx

    def _norm_slice(self, sl):
        """Return a slice normalized to vector start index."""
        limits = {'start': None, 'stop': None}
        for k in ('start', 'stop'):
            i = getattr(sl, k)
            if i is not None:
                if i >= self.start and i < self.stop:
                    limits[k] = i - self.start
                elif i >= -self.stop and i < -self.start:
                    limits[k] = i + self.stop
                else:
                    raise IndexError("list index out of range")
        return slice(limits['start'], limits['stop'])


class VectorFunction(Slicer):
    """
    Abstract base class that defines an interface for a vector Boolean function.
    """
    def restrict(self, point):
        """
        Return the vector that results from applying the 'restrict' method to
        all functions.
        """
        items = [f.restrict(point) for f in self]
        return self.__class__(items, self.start)

    def vrestrict(self, vpoint):
        """Expand all vectors before applying 'restrict'."""
        return self.restrict(_expand_vectors(vpoint))

    def to_uint(self):
        """Convert vector to an unsigned integer, if possible."""
        num = 0
        for i, f in enumerate(self):
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
            return num - (1 << self.__len__())
        else:
            return num

    def zext(self, num):
        """Zero extend this vector by N bits."""
        self.items += [0] * num

    def sext(self, num):
        """Sign extend this vector by N bits."""
        bit = self.items[-1]
        self.items += [bit] * num

    def append(self, f):
        """Append a function to the end of this vector."""
        self.items.append(f)


def _expand_vectors(vpoint):
    """Expand all vectors in a substitution dict."""
    point = dict()
    for vf, vals in vpoint.items():
        if isinstance(vf, VectorFunction):
            if len(vf) != len(vals):
                fstr = ("invalid vector point: "
                        "expected 1:1 mapping from VectorFunction => {0, 1}")
                raise ValueError(fstr)
            for i, val in enumerate(vals):
                point[vf.getifz(i)] = boolify(val)
        else:
            point[vf] = boolify(vals)
    return point
