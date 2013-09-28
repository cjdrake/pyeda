"""
Boolean Logic Expressions

Interface Functions:
    exprvar
    exprcomp
    expr
    ast2expr
    expr2dimacscnf
    expr2dimacssat
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
        ExprNot
        ExprOrAnd
            ExprOr
            ExprAnd
        ExprExclusive
            ExprXor
            ExprXnor
        ExprEqual
        ExprImplies
        ExprITE
"""

# Disable "redefining name from outer scope"
# pylint: disable=W0621

import collections

import pyeda.parsing.boolexpr
from pyeda import boolfunc
from pyeda import sat
from pyeda.util import bit_on, parity, cached_property


EXPRVARIABLES = dict()
EXPRCOMPLEMENTS = dict()


def exprvar(name, index=None):
    """Return an Expression Variable.

    Parameters
    ----------

    name : str
        The variable's identifier string.
    index : int or tuple[int], optional
        One or more integer suffixes for variables that are part of a
        multi-dimensional bit-vector, eg x[1], x[1][2][3]
    """
    bvar = boolfunc.var(name, index)
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

def expr(arg):
    """Return an Expression."""
    if isinstance(arg, Expression):
        return arg
    elif arg in {0, 1}:
        return CONSTANTS[arg]
    elif type(arg) is str:
        ast = pyeda.parsing.boolexpr.parse(arg)
        return ast2expr(ast)
    else:
        fstr = "argument cannot be converted to Expression: " + str(arg)
        raise TypeError(fstr)

def ast2expr(ast):
    """Convert an abstract syntax tree to an Expression."""
    if ast[0] == 'const':
        return CONSTANTS[ast[1]]
    elif ast[0] == 'var':
        return exprvar(ast[1], ast[2])
    else:
        args = tuple(ast2expr(arg) for arg in ast[1:])
        return ASTOPS[ast[0]](*args)

def expr2dimacscnf(expr):
    """Convert an expression into an equivalent DIMACS CNF string."""
    if not isinstance(expr, Expression):
        raise ValueError("input is not an expression")
    if not expr.is_cnf():
        raise ValueError("input is not a CNF")

    nums, nvariables = _exprnvars(expr)
    clauses = _expr2clauses(expr, nums)
    formula = " ".join(" ".join(term for term in clause) for clause in clauses)
    return "p cnf {} {}\n{}".format(nvariables, len(clauses), formula)

def expr2dimacssat(expr):
    """Convert an expression into an equivalent DIMACS SAT string."""
    if not isinstance(expr, Expression):
        raise ValueError("input is not an expression")
    if not expr.simplified:
        raise ValueError("input expression is not simplified")

    nums, nvariables = _exprnvars(expr)
    formula = _expr2sat(expr, nums)
    if 'xor' in formula:
        if '=' in formula:
            fmt = 'satex'
        else:
            fmt = 'satx'
    elif '=' in formula:
        fmt = 'sate'
    else:
        fmt = 'sat'
    return "p {} {}\n{}".format(fmt, nvariables, formula)

def _exprnvars(expr):
    """Return a remapping of Variable uniqids."""
    nums = {v.uniqid: None for v in expr.support}
    num = 1
    for uniqid in sorted(nums.keys()):
        nums[uniqid] = num
        nums[-uniqid] = -num
        num += 1
    return nums, num - 1

def _expr2clauses(expr, nums):
    """Convert an expression to a list of DIMACS CNF clauses."""
    if expr is EXPRONE:
        return []
    elif isinstance(expr, ExprLiteral):
        return [[str(nums[expr.uniqid]), '0']]
    elif isinstance(expr, ExprOr) and expr.depth == 1:
        return [[str(nums[lit.uniqid]) for lit in expr.args] + ['0']]
    elif isinstance(expr, ExprAnd) and expr.depth == 1:
        return [[str(nums[lit.uniqid]), '0'] for lit in expr.args]
    else:
        return [[str(nums[lit.uniqid]) for lit in term.arg_set] + ['0']
                for term in expr.args]

