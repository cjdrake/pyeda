"""
Boolean Algebra

Interface Functions:
    clog2

    cube_sop
    cube_pos
    iter_space
    iter_points

    vec
    svec
    zeros

    uint2vec
    int2vec
    expand_vecs

Classes:
    Boolean
        Number: {Zero, One}
        Expression
            Literal
                Variable
                Complement
            OrAnd
                Or
                And
        Buf, Not
        Nor, Nand,
        Xor, Xnor,
        Implies

    Vector

Huntington's Postulates
+---------------------------------+--------------+
| x + y = y + x                   | Commutative  |
| x * y = y * x                   | Commutative  |
+---------------------------------+--------------+
| x + (y * c) = (x + y) * (x + c) | Distributive |
| x * (y + c) = (x * y) + (x * c) | Distributive |
+---------------------------------+--------------+
| x + x' = 1                      | Complement   |
| x * x' = 0                      | Complement   |
+---------------------------------+--------------+

Properties of Boolean Algebraic Systems
+---------------------------+---------------+
| x + (y + c) = (x + y) + c | Associativity |
| x * (y * c) = (x * y) * c | Associativity |
+---------------------------+---------------+
| x + x = x                 | Idempotence   |
| x * x = x                 | Idempotence   |
+---------------------------+---------------+
| x + (x * y) = x           | Absorption    |
| x * (x + y) = x           | Absorption    |
+---------------------------+---------------+
| (x + y)' = x' * y'        | De Morgan     |
| (x * y)' = x' + y'        | De Morgan     |
+---------------------------+---------------+
| (x')' = x                 | Involution    |
+---------------------------+---------------+
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved"

#==============================================================================
# Constants
#==============================================================================

UNSIGNED, TWOS_COMPLEMENT = range(2)

#==============================================================================
# Interface Functions
#==============================================================================

def clog2(num):
    """Return the ceiling, log base two of an integer."""
    assert num >= 1
    i, x = 0, 1
    while x < num:
        x = x << 1;
        i += 1
    return i

def cube_sop(*vs):
    """
    Return the multi-dimensional space spanned by N Boolean variables as a
    sum of products.
    """
    points = [p for p in iter_points(And, *vs)]
    return Or(*points)

def cube_pos(*vs):
    """
    Return the multi-dimensional space spanned by N Boolean variables as a
    product of sums.
    """
    points = [p for p in iter_points(Or, *vs)]
    return And(*points)

def iter_space(*vs):
    """Return the multi-dimensional space spanned by N Boolean variables."""
    for i in range(2**len(vs)):
        yield [(v if _bit_on(i, j) else -v) for j, v in enumerate(vs)]

def iter_points(op, *vs):
    """
    Iterate through all OR/AND points in the multi-dimensional space spanned
    by N Boolean variables.
    """
    assert issubclass(op, OrAnd)
    for s in iter_space(*vs):
        yield op(*s)

def vec(name, *args, **kwargs):
    """Return a vector of variables."""
    if len(args) == 0:
        raise TypeError("vec expected at least two argument")
    elif len(args) == 1:
        start, stop = 0, args[0]
    elif len(args) == 2:
        start, stop = args
    else:
        raise TypeError("vec expected at most three arguments")
    fs = [Variable("{}[{}]".format(name, i)) for i in range(start, stop)]
    return Vector(*fs, offset=start, **kwargs)

def svec(name, *args, **kwargs):
    """Return a signed vector of variables."""
    return vec(name, *args, format=TWOS_COMPLEMENT, **kwargs)

def zeros(width):
    """Return a vector of zeros."""
    z = Vector()
    for i in range(width):
        z.append(Zero)
    return z

def uint2vec(num, width=None):
    """Convert an unsigned integer to a Vector."""
    assert num >= 0

    vv = Vector()
    if num == 0:
        vv.append(Zero)
    else:
        while num != 0:
            vv.append(Buf(num & 1))
            num >>= 1

    if width:
        if width < len(vv):
            raise ValueError("overflow: " + str(num))
        else:
            vv.zext(width - len(vv))

    return vv

def int2vec(num, width=None):
    """Convert a signed integer to a Vector."""
    if num < 0:
        req_width = clog2(abs(num)) + 1
        vv = uint2vec(2**req_width + num)
    else:
        req_width = clog2(num + 1) + 1
        vv = uint2vec(num)
        vv.zext(req_width - len(vv))
    vv.format = TWOS_COMPLEMENT

    if width:
        if width < req_width:
            raise ValueError("overflow: " + str(num))
        else:
            vv.sext(width - req_width)

    return vv

def expand_vecs(d):
    """Expand all vectors in a substitution dict."""
    temp = {k: v for k, v in d.items() if isinstance(k, Vector)}
    d = {k: v for k, v in d.items() if k not in temp}
    while temp:
        key, val = temp.popitem()
        if isinstance(key, Vector):
            assert len(key) == len(val)
            for i, x in enumerate(val):
                d[key[i + key.offset]] = Buf(x)
        elif isinstance(key, Literal):
            d[key] = val
    return d

#==============================================================================
# Classes
#==============================================================================

class Boolean(object):
    """Base class for boolean objects"""

    def __hash__(self):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        return self.__str__()

    def __neg__(self):
        return Not(self)

    def __add__(self, other):
        return Or(self, other)

    def __mul__(self, other):
        return And(self, other)

    def __lshift__(self, other):
        return Implies(other, self)

    def __rshift__(self, other):
        return Implies(self, other)

    def _cmp_str(self):
        """Return a string for canonical ordering comparisons."""
        return self.__str__()


class Number(Boolean):
    """Boolean number"""

    def __init__(self, val):
        self._val = val

    def __hash__(self):
        return self._val

    def __str__(self):
        return ("1" if self._val else "0")

    def __eq__(self, other):
        if isinstance(other, bool) or isinstance(other, int):
            return self._val == other
        elif isinstance(other, Number):
            return self._val == other.val
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, bool) or isinstance(other, int):
            return self._val < other
        elif isinstance(other, Number):
            return self._val < other.val
        elif isinstance(other, Expression):
            return True
        else:
            return id(self) < id(other)

    def __nonzero__(self):
        return self._val

    @property
    def val(self):
        return self._val


Zero = Number(False)
One = Number(True)


class Expression(Boolean):
    """Boolean symbol"""

    def __init__(self):
        self.cache = dict()

    @property
    def support(self):
        """Return the support of a function.

        Let f(x1, x2, ..., xn) be a Boolean function of N variables. The set
        {x1, x2, ..., xn} is called the *support* of the function.
        """
        s = self.cache.get("support", None)
        if s is None:
            s = {v for v in self.iter_vars()}
            self.cache["support"] = s
        return s

    @property
    def minterms(self):
        """The sum of products of N literals"""
        return {x for x in self.iter_minterms()}

    @property
    def maxterms(self):
        """The product of sums of N literals"""
        return {x for x in self.iter_maxterms()}

    @property
    def depth(self):
        """The number of levels in the expression tree."""
        raise NotImplementedError()

    def iter_vars(self, visit=None):
        """Recursively iterate through all variables in the expression."""
        raise NotImplementedError()

    def iter_minterms(self):
        """Iterate through the sum of products of N literals."""
        raise NotImplementedError()

    def iter_maxterms(self):
        """Iterate through the product of sums of N literals."""
        raise NotImplementedError()

    def copy(self):
        """
        Construct a new expression that contains references to the objects
        found in the original.
        """
        raise NotImplementedError()

    def deepcopy(self):
        """
        Recursively construct a new expression that contains copies of the
        objects found in the original.
        """
        raise NotImplementedError()

    def subs(self, d):
        """Substitute numbers into a boolean expression."""
        raise NotImplementedError()

    def to_pos(self):
        """Return the expression as a product of sums."""
        return self._flatten(Or)

    def to_sop(self):
        """Return the expression as a sum of products."""
        return self._flatten(And)

    def to_cpos(self):
        """Return the expression as a product of sums of N literals."""
        return self._canonize(Or)

    def to_csop(self):
        """Return the expression as a sum of products of N literals."""
        return self._canonize(And)

    def iter_cofactors(self, *vs):
        """Iterate through the cofactors of N variables."""
        for i in range(2**len(vs)):
            yield self.subs({v: _bit_on(i, j) for j, v in enumerate(vs)})

    def cofactors(self, *vs):
        """Return a list of cofactors of N variables.

        The *cofactor* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi is f[xi] = f(x1, x2, ..., 1, ..., xn)

        The *cofactor* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi' is f[xi'] = f(x1, x2, ..., 0, ..., xn)
        """
        return [cf for cf in self.iter_cofactors(*vs)]

    def is_neg_unate(self, *vs):
        """Return whether a function is negative unate.

        A function f(x1, x2, ..., xi, ..., xn) is negative unate in variable
        xi if f[xi'] >= f[xi].
        """
        vs = vs or self.support
        for v in vs:
            fv0, fv1 = self.cofactors(v)
            if isinstance(fv0, Number) or isinstance(fv1, Number):
                if not (fv0 is One or fv1 is Zero):
                    return False
            elif not (fv0.minterms >= fv1.minterms):
                return False
        return True

    def is_pos_unate(self, *vs):
        """Return whether a function is positive unate.

        A function f(x1, x2, ..., xi, ..., xn) is positive unate in variable
        xi if f[xi] >= f[xi'].
        """
        vs = vs or self.support
        for v in vs:
            fv0, fv1 = self.cofactors(v)
            if isinstance(fv0, Number) or isinstance(fv1, Number):
                if not (fv1 is One or fv0 is Zero):
                    return False
            elif not (fv1.minterms >= fv0.minterms):
                return False
        return True

    def is_binate(self, *vs):
        """Return whether a function is binate.

        A function f(x1, x2, ..., xi, ..., xn) is binate in variable xi if it
        is neither negative nor positive unate in xi.
        """
        vs = vs or self.support
        return not (self.is_neg_unate(*vs) or self.is_pos_unate(*vs))

    def smoothing(self, *vs):
        """Return the smoothing of a function.

        The *smoothing* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi is S[xi](f) = f[xi] + f[xi']
        """
        return Or(*self.cofactors(*vs))

    def consensus(self, *vs):
        """Return the consensus of a function.

        The *consensus* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi is C[xi](f) = f[xi] * f[xi']
        """
        return And(*self.cofactors(*vs))

    def derivative(self, *vs):
        """Return the derivative of a function.

        The *derivate* of f(x1, x2, ..., xi, ..., xn) with respect to
        variable xi is df/dxi = f[xi] (xor) f[xi']
        """
        cfs = self.cofactors(*vs)
        return (Xor(*cfs) if cfs else self)

    def difference(self, *vs):
        """Alias for derivative"""
        return self.derivative(*vs)

    def _flatten(self, op):
        """Return expression after flattening OR/AND."""
        raise NotImplementedError()

    def _canonize(self, op):
        """Return an expression with all terms expanded to length N."""
        raise NotImplementedError()

    def _clear_cache(self):
        self.cache.clear()


class Literal(Expression):
    """An instance of a variable or of its complement"""

    def __init__(self):
        super(Literal, self).__init__()
        self.xs = {self}

    def __hash__(self):
        h = self.cache.get("hash", None)
        if h is None:
            h = hash(self.__str__())
            self.cache["hash"] = h
        return h

    def __len__(self):
        return 1

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    @property
    def depth(self):
        return 1

    def iter_minterms(self): yield self
    def iter_maxterms(self): yield self

    def copy(self): return self
    def deepcopy(self): return self

    def _flatten(self, op): return self
    def _canonize(self, op): return self


class Variable(Literal):
    """boolean variable"""

    def __init__(self, name):
        self._name = name
        super(Variable, self).__init__()

    def __str__(self):
        return self._name

    def __lt__(self, other):
        if isinstance(other, Number):
            return False
        elif isinstance(other, Literal):
            return self._name < other.name
        elif isinstance(other, OrAnd):
            return True
        else:
            return id(self) < id(other)

    @property
    def name(self):
        return self._name

    def iter_vars(self, visit=None):
        yield self

    def subs(self, d):
        if self in d:
            return Buf(d[self])
        else:
            return self

    def _cmp_str(self):
        return self._name + "1"


class Complement(Literal):
    """boolean complement"""

    # Postfix symbol used in string representation
    OP = "'"

    def __init__(self, var):
        self._var = var
        super(Complement, self).__init__()

    def __str__(self):
        return self._var.name + self.OP

    def __lt__(self, other):
        if isinstance(other, Number):
            return False
        elif isinstance(other, Variable):
            return self._var.name <= other.name
        elif isinstance(other, Complement):
            return self._var.name < other.name
        elif isinstance(other, OrAnd):
            return True
        else:
            return id(self) < id(other)

    @property
    def name(self):
        return self._var.name

    @property
    def var(self):
        return self._var

    def iter_vars(self, visit=None):
        yield self._var

    def subs(self, d):
        if self._var in d:
            return Not(d[self._var])
        else:
            return self

    def _cmp_str(self):
        return self._var.name + "0"


class OrAnd(Expression):
    """base class for boolean OR, AND expressions"""

    def __new__(cls, *xs):
        xs = cls._reduce(set(xs))
        if len(xs) == 1:
            return xs.pop()
        else:
            self = super(OrAnd, cls).__new__(cls)
            self.xs = xs
            return self

    def __init__(self, *xs):
        super(OrAnd, self).__init__()

    def __hash__(self):
        h = self.cache.get("hash", None)
        if h is None:
            h = sum(x.__hash__() for x in self.xs)
            self.cache["hash"] = h
        return h

    def __len__(self):
        return len(self.xs)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.xs == other.xs

    def __lt__(self, other):
        if isinstance(other, Number):
            return False
        if isinstance(other, Literal):
            return False
        elif isinstance(other, OrAnd):
            return self._cmp_str() < other._cmp_str()
        else:
            return id(self) < id(other)

    @property
    def duals(self):
        ds = self.cache.get("duals", None)
        if ds is None:
            ds = {x for x in self.xs if isinstance(x, self.get_dual())}
            self.cache["duals"] = ds
        return ds

    @property
    def depth(self):
        d = self.cache.get("depth", None)
        if d is None:
            d = max((x.depth + 1 if isinstance(x, OrAnd) else x.depth)
                    for x in self.xs)
            self.cache["depth"] = d
        return d

    @staticmethod
    def get_dual():
        """The dual of OR is AND, and the dual of AND is OR."""
        raise NotImplementedError()

    def iter_vars(self, visit=None):
        if visit is None:
            visit = set()
        for x in self.xs:
            for v in x.iter_vars(visit):
                if v not in visit:
                    yield v
                visit.add(v)

    def copy(self):
        return self.__class__(*[x for x in self.xs])

    def deepcopy(self):
        return self.__class__(*[x.deepcopy() for x in self.xs])

    def subs(self, d):
        """Return expression with literal substitutions."""
        replace = []
        for x in self.xs:
            _x = x.subs(d)
            if id(x) != id(_x):
                replace.append((x, _x))
        if replace:
            f = self.copy()
            for old, new in replace:
                f.xs.remove(old)
                f.xs.add(new)
            f.xs = f._reduce(f.xs)
            if len(f.xs) == 1:
                return f.xs.pop()
            else:
                f._clear_cache()
                return f
        else:
            return self

    def iter_minterms(self):
        for term in self._iter_terms(And):
            yield term

    def iter_maxterms(self):
        for term in self._iter_terms(Or):
            yield term

    def _iter_terms(self, op):
        """Iterate through either minterms or maxterms."""
        f = self._canonize(op)
        if f.depth == 1:
            yield f
        else:
            for x in f.xs:
                yield x

    @classmethod
    def _reduce_assoc(cls, xs):
        # x + (y + z) = x + y + z; x * (y * z) = x * y * z
        temps = {x for x in xs if isinstance(x, cls)}
        xs -= temps
        while temps:
            t = temps.pop()
            if isinstance(t, cls):
                temps |= t.xs
            else:
                xs.add(t)
        return xs

    @classmethod
    def _reduce_nums(cls, xs):
        # x + 1 = 1; x * 0 = 0
        if -cls.IDENTITY in xs:
            xs = {-cls.IDENTITY}
        # x + 0 = x; x * 1 = x
        if len(xs) > 1:
            xs.discard(cls.IDENTITY)
        return xs

    @classmethod
    def _reduce_comps(cls, xs):
        # x + x' = 1; x * x' = 0
        vs = {x for x in xs if isinstance(x, Variable)}
        cvs = {x.var for x in xs if isinstance(x, Complement)}
        if vs & cvs:
            xs = {-cls.IDENTITY}
        return xs

    @staticmethod
    def _reduce_absorb(xs):
        # x + (x * y) = x; x * (x + y) = x
        xs -= {xj for xi in xs for xj in xs if xi != xj and xi.xs <= xj.xs}
        return xs

    @classmethod
    def _reduce(cls, xs):
        xs = cls._reduce_assoc(xs)
        xs = cls._reduce_nums(xs)
        xs = cls._reduce_comps(xs)
        xs = cls._reduce_absorb(xs)
        return xs

    def _flatten(self, op):
        dual_op = op.get_dual()
        if isinstance(self, op):
            if self.duals:
                dual = list(self.duals)[0]
                others = list(self.xs - {dual})
                xs = [op(x, *others) for x in dual.xs]
                f = dual_op(*xs)
                return f._flatten(op) if isinstance(f, OrAnd) else f
            else:
                return self
        else:
            nested = {x for x in self.duals if x.depth > 1}
            others = list(self.xs - nested)
            xs = [x._flatten(op) for x in nested] + others
            return dual_op(*xs)

    def _canonize(self, op):
        f = self._flatten(op)
        if isinstance(f, op):
            return f
        else:
            support_len = len(self.support)
            temps = {x for x in f.xs if len(x) < support_len}
            f.xs -= temps
            flush = bool(temps)
            while temps:
                t = temps.pop()
                vs = self.support - t.support
                if vs:
                    v, tc = vs.pop(), t.copy()
                    temps |= {op(-v, t), op(v, tc)}
                else:
                    f.xs.add(t)
            if flush:
                f._clear_cache()
        return f


class Or(OrAnd):
    """boolean addition (or) operator"""

    # Infix symbol used in string representation
    OP = "+"

    IDENTITY = Zero

    def __str__(self):
        sep = " " + self.OP + " "
        return sep.join(str(x) for x in sorted(self.xs))

    @staticmethod
    def get_dual():
        return And

    def _cmp_str(self):
        return "0".join(x._cmp_str() for x in sorted(self.xs))


class And(OrAnd):
    """boolean multiplication (and) operator"""

    # Infix symbol used in string representation
    OP = "*"

    IDENTITY = One

    def __str__(self):
        s = []
        for x in sorted(self.xs):
            if isinstance(x, Or):
                s.append("(" + str(x) + ")")
            else:
                s.append(str(x))
        sep = " " + self.OP + " "
        return sep.join(s)

    @staticmethod
    def get_dual():
        return Or

    def _cmp_str(self):
        return "1".join(x._cmp_str() for x in sorted(self.xs))


class Buf(Boolean):
    """buffer operator"""

    def __new__(cls, x):
        if isinstance(x, Boolean):
            return x
        else:
            return One if int(x) else Zero


class Not(Boolean):
    """boolean NOT operator"""

    def __new__(cls, x):
        # 0' = 1; 1' = 0
        if isinstance(x, Number):
            return Zero if x else One
        # x'
        elif isinstance(x, Variable):
            return Complement(x)
        # (x')' = x
        elif isinstance(x, Complement):
            return x.var
        # (x + y)' = x' * y'; (x * y)' = x' + y'
        elif isinstance(x, OrAnd):
            return x.get_dual()(*[Not(x) for x in x.xs])
        else:
            return Zero if int(x) else One


class Nor(Boolean):
    """boolean NOR (not or) operator"""
    def __new__(cls, *xs):
        return Not(Or(*xs))

class Nand(Boolean):
    """boolean NAND (not and) operator"""
    def __new__(cls, *xs):
        return Not(And(*xs))

class Xor(Boolean):
    """boolean XOR (exclusive or) operator"""
    def __new__(cls, x, *xs):
        if xs:
            return Or(And(Not(x), Xor(*xs)), And(x, Xnor(*xs)))
        else:
            return x

class Xnor(Boolean):
    """boolean XNOR (exclusive nor) operator"""
    def __new__(cls, *xs):
        return Not(Xor(*xs))

class Implies(Boolean):
    """boolean implication operator"""
    def __new__(cls, x0, x1):
        return Or(Not(x0), x1)


class Vector(object):
    """Boolean vector"""

    def __init__(self, *fs, **kwargs):
        self.fs = [Buf(f) for f in fs]
        self._offset = kwargs.get("offset", 0)
        self._format = kwargs.get("format", UNSIGNED)

    def __len__(self):
        return len(self.fs)

    def __int__(self):
        return self.to_int()

    def __str__(self):
        return str(self.fs)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.fs)

    def __invert__(self):
        fs = [Not(v) for v in self.fs]
        return Vector(*fs, offset=self._offset, format=self._format)

    def __or__(self, other):
        assert isinstance(other, Vector) and len(self.fs) == len(other.fs)
        fs = [Or(f, other[i + other.offset]) for i, f in enumerate(self.fs)]
        return Vector(*fs, offset=self._offset, format=self._format)

    def __and__(self, other):
        assert isinstance(other, Vector) and len(self.fs) == len(other.fs)
        fs = [And(f, other[i + other.offset]) for i, f in enumerate(self.fs)]
        return Vector(*fs, offset=self._offset, format=self._format)

    def __xor__(self, other):
        assert isinstance(other, Vector) and len(self.fs) == len(other.fs)
        fs = [Xor(f, other[i + other.offset]) for i, f in enumerate(self.fs)]
        return Vector(*fs, offset=self._offset, format=self._format)

    def __getitem__(self, sl):
        if isinstance(sl, int):
            return self.fs[self._norm_idx(sl)]
        else:
            norm = self._norm_slice(sl)
            return Vector(*self.fs.__getitem__(norm),
                          offset=(norm.start + self._offset),
                          format=self._format)

    def __setitem__(self, sl, f):
        if isinstance(sl, int):
            self.fs.__setitem__(sl, f)
        else:
            norm = self._norm_slice(sl)
            self.fs.__setitem__(norm, f)

    @property
    def offset(self):
        return self._offset

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        self._format = value

    @property
    def sl(self):
        return slice(self._offset, len(self.fs) + self._offset)

    def to_uint(self):
        """Convert vector into an unsigned integer."""
        num = 0
        for i, f in enumerate(self.fs):
            if isinstance(f, Number):
                if f is One:
                    num += 2 ** i
            else:
                raise ValueError("cannot convert to uint")
        return num

    def to_int(self):
        """Convert vector into an integer."""
        num = self.to_uint()
        if self._format == TWOS_COMPLEMENT and self.fs[-1]:
            return -2 ** (self.__len__()) + num
        else:
            return num

    def subs(self, d):
        """Substitute numbers into a boolean vector."""
        cpy = self[:]
        for i, f in enumerate(cpy.fs):
            cpy[i] = cpy[i].subs(d)
        return cpy

    def ripple_carry_add(self, b, ci=Zero):
        assert isinstance(b, Vector) and len(self.fs) == len(b.fs)
        fmt = UNSIGNED
        if self._format == TWOS_COMPLEMENT or b.format == TWOS_COMPLEMENT:
            fmt = TWOS_COMPLEMENT
        s = Vector(format=fmt)
        c = Vector()
        for i, a in enumerate(self.fs):
            carry = (ci if i == 0 else c[i-1])
            s.append(Xor(a, b[i + b.offset], carry))
            c.append(a * b[i + b.offset] + a * carry + b[i + b.offset] * carry)
        return s, c

    def append(self, f):
        """Append logic function to the end of this vector."""
        self.fs.append(f)

    def sext(self, n):
        """Sign extend this vector by n bits."""
        sign = self.fs[-1]
        for i in range(n):
            self.append(sign)

    def zext(self, n):
        """Zero extend this vector by n bits."""
        for i in range(n):
            self.append(Zero)

    def _norm_idx(self, i):
        """Return an index normalized to vector offset."""
        if i >= 0:
            if i < self._offset:
                raise IndexError("list index out of range")
            else:
                idx = i - self._offset
        else:
            idx = i + self._offset
        return idx

    def _norm_slice(self, sl):
        """Return a slice normalized to vector offset."""
        d = dict()
        for k in ("start", "stop"):
            idx = getattr(sl, k)
            if idx is not None:
                d[k] = (idx if idx >= 0 else self.sl.stop + idx)
            else:
                d[k] = getattr(self.sl, k)
        if d["start"] < self.sl.start or d["stop"] > self.sl.stop:
            raise IndexError("list index out of range")
        elif d["start"] >= d["stop"]:
            raise IndexError("zero-sized slice")
        return slice(d["start"] - self._offset, d["stop"] - self._offset)


#==============================================================================
# Internal Functions
#==============================================================================

def _bit_on(num, bit):
    return bool((num >> bit) & 1)


