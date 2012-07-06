"""
Boolean Algebra

Interface Functions:
    num
    var
    comp
    vec
    svec

    factor
    simplify

    notf, org, norf, andf, nandf, xorf, xnorf, impliesf

    cube_sop
    cube_pos
    iter_space
    iter_points

    uint2vec
    int2vec

    Nor, Nand, Xnor

Classes:
    Boolean
        Number: Zero, One
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
    Vector

Huntington's Postulates
+---------------------------------+--------------+
| x + y = y + x                   | Commutative  |
| x * y = y * x                   | Commutative  |
+---------------------------------+--------------+
| x + (y * z) = (x + y) * (x + z) | Distributive |
| x * (y + z) = (x * y) + (x * z) | Distributive |
+---------------------------------+--------------+
| x + x' = 1                      | Complement   |
| x * x' = 0                      | Complement   |
+---------------------------------+--------------+

Properties of Boolean Algebraic Systems
+---------------------------+---------------+
| x + (y + z) = (x + y) + z | Associativity |
| x * (y * z) = (x * y) * z | Associativity |
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
__license__ = "All rights reserved."

#==============================================================================
# Constants
#==============================================================================

B = {0, 1}

UNSIGNED, TWOS_COMPLEMENT = range(2)

NUMBERS = dict()
VARIABLES = dict()
COMPLEMENTS = dict()

#==============================================================================
# Interface Functions
#==============================================================================

def num(x):
    """Return a unique Boolean Number."""
    n = int(x)
    if not n in B:
        raise ValueError("invalid Boolean number: " + str(n))
    try:
        ret = NUMBERS[n]
    except KeyError:
        ret = Number(n)
        NUMBERS[n] = ret
    return ret

def var(name, index=-1):
    try:
        ret = VARIABLES[(name, index)]
    except KeyError:
        ret = Variable(name, index)
        VARIABLES[(name, index)] = ret
    return ret

def comp(var):
    try:
        ret = COMPLEMENTS[var]
    except KeyError:
        ret = Complement(var)
        COMPLEMENTS[var] = ret
    return ret

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

def factor(expr):
    """Return a factored expression."""
    return expr.factor()

def simplify(expr):
    """Return a simplified expression."""
    return expr.simplify()

def notf(x):
    return Not(x).factor()

def orf(*xs):
    return Or(*xs).factor()

def norf(*xs):
    return Nor(*xs).factor()

def andf(*xs):
    return And(*xs).factor()

def nandf(*xs):
    return Nand(*xs).factor()

def xorf(*xs):
    return Xor(*xs).factor()

def xnorf(*xs):
    return Xnor(*xs).factor()

def impliesf(x0, x1):
    return Implies(x0, x1).factor()

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
    for n in range(2 ** len(vs)):
        yield [(v if _bit_on(n, i) else -v) for i, v in enumerate(vs)]

def iter_points(op, *vs):
    """
    Iterate through all OR/AND points in the multi-dimensional space spanned
    by N Boolean variables.
    """
    if not issubclass(op, OrAnd):
        raise TypeError("iter_points() expected op type OR/AND")
    for s in iter_space(*vs):
        yield op(*s)

def uint2vec(n, length=None):
    """Convert an unsigned integer to a Vector."""
    assert n >= 0

    vv = Vector()
    if n == 0:
        vv.append(Zero)
    else:
        while n != 0:
            vv.append(num(n & 1))
            n >>= 1

    if length:
        if length < len(vv):
            raise ValueError("overflow: " + str(n))
        else:
            vv.ext(length - len(vv))

    return vv

def int2vec(n, length=None):
    """Convert a signed integer to a Vector."""
    if n < 0:
        req_length = _clog2(abs(n)) + 1
        vv = uint2vec(2 ** req_length + n)
    else:
        req_length = _clog2(n + 1) + 1
        vv = uint2vec(n)
        vv.ext(req_length - len(vv))
    vv.bnr = TWOS_COMPLEMENT

    if length:
        if length < req_length:
            raise ValueError("overflow: " + str(n))
        else:
            vv.ext(length - req_length)

    return vv

#==============================================================================
# Classes
#==============================================================================

class Boolean:
    """Base class for Boolean objects"""

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
        """Return a simplifed expression.

        The meaning of the word "simplified" is not strictly defined here.
        At a bare minimum, operators should apply idempotence, eliminate all
        numbers, eliminate literals that combine into numbers. For factored
        expressions, also absorb terms.
        """
        expr = self._simplify()
        return expr


class Number(Boolean):
    """Boolean number"""

    def __init__(self, val):
        self._val = val

    def __hash__(self):
        return self._val

    def __str__(self):
        return str(self._val)

    def __eq__(self, other):
        if isinstance(other, Boolean):
            return isinstance(other, Number) and self._val == other.val
        else:
            return self._val == num(other).val

    def __lt__(self, other):
        if isinstance(other, Number):
            return self.val < other.val
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def __bool__(self):
        return bool(self._val)

    @property
    def _depth(self):
        return 1

    @property
    def val(self):
        return self._val

    def get_dual(self):
        return num(1 - self._val)

    def subs(self, d): return self

    def _factor(self): return self
    def _simplify(self): return self


Zero = num(0)
One = num(1)


class Expression(Boolean):
    """Boolean expression"""

    def __init__(self):
        super(Expression, self).__init__()
        self.cache = dict()

    def __iter__(self):
        raise NotImplementedError()

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
        expr = self.to_pos()
        expr = expr.canonize(Or)
        return expr

    def to_csop(self):
        """Return the expression as a sum of products of N literals."""
        expr = self.to_sop()
        expr = expr.canonize(And)
        return expr

    def iter_cofactors(self, *vs):
        """Iterate through the cofactors of N variables."""
        for n in range(2 ** len(vs)):
            yield self.subs({v: _bit_on(n, i) for i, v in enumerate(vs)})

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
        return Xor(*self.cofactors(*vs))

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

    def equal(self, other):
        """Return whether this expression is equivalent to another.

        To avoid ambiguity about instantiating multiple variables with the
        same name and index, we are not overloading the __eq__ method to have
        any special meaning. This method provides a convenient way to check
        equivalence when that might not be sufficient.
        """
        raise NotImplementedError()


class Literal(Expression):
    """An instance of a variable or of its complement"""

    def __iter__(self):
        yield self

    def __len__(self):
        return 1

    @property
    def _depth(self):
        return 1

    @property
    def xs(self):
        return {self}

    def get_dual(self):
        raise NotImplementedError()

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
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    @property
    def name(self):
        return self._name

    @property
    def index(self):
        return self._index

    def get_dual(self):
        return comp(self)

    def iter_vars(self):
        yield self

    def subs(self, d):
        if self in d:
            val = d[self]
            if not isinstance(val, Boolean):
                val = num(val)
            return val
        else:
            return self

    def equal(self, other):
        return self == other


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
        if isinstance(other, Expression):
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
            val = d[self._var]
            if not isinstance(val, Boolean):
                val = num(val)
            return Not(val)
        else:
            return self

    def equal(self, other):
        return self == other


class OrAnd(Expression):
    """base class for Boolean OR/AND expressions"""

    def __new__(cls, *xs):
        temps, xs = list(xs), list()
        # x + (y + z) = (x + y) + z; x * (y * z) = (x * y) * z
        while temps:
            t = temps.pop()
            x = t if isinstance(t, Boolean) else num(t)
            if x == cls.ABSORBER:
                return cls.ABSORBER
            elif isinstance(x, cls):
                temps.extend(x.xs)
            elif x != cls.IDENTITY:
                xs.append(x)

        if len(xs) == 0:
            return cls.IDENTITY
        if len(xs) == 1:
            return xs.pop()

        self = super(OrAnd, cls).__new__(cls)
        self.xs = xs
        return self

    def __init__(self, *xs):
        super(OrAnd, self).__init__()

    def __abs__(self):
        return len(self.support)

    def __iter__(self):
        return iter(self.xs)

    def __len__(self):
        return len(self.xs)

    def __lt__(self, other):
        if isinstance(other, Number):
            return False
        if isinstance(other, Literal):
            return self.support < other.support
        if isinstance(other, self.__class__) and self.depth == other.depth == 1:
            # min/max term
            if self.support == other.support:
                return self.term_index < other.term_index
            else:
                # support containment
                if self.support < other.support:
                    return True
                if other.support < self.support:
                    return False
                # support disjoint
                v = sorted(self.support ^ other.support)[0]
                if v in self.support:
                    return True
                if v in other.support:
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
    def _duals(self):
        val = self.cache.get("duals", None)
        if val is None:
            val = [x for x in self.xs if isinstance(x, self.get_dual())]
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

    def subs(self, d):
        replace = list()
        for x in self.xs:
            _x = x.subs(d)
            if id(x) != id(_x):
                replace.append((x, _x))
        if replace:
            xs = self.xs[:]
            for old, new in replace:
                if new == self.ABSORBER:
                    return self.ABSORBER
                else:
                    old_cnt = xs.count(old)
                    for i in range(old_cnt):
                        xs.remove(old)
                    if new != self.IDENTITY:
                        xs.append(new)
            return self.__class__(*xs)
        else:
            return self

    def _factor(self):
        expr = self.__class__(*[x.factor() for x in self.xs])
        return expr.simplify()

    def _simplify(self):
        xs = [x.simplify() for x in self.xs]

        # x + x' = 1; x * x' = 0
        vs = {x for x in xs if isinstance(x, Variable)}
        for v in vs:
            if -v in xs:
                return self.ABSORBER

        # x + x = x; x * x = x
        # x + (x * y) = x; x * (x + y) = x
        self._absorb(xs)

        return self.__class__(*xs)

    def _absorb(self, xs):
        dual_op = self.get_dual()
        # Find all min/max terms
        terms = list()
        i = len(xs) - 1
        while i >= 0:
            if isinstance(xs[i], Literal):
                terms.append(xs.pop(i))
            elif isinstance(xs[i], dual_op) and xs[i].depth == 1:
                terms.append(xs.pop(i))
            i -= 1
        # Drop all terms that are a subset of other terms.
        while terms:
            fst, rst, terms = terms[0], terms[1:], list()
            drop_fst = False
            for term in rst:
                drop_term = False
                if fst.equal(term):
                    drop_term = True
                else:
                    if all(any(fx.equal(tx) for tx in term.xs) for fx in fst.xs):
                        drop_term = True
                    if all(any(fx.equal(tx) for tx in fst.xs) for fx in term.xs):
                        drop_fst = True
                if not drop_term:
                    terms.append(term)
            if not drop_fst:
                xs.append(fst)

    def _flatten(self, op):
        dual_op = op.get_dual()
        if isinstance(self, op):
            if self._duals:
                dual = self._duals[0]
                others = [x for x in self.xs if x != dual]
                expr = dual_op(*[op(x, *others) for x in dual.xs])
                if isinstance(expr, OrAnd):
                    return expr.flatten(op)
                else:
                    return expr
            else:
                return self
        else:
            nested, others = list(), list()
            for x in self.xs:
                if x.depth > 1:
                    nested.append(x)
                else:
                    others.append(x)
            xs = [x.flatten(op) for x in nested] + others
            return dual_op(*xs)

    def _canonize(self, op):
        if isinstance(self, op):
            return self
        else:
            terms, xs = list(), list()
            for x in self.xs:
                if len(x) < abs(self):
                    terms.append(x)
                else:
                    xs.append(x)
            while terms:
                term = terms.pop()
                vs = self.support - term.support
                if vs:
                    v = vs.pop()
                    terms += [op(-v, term), op(v, term)]
                else:
                    if all(term.term_index != x.term_index for x in xs):
                        xs.append(term)
            return self.__class__(*xs)

    def equal(self, other):
        raise NotImplementedError()


class Or(OrAnd):
    """Boolean addition (or) operator"""

    # Infix symbol used in string representation
    OP = "+"

    IDENTITY = Zero
    ABSORBER = One

    def __str__(self):
        sep = " " + self.OP + " "
        return sep.join(str(x) for x in sorted(self.xs))

    @staticmethod
    def get_dual():
        return And

    @property
    def term_index(self):
        n = abs(self) - 1
        idx = 0
        for i, v in enumerate(sorted(self.support)):
            if -v in self.xs:
                idx |= 1 << (n - i)
        return idx

    def equal(self, other):
        assert self.depth == 1
        return (isinstance(other, Or) and self.support == other.support and
                self.term_index == other.term_index)


class And(OrAnd):
    """Boolean multiplication (and) operator"""

    # Infix symbol used in string representation
    OP = "*"

    IDENTITY = One
    ABSORBER = Zero

    def __str__(self):
        s = list()
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

    @property
    def term_index(self):
        n = abs(self) - 1
        idx = 0
        for i, v in enumerate(sorted(self.support)):
            if v in self.xs:
                idx |= 1 << (n - i)
        return idx

    def equal(self, other):
        assert self.depth == 1
        return (isinstance(other, And) and self.support == other.support and
                self.term_index == other.term_index)


class BufNot(Expression):
    """base class for BUF/NOT operators"""

    def __init__(self, x):
        super(BufNot, self).__init__()
        self.x = x if isinstance(x, Boolean) else num(x)

    @property
    def xs(self):
        return {self.x}

    def iter_vars(self):
        for v in self.x.iter_vars():
            yield v

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
        x = x if isinstance(x, Boolean) else num(x)
        # Auto-simplify numbers and literals
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
        x = x if isinstance(x, Boolean) else num(x)
        # Auto-simplify numbers and literals
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
        temps, xs = list(xs), list()
        # x + (y + z) = (x + y) + z; x * (y * z) = (x * y) * z
        while temps:
            t = temps.pop()
            x = t if isinstance(t, Boolean) else num(t)
            if isinstance(x, cls):
                temps.extend(x.xs)
            elif x != cls.IDENTITY:
                xs.append(x)

        if len(xs) == 0:
            return cls.IDENTITY
        if len(xs) == 1:
            return xs.pop()

        self = super(Xor, cls).__new__(cls)
        self.xs = xs
        return self

    def __init__(self, *xs):
        super(Xor, self).__init__()

    def __iter__(self):
        return iter(self.xs)

    def __len__(self):
        return len(self.xs)

    def __str__(self):
        args = ", ".join(str(x) for x in self.xs)
        return "Xor(" + args + ")"

    def iter_vars(self):
        for x in self.xs:
            if not isinstance(x, Number):
                for v in x.iter_vars():
                    yield v

    def subs(self, d):
        replace = list()
        for x in self.xs:
            _x = x.subs(d)
            if id(x) != id(_x):
                replace.append((x, _x))
        if replace:
            xs = self.xs[:]
            for old, new in replace:
                old_cnt = xs.count(old)
                for i in range(old_cnt):
                    xs.remove(old)
                if new != self.IDENTITY:
                    xs.append(new)
            if xs.count(1) & 1:
                return Not(Xor(*[x for x in xs if x != 1]))
            else:
                return Xor(*[x for x in xs if x != 1])
        else:
            return self

    def _factor(self):
        x, xs = self.xs[0], self.xs[1:]
        return Or(And(Not(x), Xor(*xs)), And(x, Xnor(*xs))).factor()

    def _simplify(self):
        xs = [x.simplify() for x in self.xs]

        # XOR(x, x') = 1
        for x in xs:
            x_cnt = xs.count(x)
            xn_cnt = xs.count(-x)
            while x_cnt > 0 and xn_cnt > 0:
                xs.remove(x); x_cnt -= 1
                xs.remove(-x); xn_cnt -= 1
                xs.append(One)
        # XOR(x, x) = 0
        dups = {x for x in xs if xs.count(x) > 1}
        for dup in dups:
            dup_cnt = xs.count(dup)
            while dup_cnt > 1:
                xs.remove(dup)
                xs.remove(dup)
                dup_cnt -= 2

        if xs.count(1) & 1:
            return Not(Xor(*[x for x in xs if x != 1]))
        else:
            return Xor(*[x for x in xs if x != 1])


class Implies(Expression):
    """Boolean implication operator"""

    OP = "=>"

    def __new__(cls, x0, x1):
        xs = [x if isinstance(x, Boolean) else num(x) for x in (x0, x1)]
        # 0 => x = 1; x => 1 = 1
        if xs[0] is Zero or xs[1] is One:
            return One
        # 1 => x = x
        elif xs[0] is One:
            return xs[1]
        # x => 0 = x'
        elif xs[1] is Zero:
            return Not(xs[0])
        else:
            self = super(Implies, cls).__new__(cls)
            self.xs = xs
            return self

    def __init__(self, x0, x1):
        super(Implies, self).__init__()

    def __str__(self):
        s = list()
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

    def _factor(self):
        return Or(Not(self.xs[0]), self.xs[1]).factor()

    def _simplify(self):
        xs = [x.simplify() for x in self.xs]

        # x => x = 1
        if xs[0] == xs[1]:
            return One
        # -x => x = x; x => -x = -x
        elif -xs[0] == xs[1] or xs[0] == -xs[1]:
            return xs[1]

        return Implies(xs[0], xs[1])


# Miscellaneous operators
class Nor:
    """Boolean NOR (not or) operator"""
    def __new__(cls, *xs):
        return Not(Or(*xs))

class Nand:
    """Boolean NAND (not and) operator"""
    def __new__(cls, *xs):
        return Not(And(*xs))

class Xnor:
    """Boolean XNOR (exclusive nor) operator"""
    def __new__(cls, *xs):
        return Not(Xor(*xs))


class Vector:
    """Boolean vector"""

    def __init__(self, *fs, **kwargs):
        self.fs = [f if isinstance(f, Boolean) else num(f) for f in fs]
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
        n = 0
        for i, f in enumerate(self.fs):
            if isinstance(f, Number):
                if f is One:
                    n += 2 ** i
            else:
                raise ValueError("cannot convert to uint")
        return n

    def to_int(self):
        """Convert vector into an integer."""
        n = self.to_uint()
        if self._bnr == TWOS_COMPLEMENT and self.fs[-1]:
            return -2 ** self.__len__() + n
        else:
            return n

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

    def ext(self, n):
        """Extend this vector by N bits.

        If this vector uses two's complement representation, sign extend;
        otherwise, zero extend.
        """
        if self.bnr == TWOS_COMPLEMENT:
            bit = self.fs[-1]
        else:
            bit = Zero
        for i in range(n):
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

def _clog2(n):
    """Return the ceiling, log base two of an integer."""
    assert n >= 1
    i, x = 0, 1
    while x < n:
        x = x << 1;
        i += 1
    return i

def _bit_on(n, bit):
    return bool((n >> bit) & 1)

def _expand_vectors(d):
    """Expand all vectors in a substitution dict."""
    temp = {k: v for k, v in d.items() if isinstance(k, Vector)}
    d = {k: v for k, v in d.items() if k not in temp}
    while temp:
        key, val = temp.popitem()
        if isinstance(key, Vector):
            assert len(key) == len(val)
            for i, x in enumerate(val):
                d[key.getifz(i)] = x if isinstance(x, Boolean) else num(x)
        elif isinstance(key, Literal):
            d[key] = val
    return d
