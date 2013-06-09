"""
Boolean Logic Expressions

Interface Functions:
    exprvar
    exprcomp
    upoint2exprpoint

    Or, And, Not
    Xor, Xnor,
    Equal, Implies, ITE

    Nor, Nand
    OneHot0, OneHot

Interface Classes:
    Expression
        ExprConstant
            EXPRZERO
            EXPRONE
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

# Disable "redefining name from outer scope"
# pylint: disable=W0621

from pyeda import boolfunc
from pyeda import sat
from pyeda.common import bit_on, parity, cached_property

EXPRVARIABLES = dict()
EXPRCOMPLEMENTS = dict()


def exprvar(name, indices=None, namespace=None):
    """Return an Expression Variable.

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
    bvar = boolfunc.var(name, indices, namespace)
    try:
        var = EXPRVARIABLES[bvar.uniqid]
    except KeyError:
        var = EXPRVARIABLES[bvar.uniqid] = ExprVariable(bvar)
    return var

def exprcomp(exprvar):
    """Return an Expression Complement."""
    uniqid = -exprvar.uniqid
    try:
        comp = EXPRCOMPLEMENTS[uniqid]
    except KeyError:
        comp = ExprComplement(exprvar)
        EXPRCOMPLEMENTS[uniqid] = comp
    return comp

def upoint2exprpoint(upoint):
    """Convert an untyped point to an Expression point."""
    point = dict()
    for uniqid in upoint[0]:
        point[EXPRVARIABLES[uniqid]] = 0
    for uniqid in upoint[1]:
        point[EXPRVARIABLES[uniqid]] = 1
    return point

# basic functions
def Or(*args, **kwargs):
    """Factory function for Boolean OR expression."""
    args = tuple(Expression.box(arg) for arg in args)
    simplify = kwargs.get('simplify', True)
    factor = kwargs.get('factor', False)
    conj = kwargs.get('conj', False)
    expr = ExprOr(*args)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def And(*args, **kwargs):
    """Factory function for Boolean AND expression."""
    args = tuple(Expression.box(arg) for arg in args)
    simplify = kwargs.get('simplify', True)
    factor = kwargs.get('factor', False)
    conj = kwargs.get('conj', False)
    expr = ExprAnd(*args)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def Not(arg, simplify=True, factor=False, conj=False):
    """Factory function for Boolean NOT expression."""
    arg = Expression.box(arg)
    expr = ExprNot(arg)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def Xor(*args, **kwargs):
    """Factory function for Boolean XOR expression."""
    args = tuple(Expression.box(arg) for arg in args)
    simplify = kwargs.get('simplify', True)
    factor = kwargs.get('factor', False)
    conj = kwargs.get('conj', False)
    expr = ExprXor(*args)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def Xnor(*args, **kwargs):
    """Factory function for Boolean XNOR expression."""
    args = tuple(Expression.box(arg) for arg in args)
    simplify = kwargs.get('simplify', True)
    factor = kwargs.get('factor', False)
    conj = kwargs.get('conj', False)
    expr = ExprXnor(*args, **kwargs)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

# higher order functions
def Equal(*args, **kwargs):
    """Factory function for Boolean EQUAL expression."""
    args = tuple(Expression.box(arg) for arg in args)
    simplify = kwargs.get('simplify', True)
    factor = kwargs.get('factor', False)
    conj = kwargs.get('conj', False)
    expr = ExprEqual(*args, **kwargs)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def Implies(p, q, simplify=True, factor=False, conj=False):
    """Factory function for Boolean implication expression."""
    p = Expression.box(p)
    q = Expression.box(q)
    expr = ExprImplies(p, q)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def ITE(s, d1, d0, simplify=True, factor=False, conj=False):
    """Factory function for Boolean If-Then-Else expression."""
    s = Expression.box(s)
    d1 = Expression.box(d1)
    d0 = Expression.box(d0)
    expr = ExprITE(s, d1, d0)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def Nor(*args, **kwargs):
    """Alias for Not Or"""
    return Not(Or(*args, **kwargs), **kwargs)

def Nand(*args, **kwargs):
    """Alias for Not And"""
    return Not(And(*args, **kwargs), **kwargs)

def OneHot0(*args, **kwargs):
    """
    Return an expression that means:
        At most one input variable is true.
    """
    nargs = len(args)
    terms = list()
    for i in range(nargs-1):
        for j in range(i+1, nargs):
            not_both = Or(Not(args[i], **kwargs),
                          Not(args[j], **kwargs), **kwargs)
            terms.append(not_both)
    return And(*terms, **kwargs)

