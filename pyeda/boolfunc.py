"""
Boolean Functions

Interface Classes:
    Variable
    Function
    Slicer
    VectorFunction

Boolean Identities
+---------------------------------+--------------+
| (x')' = x                       | Involution   |
+---------------------------------+--------------+
| x + x = x                       | Idempotent   |
| x * x = x                       |              |
+---------------------------------+--------------+
| x + 0 = x                       | Identity     |
| x * 1 = x                       |              |
+---------------------------------+--------------+
| x + 1 = 1                       | Domination   |
| x * 0 = 0                       |              |
+---------------------------------+--------------+
| x + y = y + x                   | Commutative  |
| x * y = y * x                   |              |
+---------------------------------+--------------+
| x + (y + z) = (x + y) + z       | Associative  |
| x * (y * z) = (x * y) * z       |              |
+---------------------------------+--------------+
| x + (y * z) = (x + y) * (x + z) | Distributive |
| x * (y + z) = (x * y) + (x * z) |              |
+---------------------------------+--------------+
| (x + y)' = x' * y'              | De Morgan    |
| (x * y)' = x' + y'              |              |
+---------------------------------+--------------+
| x + (x * y) = x                 | Absorption   |
| x * (x + y) = x                 |              |
+---------------------------------+--------------+
| x + x' = 1                      | Complement   |
| x * x' = 0                      |              |
+---------------------------------+--------------+
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from pyeda.common import iter_space


class Variable(object):
    """
    A Boolean variable is a numerical quantity that may assume any value in the
    set B = {0, 1}.

    This implementation includes an optional "index", a nonnegative integer
    that is convenient for bit vectors.
    """
    def __init__(self, name, *indices):
        self.name = name
        self.indices = indices

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """Return the string representation.

        >>> str(Variable("a"))
        'a'
        >>> str(Variable("v", 42))
        'v[42]'
        >>> str(Variable("v", 1, 2, 3))
        'v[1][2][3]'
        """
        suffix = "".join("[{}]".format(idx) for idx in self.indices)
        return self.name + suffix

    def __lt__(self, other):
        """Return rich "less than" result, for ordering.

        >>> a, b = map(Variable, "ab")
        >>> a < b, b < a
        (True, False)

        >>> c1, c2, c10 = Variable('c', 1), Variable('c', 2), Variable('c', 10)
        >>> c1 < c2, c1 < c10, c2 < c10
        (True, True, True)
        """
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
        """Return the first variable in the ordered support set."""
        return self.inputs[0]

    @property
    def degree(self):
        """Return the degree of a function.

        A function from B^N => B is called a Boolean function of *degree* N.
        """
        return len(self.support)

    def iter_ones(self):
        fst, rst = self.inputs[0], self.inputs[1:]
        for p, cf in self.iter_cofactors(fst):
            if cf == 1:
                for point in iter_space(rst):
                    point[fst] = p[fst]
                    yield point
            elif cf != 0:
                for point in cf.iter_ones():
                    point[fst] = p[fst]
                    yield point

    def iter_zeros(self):
        fst, rst = self.inputs[0], self.inputs[1:]
        for p, cf in self.iter_cofactors(fst):
            if cf == 0:
                for point in iter_space(rst):
                    point[fst] = p[fst]
                    yield point
            elif cf != 1:
                for point in cf.iter_zeros():
                    point[fst] = p[fst]
                    yield point

    def iter_outputs(self):
        for point in iter_space(self.inputs):
            yield point, self.restrict(point)

    # Overloaded operators
    def __neg__(self):
        """Return symbolic complement of a function.

        DIMACS SAT format: -f

        +---+----+
        | f | -f |
        +---+----+
        | 0 |  1 |
        | 1 |  0 |
        +---+----+

        Also known as: NOT
        """
        raise NotImplementedError()

    def __add__(self, other):
        """Return symbolic disjunction of functions.

        DIMACS SAT format: +(f1, f2, ..., fn)

        +---+---+-------+
        | f | g | f + g |
        +---+---+-------+
        | 0 | 0 |   0   |
        | 0 | 1 |   1   |
        | 1 | 0 |   1   |
        | 1 | 1 |   1   |
        +---+---+-------+

        Also known as: sum, OR
        """
        raise NotImplementedError()

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        """Alias: a - b = a + -b"""
        raise NotImplementedError()

    def __rsub__(self, other):
        """Alias: a - b = a + -b"""
        return (- self).__add__(other)

    def __mul__(self, other):
        """Return symbolic conjunction of functions.

        DIMACS SAT format: *(f1, f2, ..., fn)

        +---+---+-------+
        | f | g | f * g |
        +---+---+-------+
        | 0 | 0 |   0   |
        | 0 | 1 |   0   |
        | 1 | 0 |   0   |
        | 1 | 1 |   1   |
        +---+---+-------+

        Also known as: product, AND
        """
        raise NotImplementedError()

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rshift__(self, other):
        """Return symbolic implication of two functions.

        +---+---+--------+
        | f | g | f <= g |
        +---+---+--------+
        | 0 | 0 |    1   |
        | 0 | 1 |    1   |
        | 1 | 0 |    0   |
        | 1 | 1 |    1   |
        +---+---+--------+
        """
        raise NotImplementedError()

    def __rrshift__(self, other):
        """Return symbolic reverse implicaton of two functions.

        +---+---+--------+
        | f | g | f >= g |
        +---+---+--------+
        | 0 | 0 |    1   |
        | 0 | 1 |    0   |
        | 1 | 0 |    1   |
        | 1 | 1 |    1   |
        +---+---+--------+
        """
        raise NotImplementedError()

    # Optional operators
    def xor(self, *args):
        """Return symbolic XOR of functions.

        DIMACS SAT format: xor(f1, f2, ..., fn)

        +---+---+----------+
        | f | g | XOR(f,g) |
        +---+---+----------+
        | 0 | 0 |     0    |
        | 0 | 1 |     1    |
        | 1 | 0 |     1    |
        | 1 | 1 |     0    |
        +---+---+----------+

        Also known as: odd parity
        """
        raise NotImplementedError()

    def equal(self, *args):
        """Return symbolic EQUAL of functions.

        DIMACS SAT format: =(f1, f2, ..., fn)

        +-------+-----------+
        | f g h | EQ(f,g,h) |
        +-------+-----------+
        | 0 0 0 |     1     |
        | 0 0 1 |     0     |
        | 0 1 0 |     0     |
        | 0 1 1 |     0     |
        | 1 0 0 |     0     |
        | 1 0 1 |     0     |
        | 1 1 0 |     0     |
        | 1 1 1 |     1     |
        +-------+-----------+
        """
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
        elif isinstance(vs, Function):
            vs = [vs]
        for point in iter_space(vs):
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
        self.items = list(items)
        self._start = start

    @property
    def sl(self):
        """Return a slice object that represents the vector's index range."""
        return slice(self._start, self._start + self.__len__())

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def getifz(self, i):
        """Get item from zero-based index."""
        return self.__getitem__(i + self.sl.start)

    def __getitem__(self, sl):
        if isinstance(sl, int):
            return self.items[self._norm_idx(sl)]
        else:
            return self.items[self._norm_slice(sl)]

    def __setitem__(self, sl, item):
        if isinstance(sl, int):
            self.items[self._norm_idx(sl)] = item
        else:
            self.items[self._norm_slice(sl)] = item

    def _norm_idx(self, i):
        """Return an index normalized to vector start index."""
        if i >= 0:
            if i < self.sl.start or i >= self.sl.stop:
                raise IndexError("list index out of range")
            else:
                idx = i - self.sl.start
        else:
            raise ValueError("negative indices not supported")
        return idx

    def _norm_slice(self, sl):
        """Return a slice normalized to vector start index."""
        limits = {'start': None, 'stop': None}
        for k in ('start', 'stop'):
            i = getattr(sl, k)
            if i is not None:
                if i >= 0:
                    if i < self.sl.start or i > self.sl.stop:
                        raise IndexError("list index out of range")
                    else:
                        limits[k] = i - self.sl.start
                else:
                    raise ValueError("negative indices not supported")
        return slice(limits['start'], limits['stop'])


