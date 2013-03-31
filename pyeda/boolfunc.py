"""
Boolean Functions

Interface Functions:
    iter_points
    iter_terms
    index2term

Interface Classes:
    Variable
    Function
    Slicer
    VectorFunction
"""

from pyeda.common import bit_on


def iter_points(vs):
    """Iterate through all points in an N-dimensional space.

    Parameters
    ----------
    vs : [Variable]
    """
    for n in range(1 << len(vs)):
        yield {v: bit_on(n, i) for i, v in enumerate(vs)}

def iter_terms(vs, cnf=False):
    """Iterate through all terms in an N-dimensional space.

    Parameters
    ----------
    vs: [Variable]
    """
    for n in range(1 << len(vs)):
        yield index2term(n, vs, cnf)

def index2term(index, vs, cnf=False):
    """Return a tuple of all variables for a given term index.

    Parameters
    ----------
    index: int
    vs: [Variable]
    cnf: bool
        cnf=False for minterms, cnf=True for maxterms

    Examples
    --------

    Table of min/max terms for Boolean space {a, b, c}

    +-------+------------+------------+
    | index |   minterm  |   maxterm  |
    +=======+============+============+
    | 0     | a', b', c' | a,  b,  c  |
    | 1     | a,  b', c' | a', b,  c  |
    | 2     | a', b,  c' | a,  b', c  |
    | 3     | a,  b,  c' | a', b', c  |
    | 4     | a', b', c  | a,  b,  c' |
    | 5     | a,  b', c  | a', b,  c' |
    | 6     | a', b,  c  | a,  b', c' |
    | 7     | a,  b,  c  | a', b', c' |
    +-------+------------+------------+
    """
    if cnf:
        return tuple(-v if bit_on(index, i) else v for i, v in enumerate(vs))
    else:
        return tuple(v if bit_on(index, i) else -v for i, v in enumerate(vs))


class Variable(object):
    """
    Abstract base class that defines an interface for a Boolean variable.

    A Boolean variable is a numerical quantity that may assume any value in the
    set B = {0, 1}.

    This implementation includes optional indices, nonnegative integers that
    can be used to construct multi-dimensional bit vectors.
    """
    def __new__(cls, name, indices=None, namespace=None):
        self = super(Variable, cls).__new__(cls)
        self.name = name
        if indices is None:
            self.indices = tuple()
        elif type(indices) is int:
            self.indices = (indices, )
        elif type(indices) is tuple:
            self.indices = indices
        else:
            raise ValueError("invalid indices")
        if namespace is None or type(namespace) is str:
            self.namespace = namespace
        else:
            raise ValueError("invalid namespace")
        self.qualname = name if namespace is None else namespace + "." + name
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