def _expr2sat(expr, nums):
    """Convert an expression to a DIMACS SAT string."""
    if isinstance(expr, ExprLiteral):
        return str(nums[expr.uniqid])
    elif isinstance(expr, ExprOr):
        return "+(" + " ".join(_expr2sat(arg, nums) for arg in expr.args) + ")"
    elif isinstance(expr, ExprAnd):
        return "*(" + " ".join(_expr2sat(arg, nums) for arg in expr.args) + ")"
    elif isinstance(expr, ExprNot):
        return "-(" + _expr2sat(expr.args[0], nums) + ")"
    elif isinstance(expr, ExprXor):
        return ("xor(" + " ".join(_expr2sat(arg, nums)
                                  for arg in expr.args) + ")")
    elif isinstance(expr, ExprEqual):
        return "=(" + " ".join(_expr2sat(arg, nums) for arg in expr.args) + ")"
    else:
        raise ValueError("invalid expression")

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
    expr = ExprXnor(*args)
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
    expr = ExprEqual(*args)
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
    def inputs(self):
        return tuple(sorted(self.support))

    def satisfy_one(self):
        if self.is_cnf():
            solution = sat.dpll(self)
        else:
            solution = sat.backtrack(self)
        if solution is None:
            return None
        else:
            return upoint2exprpoint(solution)

    def satisfy_all(self):
        for upoint in sat.iter_backtrack(self):
            yield upoint2exprpoint(upoint)

    def satisfy_count(self):
        return sum(1 for _ in self.satisfy_all())

    def is_neg_unate(self, vs=None):
        vs = self._expect_vars(vs)
        basis = self.support - set(vs)
        cov = EXPRONE.expand(basis).mincover
        for cf in self.iter_cofactors(vs):
            cf = cf.expand(basis - cf.support)
            if not cf.is_dnf():
                cf = cf.to_dnf()
            if not cf.mincover <= cov:
                return False
            cov = cf.mincover
        return True

    def is_pos_unate(self, vs=None):
        vs = self._expect_vars(vs)
        basis = self.support - set(vs)
        cov = EXPRZERO.mincover
        for cf in self.iter_cofactors(vs):
            cf = cf.expand(basis - cf.support)
            if not cf.is_dnf():
                cf = cf.to_dnf()
            if not cf.mincover >= cov:
                return False
            cov = cf.mincover
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
        return expr(arg)

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
            terms = [inner(self, *term).simplify()
                     for term in boolfunc.iter_terms(vs, conj)]
            if conj:
                terms = [term for term in terms if term is not EXPRONE]
            else:
                terms = [term for term in terms if term is not EXPRZERO]
            # simplified=False allows expressions like a * -a
            return outer(*terms, simplified=False)
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

    def tseitin(self, auxvarname='aux'):
        """Convert the expression to Tseitin's encoding."""
        if self.is_cnf():
            return self

        auxvars = list()
        _, cons = self.factor()._tseitin(auxvarname, auxvars)
        fst = cons[-1][1]
        rst = [Equal(f, expr).to_cnf() for f, expr in cons[:-1]]
        return And(fst, *rst)

    def equivalent(self, other):
        """Return whether this expression is equivalent to another."""
        other = self.box(other)
        f = Xor(self, other)
        return f.satisfy_one() is None


class ExprConstant(Expression, sat.DPLLInterface):
    """Expression constant"""

    VAL = NotImplemented

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

    def reduce(self):
        """Degenerate form of a reduced expression."""
        return self

    def complete_sum(self):
        return self


class _ExprZero(ExprConstant):
    """
    Expression zero

    .. NOTE:: Never use this class. Use EXPRZERO singleton instead.
    """

    VAL = 0

    # From Function
    def is_zero(self):
        return True

    # From Expression
    def __lt__(self, other):
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        return EXPRONE

    def is_dnf(self):
        return True

    @cached_property
    def mincover(self):
        """Return the minterm cover."""
        return set()

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

    VAL = 1

    # From Function
    def is_one(self):
        return True

    # From Expression
    def __lt__(self, other):
        if other is EXPRZERO:
            return False
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        return EXPRZERO

    def is_cnf(self):
        return True

    @cached_property
    def mincover(self):
        """Return the minterm cover."""
        return {0}

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
        self.simplified = True

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
    def _tseitin(self, auxvarname, auxvars):
        return self, list()

    def flatten(self, op):
        """Degenerate form of a flattened expression."""
        return self

    def absorb(self):
        """Degenerate form of a flattened expression."""
        return self

    def reduce(self):
        """Degenerate form of a reduced expression."""
        return self

    def complete_sum(self):
        return self

    @cached_property
    def mincover(self):
        """Return the minterm cover."""
        return {self.minterm_index}

    minterm_index = NotImplemented