def OneHot(*args, **kwargs):
    """
    Return an expression that means:
        Exactly one input variable is true.
    """
    return And(Or(*args, **kwargs), OneHot0(*args, **kwargs), **kwargs)


class Expression(boolfunc.Function):
    """Boolean function represented by a logic expression"""

    def __init__(self, args):
        self.args = args

    # Operators
    def __neg__(self):
        return Not(self)

    def __add__(self, other):
        return Or(self, other)

    def __sub__(self, other):
        return Or(self, Not(other))

    def __mul__(self, other):
        return And(self, other)

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

    def xor(self, other):
        return Xor(self, other)

    def ite(self, d1, d0):
        """If-then-else operator"""
        return ITE(self, d1, d0)

    # From Function
    @cached_property
    def support(self):
        return frozenset.union(*[arg.support for arg in self.args])

    @cached_property
    def inputs(self):
        return tuple(sorted(self.support))

    def urestrict(self, upoint):
        idx_arg = self._get_restrictions(upoint)
        return self._subs(idx_arg) if idx_arg else self

    def compose(self, mapping):
        """Implementation of compose always returns an Expression."""
        idx_arg = self._get_compositions(mapping)
        return self._subs(idx_arg) if idx_arg else self

    def satisfy_one(self, algorithm='backtrack'):
        if algorithm == 'backtrack':
            soln = sat.backtrack(self)
        elif algorithm == 'dpll':
            assert self is EXPRZERO or self is EXPRONE or self.is_cnf()
            soln = sat.dpll(self)
        else:
            raise ValueError("invalid algorithm: " + algorithm)
        if soln is None:
            return None
        else:
            return upoint2exprpoint(soln)

    def satisfy_all(self):
        for upoint in _iter_ones(self):
            yield upoint2exprpoint(upoint)

    def satisfy_count(self):
        return sum(1 for _ in self.satisfy_all())

    def is_neg_unate(self, vs=None):
        vs = self._expect_vars(vs)
        basis = self.support - set(vs)
        maxcov = set(range(1 << len(basis)))
        for cf in self.iter_cofactors(vs):
            if cf is EXPRZERO:
                idxs = set()
            elif cf is EXPRONE:
                idxs = set(range(1 << len(basis)))
            else:
                cdnf = cf.expand(basis - cf.support).to_cdnf()
                idxs = cdnf.min_indices
            if not idxs <= maxcov:
                return False
            maxcov = idxs
        return True

    def is_pos_unate(self, vs=None):
        vs = self._expect_vars(vs)
        basis = self.support - set(vs)
        mincov = set()
        for cf in self.iter_cofactors(vs):
            if cf is EXPRZERO:
                idxs = set()
            elif cf is EXPRONE:
                idxs = set(range(1 << len(basis)))
            else:
                cdnf = cf.expand(basis - cf.support).to_cdnf()
                idxs = cdnf.min_indices
            if not idxs >= mincov:
                return False
            mincov = idxs
        return True

    def smoothing(self, vs=None):
        return Or(*self.cofactors(vs))

    def consensus(self, vs=None):
        return And(*self.cofactors(vs))

    def derivative(self, vs=None):
        return Xor(*self.cofactors(vs))

    def is_zero(self):
        return False

    def is_one(self):
        return False

    @staticmethod
    def box(arg):
        if isinstance(arg, Expression):
            return arg
        elif arg == 0 or arg == '0':
            return EXPRZERO
        elif arg == 1 or arg == '1':
            return EXPRONE
        else:
            fstr = "argument cannot be converted to Expression: " + str(arg)
            raise TypeError(fstr)

    # Specific to Expression
    def __lt__(self, other):
        return id(self) < id(other)

    def __repr__(self):
        return self.__str__()

    def invert(self):
        """Return an inverted expression."""
        raise NotImplementedError()

    def simplify(self):
        """Return a simplified expression."""
        raise NotImplementedError()

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
        raise NotImplementedError()

    @property
    def depth(self):
        """Return the number of levels in the expression tree."""
        raise NotImplementedError()

    def expand(self, vs=None, conj=False):
        """Return the Shannon expansion with respect to a list of variables."""
        vs = self._expect_vars(vs)
        if vs:
            outer, inner = (ExprAnd, ExprOr) if conj else (ExprOr, ExprAnd)
            terms = [inner(self, *term)
                     for term in boolfunc.iter_terms(vs, conj)]
            return outer(*terms).simplify()
        else:
            return self

    def to_dnf(self):
        """Return the expression in disjunctive normal form."""
        return self.factor().flatten(ExprAnd)

    def to_cdnf(self):
        """Return the expression in canonical disjunctive normal form."""
        return self.to_dnf().reduce()

    def is_dnf(self):
        """Return whether this expression is in disjunctive normal form."""
        return False

    def to_cnf(self):
        """Return the expression in conjunctive normal form."""
        return self.factor().flatten(ExprOr)

    def to_ccnf(self):
        """Return the expression in canonical conjunctive normal form."""
        return self.to_cnf().reduce()

    def is_cnf(self):
        """Return whether this expression is in conjunctive normal form."""
        return False

    def equivalent(self, other, algorithm='backtrack'):
        """Return whether this expression is equivalent to another."""
        other = self.box(other)
        f = ExprAnd(ExprOr(ExprNot(self), ExprNot(other)), ExprOr(self, other))
        if algorithm == 'backtrack':
            return f.satisfy_one(algorithm='backtrack') is None
        elif algorithm == 'dpll':
            return f.to_cnf().satisfy_one(algorithm='dpll') is None
        else:
            raise ValueError("invalid algorithm: " + algorithm)

    # Helper methods
    def _get_restrictions(self, upoint):
        """Apply upoint restrictions and return a {index: expr} dict."""
        restrictions = dict()
        for i, arg in enumerate(self.args):
            new_arg = arg.urestrict(upoint)
            if id(new_arg) != id(arg):
                restrictions[i] = new_arg
        return restrictions

    def _get_compositions(self, mapping):
        """Apply mapping compositions and return a {index: expr} dict."""
        compositions = dict()
        for i, arg in enumerate(self.args):
            new_arg = arg.compose(mapping)
            if id(new_arg) != id(arg):
                compositions[i] = new_arg
        return compositions

    def _subs(self, idx_arg):
        """Substitute arguments, and return a simplified expression."""
        args = list(self.args)
        for i, arg in idx_arg.items():
            args[i] = arg
        return self.__class__(*args).simplify()


