"""
Boolean Logic Expressions

Interface Functions:
    var
    comp

    factor

    Nor, Nand
    OneHot0, OneHot

    f_not
    f_or, f_nor
    f_and, f_nand
    f_xor, f_xnor
    f_implies
    f_equal

Interface Classes:
    Expression
        Literal
        OrAnd
            Or
            And
        Not
        Exclusive
            Xor
            Xnor
        Implies
        Equal
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from collections import deque

from pyeda.common import cached_property

from pyeda.boolfunc import Variable, Function
from pyeda.constant import boolify
from pyeda.sat import backtrack

VARIABLES = dict()
COMPLEMENTS = dict()

def var(name, *indices):
    """Return a single variable expression."""
    try:
        ret = VARIABLES[(name, indices)]
    except KeyError:
        ret = _Variable(name, *indices)
        VARIABLES[(name, indices)] = ret
    return ret

def comp(v):
    """Return a single complement expression."""
    try:
        ret = COMPLEMENTS[v]
    except KeyError:
        ret = Complement(v)
        COMPLEMENTS[v] = ret
    return ret

def factor(expr):
    """Return a factored expression."""
    return expr.factor()

# convenience functions
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

    >>> a, b, c = map(var, "abc")
    >>> OneHot0(0, 0, 0, 0), OneHot0(0, 0, 0, 1), OneHot0(0, 0, 1, 1)
    (1, 1, 0)
    >>> OneHot0(a, b, c)
    (a' + b') * (a' + c') * (b' + c')
    """
    nargs = len(args)
    return And(*[Or(Not(args[i]), Not(args[j]))
                 for i in range(nargs-1) for j in range(i+1, nargs)])

def OneHot(*args):
    """
    Return an expression that means:
        Exactly one input variable is true.

    >>> a, b, c = map(var, "abc")
    >>> OneHot(0, 0, 0, 0), OneHot(0, 0, 0, 1), OneHot(0, 0, 1, 1)
    (0, 1, 0)
    >>> OneHot(a, b, c)
    (a' + b') * (a' + c') * (b' + c') * (a + b + c)
    """
    return And(Or(*args), OneHot0(*args))

# factored operators
def f_not(arg):
    """Return factored NOT expression.

    >>> a, b, c, d = map(var, "abcd")
    >>> f_not(-a * b * -c * d), f_not(-a + b + -c + d)
    (a + b' + c + d', a * b' * c * d')
    """
    return Not(arg).factor()

def f_or(*args):
    """Return factored OR expression.

    >>> a, b, c, d = map(var, "abcd")
    >>> f_or(a >> b, c >> d)
    a' + b + c' + d
    """
    return Or(*args).factor()

def f_nor(*args):
    """Return factored NOR expression.

    >>> a, b, c, d = map(var, "abcd")
    >>> f_nor(-a, b, -c, d)
    a * b' * c * d'
    """
    return Nor(*args).factor()

def f_and(*args):
    """Return factored AND expression.

    >>> a, b, c, d = map(var, "abcd")
    >>> f_and(a >> b, c >> d)
    (a' + b) * (c' + d)
    """
    return And(*args).factor()

def f_nand(*args):
    """Return factored NAND expression.

    >>> a, b, c, d = map(var, "abcd")
    >>> f_nand(-a, b, -c, d)
    a + b' + c + d'
    """
    return Nand(*args).factor()

def f_xor(*args):
    """Return factored XOR expression.

    >>> a, b, c = map(var, "abc")
    >>> f_xor(a, b, c)
    a' * (b' * c + b * c') + a * (b' * c' + b * c)
    """
    return Xor(*args).factor()

def f_xnor(*args):
    """Return factored XNOR expression.

    >>> a, b, c = map(var, "abc")
    >>> f_xnor(a, b, c)
    a' * (b' * c' + b * c) + a * (b' * c + b * c')
    """
    return Xnor(*args).factor()

def f_implies(antecedent, consequence):
    """Return factored Implies expression.

    >>> a, b = map(var, "ab")
    >>> f_implies(a, b)
    a' + b
    """
    return Implies(antecedent, consequence).factor()

