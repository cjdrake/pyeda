"""
Boolean Expressions

Interface Functions:
    var
    comp
    vec
    svec

    factor
    simplify

    nor, nand

    f_not, f_or, f_nor, f_and, f_nand, f_xor, f_xnor, f_implies

    cube_sop
    cube_pos
    iter_space
    iter_points

    uint2vec
    int2vec

Interface Classes:
    Expression
        Literal
            VariableEx
            Complement
        OrAnd
            Or
            And
        BufNot
            Buf
            Not
        Exclusive
            Xor
            Xnor
        Implies
    VectorExpression
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from .common import bit_on, cached_property

from .boolfunc import Variable, Function
from .boolfunc import VectorFunction as VF

B = {0, 1}

VARIABLES = dict()
COMPLEMENTS = dict()

def var(name, index=None):
    try:
        ret = VARIABLES[(name, index)]
    except KeyError:
        ret = VariableEx(name, index)
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
    if not 0 <= start < stop:
        raise ValueError("invalid range: [{}:{}]".format(start, stop))
    fs = [VariableEx(name, index=i) for i in range(start, stop)]
    return VectorExpression(*fs, start=start, **kwargs)

def svec(name, *args, **kwargs):
    """Return a signed vector of variables."""
    return vec(name, *args, bnr=VF.TWOS_COMPLEMENT, **kwargs)

def factor(expr):
    """Return a factored expression."""
    return expr.factor()

def simplify(expr):
    """Return a simplified expression."""
    return expr.simplify()

# operators
def nor(*args):
    """Boolean NOR (not or) operator"""
    return Not(Or(*args))

def nand(*args):
    """Boolean NAND (not and) operator"""
    return Not(And(*args))

#def ite(f, g, h):
#    """Boolean ITE (if then else) operator"""
#    return Or(And(f, g), And(Not(f), h))

# factored operators
def f_not(x):
    return Not(x).factor()

def f_or(*xs):
    return Or(*xs).factor()

def f_nor(*xs):
    return nor(*xs).factor()

def f_and(*xs):
    return And(*xs).factor()

def f_nand(*xs):
    return nand(*xs).factor()

def f_xor(*xs):
    return Xor(*xs).factor()

def f_xnor(*xs):
    return Xnor(*xs).factor()

def f_implies(x0, x1):
    return Implies(x0, x1).factor()

def cube_sop(vs):
    """
    Return the multi-dimensional space spanned by N Boolean variables as a
    sum of products.
    """
    points = [p for p in iter_points(And, vs)]
    return Or(*points)

def cube_pos(vs):
    """
    Return the multi-dimensional space spanned by N Boolean variables as a
    product of sums.
    """
    points = [p for p in iter_points(Or, vs)]
    return And(*points)

def iter_space(vs):
    """Return the multi-dimensional space spanned by N Boolean variables."""
    for n in range(2 ** len(vs)):
        yield tuple((v if bit_on(n, i) else -v) for i, v in enumerate(vs))

def iter_points(op, vs):
    """
    Iterate through all OR/AND points in the multi-dimensional space spanned
    by N Boolean variables.
    """
    if not issubclass(op, OrAnd):
        raise TypeError("iter_points() expected op type OR/AND")
    for space in iter_space(vs):
        yield op(*space)

def uint2vec(num, length=None):
    """Convert an unsigned integer to a VectorExpression."""
    assert num >= 0

    vv = VectorExpression()
    while num != 0:
        vv.append(num & 1)
        num >>= 1

    if length:
        if length < len(vv):
            raise ValueError("overflow: " + str(num))
        else:
            vv.ext(length - len(vv))

    return vv

def int2vec(n, length=None):
    """Convert a signed integer to a VectorExpression."""
    if n < 0:
        req_length = _clog2(abs(n)) + 1
        vv = uint2vec(2 ** req_length + n)
    else:
        req_length = _clog2(n + 1) + 1
        vv = uint2vec(n)
        vv.ext(req_length - len(vv))
    vv.bnr = VF.TWOS_COMPLEMENT

    if length:
        if length < req_length:
            raise ValueError("overflow: " + str(n))
        else:
            vv.ext(length - req_length)

    return vv


class Expression(Function):
    """Boolean function represented by a logic expression"""

    def __lt__(self, other):
        """Implementing this function makes expressions sortable."""
        raise NotImplementedError()

    def __repr__(self):
        """Return a printable representation."""
        return self.__str__()

    # From Function
    @cached_property
    def support(self):
        return {v for v in self.iter_vars()}

    def op_not(self):
        return Not(self)

    def op_or(self, *args):
        return Or(self, *args)

    def op_and(self, *args):
        return And(self, *args)

    def op_ge(self, other):
        return Implies(other, self)

    def op_le(self, other):
        return Implies(self, other)

    def is_neg_unate(self, vs=None):
        if vs is None:
            vs = self.support
        for v in vs:
            fv0, fv1 = self.cofactors([v])
            if fv0 in B or fv1 in B:
                if not (fv0 == 1 or fv1 == 0):
                    return False
            # FIXME -- broken
            elif not (fv0.minterms >= fv1.minterms):
                return False
        return True

    def is_pos_unate(self, vs=None):
        if vs is None:
            vs = self.support
        for v in vs:
            fv0, fv1 = self.cofactors([v])
            if fv0 in B or fv1 in B:
                if not (fv1 == 1 or fv0 == 0):
                    return False
            # FIXME -- broken
            elif not (fv1.minterms >= fv0.minterms):
                return False
        return True

    def is_binate(self, vs=None):
        return not (self.is_neg_unate(vs) or self.is_pos_unate(vs))

    def smoothing(self, *vs):
        return Or(*self.cofactors(vs))

    def consensus(self, *vs):
        return And(*self.cofactors(vs))

    def derivative(self, *vs):
        return Xor(*self.cofactors(vs))

    # Specific to Expressions
    @property
    def depth(self):
        """The number of levels in the expression tree."""
        raise NotImplementedError()

    def invert(self):
        """Return an inverted expression."""
        raise NotImplementedError()

    def vsubs(self, d):
        """Expand all vectors before doing a substitution."""
        return self.restrict(_expand_vectors(d))

    #def iter_outputs(self):
    #    for n in range(2 ** abs(self)):
    #        d = {v: bit_on(n, i) for i, v in enumerate(self.inputs)}
    #        yield self.restrict(d)

    def factor(self):
        """Return a factored expression.

        A factored expression is one and only one of the following:
        * A literal.
        * A sum / product of factored expressions.
        """
        raise NotImplementedError()

    def simplify(self):
        """Return a simplifed expression.

        The meaning of the word "simplified" is not strictly defined here.
        At a bare minimum, operators should apply idempotence, eliminate all
        numbers, eliminate literals that combine into numbers. For factored
        expressions, also absorb terms.
        """
        raise NotImplementedError()

    @cached_property
    def inputs(self):
        return sorted(self.support)

    #@property
    #def top(self):
    #    """Return the first variable in the ordered support."""
    #    return self.inputs[0]

    def iter_vars(self):
        """Recursively iterate through all variables in the expression."""
        raise NotImplementedError()

    def iter_minterms(self):
        """Iterate through the sum of products of N literals."""
        for n in range(2 ** abs(self)):
            d = dict()
            space = list()
            for i, v in enumerate(self.inputs):
                on = bit_on(n, i)
                d[v] = on
                space.append(v if on else -v)
            output = self.restrict(d)
            if output:
                yield And(*space)

    def iter_maxterms(self):
        """Iterate through the product of sums of N literals."""
        for n in range(2 ** abs(self)):
            d = dict()
            space = list()
            for i, v in enumerate(self.inputs):
                on = bit_on(n, i)
                d[v] = on
                space.append(-v if on else v)
            output = self.restrict(d)
            if not output:
                yield Or(*space)

    @cached_property
    def minterms(self):
        """The sum of products of N literals"""
        return {term for term in self.iter_minterms()}

    @cached_property
    def maxterms(self):
        """The product of sums of N literals"""
        return {term for term in self.iter_maxterms()}

    def flatten(self, op):
        """Return expression after flattening OR/AND."""
        expr = self._flatten(op)
        expr = expr.simplify()
        return expr

    def to_sop(self):
        """Return the expression as a sum of products."""
        expr = self.factor()
        expr = expr.flatten(And)
        return expr

    def to_pos(self):
        """Return the expression as a product of sums."""
        expr = self.factor()
        expr = expr.flatten(Or)
        return expr

    def to_csop(self):
        """Return the expression as a sum of products of N literals."""
        return Or(*[term for term in self.iter_minterms()])

    def to_cpos(self):
        """Return the expression as a product of sums of N literals."""
        return And(*[term for term in self.iter_maxterms()])

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
    def depth(self):
        return 0

    @property
    def args(self):
        return {self}

    def factor(self):
        return self

    def simplify(self):
        return self

    def equal(self, other):
        return self == other


class VariableEx(Variable, Literal):
    """Boolean variable (expression)"""

    def __init__(self, name, index=None):
        Variable.__init__(self, name, index)
        Literal.__init__(self)

    def __lt__(self, other):
        if other in B:
            return False
        if isinstance(other, Literal):
            return (self.name < other.name or
                    self.name == other.name and self.idx < other.idx)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    @property
    def idx(self):
        """Return an index for ordering comparison."""
        return (-1 if self.index is None else self.index)

    def iter_vars(self):
        yield self

    def invert(self):
        return comp(self)

    def restrict(self, d):
        return self.compose(d)

    def compose(self, d):
        try:
            return d[self]
        except KeyError:
            return self


class Complement(Literal):
    """Boolean complement"""

    # Postfix symbol used in string representation
    OP = "'"

    def __init__(self, var):
        self._var = var

    def __str__(self):
        return str(self._var) + self.OP

    def __lt__(self, other):
        if other in B:
            return False
        if isinstance(other, VariableEx):
            return (self.name < other.name or
                    self.name == other.name and self._var.idx <= other.idx)
        if isinstance(other, Complement):
            return (self.name < other.name or
                    self.name == other.name and self._var.idx < other.var.idx)
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

    def iter_vars(self):
        yield self._var

    def invert(self):
        return self._var

    def restrict(self, d):
        return self.compose(d)

    def compose(self, d):
        try:
            return Not(d[self._var])
        except KeyError:
            return self


class OrAnd(Expression):
    """base class for Boolean OR/AND expressions"""

    def __new__(cls, *args):
        temps, args = list(args), list()
        # x + (y + z) = (x + y) + z; x * (y * z) = (x * y) * z
        while temps:
            t = temps.pop()
            if t == cls.ABSORBER:
                return cls.ABSORBER
            elif isinstance(t, cls):
                temps.extend(t.args)
            elif t != cls.IDENTITY:
                args.append(t)

        if len(args) == 0:
            return cls.IDENTITY
        if len(args) == 1:
            return args[0]

        self = super(OrAnd, cls).__new__(cls)
        self.args = args
        return self

    def __iter__(self):
        return iter(self.args)

    def __len__(self):
        return len(self.args)

    def __lt__(self, other):
        if other in B:
            return False
        if isinstance(other, Literal):
            return self.support < other.support
        if isinstance(other, self.__class__) and self.depth == other.depth == 1:
            # min/max term
            if self.support == other.support:
                return self.index < other.index
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

    @cached_property
    def depth(self):
        return max(arg.depth + 1 for arg in self.args)

    @property
    def _duals(self):
        return [arg for arg in self.args if isinstance(arg, self.DUAL)]

    def iter_vars(self):
        for arg in self.args:
            for v in arg.iter_vars():
                yield v

    def invert(self):
        return self.DUAL(*[Not(arg) for arg in self.args])

    def restrict(self, d):
        return self.compose(d)

    def compose(self, d):
        replace = list()
        for arg in self.args:
            _arg = arg.compose(d)
            if id(arg) != id(_arg):
                replace.append((arg, _arg))
        if replace:
            args = self.args[:]
            for old, new in replace:
                if new == self.ABSORBER:
                    return self.ABSORBER
                else:
                    for i in range(args.count(old)):
                        args.remove(old)
                    if new != self.IDENTITY:
                        args.append(new)
            return self.__class__(*args)
        else:
            return self

    def factor(self):
        expr = self.__class__(*[arg.factor() for arg in self.args])
        return expr.simplify()

    def simplify(self):
        lits, terms, args = list(), list(), list()

        for arg in self.args:
            arg = arg.simplify()
            if isinstance(arg, Literal):
                lits.append(arg)
            elif isinstance(arg, self.DUAL) and arg.depth == 1:
                terms.append(arg)
            else:
                args.append(arg)

        # x + x' = 1; x * x' = 0
        while lits:
            lit = lits.pop()
            if -lit in lits:
                return self.ABSORBER
            else:
                terms.append(lit)

        # Drop all terms that are a subset of other terms
        # x + x = x; x * x = x
        # x + (x * y) = x; x * (x + y) = x
        while terms:
            fst, rst, terms = terms[0], terms[1:], list()
            drop_fst = False
            for term in rst:
                drop_term = False
                if fst.equal(term):
                    drop_term = True
                else:
                    if all(any(fx.equal(tx) for tx in term.args)
                           for fx in fst.args):
                        drop_term = True
                    if all(any(fx.equal(tx) for tx in fst.args)
                           for fx in term.args):
                        drop_fst = True
                if not drop_term:
                    terms.append(term)
            if not drop_fst:
                args.append(fst)

        return self.__class__(*args)

    def _flatten(self, op):
        if isinstance(self, op):
            if self._duals:
                dual = self._duals[0]
                others = [arg for arg in self.args if arg != dual]
                expr = op.DUAL(*[op(arg, *others) for arg in dual.args])
                if isinstance(expr, OrAnd):
                    return expr.flatten(op)
                else:
                    return expr
            else:
                return self
        else:
            nested, others = list(), list()
            for arg in self.args:
                if arg.depth > 1:
                    nested.append(arg)
                else:
                    others.append(arg)
            args = [arg.flatten(op) for arg in nested] + others
            return op.DUAL(*args)

    def equal(self, other):
        assert self.depth == 1
        return (isinstance(other, self.__class__) and self.support == other.support and
                self.index == other.index)


class Or(OrAnd):
    """Boolean addition (or) operator"""

    # Infix symbol used in string representation
    OP = "+"

    IDENTITY = 0
    ABSORBER = 1

    def __str__(self):
        sep = " " + self.OP + " "
        return sep.join(str(arg) for arg in sorted(self.args))

    @cached_property
    def index(self):
        n = abs(self) - 1
        idx = 0
        for i, v in enumerate(sorted(self.support)):
            if -v in self.args:
                idx |= 1 << (n - i)
        return idx


class And(OrAnd):
    """Boolean multiplication (and) operator"""

    # Infix symbol used in string representation
    OP = "*"

    IDENTITY = 1
    ABSORBER = 0

    def __str__(self):
        s = list()
        for arg in sorted(self.args):
            if isinstance(arg, Or):
                s.append("(" + str(arg) + ")")
            else:
                s.append(str(arg))
        sep = " " + self.OP + " "
        return sep.join(s)

    @cached_property
    def index(self):
        n = abs(self) - 1
        idx = 0
        for i, v in enumerate(sorted(self.support)):
            if v in self.args:
                idx |= 1 << (n - i)
        return idx


Or.DUAL = And
And.DUAL = Or


class BufNot(Expression):
    """base class for BUF/NOT operators"""

    def __init__(self, arg):
        self.arg = arg

    @property
    def depth(self):
        return self.arg.depth

    @property
    def args(self):
        return {self.arg}

    def iter_vars(self):
        for v in self.arg.iter_vars():
            yield v

    def restrict(self, d):
        expr = self.arg.restrict(d)
        if id(expr) == id(self.arg):
            return self
        else:
            return self.__class__(expr)

    def simplify(self):
        expr = self.arg.simplify()
        if id(expr) == id(self.arg):
            return self
        else:
            return self.__class__(expr)


class Buf(BufNot):
    """buffer operator"""

    def __new__(cls, arg):
        # Auto-simplify numbers and literals
        if arg in B or isinstance(arg, Literal):
            return arg
        else:
            return super(Buf, cls).__new__(cls)

    def __str__(self):
        return "Buf({0.arg})".format(self)

    def factor(self):
        return self.arg.factor()


class Not(BufNot):
    """Boolean NOT operator"""

    def __new__(cls, arg):
        # Auto-simplify numbers and literals
        if arg in B:
            return 1 - arg
        elif isinstance(arg, Literal):
            return arg.invert()
        else:
            return super(Not, cls).__new__(cls)

    def __str__(self):
        return "Not({0.arg})".format(self)

    def factor(self):
        return self.arg.invert().factor()


class Exclusive(Expression):
    """Boolean exclusive (XOR, XNOR) operator"""

    IDENTITY = 0

    def __new__(cls, *args):
        parity = cls.PARITY
        temps, args = list(args), list()
        while temps:
            t = temps.pop()
            if t == 1:
                parity ^= 1
            elif isinstance(t, cls):
                temps.extend(t.args)
            elif t != cls.IDENTITY:
                args.append(t)

        if len(args) == 0:
            return Not(cls.IDENTITY) if parity else cls.IDENTITY
        if len(args) == 1:
            return Not(args[0]) if parity else args[0]

        self = super(Exclusive, cls).__new__(cls)
        self.args = args
        self._parity = parity
        return self

    def __iter__(self):
        return iter(self.args)

    def __len__(self):
        return len(self.args)

    def __str__(self):
        args = ", ".join(str(arg) for arg in self.args)
        if self._parity:
            return "Xnor(" + args + ")"
        else:
            return "Xor(" + args + ")"

    @property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)

    def iter_vars(self):
        for arg in self.args:
            for v in arg.iter_vars():
                yield v

    def restrict(self, d):
        replace = list()
        for arg in self.args:
            _arg = arg.restrict(d)
            if id(arg) != id(_arg):
                replace.append((arg, _arg))
        if replace:
            args = self.args[:]
            parity = self._parity
            for old, new in replace:
                for i in range(args.count(old)):
                    args.remove(old)
                if new == 1:
                    parity ^= 1
                elif new != self.IDENTITY:
                    args.append(new)
            return Xnor(*args) if parity else Xor(*args)
        else:
            return self

    def factor(self):
        arg, args = self.args[0], self.args[1:]
        expr = Or(And(Not(arg), Xor(*args)), And(arg, Xnor(*args)))
        if self._parity:
            return Not(expr).factor()
        else:
            return expr.factor()

    def simplify(self):
        parity = self._parity

        lits, args = list(), list()
        for arg in self.args:
            arg = arg.simplify()
            if isinstance(arg, Literal):
                lits.append(arg)
            else:
                args.append(arg)

        while lits:
            arg = lits.pop()
            # XOR(x, x) = 0
            if arg in lits:
                lits.remove(arg)
            # XOR(x, x') = 1
            elif -arg in lits:
                lits.remove(-arg)
                parity ^= 1
            else:
                args.append(arg)

        return Xnor(*args) if parity else Xor(*args)


class Xor(Exclusive):
    PARITY = 0


class Xnor(Exclusive):
    PARITY = 1


class Implies(Expression):
    """Boolean implication operator"""

    OP = "->"

    def __new__(cls, x0, x1):
        args = [x0, x1]
        # 0 => x = 1; x => 1 = 1
        if args[0] == 0 or args[1] == 1:
            return 1
        # 1 => x = x
        elif args[0] == 1:
            return args[1]
        # x => 0 = x'
        elif args[1] == 0:
            return Not(args[0])
        else:
            self = super(Implies, cls).__new__(cls)
            self.args = args
            return self

    def __str__(self):
        s = list()
        for arg in self.args:
            if isinstance(arg, Implies):
                s.append("(" + str(arg) + ")")
            else:
                s.append(str(arg))
        sep = " " + self.OP + " "
        return sep.join(s)

    @property
    def depth(self):
        return max(arg.depth + 1 for arg in self.args)

    def iter_vars(self):
        for arg in self.args:
            for v in arg.iter_vars():
                yield v

    def factor(self):
        return Or(Not(self.args[0]), self.args[1]).factor()

    def simplify(self):
        args = [arg.simplify() for arg in self.args]

        # x => x = 1
        if args[0] == args[1]:
            return 1
        # -x => x = x; x => -x = -x
        elif -args[0] == args[1] or args[0] == -args[1]:
            return args[1]

        return Implies(args[0], args[1])


class VectorExpression(VF):
    """Vector Boolean function"""

    def __init__(self, *fs, **kwargs):
        self.fs = list(fs)
        self._start = kwargs.get("start", 0)
        self._bnr = kwargs.get("bnr", VF.UNSIGNED)

    def __str__(self):
        return str(self.fs)

    # Operators
    def uor(self):
        return Or(*list(self.fs))

    def uand(self):
        return And(*list(self.fs))

    def uxor(self):
        return Xor(*list(self.fs))

    def __invert__(self):
        fs = [Not(v) for v in self.fs]
        return VectorExpression(*fs, start=self._start, bnr=self._bnr)

    def __or__(self, other):
        assert isinstance(other, VectorExpression) and len(self) == len(other)
        return VectorExpression(*[Or(*t) for t in zip(self.fs, other.fs)])

    def __and__(self, other):
        assert isinstance(other, VectorExpression) and len(self) == len(other)
        return VectorExpression(*[And(*t) for t in zip(self.fs, other.fs)])

    def __xor__(self, other):
        assert isinstance(other, VectorExpression) and len(self) == len(other)
        return VectorExpression(*[Xor(*t) for t in zip(self.fs, other.fs)])

    def to_uint(self):
        """Convert vector to an unsigned integer."""
        n = 0
        for i, f in enumerate(self.fs):
            if type(f) is int:
                if f:
                    n += 2 ** i
            else:
                raise ValueError("cannot convert to uint")
        return n

    def to_int(self):
        """Convert vector to an integer."""
        n = self.to_uint()
        if self._bnr == VF.TWOS_COMPLEMENT and self.fs[-1]:
            return -2 ** self.__len__() + n
        else:
            return n

    def subs(self, d):
        """Substitute numbers into a Boolean vector."""
        cpy = self[:]
        for i, f in enumerate(cpy.fs):
            cpy[i] = cpy[i].restrict(d)
        return cpy

    def vsubs(self, d):
        """Expand all vectors before doing a substitution."""
        return self.subs(_expand_vectors(d))

    def ext(self, n):
        """Extend this vector by N bits.

        If this vector uses two's complement representation, sign extend;
        otherwise, zero extend.
        """
        if self.bnr == VF.TWOS_COMPLEMENT:
            bit = self.fs[-1]
        else:
            bit = 0
        for i in range(n):
            self.append(bit)

    #def eq(A, B):
    #    assert isinstance(B, Vector) and len(A) == len(B)
    #    return And(*[Xnor(*t) for t in zip(A.fs, B.fs)])

    #def decode(A):
    #    return Vector(*[And(*[f if bit_on(i, j) else -f
    #                          for j, f in enumerate(A.fs)])
    #                    for i in range(2 ** len(A))])

    def ripple_carry_add(A, B, ci=0):
        assert isinstance(B, VectorExpression) and len(A) == len(B)
        if A.bnr == VF.TWOS_COMPLEMENT or B.bnr == VF.TWOS_COMPLEMENT:
            sum_bnr = VF.TWOS_COMPLEMENT
        else:
            sum_bnr = VF.UNSIGNED
        S = VectorExpression(bnr=sum_bnr)
        C = VectorExpression()
        for i, A in enumerate(A.fs):
            carry = (ci if i == 0 else C[i-1])
            S.append(Xor(A, B.getifz(i), carry))
            C.append(A * B.getifz(i) + A * carry + B.getifz(i) * carry)
        return S, C


def _clog2(n):
    """Return the ceiling, log base two of an integer."""
    assert n >= 1
    i, x = 0, 1
    while x < n:
        x = x << 1;
        i += 1
    return i

def _expand_vectors(d):
    """Expand all vectors in a substitution dict."""
    temp = {k: v for k, v in d.items() if isinstance(k, VectorExpression)}
    d = {k: v for k, v in d.items() if k not in temp}
    while temp:
        key, val = temp.popitem()
        if isinstance(key, VectorExpression):
            assert len(key) == len(val)
            for i, x in enumerate(val):
                d[key.getifz(i)] = x
        elif isinstance(key, Literal):
            d[key] = val
    return d