class ExprConstant(Expression, sat.DPLLInterface):
    """Expression constant"""

    def __init__(self):
        super(ExprConstant, self).__init__(None)

    # From Function
    @cached_property
    def support(self):
        return frozenset()

    def urestrict(self, upoint):
        return self

    def compose(self, mapping):
        return self

    # From Expression
    def invert(self):
        raise NotImplementedError()

    def simplify(self):
        return self

    def factor(self, conj=False):
        return self

    @property
    def depth(self):
        return 0

    # FactoredExpression
    def flatten(self, op):
        """Degenerate form of a flattened expression."""
        return self

    def absorb(self):
        """Degenerate form of a flattened expression."""
        return self


class _ExprZero(ExprConstant):
    """
    Expression zero

    .. NOTE:: Never use this class. Use EXPRZERO singleton instead.
    """
    def __bool__(self):
        return False

    def __int__(self):
        return 0

    def __str__(self):
        return '0'

    def __lt__(self, other):
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def is_zero(self):
        return True

    def invert(self):
        return EXPRONE

    # DPLL IF
    def bcp(self):
        return None

    def ple(self):
        return None


class _ExprOne(ExprConstant):
    """
    Expression one

    .. NOTE:: Never use this class. Use EXPRONE singleton instead.
    """
    def __bool__(self):
        return True

    def __int__(self):
        return 1

    def __str__(self):
        return '1'

    def __lt__(self, other):
        if other is EXPRZERO:
            return False
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def is_one(self):
        return True

    def invert(self):
        return EXPRZERO

    # DPLL IF
    def bcp(self):
        return frozenset(), frozenset()

    def ple(self):
        return frozenset(), frozenset()


EXPRZERO = _ExprZero()
EXPRONE = _ExprOne()


class ExprLiteral(Expression, sat.DPLLInterface):
    """An instance of a variable or of its complement"""

    def __init__(self):
        super(ExprLiteral, self).__init__(None)

    @cached_property
    def arg_set(self):
        """Return the argument set for a normal form term."""
        return frozenset([self])

    # From Expression
    def invert(self):
        raise NotImplementedError()

    def simplify(self):
        return self

    def factor(self, conj=False):
        return self

    @property
    def depth(self):
        return 0

    def is_dnf(self):
        return True

    def is_cnf(self):
        return True

    # FactoredExpression
    def flatten(self, op):
        """Degenerate form of a flattened expression."""
        return self

    def absorb(self):
        """Degenerate form of a flattened expression."""
        return self

    def reduce(self):
        """Degenerate form of a reduced expression."""
        return self

    @cached_property
    def min_indices(self):
        return {self.minterm_index}

    minterm_index = NotImplemented