def f_equal(*args):
    """Return factored Equal expression.

    >>> a, b, c = map(var, "abc")
    >>> f_equal(a, b, c)
    a' * b' * c' + a * b * c
    """
    return Equal(*args).factor()


class Expression(Function):
    """Boolean function represented by a logic expression"""

    SOP, POS = range(2)

    # From Function
    @cached_property
    def support(self):
        s = set()
        for arg in self._args:
            s |= arg.support
        return s

    @cached_property
    def inputs(self):
        return sorted(self.support)

    def __neg__(self):
        return Not(self)

    def __add__(self, arg):
        return Or(self, arg)

    def __sub__(self, arg):
        return Or(self, Not(arg))

    def __mul__(self, arg):
        return And(self, arg)

    def __rshift__(self, arg):
        return Implies(self, arg)

    def __rrshift__(self, arg):
        return Implies(arg, self)

    def xor(self, *args):
        return Xor(self, *args)

    def equal(self, *args):
        return Equal(self, *args)

    def satisfy_one(self, algorithm='backtrack'):
        if algorithm == 'backtrack':
            return backtrack(self)
        else:
            raise ValueError("invalid algorithm")

    def satisfy_all(self):
        """Iterate through all satisfying input points.

        >>> a, b, c = map(var, "abc")
        >>> ans = [sorted(p.items()) for p in Xor(a, b, c).satisfy_all()]
        >>> ans[:2]
        [[(a, 0), (b, 0), (c, 1)], [(a, 0), (b, 1), (c, 0)]]
        >>> ans[2:]
        [[(a, 1), (b, 0), (c, 0)], [(a, 1), (b, 1), (c, 1)]]
        """
        for point in self.iter_ones():
            yield point

    def satisfy_count(self):
        return len(self.satisfy_all())

    def is_neg_unate(self, vs=None):
        if vs is None:
            vs = self.support
        elif isinstance(vs, Function):
            vs = [vs]
        for v in vs:
            fv0, fv1 = self.cofactors(v)
            if fv0 in {0, 1} or fv1 in {0, 1}:
                if not (fv0 == 1 or fv1 == 0):
                    return False
            elif not fv0.min_indices >= fv1.min_indices:
                return False
        return True

    def is_pos_unate(self, vs=None):
        if vs is None:
            vs = self.support
        elif isinstance(vs, Function):
            vs = [vs]
        for v in vs:
            fv0, fv1 = self.cofactors(v)
            if fv0 in {0, 1} or fv1 in {0, 1}:
                if not (fv1 == 1 or fv0 == 0):
                    return False
            elif not fv1.min_indices >= fv0.min_indices:
                return False
        return True

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
        """Return a printable representation."""
        return self.__str__()

    @property
    def args(self):
        """Return the expression argument list."""
        return self._args

    @property
    def depth(self):
        """Return the number of levels in the expression tree."""
        raise NotImplementedError()

    def invert(self):
        """Return an inverted expression."""
        raise NotImplementedError()

    def factor(self):
        """Return a factored expression.

        A factored expression is one and only one of the following:
        * A literal.
        * A sum / product of factored expressions.
        """
        raise NotImplementedError()

    def iter_minterms(self):
        """Iterate through the sum of products of N literals."""
        for point in self.iter_ones():
            space = [(v if val else -v) for v, val in point.items()]
            yield And(*space)

    @cached_property
    def minterms(self):
        """The sum of products of N literals"""
        return {term for term in self.iter_minterms()}

    def iter_maxterms(self):
        """Iterate through the product of sums of N literals."""
        for point in self.iter_zeros():
            space = [(-v if val else v) for v, val in point.items()]
            yield Or(*space)

    @cached_property
    def maxterms(self):
        """The product of sums of N literals"""
        return {term for term in self.iter_maxterms()}

    def is_sop(self):
        """Return whether this expression is a sum of products."""
        return False

    def to_sop(self):
        """Return the expression as a sum of products.

        >>> a, b, c = map(var, "abc")
        >>> Xor(a, b, c).to_sop()
        a' * b' * c + a' * b * c' + a * b' * c' + a * b * c
        >>> Xnor(a, b, c).to_sop()
        a' * b' * c' + a' * b * c + a * b' * c + a * b * c'
        """
        return self.factor()._flatten(And).absorb()

    def to_csop(self):
        """Return the expression as a sum of products of N literals.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).to_csop()
        a' * b * c + a * b' * c + a * b * c' + a * b * c
        """
        return Or(*[term for term in self.iter_minterms()])

    def is_pos(self):
        """Return whether this expression is a products of sums."""
        return False

    def to_pos(self):
        """Return the expression as a product of sums.

        >>> a, b, c = map(var, "abc")
        >>> Xor(a, b, c).to_pos()
        (a + b + c) * (a + b' + c') * (a' + b + c') * (a' + b' + c)
        >>> Xnor(a, b, c).to_pos()
        (a + b + c') * (a + b' + c) * (a' + b + c) * (a' + b' + c')
        """
        return self.factor()._flatten(Or).absorb()

    def to_cpos(self):
        """Return the expression as a product of sums of N literals.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).to_cpos()
        (a + b + c) * (a + b + c') * (a + b' + c) * (a' + b + c)
        """
        return And(*[term for term in self.iter_maxterms()])

    @cached_property
    def min_indices(self):
        """Return the minterm indices.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).min_indices
        set([3, 5, 6, 7])
        """
        return {term.minterm_index for term in self.iter_minterms()}

    @cached_property
    def max_indices(self):
        """Return the maxterm indices.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).max_indices
        set([0, 1, 2, 4])
        """
        return {term.maxterm_index for term in self.iter_maxterms()}

    def equivalent(self, other):
        """Return whether this expression is equivalent to another.

        NOTE: This algorithm uses exponential time and memory.
        """
        if self.support == other.support:
            return self.min_indices == other.min_indices
        else:
            return False

    # Convenience methods
    def _get_restrictions(self, mapping):
        restrictions = dict()
        for i, arg in enumerate(self._args):
            new_arg = arg.restrict(mapping)
            if id(new_arg) != id(arg):
                restrictions[i] = new_arg
        return restrictions

    def _get_compositions(self, mapping):
        compositions = dict()
        for i, arg in enumerate(self._args):
            new_arg = arg.compose(mapping)
            if id(new_arg) != id(arg):
                compositions[i] = new_arg
        return compositions

    def _subs(self, idx_arg):
        args = list(self._args)
        for i, arg in idx_arg.items():
            args[i] = arg
        return self.__class__(*args)


