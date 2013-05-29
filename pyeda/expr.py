"""
Boolean Logic Expressions

Interface Functions:
    exprvar
    var

    factor
    simplify

    Or, And, Not
    Xor, Xnor,
    Equal, Implies, ITE

    Nor, Nand
    OneHot0, OneHot

Interface Classes:
    Expression
        ExprLiteral
            ExprVariable
            ExprComplement
        ExprOrAnd
            ExprOr
            ExprAnd
        ExprNot

        ExprExclusive
            ExprXor
            ExprXnor
        ExprEqual
        ExprImplies
        ExprITE
"""

import weakref
from collections import Counter

from pyeda import boolfunc
from pyeda import sat
from pyeda.common import bit_on, parity, cached_property

B = {0, 1}

EXPRVARIABLES = dict()
EXPRCOMPLEMENTS = dict()


def exprify(arg):
    """Convert the input argument to an expression."""
    if arg == 0 or arg == '0':
        return EXPRZERO
    elif arg == 1 or arg == '1':
        return EXPRONE
    elif isinstance(arg, Expression):
        return arg
    else:
        raise ValueError("invalid argument: " + str(arg))

def constify(expr):
    """Convert constant expressions to integers."""
    if isinstance(expr, ExprConstant):
        return expr.VAL
    elif isinstance(expr, Expression):
        return expr
    else:
        raise ValueError("not an expression: " + str(expr))

def exprvar(name, indices=None, namespace=None):
    """Return an Expression variable.

    Parameters
    ----------

    name : str
        The variable's identifier string.
    indices : int or tuple[int], optional
        One or more integer suffixes for variables that are part of a
        multi-dimensional bit-vector, eg x[1], x[1][2][3]
    namespace : str or tuple[str], optional
        A container for a set of variables. Since a Variable instance is global,
        a namespace can be used for local scoping.
    """
    return ExprVariable(name, indices, namespace)

def var(name, indices=None, namespace=None):
    """Return a variable expression.

    Parameters
    ----------

    name : str
        The variable's identifier string.
    indices : int or tuple[int], optional
        One or more integer suffixes for variables that are part of a
        multi-dimensional bit-vector, eg x[1], x[1][2][3]
    namespace : str or tuple[str], optional
        A container for a set of variables. Since a Variable instance is global,
        a namespace can be used for local scoping.
    """
    return ExprVariable(name, indices, namespace)

def simplify(arg):
    """Return a simplified expression.

    Parameters
    ----------
    arg : {0, 1} or str or Expression
    """
    return exprify(arg).simplify()

def factor(arg, conj=False):
    """Return a factored expression.

    Parameters
    ----------

    arg : {0, 1} or str or Expression
    conj : bool
        Always choose a conjunctive form when there's a choice
    """
    return exprify(arg).factor(conj)

# convenience functions
def Or(*args, **kwargs):
    args = tuple(exprify(arg) for arg in args)
    expr = ExprOr(*args, **kwargs)
    return constify(expr)

def And(*args, **kwargs):
    args = tuple(exprify(arg) for arg in args)
    expr = ExprAnd(*args, **kwargs)
    return constify(expr)

def Not(arg, simplify=True):
    arg = exprify(arg)
    expr = ExprNot(arg, simplify)
    return constify(expr)

def Xor(*args, **kwargs):
    args = tuple(exprify(arg) for arg in args)
    expr = ExprXor(*args, **kwargs)
    return constify(expr)

def Xnor(*args, **kwargs):
    args = tuple(exprify(arg) for arg in args)
    expr = ExprXnor(*args, **kwargs)
    return constify(expr)

def Equal(*args, **kwargs):
    args = tuple(exprify(arg) for arg in args)
    expr = ExprEqual(*args, **kwargs)
    return constify(expr)

def Implies(p, q, simplify=True):
    p = exprify(p)
    q = exprify(q)
    expr = ExprImplies(p, q, simplify)
    return constify(expr)

def ITE(s, a, b, simplify=True):
    s = exprify(s)
    a = exprify(a)
    b = exprify(b)
    expr = ExprITE(s, a, b, simplify)
    return constify(expr)

def Nor(*args):
    """Alias for Not Or"""
    return Not(Or(*args))

def Nand(*args):
    """Alias for Not And"""
    return Not(And(*args))

def OneHot0(*args):
    """
    Return an expression that means:
        At most one input variable is true.
    """
    nargs = len(args)
    return And(*[Or(Not(args[i]), Not(args[j]))
                 for i in range(nargs-1) for j in range(i+1, nargs)])