class ExprVariable(boolfunc.Variable, ExprLiteral):
    """Expression variable"""

    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.namespace, bvar.name,
                                   bvar.indices)
        ExprLiteral.__init__(self)

    # From Function
    @cached_property
    def support(self):
        return frozenset([self, ])

    def urestrict(self, upoint):
        if self.uniqid in upoint[0]:
            return EXPRZERO
        elif self.uniqid in upoint[1]:
            return EXPRONE
        else:
            return self

    def compose(self, mapping):
        try:
            return mapping[self]
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, ExprConstant):
            return False
        if isinstance(other, ExprVariable):
            return boolfunc.Variable.__lt__(self, other)
        if isinstance(other, ExprComplement):
            return boolfunc.Variable.__lt__(self, other.exprvar)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        return exprcomp(self)

    # DPLL IF
    def bcp(self):
        return frozenset(), frozenset([self.uniqid])

    def ple(self):
        return frozenset(), frozenset([self.uniqid])

    minterm_index = 1
    maxterm_index = 0


class ExprComplement(ExprLiteral):
    """Expression complement"""

    def __init__(self, exprvar):
        ExprLiteral.__init__(self)
        self.exprvar = exprvar
        self.uniqid = -exprvar.uniqid

    def __str__(self):
        return str(self.exprvar) + "'"

    # From Function
    @cached_property
    def support(self):
        return frozenset([self.exprvar, ])

    def urestrict(self, upoint):
        if self.exprvar.uniqid in upoint[0]:
            return EXPRONE
        elif self.exprvar.uniqid in upoint[1]:
            return EXPRZERO
        else:
            return self

    def compose(self, mapping):
        try:
            return ExprNot(mapping[self.exprvar]).simplify()
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, ExprConstant):
            return False
        if isinstance(other, ExprVariable):
            return ( self.exprvar.name < other.name or
                     self.exprvar.name == other.name and
                     self.exprvar.indices <= other.indices )
        if isinstance(other, ExprComplement):
            return boolfunc.Variable.__lt__(self.exprvar, other.exprvar)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        return self.exprvar

    # DPLL IF
    def bcp(self):
        return frozenset([self.exprvar.uniqid]), frozenset()

    def ple(self):
        return frozenset([self.exprvar.uniqid]), frozenset()

    minterm_index = 0
    maxterm_index = 1