class Literal(Expression):
    """An instance of a variable or of its complement"""

    # From Expression
    @property
    def depth(self):
        """Return the number of levels in the expression tree.

        >>> a = var("a")
        >>> a.depth, (-a).depth
        (0, 0)
        """
        return 0

    def factor(self):
        return self

    def is_sop(self):
        return True

    def is_pos(self):
        return True


class _Variable(Variable, Literal):
    """Boolean variable (expression)"""

    def __init__(self, name, *indices):
        Variable.__init__(self, name, *indices)
        self._support = {self}
        self._args = (self, )

    # From Function
    @property
    def support(self):
        return self._support

    def restrict(self, mapping):
        try:
            return boolify(mapping[self])
        except KeyError:
            return self

    def compose(self, mapping):
        try:
            return mapping[self]
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, _Variable):
            return Variable.__lt__(self, other)
        if isinstance(other, Complement):
            return Variable.__lt__(self, other.var)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        return comp(self)

    # Specific to _Variable
    @property
    def minterm_index(self):
        return 1

    @property
    def maxterm_index(self):
        return 0


class Complement(Literal):
    """Boolean complement"""

    # Postfix symbol used in string representation
    OP = "'"

    def __init__(self, v):
        self._var = v
        self._support = {v}
        self._args = (self, )

    def __str__(self):
        return str(self._var) + self.OP

    # From Function
    @property
    def support(self):
        return self._support

    def restrict(self, mapping):
        return self.compose(mapping)

    def compose(self, mapping):
        try:
            return Not(mapping[self._var])
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, _Variable):
            return ( self.var.name < other.name or
                         self.var.name == other.name and
                         self._var.indices <= other.indices )
        if isinstance(other, Complement):
            return Variable.__lt__(self._var, other.var)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        return self._var

    # Specific to Complement
    @property
    def var(self):
        return self._var

    @property
    def minterm_index(self):
        return 0

    @property
    def maxterm_index(self):
        return 1