def OneHot(*args):
    """
    Return an expression that means:
        Exactly one input variable is true.
    """
    return And(Or(*args), OneHot0(*args))


class Expression(boolfunc.Function):
    """Boolean function represented by a logic expression"""

    def __new__(cls):
        self = super(Expression, cls).__new__(cls)
        self._RESTRICT_CACHE = weakref.WeakValueDictionary()
        return self

    # Operators
    def __neg__(self):
        return Not(self)

    def __add__(self, other):
        return Or(self, other)

    def __sub__(self, other):
        return Or(self, Not(other))

    def __mul__(self, other):
        return And(self, other)

    def xor(self, *args):
        """Boolean XOR (odd parity)

        +---+---+----------+
        | f | g | XOR(f,g) |
        +---+---+----------+
        | 0 | 0 |     0    |
        | 0 | 1 |     1    |
        | 1 | 0 |     1    |
        | 1 | 1 |     0    |
        +---+---+----------+
        """
        return Xor(self, *args)

    def equal(self, *args):
        """Boolean equality

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
        return Equal(self, *args)

    def __rshift__(self, other):
        """Boolean implication

        +---+---+--------+
        | f | g | f -> g |
        +---+---+--------+
        | 0 | 0 |    1   |
        | 0 | 1 |    1   |
        | 1 | 0 |    0   |
        | 1 | 1 |    1   |
        +---+---+--------+
        """
        return Implies(self, other)

    def __rrshift__(self, other):
        """Reverse Boolean implication

        +---+---+--------+
        | f | g | f <- g |
        +---+---+--------+
        | 0 | 0 |    1   |
        | 0 | 1 |    0   |
        | 1 | 0 |    1   |
        | 1 | 1 |    1   |
        +---+---+--------+
        """
        return Implies(other, self)

    def ite(self, a, b):
        """If-then-else operator"""
        return ITE(self, a, b)

    # From Function
    @cached_property
    def support(self):
        return frozenset.union(*[arg.support for arg in self.args])

    @cached_property
    def inputs(self):
        return tuple(sorted(self.support))

    def iter_zeros(self):
        top, rest = self.inputs[0], self.inputs[1:]
        for p, cf in self._iter_cofactors(top):
            if cf is EXPRZERO:
                for point in boolfunc.iter_points(rest):
                    point[top] = p[top]
                    yield point
            elif cf is not EXPRONE:
                for point in cf.iter_zeros():
                    point[top] = p[top]
                    yield point

    def iter_ones(self):
        rest, top = self.inputs[:-1], self.inputs[-1]
        for p, cf in self._iter_cofactors(top):
            if cf is EXPRONE:
                for point in boolfunc.iter_points(rest):
                    point[top] = p[top]
                    yield point
            elif cf is not EXPRZERO:
                for point in cf.iter_ones():
                    point[top] = p[top]
                    yield point

    def reduce(self, conj=False):
        if conj:
            return self.to_ccnf()
        else:
            return self.to_cdnf()

    def _restrict(self, point):
        upoint = boolfunc.point2upoint(point)
        return self._urestrict1(upoint)

    def urestrict(self, upoint):
        return constify(self._urestrict1(upoint))

    def _urestrict1(self, upoint):
        try:
            ret = self._RESTRICT_CACHE[upoint]
        except KeyError:
            ret = self._RESTRICT_CACHE[upoint] = self._urestrict2(upoint)
        return ret

    def _urestrict2(self, upoint):
        idx_arg = self._get_restrictions(upoint)
        return self._subs(idx_arg) if idx_arg else self

    def compose(self, mapping):
        return constify(self._compose(mapping))

    def _compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    def satisfy_one(self, algorithm='backtrack'):
        if algorithm == 'backtrack':
            return sat.backtrack(self)
        elif algorithm == 'dpll':
            if self.is_cnf():
                return sat.dpll(self)
            else:
                raise TypeError("expression is not a CNF")
        else:
            raise ValueError("invalid algorithm")

    def satisfy_all(self):
        for point in self.iter_ones():
            yield point

    def satisfy_count(self):
        return sum(1 for _ in self.satisfy_all())

    def iter_cofactors(self, vs=None):
        for point, expr in self._iter_cofactors(vs):
            yield point, constify(expr)

    def _iter_cofactors(self, vs=None):
        if vs is None:
            vs = list()
        elif isinstance(vs, ExprVariable):
            vs = [vs]
        for point in boolfunc.iter_points(vs):
            yield point, self._restrict(point)

    def is_neg_unate(self, vs=None):
        raise NotImplementedError()

    def is_pos_unate(self, vs=None):
        raise NotImplementedError()

    def smoothing(self, vs=None):
        return Or(*self.cofactors(vs))

    def consensus(self, vs=None):
        return And(*self.cofactors(vs))

    def derivative(self, vs=None):
        return Xor(*self.cofactors(vs))

    # Specific to Expression
    def __lt__(self, other):
        """Implementing this function makes expressions sortable."""
        return id(self) < id(other)

    def __repr__(self):
        return self.__str__()

    def _invert(self):
        """Return an inverted expression."""
        raise NotImplementedError()

    def simplify(self):
        """Return a simplified expression."""
        ret = self._simplify()
        return constify(ret)

    def _simplify(self):
        if self._simplified:
            return self
        else:
            return self._init1(*self.args)

    def factor(self, conj=False):
        """Return a factored expression.

        A factored expression is one and only one of the following:
        * A literal.
        * A disjunction / conjunction of factored expressions.

        Parameters
        ----------

        conj : bool
            Always choose a conjunctive form when there's a choice
        """
        ret = self._simplify()
        ret = self._factor(conj)
        return constify(ret)

    def _factor(self, conj=False):
        raise NotImplementedError()

    @property
    def depth(self):
        """Return the number of levels in the expression tree."""
        raise NotImplementedError()

    def expand(self, vs=None, conj=False):
        """Return the Shannon expansion with respect to a list of variables."""
        if vs is None:
            vs = list()
        elif isinstance(vs, ExprVariable):
            vs = [vs]
        if vs:
            outer, inner = (ExprAnd, ExprOr) if conj else (ExprOr, ExprAnd)
            terms = [inner(self, *term) for term in boolfunc.iter_terms(vs, conj)]
            return outer(*terms)
        else:
            return self

    def iter_minterms(self):
        """Iterate through the sum of products of N literals."""
        for point in self.iter_ones():
            space = [(v if val else -v) for v, val in point.items()]
            yield ExprAnd(*space)

    def iter_maxterms(self):
        """Iterate through the product of sums of N literals."""
        for point in self.iter_zeros():
            space = [(-v if val else v) for v, val in point.items()]
            yield ExprOr(*space)

    def is_dnf(self):
        """Return whether this expression is in disjunctive normal form."""
        return False

    def to_dnf(self):
        """Return the expression in disjunctive normal form."""
        f = self._factor()
        f = f._flatten(ExprAnd)
        f = f.absorb()
        return f

    def to_cdnf(self):
        """Return the expression in canonical disjunctive normal form."""
        return Or(*[term for term in self.iter_minterms()])

    def is_cnf(self):
        """Return whether this expression is in conjunctive normal form."""
        return False

    def to_cnf(self):
        """Return the expression in conjunctive normal form."""
        f = self._factor()
        f = f._flatten(ExprOr)
        f = f.absorb()
        return f

    def to_ccnf(self):
        """Return the expression in canonical conjunctive normal form."""
        return And(*[term for term in self.iter_maxterms()])

    @cached_property
    def min_indices(self):
        """Return the minterm indices."""
        return {term.minterm_index for term in self.iter_minterms()}

    @cached_property
    def max_indices(self):
        """Return the maxterm indices."""
        return {term.maxterm_index for term in self.iter_maxterms()}

    def equivalent(self, other, algorithm='backtrack'):
        """Return whether this expression is equivalent to another."""
        other = exprify(other)

        f = ExprAnd(ExprOr(ExprNot(self), ExprNot(other)), ExprOr(self, other))
        if isinstance(f, ExprConstant):
            return not f.__bool__()
        if algorithm == 'backtrack':
            return f.satisfy_one(algorithm='backtrack') is None
        elif algorithm == 'dpll':
            return f.to_cnf().satisfy_one(algorithm='dpll') is None
        else:
            raise ValueError("invalid algorithm")

    # Helper methods
    def _get_restrictions(self, upoint):
        restrictions = dict()
        for i, arg in enumerate(self.args):
            new_arg = arg._urestrict2(upoint)
            if id(new_arg) != id(arg):
                restrictions[i] = new_arg
        return restrictions

    def _get_compositions(self, mapping):
        compositions = dict()
        for i, arg in enumerate(self.args):
            new_arg = arg._compose(mapping)
            if id(new_arg) != id(arg):
                compositions[i] = new_arg
        return compositions

    def _subs(self, idx_arg):
        args = list(self.args)
        for i, arg in idx_arg.items():
            args[i] = arg
        return self._init1(*args)


class ExprConstant(Expression):
    """Boolean Constant"""
    def __new__(cls):
        return super(ExprConstant, cls).__new__(cls)

    def __bool__(self):
        return bool(self.VAL)

    def __int__(self):
        return self.VAL

    def __str__(self):
        return str(self.VAL)

    # From Function
    @cached_property
    def support(self):
        return frozenset()

    def _urestrict2(self, upoint):
        return self

    def _compose(self, mapping):
        return self

    # From Expression
    def _simplify(self):
        return self

    def _factor(self, conj=False):
        return self

    @property
    def depth(self):
        return 0

    def _flatten(self, op):
        return self


class _ExprZero(ExprConstant):
    VAL = 0

    def __lt__(self, other):
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def _invert(self):
        return EXPRONE


class _ExprOne(ExprConstant):
    VAL = 1

    def __lt__(self, other):
        if other is EXPRZERO:
            return False
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def _invert(self):
        return EXPRZERO


EXPRZERO = _ExprZero()
EXPRONE = _ExprOne()


class ExprLiteral(Expression):
    """An instance of a variable or of its complement"""

    # From Expression
    def _simplify(self):
        return self

    def _factor(self, conj=False):
        return self

    @property
    def depth(self):
        return 0

    def is_dnf(self):
        return True

    def is_cnf(self):
        return True

    def _flatten(self, op):
        return self


class ExprVariable(boolfunc.Variable, ExprLiteral):
    """Boolean expression variable"""

    def __new__(cls, name, indices=None, namespace=None):
        _var = boolfunc.Variable(name, indices, namespace)
        try:
            self = EXPRVARIABLES[_var.uniqid]
        except KeyError:
            self = ExprLiteral.__new__(cls)
            self.args = (self, )
            self.arg_set = {self, }
            self._var = _var
            EXPRVARIABLES[_var.uniqid] = self
        return self

    # From Function
    @cached_property
    def support(self):
        return frozenset([self, ])

    def _urestrict2(self, upoint):
        if self.uniqid in upoint[0]:
            return EXPRZERO
        elif self.uniqid in upoint[1]:
            return EXPRONE
        else:
            return self

    def _compose(self, mapping):
        try:
            return mapping[self]
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, ExprConstant):
            return False
        if isinstance(other, ExprVariable):
            return self._var < other.var
        if isinstance(other, ExprComplement):
            return self._var < other.exprvar.var
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def _invert(self):
        return ExprComplement(self)

    # DPLL IF
    def bcp(self):
        return 1, {self: 1}

    def ple(self):
        return 1, {self: 1}

    # From Variable
    @property
    def uniqid(self):
        return self._var.uniqid

    @property
    def namespace(self):
        return self._var.namespace

    @property
    def name(self):
        return self._var.name

    @property
    def indices(self):
        return self._var.indices

    # Specific to ExprVariable
    @property
    def var(self):
        return self._var

    @property
    def minterm_index(self):
        return 1

    @property
    def maxterm_index(self):
        return 0


class ExprComplement(ExprLiteral):
    """Boolean complement"""

    def __new__(cls, exprvar):
        uniqid = -exprvar.uniqid
        try:
            self = EXPRCOMPLEMENTS[uniqid]
        except KeyError:
            self = super(ExprComplement, cls).__new__(cls)
            self.args = (self, )
            self.arg_set = {self, }
            self.uniqid = uniqid
            self._exprvar = exprvar
            EXPRCOMPLEMENTS[-exprvar.uniqid] = self
        return self

    def __str__(self):
        return str(self._exprvar) + "'"

    # From Function
    @cached_property
    def support(self):
        return frozenset([self._exprvar, ])

    def _urestrict2(self, upoint):
        if self._exprvar.uniqid in upoint[0]:
            return EXPRONE
        elif self._exprvar.uniqid in upoint[1]:
            return EXPRZERO
        else:
            return self

    def _compose(self, mapping):
        try:
            return ExprNot(mapping[self.exprvar])
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, ExprConstant):
            return False
        if isinstance(other, ExprVariable):
            return ( self._exprvar.name < other.name or
                     self._exprvar.name == other.name and
                     self._exprvar.indices <= other.indices )
        if isinstance(other, ExprComplement):
            return self._exprvar.var < other.exprvar.var
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def _invert(self):
        return self._exprvar

    # DPLL IF
    def bcp(self):
        return 1, {self._exprvar: 0}

    def ple(self):
        return 1, {self._exprvar: 0}

    # Specific to ExprComplement
    @property
    def exprvar(self):
        return self._exprvar

    @property
    def minterm_index(self):
        return 0

    @property
    def maxterm_index(self):
        return 1


class ExprOrAnd(Expression):
    """Base class for Boolean OR/AND expressions"""

    def __new__(cls, *args, **kwargs):
        simplify = kwargs.get('simplify', True)
        if simplify:
            self = cls._init1(*args)
        else:
            self = cls._init0(*args)
        return self

    @classmethod
    def _init0(cls, *args, **kwargs):
        obj = super(ExprOrAnd, cls).__new__(cls)
        obj.args = args
        obj.arg_set = frozenset(args)
        obj._simplified = kwargs.get('simplified', False)
        return obj

    @classmethod
    def _init1(cls, *args):
        temps, args = list(args), set()

        while temps:
            arg = temps.pop()
            arg = arg._simplify()
            if arg is cls.DOMINATOR:
                return arg
            elif arg is cls.IDENTITY:
                pass
            # associative
            elif isinstance(arg, cls):
                temps.extend(arg.args)
            # complement
            elif isinstance(arg, ExprLiteral) and -arg in args:
                return cls.DOMINATOR
            else:
                args.add(arg)

        # Or() = 0; And() = 1
        if len(args) == 0:
            return cls.IDENTITY
        # Or(x) = x; And(x) = x
        if len(args) == 1:
            return args.pop()

        args = tuple(args)
        return cls._init0(*args, simplified=True)

    # From Function
    def _urestrict2(self, upoint):
        idx_arg = self._get_restrictions(upoint)
        if idx_arg:
            args = list(self.args)
            for i, arg in idx_arg.items():
                # speed hack
                if arg == self.DOMINATOR:
                    return self.DOMINATOR
                else:
                    args[i] = arg
            else:
                return self._init1(*args)
        else:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, ExprConstant):
            return False
        if isinstance(other, ExprLiteral):
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

    def _invert(self):
        args = [arg._invert() for arg in self.args]
        return self.DUAL(*args, simplify=self._simplified)

    def _factor(self, conj=False):
        args = [arg._factor(conj) for arg in self.args]
        return self._init1(*args)

    @cached_property
    def depth(self):
        return max(arg.depth + 1 for arg in self.args)

    # Specific to ExprOrAnd
    def is_nf(self):
        """Return whether this expression is in normal form."""
        return (
            self.depth <= 2 and
            all(isinstance(arg, ExprLiteral) or isinstance(arg, self.DUAL)
                for arg in self.args)
        )

    def absorb(self):
        """Return the OR/AND expression after absorption.

        x + (x * y) = x
        x * (x + y) = x

        The reason this is not included as an automatic simplification is that
        it is too expensive to put into the constructor. We have to check
        whether each term is a subset of another term, which is N^3.
        """
        if not self.is_nf():
            raise TypeError("expression is not in normal form")

        temps, args = list(self.args), list()

        # Drop all terms that are a subset of other terms
        while temps:
            fst, rst, temps = temps[0], temps[1:], list()
            drop_fst = False
            for term in rst:
                drop_term = False
                if fst.arg_set <= term.arg_set:
                    drop_term = True
                elif fst.arg_set > term.arg_set:
                    drop_fst = True
                if not drop_term:
                    temps.append(term)
            if not drop_fst:
                args.append(fst)

        return self._init1(*args)

    def _flatten(self, op):
        """Return a flattened OR/AND expression.

        Use the distributive law to flatten all nested expressions:
        x + (y * z) = (x + y) * (x + z)
        x * (y + z) = (x * y) + (x * z)

        NOTE: This function assumes the expression is already factored. Do NOT
              call this method directly -- use the 'to_dnf' or 'to_cnf' methods
              instead.
        """
        if isinstance(self, op):
            for i, arg in enumerate(self.args):
                if isinstance(arg, self.DUAL):
                    others = self.args[:i] + self.args[i+1:]
                    args = [op(a, *others) for a in arg.args]
                    expr = op.DUAL(*args)
                    return expr._flatten(op)
            else:
                return self
        else:
            nested, others = list(), list()
            for arg in self.args:
                if arg.depth > 1:
                    nested.append(arg)
                else:
                    others.append(arg)
            args = [arg._flatten(op) for arg in nested] + others
            return op.DUAL(*args)


class ExprOr(ExprOrAnd):
    """Boolean OR operator"""

    # Infix symbol used in string representation
    IDENTITY = EXPRZERO
    DOMINATOR = EXPRONE

    def __str__(self):
        return " + ".join(str(arg) for arg in sorted(self.args))

    def is_dnf(self):
        """Return whether this expression is in disjunctive normal form."""
        return self.is_nf()

    # Specific to Or
    @property
    def term_index(self):
        return self.maxterm_index

    @cached_property
    def maxterm_index(self):
        if self.depth > 1:
            return None
        n = self.degree - 1
        index = 0
        for i, v in enumerate(self.inputs):
            if -v in self.args:
                index |= 1 << (n - i)
        return index


class ExprAnd(ExprOrAnd):
    """Boolean AND operator"""

    # Infix symbol used in string representation
    IDENTITY = EXPRONE
    DOMINATOR = EXPRZERO

    def __str__(self):
        args = sorted(self.args)
        parts = list()
        for arg in args:
            if isinstance(arg, ExprOr):
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        return " * ".join(parts)

    def is_cnf(self):
        """Return whether this expression is in conjunctive normal form."""
        return self.is_nf()

    # DPLL IF
    def bcp(self):
        """Boolean Constraint Propagation"""
        assert self.is_nf()
        return _bcp(self)

    def ple(self):
        """Pure Literal Elimination"""
        assert self.is_nf()

        cntr = Counter()
        for clause in self.args:
            cntr.update(clause.args)

        point = dict()
        while cntr:
            lit, cnt = cntr.popitem()
            if -lit in cntr:
                cntr.pop(-lit)
            else:
                if isinstance(lit, ExprComplement):
                    point[lit.exprvar] = 0
                else:
                    point[lit] = 1
        if point:
            return self.restrict(point), point
        else:
            return self, {}

    # Specific to ExprAnd
    @property
    def term_index(self):
        return self.minterm_index

    @cached_property
    def minterm_index(self):
        if self.depth > 1:
            return None
        n = self.degree - 1
        index = 0
        for i, v in enumerate(self.inputs):
            if v in self.args:
                index |= 1 << (n - i)
        return index


ExprOr.DUAL = ExprAnd
ExprAnd.DUAL = ExprOr


class ExprNot(Expression):
    """Boolean NOT operator"""

    def __new__(cls, arg, simplify=True):
        if simplify:
            self = cls._init1(arg)
        else:
            self = cls._init0(arg)
        return self

    def __str__(self):
        return "Not(" + str(self.arg) + ")"

    @classmethod
    def _init0(cls, arg, simplified=False):
        obj = super(ExprNot, cls).__new__(cls)
        obj.arg = arg
        obj._simplified = simplified
        return obj

    @classmethod
    def _init1(cls, arg):
        arg = arg._simplify()
        if isinstance(arg, ExprConstant) or isinstance(arg, ExprLiteral):
            return arg._invert()
        else:
            return cls._init0(arg, simplified=True)

    # From Function
    @property
    def support(self):
        return self.arg.support

    def _urestrict2(self, upoint):
        new_arg = self.arg._urestrict2(upoint)
        if id(new_arg) != id(self.arg):
            return self._init1(new_arg)
        else:
            return self

    def _compose(self, mapping):
        new_arg = self.arg._compose(mapping)
        if id(new_arg) != id(self.arg):
            return self._init1(new_arg)
        else:
            return self

    # From Expression
    def _invert(self):
        return self.arg

    def _simplify(self):
        if self._simplified:
            return self
        else:
            return self._init1(self.arg)

    def _factor(self, conj=False):
        return self.arg._invert()._factor(conj)

    @cached_property
    def depth(self):
        return self.arg.depth


class ExprExclusive(Expression):
    """Boolean exclusive (XOR, XNOR) operator"""

    def __new__(cls, *args, **kwargs):
        simplify = kwargs.get('simplify', True)
        if simplify:
            self = cls._init1(*args)
        else:
            self = cls._init0(*args)
        return self

    @classmethod
    def _init0(cls, *args, **kwargs):
        obj = super(ExprExclusive, cls).__new__(cls)
        obj.args = args
        obj._simplified = kwargs.get('simplified', False)
        return obj

    @classmethod
    def _init1(cls, *args):
        par = cls.PARITY
        temps, args = list(args), set()

        while temps:
            arg = temps.pop()
            arg = arg._simplify()
            if isinstance(arg, ExprConstant):
                par ^= arg.VAL
            # associative
            elif isinstance(arg, cls):
                temps.extend(arg.args)
            # Xor(x, x') = 1
            elif isinstance(arg, ExprLiteral) and -arg in args:
                args.remove(-arg)
                par ^= 1
            # Xor(x, x) = 0
            elif arg in args:
                args.remove(arg)
            else:
                args.add(arg)

        # Xor() = 0; Xnor() = 1
        if len(args) == 0:
            return { ExprXor.PARITY  : EXPRZERO,
                     ExprXnor.PARITY : EXPRONE }[par]
        # Xor(x) = x; Xnor(x) = x'
        if len(args) == 1:
            if par:
                return args.pop()
            else:
                return ExprNot(args.pop())

        xcls = { ExprXor.PARITY  : ExprXor,
                 ExprXnor.PARITY : ExprXnor }[par]
        return xcls._init0(*args, simplified=True)

    # From Expression
    def _invert(self):
        return self.DUAL(*self.args, simplify=self._simplified)

    def _factor(self, conj=False):
        outer, inner = (ExprAnd, ExprOr) if conj else (ExprOr, ExprAnd)
        terms = list()
        for n in range(1 << len(self.args)):
            if parity(n) == self.PARITY:
                term = list()
                for i, arg in enumerate(self.args):
                    if bit_on(n, i):
                        term.append(arg._factor(conj))
                    else:
                        term.append(arg._invert()._factor(conj))
                terms.append(inner(*term))
        return outer(*terms)

    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)


class ExprXor(ExprExclusive):
    """Boolean Exclusive OR (XOR) operator"""

    PARITY = 1

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in sorted(self.args))
        return "Xor(" + args_str + ")"


class ExprXnor(ExprExclusive):
    """Boolean Exclusive NOR (XNOR) operator"""

    PARITY = 0

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in sorted(self.args))
        return "Xnor(" + args_str + ")"


ExprXor.DUAL = ExprXnor
ExprXnor.DUAL = ExprXor


class ExprEqual(Expression):
    """Boolean EQUAL operator"""

    def __new__(cls, *args, **kwargs):
        simplify = kwargs.get('simplify', True)
        if simplify:
            self = cls._init1(*args)
        else:
            self = cls._init0(*args)
        return self

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in sorted(self.args))
        return "Equal(" + args_str + ")"

    @classmethod
    def _init0(cls, *args, **kwargs):
        obj = super(ExprEqual, cls).__new__(cls)
        obj.args = args
        obj._simplified = kwargs.get('simplified', False)
        return obj

    @classmethod
    def _init1(cls, *args):
        args = tuple(arg._simplify() for arg in args)

        if EXPRZERO in args:
            # Equal(0, 1, ...) = 0
            if EXPRONE in args:
                return EXPRZERO
            # Equal(0, x0, x1, ...) = Nor(x0, x1, ...)
            else:
                return ExprNot(ExprOr(*args))
        # Equal(1, x0, x1, ...)
        if EXPRONE in args:
            return ExprAnd(*args)

        # no constants; all simplified
        temps, args = list(args), set()
        while temps:
            arg = temps.pop()
            # Equal(x, -x) = 0
            if isinstance(arg, ExprLiteral) and -arg in args:
                return EXPRZERO
            # Equal(x, x, ...) = Equal(x, ...)
            elif arg not in args:
                args.add(arg)

        # Equal(x) = Equal() = 1
        if len(args) <= 1:
            return EXPRONE

        return cls._init0(*args, simplified=True)

    # From Expression
    def _invert(self):
        a = ExprOr(*self.args, simplify=self._simplified)
        b = ExprAnd(*self.args, simplify=self._simplified)._invert()
        return ExprAnd(a, b, simplify=self._simplified)

    def _factor(self, conj=False):
        if conj:
            args = list()
            for i, argi in enumerate(self.args):
                for j, argj in enumerate(self.args, start=i):
                    args.append(ExprOr(argi, argj._invert()._factor(conj)))
                    args.append(ExprOr(argi._invert()._factor(conj), argj))
            return ExprAnd(*args)
        else:
            all_zero = ExprAnd(*[arg._invert()._factor(conj) for arg in self.args])
            all_one = ExprAnd(*[arg._factor(conj) for arg in self.args])
            return ExprOr(all_zero, all_one)

    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)


class ExprImplies(Expression):
    """Boolean implication operator"""

    def __new__(cls, p, q, simplify=True):
        if simplify:
            self = cls._init1(p, q)
        else:
            self = cls._init0(p, q)
        return self

    def __str__(self):
        parts = list()
        for arg in self.args:
            if isinstance(arg, ExprConstant) or isinstance(arg, ExprLiteral):
                parts.append(str(arg))
            else:
                parts.append("(" + str(arg) + ")")
        return " => ".join(parts)

    @classmethod
    def _init0(cls, p, q, simplified=False):
        obj = super(ExprImplies, cls).__new__(cls)
        obj.args = (p, q)
        obj._simplified = simplified
        return obj

    @classmethod
    def _init1(cls, p, q):
        p = p._simplify()
        q = q._simplify()

        # 0 => q = 1; p => 1 = 1
        if p is EXPRZERO or q is EXPRONE:
            return EXPRONE
        # 1 => q = q
        elif p is EXPRONE:
            return q
        # p => 0 = p'
        elif q is EXPRZERO:
            return ExprNot(p)
        # p -> p = 1
        elif p == q:
            return EXPRONE
        # -p -> p = p
        elif isinstance(p, ExprLiteral) and -p == q:
            return q

        return cls._init0(p, q, simplified=True)

    # From Expression
    def _invert(self):
        p, q = self.args
        return ExprAnd(p, q._invert(), simplify=self._simplified)

    def _factor(self, conj=False):
        p, q = self.args
        return ExprOr(p._invert()._factor(conj), q._factor(conj))

    @cached_property
    def depth(self):
        return max(arg.depth + 1 for arg in self.args)


class ExprITE(Expression):
    """Boolean if-then-else ternary operator"""

    def __new__(cls, s, a, b, simplify=True):
        if simplify:
            self = cls._init1(s, a, b)
        else:
            self = cls._init0(s, a, b)
        return self

    def __str__(self):
        parts = list()
        for arg in self.args:
            if isinstance(arg, ExprConstant) or isinstance(arg, ExprLiteral):
                parts.append(str(arg))
            else:
                parts.append("(" + str(arg) + ")")
        return "{} ? {} : {}".format(*parts)

    @classmethod
    def _init0(cls, s, a, b, simplified=False):
        obj = super(ExprITE, cls).__new__(cls)
        obj.args = (s, a, b)
        obj._simplified = simplified
        return obj

    @classmethod
    def _init1(cls, s, a, b):
        s = s._simplify()
        a = a._simplify()
        b = b._simplify()

        # 0 ? a : b = b
        if s is EXPRZERO:
            return b
        # 1 ? a : b = a
        elif s is EXPRONE:
            return a
        elif a is EXPRZERO:
            # s ? 0 : 0 = 0
            if b is EXPRZERO:
                return EXPRZERO
            # s ? 0 : 1 = s'
            elif b is EXPRONE:
                return ExprNot(s)
            # s ? 0 : b = s' * b
            else:
                return ExprAnd(ExprNot(s), b)
        elif a is EXPRONE:
            # s ? 1 : 0 = s
            if b is EXPRZERO:
                return s
            # s ? 1 : 1 = 1
            elif b is EXPRONE:
                return EXPRONE
            # s ? 1 : b = s + b
            else:
                return ExprOr(s, b)
        # s ? a : 0 = s * a
        elif b is EXPRZERO:
            return ExprAnd(s, a)
        # s ? a : 1 = s' + a
        elif b is EXPRONE:
            return ExprOr(ExprNot(s), a)
        # s ? a : a = a
        elif a == b:
            return a

        return cls._init0(s, a, b, simplified=True)

    # From Expression
    def _invert(self):
        s, a, b = self.args
        return ExprITE(s, a._invert(), b._invert(), simplify=self._simplified)

    def _factor(self, conj=False):
        s, a, b = self.args
        return ExprOr(ExprAnd(s, a), ExprAnd(s._invert()._factor(conj), b))

    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)


def _bcp(cnf):
    """Boolean Constraint Propagation"""
    if cnf in B:
        return cnf, {}
    else:
        point = dict()
        for clause in cnf.args:
            if len(clause.args) == 1:
                lit = clause.args[0]
                if isinstance(lit, ExprComplement):
                    point[lit.exprvar] = 0
                else:
                    point[lit] = 1
        if point:
            _cnf, _point = _bcp(cnf.restrict(point))
            point.update(_point)
            return _cnf, point
        else:
            return cnf, point