class ExprOrAnd(Expression, sat.DPLLInterface):
    """Base class for Expression OR/AND expressions"""

    def __new__(cls, *args, **kwargs):
        # Or() = 0; And() = 1
        if len(args) == 0:
            return cls.IDENTITY
        # Or(x) = x; And(x) = x
        elif len(args) == 1:
            return args[0]
        else:
            return super(ExprOrAnd, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        super(ExprOrAnd, self).__init__(args)
        self.simplified = kwargs.get('simplified', False)

    @cached_property
    def arg_set(self):
        """Return the argument set for a normal form term."""
        return frozenset(self.args)

    # From Function
    def urestrict(self, upoint):
        idx_arg = self._get_restrictions(upoint)
        if idx_arg:
            args = list(self.args)
            for i, arg in idx_arg.items():
                # speed hack
                if arg == self.DOMINATOR:
                    return self.DOMINATOR
                else:
                    args[i] = arg
            return self.__class__(*args).simplify()
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

    def invert(self):
        args = [arg.invert() for arg in self.args]
        return self.get_dual()(*args, simplified=self.simplified)

    def simplify(self):
        if self.simplified:
            return self

        temps, args = list(self.args), set()
        while temps:
            arg = temps.pop()
            arg = arg.simplify()
            if arg is self.DOMINATOR:
                return arg
            elif arg is self.IDENTITY:
                pass
            # associative
            elif isinstance(arg, self.__class__):
                temps.extend(arg.args)
            # complement
            elif isinstance(arg, ExprLiteral) and -arg in args:
                return self.DOMINATOR
            else:
                args.add(arg)

        args = tuple(args)
        return self.__class__(*args, simplified=True)

    def factor(self, conj=False):
        args = [arg.factor(conj) for arg in self.args]
        return self.__class__(*args).simplify()

    @cached_property
    def depth(self):
        return max(arg.depth + 1 for arg in self.args)

    # Specific to ExprOrAnd
    IDENTITY = NotImplemented
    DOMINATOR = NotImplemented

    @staticmethod
    def get_dual():
        """Return the dual function.

        The dual of Or is And, and the dual of And is Or.
        """
        raise NotImplementedError()

    @property
    def term_index(self):
        """
        Return an integer bitstring that uniquely identifies this min/max term.

        Examples
        --------

        +--------------+-------+
        | term         | index |
        +==============+=======+
        | a' * b' * c' | 000   |
        | a  * b  * c' | 110   |
        | a  * b  * c  | 111   |
        +--------------+-------+
        | a' + b' + c' | 111   |
        | a  + b  + c' | 001   |
        | a  + b  + c  | 000   |
        +==============+=======+
        """
        raise NotImplementedError()

    # FactoredExpression
    def flatten(self, op):
        """Return a flattened OR/AND expression.

        Use the distributive law to flatten all nested expressions:
        x + (y * z) = (x + y) * (x + z)
        x * (y + z) = (x * y) + (x * z)

        Parameters
        ----------

        op : ExprOr or ExprAnd
            The operator you want to flatten. For example, if you want to
            produce an ExprOr expression, flatten all the nested ExprAnds.

        .. NOTE:: This method assumes the expression is already factored.
                  Do NOT call this method directly -- use the 'to_dnf' or
                  'to_cnf' methods instead.
        """
        if isinstance(self, op):
            for i, argi in enumerate(self.args):
                if isinstance(argi, self.get_dual()):
                    others = self.args[:i] + self.args[i+1:]
                    args = [op(arg, *others) for arg in argi.args]
                    expr = op.get_dual()(*args).simplify()
                    return expr.flatten(op).absorb()
            return self
        else:
            nested, others = list(), list()
            for arg in self.args:
                if arg.depth > 1:
                    nested.append(arg)
                else:
                    others.append(arg)
            args = [arg.flatten(op).absorb() for arg in nested] + others
            return op.get_dual()(*args).simplify()

    # FlattenedExpression
    def absorb(self):
        """Return the OR/AND expression after absorption.

        x + (x * y) = x
        x * (x + y) = x

        .. NOTE:: This method assumes the expression is already factored and
                  flattened. Do NOT call this method directly -- use the
                  'to_dnf' or 'to_cnf' methods instead.
        """
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

        return self.__class__(*args, simplified=True)

    def reduce(self):
        """Reduce this expression to a canonical form.

        .. NOTE:: This method assumes the expression is already in normal form.
                  Do NOT call this method directly. Use 'to_cdnf' instead.
        """
        if self.depth == 1:
            return self

        terms = list()
        indices = set()
        for term in self.args:
            vs = list(self.support - term.support)
            eterms = self._term_expand(term, vs) if vs else (term, )
            for eterm in eterms:
                if eterm.term_index not in indices:
                    terms.append(eterm)
                    indices.add(eterm.term_index)

        return self.__class__(*terms, simplified=True)

    def _term_expand(self, term, vs):
        raise NotImplementedError()


class ExprOr(ExprOrAnd):
    """Expression OR operator"""

    def __str__(self):
        return " + ".join(str(arg) for arg in sorted(self.args))

    # From Expression
    def is_dnf(self):
        return self.simplified and self.depth <= 2

    def is_cnf(self):
        return self.simplified and self.depth == 1

    # DPLL IF
    def bcp(self):
        return frozenset(), frozenset()

    def ple(self):
        upnt = frozenset(), frozenset()
        for lit in self.args:
            ple_upnt = lit.ple()
            upnt = (upnt[0] | ple_upnt[0], upnt[1] | ple_upnt[1])
        return upnt

    # Specific to ExprOrAnd
    IDENTITY = EXPRZERO
    DOMINATOR = EXPRONE

    @staticmethod
    def get_dual():
        return ExprAnd

    @property
    def term_index(self):
        return self.maxterm_index

    # Specific to ExprOr
    @cached_property
    def maxterm_index(self):
        """Return this maxterm's unique index."""
        num = self.degree - 1
        index = 0
        for i, v in enumerate(self.inputs):
            if -v in self.args:
                index |= 1 << (num - i)
        return index

    @cached_property
    def min_indices(self):
        return {term.minterm_index for term in self.args}

    def _term_expand(self, term, vs):
        return term.expand(vs, conj=False).args


class ExprAnd(ExprOrAnd):
    """Expression AND operator"""

    def __str__(self):
        args = sorted(self.args)
        parts = list()
        for arg in args:
            if isinstance(arg, ExprOr):
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        return " * ".join(parts)

    # From Expression
    def is_dnf(self):
        return self.simplified and self.depth == 1

    def is_cnf(self):
        return self.simplified and self.depth <= 2

    # DPLL IF
    def bcp(self):
        upnt = frozenset(), frozenset()
        for clause in self.args:
            if isinstance(clause, ExprLiteral):
                bcp_upnt = clause.bcp()
                upnt = (upnt[0] | bcp_upnt[0], upnt[1] | bcp_upnt[1])
        if upnt[0] or upnt[1]:
            bcp_upnt = self.urestrict(upnt).bcp()
            if bcp_upnt is None:
                return None
            else:
                return (upnt[0] | bcp_upnt[0], upnt[1] | bcp_upnt[1])
        else:
            return frozenset(), frozenset()

    def ple(self):
        upnt = frozenset(), frozenset()
        for clause in self.args:
            ple_upnt = clause.ple()
            upnt = (upnt[0] | ple_upnt[0], upnt[1] | ple_upnt[1])
        zos = upnt[0] & upnt[1]
        if zos:
            return (upnt[0] - zos, upnt[1] - zos)
        else:
            return frozenset(), frozenset()

    # From ExprOrAnd
    IDENTITY = EXPRONE
    DOMINATOR = EXPRZERO

    @staticmethod
    def get_dual():
        return ExprOr

    @property
    def term_index(self):
        return self.minterm_index

    # Specific to ExprAnd
    @cached_property
    def minterm_index(self):
        """Return this minterm's unique index."""
        num = self.degree - 1
        index = 0
        for i, v in enumerate(self.inputs):
            if v in self.args:
                index |= 1 << (num - i)
        return index

    @cached_property
    def min_indices(self):
        return {self.minterm_index}

    def _term_expand(self, term, vs):
        return term.expand(vs, conj=True).args


class ExprNot(Expression):
    """Expression NOT operator"""

    def __new__(cls, arg, simplified=False):
        if isinstance(arg, ExprConstant) or isinstance(arg, ExprLiteral):
            return arg.invert()
        else:
            return super(ExprNot, cls).__new__(cls)

    def __init__(self, arg, simplified=False):
        args = (arg, )
        super(ExprNot, self).__init__(args)
        self.simplified = simplified

    def __str__(self):
        return "Not(" + str(self.args[0]) + ")"

    # From Function
    @property
    def support(self):
        return self.args[0].support

    def urestrict(self, upoint):
        new_arg = self.args[0].urestrict(upoint)
        if id(new_arg) != id(self.args[0]):
            return self.__class__(new_arg).simplify()
        else:
            return self

    def compose(self, mapping):
        new_arg = self.args[0].compose(mapping)
        if id(new_arg) != id(self.args[0]):
            return self.__class__(new_arg).simplify()
        else:
            return self

    # From Expression
    def invert(self):
        return self.args[0]

    def simplify(self):
        if self.simplified:
            return self

        arg = self.args[0].simplify()
        return self.__class__(arg, simplified=True)

    def factor(self, conj=False):
        return self.args[0].invert().factor(conj)

    @cached_property
    def depth(self):
        return self.args[0].depth


class ExprExclusive(Expression):
    """Expression exclusive (XOR, XNOR) operator"""

    def __init__(self, *args, **kwargs):
        super(ExprExclusive, self).__init__(args)
        self.simplified = kwargs.get('simplified', False)

    # From Expression
    def invert(self):
        return self.get_dual()(*self.args, simplified=self.simplified)

    def simplify(self):
        if self.simplified:
            return self

        par = self.PARITY
        temps, args = list(self.args), set()
        while temps:
            arg = temps.pop()
            arg = arg.simplify()
            if isinstance(arg, ExprConstant):
                par ^= int(arg)
            # associative
            elif isinstance(arg, self.__class__):
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

        xcls = { ExprXor.PARITY  : ExprXor,
                 ExprXnor.PARITY : ExprXnor }[par]
        return xcls(*args, simplified=True)

    def factor(self, conj=False):
        outer, inner = (ExprAnd, ExprOr) if conj else (ExprOr, ExprAnd)
        terms = list()
        for num in range(1 << len(self.args)):
            if parity(num) == self.PARITY:
                term = list()
                for i, arg in enumerate(self.args):
                    if bit_on(num, i):
                        term.append(arg.factor(conj))
                    else:
                        term.append(arg.invert().factor(conj))
                terms.append(inner(*term))
        return outer(*terms).simplify()

    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)

    # Specific to ExprExclusive
    PARITY = NotImplemented

    @staticmethod
    def get_dual():
        """Return the dual function.

        The dual of Xor and Xnor, and the dual of Xnor is Xor.
        """
        raise NotImplementedError()