class OrAnd(Expression):
    """Base class for Boolean OR/AND expressions"""

    def __new__(cls, *args):
        temps, args = deque(args), list()
        while temps:
            arg = temps.popleft()
            if isinstance(arg, Expression):
                # associative
                if isinstance(arg, cls):
                    temps.extendleft(reversed(arg.args))
                # complement
                elif isinstance(arg, Literal) and -arg in args:
                    return cls.DOMINATOR
                # idempotent
                elif arg not in args:
                    args.append(arg)
            else:
                num = boolify(arg)
                # domination
                if num == cls.DOMINATOR:
                    return cls.DOMINATOR

        # Or() = 0; And() = 1
        if len(args) == 0:
            return cls.IDENTITY
        # Or(x) = x; And(x) = x
        if len(args) == 1:
            return args[0]

        self = super(OrAnd, cls).__new__(cls)
        self._args = tuple(args)
        return self

    # From Function
    def restrict(self, mapping):
        idx_arg = self._get_restrictions(mapping)
        if idx_arg:
            args = list(self._args)
            for i, arg in idx_arg.items():
                # speed hack
                if arg == self.DOMINATOR:
                    return self.DOMINATOR
                else:
                    args[i] = arg
            return self.__class__(*args)
        else:
            return self

    def compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    # From Expression
    def __lt__(self, other):
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

    @cached_property
    def depth(self):
        """Return the number of levels in the expression tree.

        >>> a, b, c, d = map(var, "abcd")
        >>> (a + b).depth, (a + (b * c)).depth, (a + (b * (c + d))).depth
        (1, 2, 3)
        >>> (a * b).depth, (a * (b + c)).depth, (a * (b + (c * d))).depth
        (1, 2, 3)
        """
        return max(arg.depth + 1 for arg in self._args)

    def invert(self):
        return self.DUAL(*[Not(arg) for arg in self._args])

    def factor(self):
        return self.__class__(*[arg.factor() for arg in self._args])

    # Specific to OrAnd
    def absorb(self):
        """Return the OR/AND expression after absorption.

        x + (x * y) = x
        x * (x + y) = x

        The reason this is not included as an automatic simplification is that
        it is too expensive to put into the constructor. We have to check
        whether each term is a subset of another term, which is N^3.
        """
        clauses, args = list(), list()
        for arg in self._args:
            if isinstance(arg, Literal) or arg.depth == 1:
                clauses.append(arg)
            else:
                args.append(arg)

        # Drop all clauses that are a subset of other clauses
        while clauses:
            fst, rst, clauses = clauses[0], clauses[1:], list()
            drop_fst = False
            for term in rst:
                drop_clause = False
                if fst.equivalent(term):
                    drop_clause = True
                else:
                    if all(any(farg.equivalent(targ) for targ in term.args)
                           for farg in fst.args):
                        drop_clause = True
                    if all(any(farg.equivalent(targ) for targ in fst.args)
                           for farg in term.args):
                        drop_fst = True
                if not drop_clause:
                    clauses.append(term)
            if not drop_fst:
                args.append(fst)

        return self.__class__(*args)

    def _flatten(self, op):
        """Return a flattened OR/AND expression.

        Use the distributive law to flatten all nested expressions:
        x + (y * z) = (x + y) * (x + z)
        x * (y + z) = (x * y) + (x * z)

        NOTE: This function assumes the expression is already factored. Do NOT
              call this method directly -- use the "to_sop" or "to_pos" methods
              instead.
        """
        if isinstance(self, op):
            for i, arg in enumerate(self._args):
                if isinstance(arg, self.DUAL):
                    others = self._args[:i] + self._args[i+1:]
                    expr = op.DUAL(*[op(a, *others) for a in arg.args])
                    if isinstance(expr, OrAnd):
                        return expr._flatten(op)
                    else:
                        return expr
            else:
                return self
        else:
            nested, others = list(), list()
            for arg in self._args:
                if arg.depth > 1:
                    nested.append(arg)
                else:
                    others.append(arg)
            args = [arg._flatten(op) for arg in nested] + others
            return op.DUAL(*args)