class Function(object):
    """
    Abstract base class that defines an interface for a scalar Boolean function
    of N variables.
    """
    @property
    def support(self):
        """Return the support set of a function.

        Let f(x1, x2, ..., xn) be a Boolean function of N variables. The set
        {x1, x2, ..., xn} is called the *support* of the function.
        """
        raise NotImplementedError()

    @property
    def inputs(self):
        """Return the support set in name/index order."""
        raise NotImplementedError()

    @property
    def top(self):
        """Return the last variable in the ordered support set."""
        return self.inputs[-1]

    @property
    def degree(self):
        """Return the degree of a function.

        A function from B^N => B is called a Boolean function of *degree* N.
        """
        return len(self.support)

    def iter_ones(self):
        """Iterate through all points this function maps to output one."""
        rest, top = self.inputs[:-1], self.inputs[-1]
        for p, cf in self.iter_cofactors(top):
            if cf == 1:
                for point in iter_points(rest):
                    point[top] = p[top]
                    yield point
            elif cf != 0:
                for point in cf.iter_ones():
                    point[top] = p[top]
                    yield point

    def iter_zeros(self):
        """Iterate through all points this function maps to output zero."""
        rest, top = self.inputs[:-1], self.inputs[-1]
        for p, cf in self.iter_cofactors(top):
            if cf == 0:
                for point in iter_points(rest):
                    point[top] = p[top]
                    yield point
            elif cf != 1:
                for point in cf.iter_zeros():
                    point[top] = p[top]
                    yield point

    def iter_outputs(self):
        """Iterate through all (point, output) pairs."""
        for point in iter_points(self.inputs):
            yield point, self.restrict(point)

    def reduce(self):
        """Return the function reduced to a canonical form."""
        raise NotImplementedError()

    def restrict(self, mapping):
        """
        Return the Boolean function that results after restricting a subset of
        its input variables to {0, 1}.

        g = f | xi=b
        """
        raise NotImplementedError()

    def vrestrict(self, mapping):
        """Expand all vectors before applying 'restrict'."""
        return self.restrict(_expand_vectors(mapping))

    def compose(self, mapping):
        """
        Return the Boolean function that results after substituting a subset of
        its input variables for other Boolean functions.

        g = f1 | xi=f2
        """
        raise NotImplementedError()

    def satisfy_one(self):
        """
        If this function is satisfiable, return a satisfying input point. A
        tautology *may* return an empty dictionary; a contradiction *must*
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
        """Iterate through the cofactors of N variables."""
        if vs is None:
            vs = list()
        elif isinstance(vs, Variable):
            vs = [vs]
        for point in iter_points(vs):
            yield point, self.restrict(point)

    def cofactors(self, vs=None):
        """Return a tuple of cofactors of N variables.

        The *cofactor* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi is f[xi] = f(x1, x2, ..., 1, ..., xn)

        The *cofactor* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi' is f[xi'] = f(x1, x2, ..., 0, ..., xn)
        """
        return tuple(cf for p, cf in self.iter_cofactors(vs))

    def is_neg_unate(self, vs=None):
        """Return whether a function is negative unate.

        A function f(x1, x2, ..., xi, ..., xn) is negative unate in variable
        xi if f[xi'] >= f[xi].
        """
        raise NotImplementedError()

    def is_pos_unate(self, vs=None):
        """Return whether a function is positive unate.

        A function f(x1, x2, ..., xi, ..., xn) is positive unate in variable
        xi if f[xi] >= f[xi'].
        """
        raise NotImplementedError()

    def is_binate(self, vs=None):
        """Return whether a function is binate.

        A function f(x1, x2, ..., xi, ..., xn) is binate in variable xi if it
        is neither negative nor positive unate in xi.
        """
        return not (self.is_neg_unate(vs) or self.is_pos_unate(vs))

    def smoothing(self, vs=None):
        """Return the smoothing of a function.

        The *smoothing* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi is S[xi](f) = f[xi] + f[xi']
        """
        raise NotImplementedError()

    def consensus(self, vs=None):
        """Return the consensus of a function.

        The *consensus* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi is C[xi](f) = f[xi] * f[xi']
        """
        raise NotImplementedError()

    def derivative(self, vs=None):
        """Return the derivative of a function.

        The *derivate* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi is df/dxi = f[xi] (xor) f[xi']
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
    def restrict(self, mapping):
        """
        Return the vector that results from applying the 'restrict' method to
        all functions.
        """
        items = [f.restrict(mapping) for f in self]
        return self.__class__(items, self.start)

    def vrestrict(self, mapping):
        """Expand all vectors before applying 'restrict'."""
        return self.restrict(_expand_vectors(mapping))

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


def _expand_vectors(mapping):
    """Expand all vectors in a substitution dict."""
    temp = { vf: val for vf, val in mapping.items() if
             isinstance(vf, VectorFunction) }
    mapping = {v: val for v, val in mapping.items() if v not in temp}
    while temp:
        key, val = temp.popitem()
        if isinstance(key, VectorFunction):
            assert len(key) == len(val)
            for i, f in enumerate(val):
                mapping[key.getifz(i)] = f
        else:
            mapping[key] = val
    return mapping