class ExprXor(ExprExclusive):
    """Expression Exclusive OR (XOR) operator"""

    def __new__(cls, *args, **kwargs):
        # Xor() = 0
        if len(args) == 0:
            return EXPRZERO
        # Xor(x) = x
        elif len(args) == 1:
            return args[0]
        else:
            return super(ExprXor, cls).__new__(cls)

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in sorted(self.args))
        return "Xor(" + args_str + ")"

    PARITY = 1

    @staticmethod
    def get_dual():
        return Xnor


class ExprXnor(ExprExclusive):
    """Expression Exclusive NOR (XNOR) operator"""

    def __new__(cls, *args, **kwargs):
        # Xnor() = 1
        if len(args) == 0:
            return EXPRONE
        # Xnor(x) = x'
        elif len(args) == 1:
            return ExprNot(args[0]).simplify()
        else:
            return super(ExprXnor, cls).__new__(cls)

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in sorted(self.args))
        return "Xnor(" + args_str + ")"

    PARITY = 0

    @staticmethod
    def get_dual():
        return Xor


class ExprEqual(Expression):
    """Expression EQUAL operator"""

    def __new__(cls, *args, **kwargs):
        # Equal(x) = Equal() = 1
        if len(args) <= 1:
            return EXPRONE
        else:
            return super(ExprEqual, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        super(ExprEqual, self).__init__(args)
        self.simplified = kwargs.get('simplified', False)

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in sorted(self.args))
        return "Equal(" + args_str + ")"

    # From Expression
    def invert(self):
        exist_one = ExprOr(*self.args, simplified=self.simplified)
        exist_zero = ExprAnd(*self.args, simplified=self.simplified).invert()
        return ExprAnd(exist_one, exist_zero, simplified=self.simplified)

    def simplify(self):
        if self.simplified:
            return self

        args = {arg.simplify() for arg in self.args}

        if EXPRZERO in args:
            # Equal(0, 1, ...) = 0
            if EXPRONE in args:
                return EXPRZERO
            # Equal(0, x0, x1, ...) = Nor(x0, x1, ...)
            else:
                args = tuple(args)
                return ExprNot(ExprOr(*args)).simplify()
        # Equal(1, x0, x1, ...)
        if EXPRONE in args:
            args = tuple(args)
            return ExprAnd(*args).simplify()

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

        args = tuple(args)
        return self.__class__(*args, simplified=True)

    def factor(self, conj=False):
        if conj:
            args = list()
            for i, argi in enumerate(self.args):
                for _, argj in enumerate(self.args, start=i):
                    args.append(ExprOr(argi.factor(conj),
                                       argj.invert().factor(conj)))
                    args.append(ExprOr(argi.invert().factor(conj),
                                       argj.factor(conj)))
            return ExprAnd(*args).simplify()
        else:
            all_zero = ExprAnd(*[arg.invert().factor(conj)
                                 for arg in self.args])
            all_one = ExprAnd(*[arg.factor(conj) for arg in self.args])
            return ExprOr(all_zero, all_one).simplify()

    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)