class Or(OrAnd):
    """Boolean OR operator

    >>> a, b, c, d = map(var, "abcd")

    >>> Or(), Or(a)
    (0, a)
    >>> a + 1, a + b + 1, a + 0
    (1, 1, a)
    >>> -a + a, -a + b + a
    (1, 1)

    test associativity

    >>> (a + b) + c + d
    a + b + c + d
    >>> a + (b + c) + d
    a + b + c + d
    >>> a + b + (c + d)
    a + b + c + d
    >>> (a + b) + (c + d)
    a + b + c + d
    >>> (a + b + c) + d
    a + b + c + d
    >>> a + (b + c + d)
    a + b + c + d
    >>> a + (b + (c + d))
    a + b + c + d
    >>> ((a + b) + c) + d
    a + b + c + d

    test idempotence

    >>> a + a, a + a + a, a + a + a + a, (a + a) + (a + a)
    (a, a, a, a)
    """

    # Infix symbol used in string representation
    OP = "+"

    IDENTITY = 0
    DOMINATOR = 1

    def __str__(self):
        sep = " " + self.OP + " "
        return sep.join(str(arg) for arg in sorted(self._args))

    def is_sop(self):
        """Return whether this expression is a sum of products.

        >>> a, b, c, d = map(var, "abcd")
        >>> (a + b + c).is_sop()
        True
        >>> (a + (b * c) + (c * d)).is_sop()
        True
        >>> ((a * b) + (b * (c + d))).is_sop()
        False
        """
        return ( self.depth <= 2 and
                 all(isinstance(arg, Literal) or isinstance(arg, self.DUAL)
                     for arg in self._args) )

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
            if -v in self._args:
                index |= 1 << (n - i)
        return index


class And(OrAnd):
    """Boolean AND operator

    >>> a, b, c, d = map(var, "abcd")

    >>> And(), And(a)
    (1, a)
    >>> a * 0, a * b * 0, a * 1
    (0, 0, a)
    >>> -a * a, -a * b * a
    (0, 0)

    test associativity

    >>> (a * b) * c * d
    a * b * c * d
    >>> a * (b * c) * d
    a * b * c * d
    >>> a * b * (c * d)
    a * b * c * d
    >>> (a * b) * (c * d)
    a * b * c * d
    >>> (a * b * c) * d
    a * b * c * d
    >>> a * (b * c * d)
    a * b * c * d
    >>> a * (b * (c * d))
    a * b * c * d
    >>> ((a * b) * c) * d
    a * b * c * d

    test idempotence

    >>> a * a, a * a * a, a * a * a * a, (a * a) + (a * a)
    (a, a, a, a)
    """

    # Infix symbol used in string representation
    OP = "*"

    IDENTITY = 1
    DOMINATOR = 0

    def __str__(self):
        s = list()
        for arg in sorted(self._args):
            if isinstance(arg, Or):
                s.append("(" + str(arg) + ")")
            else:
                s.append(str(arg))
        sep = " " + self.OP + " "
        return sep.join(s)

    def is_pos(self):
        """Return whether this expression is a products of sums.

        >>> a, b, c, d = map(var, "abcd")
        >>> (a * b * c).is_pos()
        True
        >>> (a * (b + c) * (c + d)).is_pos()
        True
        >>> ((a + b) * (b + c * d)).is_pos()
        False
        """
        return ( self.depth <= 2 and
                 all(isinstance(arg, Literal) or isinstance(arg, self.DUAL)
                     for arg in self._args) )

    # Specific to And
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
            if v in self._args:
                index |= 1 << (n - i)
        return index


Or.DUAL = And
And.DUAL = Or


