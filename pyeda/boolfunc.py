"""
Boolean Functions

Globals:
    VARIABLES

Interface Functions:
    num2point
    point2term
    num2term
    iter_points
    iter_terms

Interface Classes:
    Variable
    Function
    Slicer
    VectorFunction
"""

from pyeda.common import bit_on

VARIABLES = dict()


def num2point(num, vs):
    """Convert a number to a point in an N-dimensional space."""
    return {v: bit_on(num, i) for i, v in enumerate(vs)}

def point2term(point, conj=False):
    """Convert a point in an N-dimension space to a min/max term."""
    if conj:
        return tuple(-v if val else v for v, val in point.items())
    else:
        return tuple(v if val else -v for v, val in point.items())

def num2term(num, vs, conj=False):
    """Return a tuple of all variables for a given term index.

    Parameters
    ----------
    num: int
    vs: [Variable]
    conj: bool
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

def iter_points(vs):
    """Iterate through all points in an N-dimensional space.

    Parameters
    ----------
    vs : [Variable]
    """
    for num in range(1 << len(vs)):
        yield num2point(num, vs)

def iter_terms(vs, conj=False):
    """Iterate through all terms in an N-dimensional space.

    Parameters
    ----------
    vs: [Variable]
    """
    for num in range(1 << len(vs)):
        yield num2term(num, vs, conj)


class Variable(object):
    """
    Abstract base class that defines an interface for a Boolean variable.

    A Boolean variable is a numerical quantity that may assume any value in the
    set B = {0, 1}.

    This implementation includes optional indices, nonnegative integers that
    can be used to construct multi-dimensional bit vectors.
    """

    _UNIQIDS = dict()
    _CNT = 1

    def __new__(cls, name, indices=None, namespace=None):
        if indices is None:
            indices = tuple()
        elif type(indices) is int:
            indices = (indices, )
        try:
            uniqid = cls._UNIQIDS[(namespace, name, indices)]
        except KeyError:
            uniqid = cls._CNT
            cls._CNT += 1
            cls._UNIQIDS[(namespace, name, indices)] = uniqid
        try:
            self = VARIABLES[uniqid]
        except KeyError:
            self = super(Variable, cls).__new__(cls)
            self.namespace = namespace
            self.name = name
            self.indices = indices
            self.uniqid = uniqid
            VARIABLES[self.uniqid] = self
        return self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        suffix = "".join("[{}]".format(idx) for idx in self.indices)
        return self.qualname + suffix

    def __lt__(self, other):
        if self.name == other.name:
            return self.indices < other.indices
        else:
            return self.name < other.name

    @property
    def qualname(self):
        if self.namespace is None:
            return self.name
        else:
            return self.namespace + "." + self.name


class Function(object):
    """
    Abstract base class that defines an interface for a scalar Boolean function
    of :math:`N` variables.
    """
    @property
    def support(self):
        """Return the support set of a function.

        Let :math:`f(x_1, x_2, ..., x_n)` be a Boolean function of :math:`N`
        variables. The set :math:`\{x_1, x_2, ..., x_n\}` is called the
        *support* of the function.
        """
        raise NotImplementedError()

    @property
    def inputs(self):
        """Return the support set in name/index order."""
        raise NotImplementedError()

    @property
    def top(self):
        """Return the first variable in the ordered support set."""
        return self.inputs[0]

    @property
    def bottom(self):
        """Return the last variable in the ordered support set."""
        return self.inputs[-1]

    @property
    def degree(self):
        """Return the degree of a function.

        A function from :math:`B^{N} \Rightarrow B` is called a Boolean
        function of *degree* :math:`N`.
        """
        return len(self.support)

    @property
    def cardinality(self):
        """Return the cardinality of the relation :math:`B^{N} \Rightarrow B`.

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

    def iter_zeros(self):
        """Iterate through all points this function maps to element zero."""
        raise NotImplementedError()

    def iter_ones(self):
        """Iterate through all points this function maps to element one."""
        raise NotImplementedError()

    def reduce(self):
        """Return the function reduced to a canonical form."""
        raise NotImplementedError()

    def restrict(self, point):
        """
        Return the Boolean function that results after restricting a subset of
        its input variables to :math:`\{0, 1\}`.

        :math:`g = f \: | \: x_i = b`
        """
        raise NotImplementedError()

    def vrestrict(self, point):
        """Expand all vectors before applying 'restrict'."""
        return self.restrict(_expand_vectors(point))

    def compose(self, mapping):
        """
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
        """Iterate through the cofactors of :math:`N` variables."""
        if vs is None:
            vs = list()
        elif isinstance(vs, Variable):
            vs = [vs]
        for point in iter_points(vs):
            yield point, self.restrict(point)

    def cofactors(self, vs=None):
        """Return a tuple of cofactors of N variables.

        The *cofactor* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)`
        with respect to variable :math:`x_i` is
        :math:`f_{x_i} = f(x_1, x_2, ..., 1, ..., x_n)`

        The *cofactor* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)`
        with respect to variable :math:`x_i'` is
        :math:`f_{x_i'} = f(x_1, x_2, ..., 0, ..., x_n)`
        """
        return tuple(cf for p, cf in self.iter_cofactors(vs))

    def is_neg_unate(self, vs=None):
        """Return whether a function is negative unate.

        A function :math:`f(x_1, x_2, ..., x_i, ..., x_n)` is *negative unate*
        in variable :math:`x_i` if :math:`f_{x_i'} \geq f_{xi}`.
        """
        raise NotImplementedError()

    def is_pos_unate(self, vs=None):
        """Return whether a function is positive unate.

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
        raise NotImplementedError()

    def consensus(self, vs=None):
        """Return the consensus of a function.

        The *consensus* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)` with respect
        to variable :math:`x_i` is :math:`C_{x_i}(f) = f_{x_i} \cdot f_{x_i'}`.
        """
        raise NotImplementedError()

    def derivative(self, vs=None):
        r"""Return the derivative of a function.

        The *derivate* of :math:`f(x_1, x_2, ..., x_i, ..., x_n)` with respect
        to variable :math:`x_i` is
        :math:`\frac{\partial}{\partial x_i} f = f_{x_i} \oplus f_{x_i'}`.
        """
        raise NotImplementedError()


class Slicer(object):
    def __init__(self, items, start=0):
        self.items = items
        self.start = start

    @property
    def stop(self):
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

    def vrestrict(self, point):
        """Expand all vectors before applying 'restrict'."""
        return self.restrict(_expand_vectors(point))

    def to_uint(self):
        """Convert vector to an unsigned integer, if possible."""
        num = 0
        for i, f in enumerate(self):
            if f in {0, 1}:
                if f:
                    num += 1 << i
            else:
                raise ValueError("cannot convert to uint")
        return num

    def to_int(self):
        """Convert vector to an integer, if possible."""
        num = self.to_uint()
        if self.items[-1]:
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


def _expand_vectors(point):
    """Expand all vectors in a substitution dict."""
    temp = { vf: val for vf, val in point.items() if
             isinstance(vf, VectorFunction) }
    point = {v: val for v, val in point.items() if v not in temp}
    while temp:
        vf, val = temp.popitem()
        if isinstance(vf, VectorFunction):
            assert len(vf) == len(val)
            for i, f in enumerate(val):
                point[vf.getifz(i)] = f
        else:
            point[vf] = val
    return point