class ExprImplies(Expression):
    """Expression implication operator"""

    def __init__(self, p, q, simplified=False):
        args = (p, q)
        super(ExprImplies, self).__init__(args)
        self.simplified = simplified

    def __str__(self):
        parts = list()
        for arg in self.args:
            if isinstance(arg, ExprConstant) or isinstance(arg, ExprLiteral):
                parts.append(str(arg))
            else:
                parts.append("(" + str(arg) + ")")
        return " => ".join(parts)

    # From Expression
    def invert(self):
        args = (self.args[0], self.args[1].invert())
        return ExprAnd(*args, simplified=self.simplified)

    def simplify(self):
        p = self.args[0].simplify()
        q = self.args[1].simplify()

        # 0 => q = 1; p => 1 = 1
        if p is EXPRZERO or q is EXPRONE:
            return EXPRONE
        # 1 => q = q
        elif p is EXPRONE:
            return q
        # p => 0 = p'
        elif q is EXPRZERO:
            return ExprNot(p).simplify()
        # p -> p = 1
        elif p == q:
            return EXPRONE
        # -p -> p = p
        elif isinstance(p, ExprLiteral) and -p == q:
            return q

        return self.__class__(p, q, simplified=True)

    def factor(self, conj=False):
        p, q = self.args
        args = list()
        args.append(p.invert().factor(conj))
        args.append(q.factor(conj))
        return ExprOr(*args).simplify()

    @cached_property
    def depth(self):
        return max(arg.depth + 1 for arg in self.args)


