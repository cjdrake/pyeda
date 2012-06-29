"""
Boolean Algebra

Interface Functions:
    tobool

    factor
    simplify

    cube_sop
    cube_pos
    iter_space
    iter_points

    vec
    svec

    zeros

    uint2vec
    int2vec

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
            BufNot
                Buf
                Not
            Xor
            Implies

    Nor, Nand, Xnor
    NotF, OrF, NorF, AndF, NandF, XorF, XnorF, ImpliesF

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

import multiprocessing

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved"

#==============================================================================
# Constants
#==============================================================================

UNSIGNED, TWOS_COMPLEMENT = range(2)

COMPLEMENTS = dict()

#==============================================================================
# Interface Functions
#==============================================================================

def tobool(x):
    """Return a Boolean data type."""
    if isinstance(x, Boolean):
        return x
    else:
        num = int(x)
        if num == 0:
            return Zero
        elif num == 1:
            return One
        else:
            raise ValueError("invalid input for tobool()")

def factor(expr):
    """Return a factored expression."""
    return expr.factor()

def simplify(expr):
    """Return a simplified expression."""
    return expr.simplify()

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
    for num in range(2 ** len(vs)):
        yield [(v if _bit_on(num, i) else -v) for i, v in enumerate(vs)]

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
        raise TypeError("vec() expected at least two argument")
    elif len(args) == 1:
        start, stop = 0, args[0]
    elif len(args) == 2:
        start, stop = args
    else:
        raise TypeError("vec() expected at most three arguments")
    fs = [Variable(name, index=i) for i in range(start, stop)]
    return Vector(*fs, start=start, **kwargs)

def svec(name, *args, **kwargs):
    """Return a signed vector of variables."""
    return vec(name, *args, bnr=TWOS_COMPLEMENT, **kwargs)

def zeros(length):
    """Return a vector of zeros."""
    z = Vector()
    for i in range(length):
        z.append(Zero)
    return z

def uint2vec(num, length=None):
    """Convert an unsigned integer to a Vector."""
    assert num >= 0

    vv = Vector()
    if num == 0:
        vv.append(Zero)
    else:
        while num != 0:
            vv.append(tobool(num & 1))
            num >>= 1

    if length:
        if length < len(vv):
            raise ValueError("overflow: " + str(num))
        else:
            vv.ext(length - len(vv))

    return vv

def int2vec(num, length=None):
    """Convert a signed integer to a Vector."""
    if num < 0:
        req_length = _clog2(abs(num)) + 1
        vv = uint2vec(2 ** req_length + num)
    else:
        req_length = _clog2(num + 1) + 1
        vv = uint2vec(num)
        vv.ext(req_length - len(vv))
    vv.bnr = TWOS_COMPLEMENT

    if length:
        if length < req_length:
            raise ValueError("overflow: " + str(num))
        else:
            vv.ext(length - req_length)

    return vv

#==============================================================================
# Classes
#==============================================================================

class Boolean(object):
    """Base class for Boolean objects"""

    def __init__(self):
        pass

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

    @property
    def depth(self):
        """The number of levels in the expression tree."""
        expr = self.factor()
        return expr._depth

    def copy(self):
        """
        Construct a new expression that contains references to the objects
        found in the original.
        """
        raise NotImplementedError()

    def subs(self, d):
        """Substitute numbers into a Boolean expression."""
        raise NotImplementedError()

    def vsubs(self, d):
        """Expand all vectors before doing a substitution."""
        return self.subs(_expand_vectors(d))

    def factor(self):
        """Return a factored expression.

        A factored expression is one and only one of the following:
        * A literal.
        * A sum / product of factored expressions.
        """
        expr = self._factor()
        return expr

    def simplify(self):
        """Return a simplifed expression."""
        expr = self._simplify()
        return expr


class Number(Boolean):
    """Boolean number"""

    def __init__(self, val):
        super(Number, self).__init__()
        self._val = val

    def __hash__(self):
        return self._val

    def __str__(self):
        return str(self._val)

    def __eq__(self, other):
        other = tobool(other)
        return isinstance(other, Number) and self._val == other.val

    def __lt__(self, other):
        if isinstance(other, Number):
            return self.val < other.val
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def __nonzero__(self):
        return self._val

    @property
    def _depth(self):
        return 0

    @property
    def val(self):
        return self._val

    def get_dual(self):
        return Zero if self._val else One

    def copy(self): return self
    def subs(self, d): return self

    def _factor(self): return self
    def _simplify(self): return self


Zero = Number(0)
One = Number(1)


class Expression(Boolean):
    """Boolean expression"""

    def __init__(self):
        super(Expression, self).__init__()
        self.cache = dict()

    def __hash__(self):
        val = self.cache.get("hash", None)
        if val is None:
            val = sum(x.__hash__() for x in self.xs)
            self.cache["hash"] = val
        return val

    @property
    def support(self):
        """Return the support of a function.

        Let f(x1, x2, ..., xn) be a Boolean function of N variables. The set
        {x1, x2, ..., xn} is called the *support* of the function.
        """
        val = self.cache.get("support", None)
        if val is None:
            val = {v for v in self.iter_vars()}
            self.cache["support"] = val
        return val

    @property
    def minterms(self):
        """The sum of products of N literals"""
        val = self.cache.get("minterms", None)
        if val is None:
            val = {x for x in self.iter_minterms()}
            self.cache["minterms"] = val
        return val

    @property
    def maxterms(self):
        """The product of sums of N literals"""
        val = self.cache.get("maxterms", None)
        if val is None:
            val = {x for x in self.iter_maxterms()}
            self.cache["maxterms"] = val
        return val

    def iter_vars(self):
        """Recursively iterate through all variables in the expression."""
        raise NotImplementedError()

    def iter_minterms(self):
        """Iterate through the sum of products of N literals."""
        for term in self.to_csop():
            yield term

    def iter_maxterms(self):
        """Iterate through the product of sums of N literals."""
        for term in self.to_cpos():
            yield term

    def to_pos(self):
        """Return the expression as a product of sums."""
        expr = self.factor()
        expr = expr.flatten(Or)
        return expr

    def to_sop(self):
        """Return the expression as a sum of products."""
        expr = self.factor()
        expr = expr.flatten(And)
        return expr

    def to_cpos(self):
        """Return the expression as a product of sums of N literals."""
        return self.to_pos().canonize(Or)

    def to_csop(self):
        """Return the expression as a sum of products of N literals."""
        return self.to_sop().canonize(And)

    def iter_cofactors(self, *vs):
        """Iterate through the cofactors of N variables."""
        for num in range(2 ** len(vs)):
            yield self.subs({v: _bit_on(num, i) for i, v in enumerate(vs)})

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

    def flatten(self, op):
        """Return expression after flattening OR/AND."""
        expr = self._flatten(op)
        expr = expr.simplify()
        return expr

    def canonize(self, op):
        """Return an expression with all terms expanded to length N."""
        expr = self._canonize(op)
        return expr


class Literal(Expression):
    """An instance of a variable or of its complement"""

    def __init__(self):
        super(Literal, self).__init__()

    def __hash__(self):
        val = self.cache.get("hash", None)
        if val is None:
            val = hash(self.__str__())
            self.cache["hash"] = val
        return val

    def __iter__(self):
        yield self

    def __len__(self):
        return 1

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.name == other.name and self.index == other.index)

    @property
    def _depth(self):
        return 1

    @property
    def xs(self):
        return {self}

    def get_dual(self):
        raise NotImplementedError()

    def copy(self): return self

    def _factor(self): return self
    def _simplify(self): return self


class Variable(Literal):
    """Boolean variable"""

    def __init__(self, name, index=-1):
        super(Variable, self).__init__()
        self._name = name
        self._index = index

    def __str__(self):
        if self._index >= 0:
            return "{0._name}[{0.index}]".format(self)
        else:
            return self._name

    def __lt__(self, other):
        if isinstance(other, Number):
            return False
        if isinstance(other, Literal):
            return (self.name < other.name or
                    self.name == other.name and self.index < other.index)
        if isinstance(other, OrAnd):
            return True
        return id(self) < id(other)

    @property
    def name(self):
        return self._name

    @property
    def index(self):
        return self._index

    def get_dual(self):
        if self not in COMPLEMENTS:
            COMPLEMENTS[self] = Complement(self)
        return COMPLEMENTS[self]

    def iter_vars(self):
        yield self

    def subs(self, d):
        if self in d:
            return tobool(d[self])
        else:
            return self


class Complement(Literal):
    """Boolean complement"""

    # Postfix symbol used in string representation
    OP = "'"

    def __init__(self, var):
        super(Complement, self).__init__()
        self._var = var

    def __str__(self):
        return str(self._var) + self.OP

    def __lt__(self, other):
        if isinstance(other, Number):
            return False
        if isinstance(other, Variable):
            return (self.name < other.name or
                    self.name == other.name and self.index <= other.index)
        if isinstance(other, Complement):
            return (self.name < other.name or
                    self.name == other.name and self.index < other.index)
        if isinstance(other, OrAnd):
            return True
        return id(self) < id(other)

    @property
    def name(self):
        return self._var.name

    @property
    def index(self):
        return self._var.index

    @property
    def var(self):
        return self._var

    def get_dual(self):
        return self._var

    def iter_vars(self):
        yield self._var

    def subs(self, d):
        if self._var in d:
            return Not(d[self._var])
        else:
            return self


class OrAnd(Expression):
    """base class for Boolean OR/AND expressions"""

    def __new__(cls, *xs):
        xs = {tobool(x) for x in xs}
        if len(xs) == 0:
            return cls.IDENTITY
        if len(xs) == 1:
            return xs.pop()
        else:
            return super(OrAnd, cls).__new__(cls)

    def __init__(self, *xs):
        super(OrAnd, self).__init__()
        self.xs = {tobool(x) for x in xs}
        self._reduce_assoc()

    def __iter__(self):
        for x in self.xs:
            yield x

    def __len__(self):
        return len(self.xs)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.xs == other.xs

    def __lt__(self, other):
        if isinstance(other, Number):
            return False
        if isinstance(other, Literal):
            return False
        if isinstance(other, OrAnd):
            vs = self.support | other.support
            for v in sorted(vs):
                if -v in self.xs and v in other.xs:
                    return True
                if v in self.xs and -v in other.xs:
                    return False
        return id(self) < id(other)

    @property
    def _depth(self):
        val = self.cache.get("depth", None)
        if val is None:
            val = max((x.depth + 1 if isinstance(x, OrAnd) else x.depth)
                      for x in self.xs)
            self.cache["depth"] = val
        return val

    @property
    def duals(self):
        val = self.cache.get("duals", None)
        if val is None:
            val = {x for x in self.xs if isinstance(x, self.get_dual())}
            self.cache["duals"] = val
        return val

    @staticmethod
    def get_dual():
        """The dual of OR is AND, and the dual of AND is OR."""
        raise NotImplementedError()

    def iter_vars(self):
        for x in self.xs:
            if not isinstance(x, Number):
                for v in x.iter_vars():
                    yield v

    def copy(self):
        return self.__class__(*[x for x in self.xs])

    def subs(self, d):
        replace = []
        for x in self.xs:
            _x = x.subs(d)
            if id(x) != id(_x):
                replace.append((x, _x))
        if replace:
            expr = self.copy()
            for old, new in replace:
                expr.xs.remove(old)
                expr.xs.add(new)
            return expr.simplify()
        else:
            return self

    def _factor(self):
        expr = self.copy()
        expr.xs = {x.factor() for x in self.xs}
        expr._reduce_assoc()
        return expr.simplify()

    def _simplify(self):
        expr = self.copy()
        expr.xs = {x.simplify() for x in self.xs}

        _zero = self.IDENTITY.get_dual()

        # x + 1 = 1; x * 0 = 0
        if _zero in expr.xs:
            return _zero

        # x + x' = 1; x * x' = 0
        vs = {x for x in expr.xs if isinstance(x, Variable)}
        for v in vs:
            if -v in expr.xs:
                return _zero

        # x + 0 = x; x * 1 = x
        expr.xs.discard(self.IDENTITY)

        if len(expr.xs) > 1:
            expr._reduce_absorb()

        if len(expr.xs) == 0:
            return self.IDENTITY
        elif len(expr.xs) == 1:
            return expr.xs.pop()
        else:
            return expr

    def _reduce_assoc(self):
        """
        x + (y + z) = x + y + z
        x * (y * z) = x * y * z
        """
        temps = {x for x in self.xs if isinstance(x, self.__class__)}
        self.xs -= temps
        while temps:
            t = temps.pop()
            if isinstance(t, self.__class__):
                temps |= t.xs
            else:
                self.xs.add(t)

    def _reduce_absorb(self):
        """
        x + (x * y) = x
        x * (x + y) = x
        """
        absorb = set()
        for xi in self.xs:
            for xj in self.xs:
                if xi != xj and xj not in absorb and xi.xs < xj.xs:
                    absorb.add(xj)
        self.xs -= absorb

    def _flatten(self, op):
        dual_op = op.get_dual()
        if isinstance(self, op):
            if self.duals:
                dual = list(self.duals)[0]
                others = list(self.xs - {dual})
                xs = [op(x, *others) for x in dual.xs]
                expr = dual_op(*xs)
                if isinstance(expr, OrAnd):
                    return expr.flatten(op)
                else:
                    return expr
            else:
                return self
        else:
            nested = {x for x in self.duals if x.depth > 1}
            others = list(self.xs - nested)
            xs = [x.flatten(op) for x in nested] + others
            return dual_op(*xs)

    def _canonize(self, op):
        if isinstance(self, op):
            return self
        else:
            expr = self.copy()
            support_len = len(expr.support)
            temps = {x for x in expr.xs if len(x) < support_len}
            expr.xs -= temps
            while temps:
                t = temps.pop()
                vs = expr.support - t.support
                if vs:
                    v, tc = vs.pop(), t.copy()
                    temps |= {op(-v, t), op(v, tc)}
                else:
                    expr.xs.add(t)
            return expr


class Or(OrAnd):
    """Boolean addition (or) operator"""

    # Infix symbol used in string representation
    OP = "+"

    IDENTITY = Zero

    def __str__(self):
        sep = " " + self.OP + " "
        return sep.join(str(x) for x in sorted(self.xs))

    @staticmethod
    def get_dual():
        return And


class And(OrAnd):
    """Boolean multiplication (and) operator"""

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


class BufNot(Expression):
    """base class for BUF/NOT operators"""

    def __init__(self, x):
        super(BufNot, self).__init__()
        self.x = tobool(x)

    def __eq__(self, other):
        other = tobool(other)
        return isinstance(other, self.__class__) and self.x == other.x

    def __lt__(self, other):
        return id(self) < id(other)

    @property
    def xs(self):
        return {self.x}

    def iter_vars(self):
        for v in self.x.iter_vars():
            yield v

    def copy(self):
        return self.__class__(self.x)

    def subs(self, d):
        expr = self.x.subs(d)
        if id(expr) == id(self.x):
            return self
        else:
            return self.__class__(expr)

    def _simplify(self):
        expr = self.x.simplify()
        if id(expr) == id(self.x):
            return self
        else:
            return self.__class__(expr)


class Buf(BufNot):
    """buffer operator"""

    def __new__(cls, x):
        x = tobool(x)
        if isinstance(x, Number) or isinstance(x, Literal):
            return x
        else:
            return super(Buf, cls).__new__(cls)

    def __str__(self):
        return "Buf({0.x})".format(self)

    def _factor(self):
        return self.x.factor()


class Not(BufNot):
    """Boolean NOT operator"""

    def __new__(cls, x):
        x = tobool(x)
        # 0' = 1; 1' = 0; x', (x')'
        if isinstance(x, Number) or isinstance(x, Literal):
            return x.get_dual()
        else:
            return super(Not, cls).__new__(cls)

    def __str__(self):
        return "Not({0.x})".format(self)

    def _factor(self):
        expr = self.x.factor()
        # 0' = 1; 1' = 0; x', (x')'
        if isinstance(expr, Number) or isinstance(expr, Literal):
            return expr.get_dual()
        # (x + y)' = x' * y'; (x * y)' = x' + y'
        elif isinstance(expr, OrAnd):
            expr = expr.get_dual()(*[Not(x) for x in expr.xs])
            return expr.factor()
        else:
            raise Exception("factor() returned unfactored expression")


class Xor(Expression):
    """Boolean XOR (exclusive or) operator"""

    IDENTITY = Zero

    def __new__(cls, *xs):
        xs = [tobool(x) for x in xs]
        if len(xs) == 0:
            return cls.IDENTITY
        elif len(xs) == 1:
            return xs.pop()
        else:
            return super(Xor, cls).__new__(cls)

    def __init__(self, *xs):
        super(Xor, self).__init__()
        self.xs = [tobool(x) for x in xs]
        self._reduce_assoc()

    def __str__(self):
        args = ", ".join(str(x) for x in self.xs)
        return "Xor(" + args + ")"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.xs == other.xs

    def __lt__(self, other):
        return id(self) < id(other)

    def iter_vars(self):
        for x in self.xs:
            if not isinstance(x, Number):
                for v in x.iter_vars():
                    yield v

    def copy(self):
        return self.__class__(*self.xs)

    def subs(self, d):
        replace = []
        for x in self.xs:
            _x = x.subs(d)
            if id(x) != id(_x):
                replace.append((x, _x))
        if replace:
            expr = self.copy()
            for old, new in replace:
                expr.xs.remove(old)
                expr.xs.append(new)
            return expr.simplify()
        else:
            return self

    def _factor(self):
        x, xs = self.xs[0], self.xs[1:]
        return OrF(And(Not(x), Xor(*xs)), And(x, Xnor(*xs)))

    def _simplify(self):
        xs = [x.simplify() for x in self.xs]

        # XOR(x, x') = 1
        for x in xs:
            while xs.count(x) > 0 and xs.count(-x) > 0:
                xs.remove(x)
                xs.remove(-x)
                xs.append(One)
        # XOR(x, x) = 0
        dups = {x for x in xs if xs.count(x) > 1}
        for dup in dups:
            while xs.count(dup) > 1:
                xs.remove(dup)
                xs.remove(dup)
        # XOR(x, 0) = x
        while xs.count(self.IDENTITY) > 0:
            xs.remove(self.IDENTITY)

        if len(xs) == 0:
            return self.IDENTITY
        if len(xs) == 1:
            return xs.pop()

        # XOR(x, 1) = x'
        if One in xs:
            xs.remove(One)
            return Xnor(*xs)
        elif xs == self.xs:
            return self
        else:
            return self.__class__(*xs)

    def _reduce_assoc(self):
        """XOR(a, XOR(b, c)) = XOR(a, b, c)"""
        temps = [x for x in self.xs if isinstance(x, self.__class__)]
        self.xs = [x for x in self.xs if not isinstance(x, self.__class__)]
        while temps:
            t = temps.pop()
            if isinstance(t, self.__class__):
                temps += t.xs
            else:
                self.xs.append(t)


class Implies(Expression):
    """Boolean implication operator"""

    OP = "=>"

    def __init__(self, x0, x1):
        super(Implies, self).__init__()
        self.xs = [tobool(x0), tobool(x1)]

    def __str__(self):
        s = []
        for x in self.xs:
            if isinstance(x, Implies):
                s.append("(" + str(x) + ")")
            else:
                s.append(str(x))
        sep = " " + self.OP + " "
        return sep.join(s)

    def iter_vars(self):
        for x in self.xs:
            for v in x.iter_vars():
                yield v

    def copy(self):
        return Implies(*self.xs)

    def _factor(self):
        return OrF(Not(self.xs[0]), self.xs[1])

    def _simplify(self):
        xs = [x.simplify() for x in self.xs]

        # 0 => x = 1; x => 1 = 1
        if xs[0] is Zero or xs[1] is One:
            return One
        # 1 => x = x
        elif xs[0] is One:
            return xs[1]
        # x => 0 = x'
        elif xs[1] is Zero:
            return Not(xs[0])

        if xs == self.xs:
            return self
        else:
            return self.__class__(xs[0], xs[1])


# Miscellaneous operators
class Nor(object):
    """Boolean NOR (not or) operator"""
    def __new__(cls, *xs):
        return Not(Or(*xs))

class Nand(object):
    """Boolean NAND (not and) operator"""
    def __new__(cls, *xs):
        return Not(And(*xs))

class Xnor(Boolean):
    """Boolean XNOR (exclusive nor) operator"""
    def __new__(cls, *xs):
        return Not(Xor(*xs))


# Factored convenience classes
class NotF(object):
    """factored NOT operator"""
    def __new__(cls, x):
        return Not(x).factor()

class OrF(object):
    """factored OR operator"""
    def __new__(cls, *xs):
        return Or(*xs).factor()

class NorF(object):
    """Boolean NOR (not or) operator"""
    def __new__(cls, *xs):
        return Nor(*xs).factor()

class AndF(object):
    """factored AND operator"""
    def __new__(cls, *xs):
        return And(*xs).factor()

class NandF(object):
    """Boolean NAND (not and) operator"""
    def __new__(cls, *xs):
        return Nand(*xs).factor()

class XorF(object):
    """factored XOR operator"""
    def __new__(cls, *xs):
        return Xor(*xs).factor()

class XnorF(object):
    """Boolean XNOR (not xor) operator"""
    def __new__(cls, *xs):
        return Xnor(*xs).factor()

class ImpliesF(Boolean):
    """Factored IMPLIES operator"""
    def __new__(cls, x0, x1):
        return Implies(x0, x1).factor()


class Vector(object):
    """Boolean vector"""

    def __init__(self, *fs, **kwargs):
        self.fs = [tobool(f) for f in fs]
        self._start = kwargs.get("start", 0)
        self._bnr = kwargs.get("bnr", UNSIGNED)

    def __len__(self):
        return len(self.fs)

    def __int__(self):
        return self.to_int()

    def __str__(self):
        return str(self.fs)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        for f in self.fs:
            yield f

    # unary operators
    def __invert__(self):
        fs = [Not(v) for v in self.fs]
        return Vector(*fs, start=self._start, bnr=self._bnr)

    def uor(self):
        return Or(*list(self.fs))

    def uand(self):
        return And(*list(self.fs))

    def uxor(self):
        return Xor(*list(self.fs))

    # binary operators
    def __or__(self, other):
        assert isinstance(other, Vector) and len(self) == len(other)
        return Vector(*[Or(*t) for t in zip(self.fs, other.fs)])

    def __and__(self, other):
        assert isinstance(other, Vector) and len(self) == len(other)
        return Vector(*[And(*t) for t in zip(self.fs, other.fs)])

    def __xor__(self, other):
        assert isinstance(other, Vector) and len(self) == len(other)
        return Vector(*[Xor(*t) for t in zip(self.fs, other.fs)])

    def getifz(self, i):
        """Get item from zero-based index."""
        return self.__getitem__(i + self.start)

    def __getitem__(self, sl):
        if isinstance(sl, int):
            return self.fs[self._norm_idx(sl)]
        else:
            norm = self._norm_slice(sl)
            return Vector(*self.fs.__getitem__(norm),
                          start=(norm.start + self._start),
                          bnr=self._bnr)

    def __setitem__(self, sl, f):
        if isinstance(sl, int):
            self.fs.__setitem__(sl, f)
        else:
            norm = self._norm_slice(sl)
            self.fs.__setitem__(norm, f)

    @property
    def start(self):
        return self._start

    @property
    def bnr(self):
        return self._bnr

    @bnr.setter
    def bnr(self, value):
        self._bnr = value

    @property
    def sl(self):
        return slice(self._start, len(self.fs) + self._start)

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
        if self._bnr == TWOS_COMPLEMENT and self.fs[-1]:
            return -2 ** self.__len__() + num
        else:
            return num

    def subs(self, d):
        """Substitute numbers into a Boolean vector."""
        cpy = self[:]
        for i, f in enumerate(cpy.fs):
            cpy[i] = cpy[i].subs(d)
        return cpy

    def vsubs(self, d):
        """Expand all vectors before doing a substitution."""
        return self.subs(_expand_vectors(d))

    def append(self, f):
        """Append logic function to the end of this vector."""
        self.fs.append(f)

    def ext(self, num):
        """Extend this vector by N bits.

        If this vector uses two's complement representation, sign extend;
        otherwise, zero extend.
        """
        if self.bnr == TWOS_COMPLEMENT:
            bit = self.fs[-1]
        else:
            bit = Zero
        for i in range(num):
            self.append(bit)

    def eq(A, B):
        assert isinstance(B, Vector) and len(A) == len(B)
        return And(*[Xnor(*t) for t in zip(A.fs, B.fs)])

    def decode(A):
        return Vector(*[And(*[f if _bit_on(i, j) else -f
                              for j, f in enumerate(A.fs)])
                        for i in range(2 ** len(A))])

    def ripple_carry_add(A, B, ci=Zero):
        assert isinstance(B, Vector) and len(A) == len(B)
        if A.bnr == TWOS_COMPLEMENT or B.bnr == TWOS_COMPLEMENT:
            sum_bnr = TWOS_COMPLEMENT
        else:
            sum_bnr = UNSIGNED
        S = Vector(bnr=sum_bnr)
        C = Vector()
        for i, A in enumerate(A.fs):
            carry = (ci if i == 0 else C[i-1])
            S.append(Xor(A, B.getifz(i), carry))
            C.append(A * B.getifz(i) + A * carry + B.getifz(i) * carry)
        return S, C

    def _norm_idx(self, i):
        """Return an index normalized to vector start index."""
        if i >= 0:
            if i < self._start:
                raise IndexError("list index out of range")
            else:
                idx = i - self._start
        else:
            idx = i + self._start
        return idx

    def _norm_slice(self, sl):
        """Return a slice normalized to vector start index."""
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
        return slice(d["start"] - self._start, d["stop"] - self._start)


#==============================================================================
# Internal Functions
#==============================================================================

def _clog2(num):
    """Return the ceiling, log base two of an integer."""
    assert num >= 1
    i, x = 0, 1
    while x < num:
        x = x << 1;
        i += 1
    return i

def _bit_on(num, bit):
    return bool((num >> bit) & 1)

def _expand_vectors(d):
    """Expand all vectors in a substitution dict."""
    temp = {k: v for k, v in d.items() if isinstance(k, Vector)}
    d = {k: v for k, v in d.items() if k not in temp}
    while temp:
        key, val = temp.popitem()
        if isinstance(key, Vector):
            assert len(key) == len(val)
            for i, x in enumerate(val):
                d[key.getifz(i)] = tobool(x)
        elif isinstance(key, Literal):
            d[key] = val
    return d