class ExprVariable(boolfunc.Variable, ExprLiteral):
    """Expression variable"""

    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.names, bvar.indices)
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
            return ( self.exprvar.names < other.names or
                     self.exprvar.names == other.names and
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


class ExprNot(Expression):
    """Expression NOT operator"""

    ASTOP = 'not'

    def __new__(cls, arg, simplified=False):
        if isinstance(arg, ExprConstant) or isinstance(arg, ExprLiteral):
            return arg.invert()
        else:
            return super(ExprNot, cls).__new__(cls)

    def __init__(self, arg, simplified=False):
        self.arg = arg
        self.simplified = simplified

    def __str__(self):
        return "Not(" + str(self.arg) + ")"

    # From Function
    @property
    def support(self):
        return self.arg.support

    def urestrict(self, upoint):
        new_arg = self.arg.urestrict(upoint)
        if id(new_arg) != id(self.arg):
            return self.__class__(new_arg).simplify()
        else:
            return self

    def compose(self, mapping):
        new_arg = self.arg.compose(mapping)
        if id(new_arg) != id(self.arg):
            return self.__class__(new_arg).simplify()
        else:
            return self

    # From Expression
    def invert(self):
        return self.arg

    def simplify(self):
        if self.simplified:
            return self

        arg = self.arg.simplify()
        return self.__class__(arg, simplified=True)

    def factor(self, conj=False):
        return self.arg.invert().factor(conj)

    @cached_property
    def depth(self):
        return self.arg.depth


class _ArgContainer(Expression):
    """Common methods for expressions that are argument containers."""

    def __init__(self, args):
        self.args = args

    # From Function
    @cached_property
    def support(self):
        return frozenset.union(*[arg.support for arg in self.args])

    # From Expression
    def invert(self):
        raise NotImplementedError()

    def simplify(self):
        raise NotImplementedError()

    def factor(self, conj=False):
        raise NotImplementedError()

    @property
    def depth(self):
        raise NotImplementedError()

    # Specific to _ArgContainer
    def args_str(self, sep):
        """Return arguments as a string, joined by a separator."""
        return sep.join(str(arg) for arg in sorted(self.args))

    def urestrict(self, upoint):
        if self.usupport & (upoint[0] | upoint[1]):
            args = [arg.urestrict(upoint) for arg in self.args]
            return self.__class__(*args).simplify()
        else:
            return self.simplify()

    def compose(self, mapping):
        if self.support & set(mapping.keys()):
            args = [arg.compose(mapping) for arg in self.args]
            return self.__class__(*args).simplify()
        else:
            return self.simplify()


class ExprOrAnd(_ArgContainer, sat.DPLLInterface):
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
        super(ExprOrAnd, self).__init__(frozenset(args))
        self.simplified = kwargs.get('simplified', False)

    def __eq__(self, other):
        return isinstance(other, ExprOrAnd) and self.args == other.args

    def __hash__(self):
        return hash(self.args)

    @cached_property
    def arg_set(self):
        """Return the argument set for a normal form term."""
        return self.args

    # From Function
    def urestrict(self, upoint):
        if self.usupport & (upoint[0] | upoint[1]):
            # speed hack
            if self.DOMINATOR in self.args:
                return self.DOMINATOR
            else:
                args = {arg.urestrict(upoint) for arg in self.args}
            return self.__class__(*args).simplify()
        else:
            return self.simplify()

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
        args = {arg.invert() for arg in self.args}
        return self.get_dual()(*args, simplified=self.simplified)

    def simplify(self):
        if self.simplified:
            return self

        temps, args = set(self.args), set()
        while temps:
            arg = temps.pop()
            arg = arg.simplify()
            if arg is self.DOMINATOR:
                return arg
            elif arg is self.IDENTITY:
                pass
            # associative
            elif isinstance(arg, self.__class__):
                temps.update(arg.args)
            # complement
            elif isinstance(arg, ExprLiteral) and -arg in args:
                return self.DOMINATOR
            else:
                args.add(arg)

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
            for arg in self.args:
                if isinstance(arg, self.get_dual()):
                    others = self.args - {arg}
                    args = [op(arg, *others) for arg in arg.args]
                    expr = op.get_dual()(*args).simplify()
                    return expr.flatten(op).absorb()
            return self
        else:
            args = [arg.flatten(op).absorb() if arg.depth > 1 else arg
                    for arg in self.args]
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

        # Drop all terms that are a superset of other terms
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

    def _tseitin(self, auxvarname, auxvars):
        fs = list()
        cons = list()
        for arg in self.args:
            f, _cons = arg._tseitin(auxvarname, auxvars)
            fs.append(f)
            cons.extend(_cons)

        auxvaridx = len(auxvars)
        auxvar = exprvar(auxvarname, auxvaridx)
        auxvars.append(auxvar)

        cons.append((auxvar, self.__class__(*fs)))
        return auxvar, cons

    def _term_expand(self, term, vs):
        """Return a term expanded by a list of variables."""
        raise NotImplementedError()


class ExprOr(ExprOrAnd):
    """Expression OR operator"""

    ASTOP = 'or'

    def __str__(self):
        return self.args_str(" + ")

    # From Expression
    def is_dnf(self):
        # a + b
        if self.depth == 1:
            return all(isinstance(arg, ExprLiteral) for arg in self.args)
        # a + b * c
        elif self.depth == 2:
            return all(
                       isinstance(arg, ExprLiteral) or
                       isinstance(arg, ExprAnd) and arg.is_cnf()
                       for arg in self.args
                   )
        else:
            return False

    def is_cnf(self):
        # a * b
        if self.depth == 1:
            return all(isinstance(arg, ExprLiteral) for arg in self.args)
        else:
            return False

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
    def mincover(self):
        """Return the minterm cover."""
        return {term.minterm_index for term in self.args}

    def _term_expand(self, term, vs):
        return term.expand(vs, conj=False).args

    def complete_sum(self):
        if self.depth == 1:
            return self
        else:
            cnt = collections.Counter(v for clause in self.args
                                        for v in clause.support)
            v = cnt.most_common(1)[0][0]
            fv0, fv1 = self.cofactors(v)
            f = (v + fv0.complete_sum()) * (-v + fv1.complete_sum())
            return f.flatten(ExprAnd)


class ExprAnd(ExprOrAnd):
    """Expression AND operator"""

    ASTOP = 'and'

    def __str__(self):
        parts = list()
        for arg in sorted(self.args):
            if isinstance(arg, ExprOr):
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        return " * ".join(parts)

    # From Expression
    def is_dnf(self):
        # a * b
        if self.depth == 1:
            return all(isinstance(arg, ExprLiteral) for arg in self.args)
        else:
            return False

    def is_cnf(self):
        # a * b
        if self.depth == 1:
            return all(isinstance(arg, ExprLiteral) for arg in self.args)
        # a * (b + c)
        elif self.depth == 2:
            return all(
                       isinstance(arg, ExprLiteral) or
                       isinstance(arg, ExprOr) and arg.is_dnf()
                       for arg in self.args
                   )
        else:
            return False

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
        return upnt[0] - upnt[1], upnt[1] - upnt[0]

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
    def mincover(self):
        """Return the minterm cover."""
        return {self.minterm_index}

    def _term_expand(self, term, vs):
        return term.expand(vs, conj=True).args

    def complete_sum(self):
        if self.depth == 1:
            return self
        else:
            cnt = collections.Counter(v for clause in self.args
                                        for v in clause.support)
            v = cnt.most_common(1)[0][0]
            fv0, fv1 = self.cofactors(v)
            f = (-v * fv0.complete_sum()) + (v * fv1.complete_sum())
            return f.flatten(ExprOr)


class ExprExclusive(_ArgContainer):
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

        return EXCLOPS[par](*args, simplified=True)

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

    ASTOP = 'xor'

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
        return "Xor(" + self.args_str(", ") + ")"

    PARITY = 1

    @staticmethod
    def get_dual():
        return Xnor


class ExprXnor(ExprExclusive):
    """Expression Exclusive NOR (XNOR) operator"""

    ASTOP = 'xnor'

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
        return "Xnor(" + self.args_str(", ") + ")"

    PARITY = 0

    @staticmethod
    def get_dual():
        return Xor


class ExprEqual(_ArgContainer):
    """Expression EQUAL operator"""

    ASTOP = 'equal'

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
        return "Equal(" + self.args_str(", ") + ")"

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
                return ExprNot(ExprOr(*args)).simplify()
        # Equal(1, x0, x1, ...)
        if EXPRONE in args:
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


class ExprImplies(_ArgContainer):
    """Expression implication operator"""

    ASTOP = 'ite'

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


class ExprITE(_ArgContainer):
    """Expression if-then-else ternary operator"""

    ASTOP = 'ite'

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


# Convenience dictionaries
CONSTANTS = {
    _ExprZero.VAL : EXPRZERO,
    _ExprOne.VAL  : EXPRONE
}

ASTOPS = {
    ExprNot.ASTOP     : ExprNot,
    ExprOr.ASTOP      : ExprOr,
    ExprAnd.ASTOP     : ExprAnd,
    ExprXor.ASTOP     : ExprXor,
    ExprXnor.ASTOP    : ExprXnor,
    ExprEqual.ASTOP   : ExprEqual,
    ExprImplies.ASTOP : ExprImplies,
    ExprITE.ASTOP     : ExprITE,
}

EXCLOPS = {
    ExprXor.PARITY  : ExprXor,
    ExprXnor.PARITY : ExprXnor
}