class ExprITE(Expression):
    """Expression if-then-else ternary operator"""

    def __init__(self, s, d1, d0, simplified=False):
        args = (s, d1, d0)
        super(ExprITE, self).__init__(args)
        self.simplified = simplified

    def __str__(self):
        parts = list()
        for arg in self.args:
            if isinstance(arg, ExprConstant) or isinstance(arg, ExprLiteral):
                parts.append(str(arg))
            else:
                parts.append("(" + str(arg) + ")")
        return "{} ? {} : {}".format(*parts)

    # From Expression
    def invert(self):
        s = self.args[0]
        d1 = self.args[1].invert()
        d0 = self.args[2].invert()
        return ExprITE(s, d1, d0, simplified=self.simplified)

    def simplify(self):
        s = self.args[0].simplify()
        d1 = self.args[1].simplify()
        d0 = self.args[2].simplify()

        # 0 ? d1 : d0 = d0
        if s is EXPRZERO:
            return d0
        # 1 ? d1 : d0 = d1
        elif s is EXPRONE:
            return d1
        elif d1 is EXPRZERO:
            # s ? 0 : 0 = 0
            if d0 is EXPRZERO:
                return EXPRZERO
            # s ? 0 : 1 = s'
            elif d0 is EXPRONE:
                return ExprNot(s).simplify()
            # s ? 0 : d0 = s' * d0
            else:
                return ExprAnd(ExprNot(s), d0).simplify()
        elif d1 is EXPRONE:
            # s ? 1 : 0 = s
            if d0 is EXPRZERO:
                return s
            # s ? 1 : 1 = 1
            elif d0 is EXPRONE:
                return EXPRONE
            # s ? 1 : d0 = s + d0
            else:
                return ExprOr(s, d0).simplify()
        # s ? d1 : 0 = s * d1
        elif d0 is EXPRZERO:
            return ExprAnd(s, d1).simplify()
        # s ? d1 : 1 = s' + d1
        elif d0 is EXPRONE:
            return ExprOr(ExprNot(s), d1).simplify()
        # s ? d1 : d1 = d1
        elif d1 == d0:
            return d1

        return self.__class__(s, d1, d0, simplified=True)

    def factor(self, conj=False):
        s, d1, d0 = self.args
        args = list()
        args.append(ExprAnd(s.factor(conj), d1.factor(conj)))
        args.append(ExprAnd(s.invert().factor(conj), d0.factor(conj)))
        return ExprOr(*args).simplify()

    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)


def _iter_zeros(expr):
    """Iterate through all upoints that map to element zero."""
    if expr is EXPRZERO:
        yield frozenset(), frozenset()
    elif expr is not EXPRONE:
        v = expr.top
        upnt0 = frozenset([v.uniqid]), frozenset()
        upnt1 = frozenset(), frozenset([v.uniqid])
        for upnt in [upnt0, upnt1]:
            for zero_upnt in _iter_zeros(expr.urestrict(upnt)):
                yield (upnt[0] | zero_upnt[0], upnt[1] | zero_upnt[1])

def _iter_ones(expr):
    """Iterate through all upoints that map to element one."""
    if expr is EXPRONE:
        yield frozenset(), frozenset()
    elif expr is not EXPRZERO:
        v = expr.top
        upnt0 = frozenset([v.uniqid]), frozenset()
        upnt1 = frozenset(), frozenset([v.uniqid])
        for upnt in [upnt0, upnt1]:
            for one_upnt in _iter_ones(expr.urestrict(upnt)):
                yield (upnt[0] | one_upnt[0], upnt[1] | one_upnt[1])