class Not(Expression):
    """Boolean NOT operator

    >>> a = var("a")
    >>> Not(0), Not(1)
    (1, 0)
    >>> Not(-a), Not(a)
    (a, a')
    >>> -(-a), -(-(-a)), -(-(-(-a)))
    (a, a', a)
    >>> Not(a + -a), Not(a * -a)
    (0, 1)
    """
    def __new__(cls, arg):
        # Auto-simplify numbers and literals
        if isinstance(arg, Expression):
            if isinstance(arg, Literal):
                return arg.invert()
            else:
                self = super(Not, cls).__new__(cls)
                self._args = (arg, )
                return self
        else:
            return 1 - boolify(arg)

    def __str__(self):
        return "Not({0.arg})".format(self)

    # From Function
    def restrict(self, mapping):
        arg = self.arg.restrict(mapping)
        # speed hack
        if arg in {0, 1}:
            return 1 - arg
        elif id(arg) == id(self.arg):
            return self
        else:
            return self.__class__(arg)

    def compose(self, mapping):
        expr = self.arg.compose(mapping)
        if id(expr) == id(self.arg):
            return self
        else:
            return self.__class__(expr)

    # From Expression
    @cached_property
    def depth(self):
        return self.arg.depth

    def invert(self):
        return self.arg

    def factor(self):
        return self.arg.invert().factor()

    # Specific to Not
    @property
    def arg(self):
        return self._args[0]


class Exclusive(Expression):
    """Boolean exclusive (XOR, XNOR) operator"""

    def __new__(cls, *args):
        parity = cls.PARITY
        temps, args = deque(args), list()
        while temps:
            arg = temps.popleft()
            if isinstance(arg, Expression):
                # associative
                if isinstance(arg, cls):
                    temps.extendleft(reversed(arg.args))
                # XOR(x, x') = 1
                elif isinstance(arg, Literal) and -arg in args:
                    args.remove(-arg)
                    parity ^= 1
                # XOR(x, x) = 0
                elif arg in args:
                    args.remove(arg)
                else:
                    args.append(arg)
            else:
                parity ^= boolify(arg)

        # Xor() = 0; Xnor() = 1
        if len(args) == 0:
            return parity
        # Xor(x) = x; Xnor(x) = x'
        if len(args) == 1:
            return Not(args[0]) if parity else args[0]

        self = super(Exclusive, cls).__new__(cls)
        self._args = tuple(args)
        self._parity = parity
        return self

    def __str__(self):
        args = ", ".join(str(arg) for arg in self._args)
        if self._parity:
            return "Xnor(" + args + ")"
        else:
            return "Xor(" + args + ")"

    # From Function
    def restrict(self, mapping):
        idx_arg = self._get_restrictions(mapping)
        if idx_arg:
            args = list(self._args)
            for i, arg in idx_arg.items():
                args[i] = arg
            return Xnor(*args) if self._parity else Xor(*args)
        else:
            return self

    def compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        if idx_arg:
            args = self._args[:]
            for i, arg in idx_arg.items():
                args[i] = arg
            return Xnor(*args) if self._parity else Xor(*args)
        else:
            return self

    # From Expression
    @property
    def depth(self):
        """
        >>> a, b, c, d, e = map(var, "abcde")
        >>> Xor(a, b, c).depth
        2
        >>> Xor(a, b, c + d).depth
        3
        >>> Xor(a, b, c + Xor(d, e)).depth
        5
        """
        return max(arg.depth + 2 for arg in self._args)

    def invert(self):
        if self._parity == Xor.PARITY:
            return Xnor(*self._args)
        else:
            return Xor(*self._args)

    def factor(self):
        fst, rst = self._args[0], self._args[1:]
        if self._parity == Xor.PARITY:
            return Or(And(Not(fst).factor(), Xor(*rst).factor()),
                      And(fst.factor(), Xnor(*rst).factor()))
        else:
            return Or(And(Not(fst).factor(), Xnor(*rst).factor()),
                      And(fst.factor(), Xor(*rst).factor()))

class Xor(Exclusive):
    """Boolean Exclusive OR (XOR) operator

    >>> a, b, c = map(var, "abc")
    >>> Xor(), Xor(a)
    (0, a)
    >>> Xor(0, 0), Xor(0, 1), Xor(1, 0), Xor(1, 1)
    (0, 1, 1, 0)
    >>> Xor(a, a), Xor(a, -a)
    (0, 1)
    """
    PARITY = 0

class Xnor(Exclusive):
    """Boolean Exclusive NOR (XNOR) operator

    >>> a, b, c = map(var, "abc")
    >>> Xnor(), Xnor(a)
    (1, a')
    >>> Xnor(0, 0), Xnor(0, 1), Xnor(1, 0), Xnor(1, 1)
    (1, 0, 0, 1)
    >>> Xnor(a, a), Xnor(a, -a)
    (1, 0)
    """
    PARITY = 1