class VectorFunction(Slicer):
    """
    Abstract base class that defines an interface for a vector Boolean function.
    """
    UNSIGNED, TWOS_COMPLEMENT = range(2)

    def __init__(self, items, sl=None, bnr=UNSIGNED):
        if sl is None:
            sl = slice(0, len(items))
        elif type(sl) is tuple and len(sl) == 2:
            sl = slice(*sl)
            assert (sl.stop - sl.start) == len(items)
        else:
            raise ValueError("invalid inputs")
        super(VectorFunction, self).__init__(items, sl.start)
        self.bnr = bnr

    def __int__(self):
        return self.to_int()

    # Operators
    def uor(self):
        """Return the unary OR reduction."""
        raise NotImplementedError()

    def uand(self):
        """Return the unary AND reduction."""
        raise NotImplementedError()

    def uxor(self):
        """Return the unary XOR reduction."""
        raise NotImplementedError()

    def __invert__(self):
        raise NotImplementedError()

    def __or__(self, other):
        raise NotImplementedError()

    def __and__(self, other):
        raise NotImplementedError()

    def __xor__(self, other):
        raise NotImplementedError()

    def restrict(self, mapping):
        """
        Return the vector that results from applying the 'restrict' method to
        all functions.
        """
        items = [f.restrict(mapping) for f in self]
        return self.__class__(items, sl=(self.sl.start, self.sl.stop),
                              bnr=self.bnr)

    def vrestrict(self, mapping):
        """Expand all vectors before applying 'restrict'."""
        return self.restrict(_expand_vectors(mapping))

    def to_uint(self):
        """Convert vector to an unsigned integer, if possible."""
        num = 0
        for i, f in enumerate(self):
            if type(f) is int:
                if f:
                    num += 2 ** i
            else:
                raise ValueError("cannot convert to uint")
        return num

    def to_int(self):
        """Convert vector to an integer, if possible."""
        num = self.to_uint()
        if self.bnr == self.TWOS_COMPLEMENT and self.items[-1]:
            return -2 ** self.__len__() + num
        else:
            return num

    def ext(self, num):
        """Extend this vector by N bits.

        If this vector uses two's complement representation, sign extend;
        otherwise, zero extend.
        """
        if self.bnr == self.TWOS_COMPLEMENT:
            bit = self.items[-1]
        else:
            bit = 0
        for _ in range(num):
            self.append(bit)

    def append(self, f):
        """Append a function to the end of this vector."""
        self.items.append(f)


def _expand_vectors(mapping):
    """Expand all vectors in a substitution dict."""
    temp = { k: v for k, v in mapping.items() if
             isinstance(k, VectorFunction) }
    mapping = {k: v for k, v in mapping.items() if k not in temp}
    while temp:
        key, val = temp.popitem()
        if isinstance(key, VectorFunction):
            assert len(key) == len(val)
            for i, f in enumerate(val):
                mapping[key.getifz(i)] = f
        else:
            mapping[key] = val
    return mapping