class Implies(Expression):
    """Boolean implication operator

    >>> a, b = map(var, "ab")
    >>> 0 >> a, 1 >> a, a >> 0, a >> 1
    (1, a, a', 1)
    >>> a >> a, a >> -a, -a >> a
    (1, a', a)
    >>> (a >> b).factor()
    a' + b
    """

    OP = "=>"

    def __new__(cls, antecedent, consequence):
        args = [arg if isinstance(arg, Expression) else boolify(arg)
                for arg in (antecedent, consequence)]
        # 0 => x = 1; x => 1 = 1
        if args[0] == 0 or args[1] == 1:
            return 1
        # 1 => x = x
        elif args[0] == 1:
            return args[1]
        # x => 0 = x'
        elif args[1] == 0:
            return Not(args[0])
        elif isinstance(args[0], Literal):
            # x -> x = 1
            if args[0] == args[1]:
                return 1
            # -x -> x = x
            elif args[0] == -args[1]:
                return args[1]
        self = super(Implies, cls).__new__(cls)
        self._args = tuple(args)
        return self

    def __str__(self):
        s = list()
        for arg in self._args:
            if isinstance(arg, Literal):
                s.append(str(arg))
            else:
                s.append("(" + str(arg) + ")")
        sep = " " + self.OP + " "
        return sep.join(s)

    # From Function
    def restrict(self, mapping):
        idx_arg = self._get_restrictions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    def compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    # From Expression
    @property
    def depth(self):
        return max(arg.depth + 1 for arg in self._args)

    def invert(self):
        return And(self._args[0], Not(self._args[1]))

    def factor(self):
        return Or(Not(self._args[0]).factor(), self._args[1].factor())


class Equal(Expression):
    """Boolean EQUAL operator

    >>> a, b, c = map(var, "abc")
    >>> Equal(0, 0), Equal(0, 1), Equal(1, 0), Equal(1, 1)
    (1, 0, 0, 1)
    >>> Equal(0, a), Equal(a, 0), Equal(1, a), Equal(a, 1)
    (a', a', a, a)
    >>> Equal(a, a), Equal(a, -a)
    (1, 0)
    >>> Equal(a, b, c).invert().factor()
    (a + b + c) * (a' + b' + c')
    >>> Equal(a, b, c).factor()
    a' * b' * c' + a * b * c
    """

    OP = "="

    def __new__(cls, *args):
        args = deque(arg if isinstance(arg, Expression) else boolify(arg)
                     for arg in args)
        if 0 in args:
            # EQUAL(0, 1, ...) = 0
            if 1 in args:
                return 0
            # EQUAL(0, x0, x1, ...) = Nor(x0, x1, ...)
            else:
                return Not(Or(*args))
        # EQUAL(1, x0, x1, ...)
        if 1 in args:
            return And(*args)

        temps, args = args, list()
        while temps:
            arg = temps.popleft()
            # EQUAL(x, -x) = 0
            if isinstance(arg, Literal) and -arg in args:
                return 0
            # EQUAL(x, x, ...) = EQUAL(x, ...)
            elif arg not in args:
                args.append(arg)

        # EQUAL(x) = EQUAL() = 1
        if len(args) <= 1:
            return 1

        self = super(Equal, cls).__new__(cls)
        self._args = tuple(args)
        return self

    def __str__(self):
        s = list()
        for arg in self._args:
            if isinstance(arg, Literal):
                s.append(str(arg))
            else:
                s.append("(" + str(arg) + ")")
        sep = " " + self.OP + " "
        return sep.join(s)

    # From Function
    def restrict(self, mapping):
        idx_arg = self._get_restrictions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    def compose(self, mapping):
        idx_arg = self._get_compositions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    # From Expression
    @property
    def depth(self):
        return max(arg.depth + 2 for arg in self._args)

    def invert(self):
        return And(Or(*self._args), Not(And(*self._args)))

    def factor(self):
        return Or(And(*[Not(arg).factor() for arg in self._args]),
                  And(*[arg.factor() for arg in self._args]))
