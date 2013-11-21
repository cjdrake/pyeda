"""
Boolean Logic Expressions

Interface Functions:
    exprvar
    exprcomp
    expr
    ast2expr
    expr2dimacssat
    upoint2exprpoint

    Not, Or, And,
    Xor, Xnor,
    Equal, Unequal, Implies, ITE

    Nor, Nand
    OneHot0, OneHot
    Majority

    ForAll, Exists

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
        ExprNorNand
            ExprNor
            ExprNand
        ExprExclusive
            ExprXor
            ExprXnor
        ExprEqualBase
            ExprEqual
            ExprUnequal
        ExprImplies
        ExprITE

    DimacsCNF
"""

# Disable "redefining name from outer scope"
# pylint: disable=W0621

import collections
import itertools

import pyeda.parsing.boolexpr
from pyeda.boolalg import boolfunc, sat
from pyeda.util import bit_on, parity, cached_property

try:
    from pyeda.boolalg import picosat
except ImportError:
    PICOSAT_IMPORTED = False
else:
    PICOSAT_IMPORTED = True


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

def expr(arg, simplify=True, factor=False):
    """Return an Expression."""
    if isinstance(arg, Expression):
        return arg
    elif arg in {0, 1}:
        return CONSTANTS[arg]
    elif type(arg) is str:
        ex = ast2expr(pyeda.parsing.boolexpr.parse(arg))
        if factor:
            ex = ex.factor()
        elif simplify:
            ex = ex.simplify()
        return ex
    else:
        return CONSTANTS[bool(arg)]

def ast2expr(ast):
    """Convert an abstract syntax tree to an Expression."""
    if ast[0] == 'const':
        return CONSTANTS[ast[1]]
    elif ast[0] == 'var':
        return exprvar(ast[1], ast[2])
    else:
        args = [ast2expr(arg) for arg in ast[1:]]
        return ASTOPS[ast[0]](*args)

def expr2dimacssat(expr):
    """Convert an expression into an equivalent DIMACS SAT string."""
    if not isinstance(expr, Expression):
        fstr = "expected expr to be an Expression, got {0.__name__}"
        raise TypeError(fstr.format(type(expr)))
    if not expr.simplified:
        raise ValueError("expected expr to be simplified")

    lit2idx = dict()
    idx2var = dict()
    for i, v in enumerate(expr.inputs, start=1):
        lit2idx[v] = i
        lit2idx[-v] = -i
        idx2var[i] = v

    formula = _expr2sat(expr, lit2idx)
    if 'xor' in formula:
        if '=' in formula:
            fmt = 'satex'
        else:
            fmt = 'satx'
    elif '=' in formula:
        fmt = 'sate'
    else:
        fmt = 'sat'
    return "p {} {}\n{}".format(fmt, len(idx2var), formula)

def _expr2sat(expr, lit2idx):
    """Convert an expression to a DIMACS SAT string."""
    if isinstance(expr, ExprLiteral):
        return str(lit2idx[expr])
    elif isinstance(expr, ExprNot):
        return "-(" + _expr2sat(expr.arg, lit2idx) + ")"
    elif isinstance(expr, ExprOr):
        return "+(" + " ".join(_expr2sat(arg, lit2idx)
                               for arg in expr.args) + ")"
    elif isinstance(expr, ExprAnd):
        return "*(" + " ".join(_expr2sat(arg, lit2idx)
                               for arg in expr.args) + ")"
    elif isinstance(expr, ExprXor):
        return ("xor(" + " ".join(_expr2sat(arg, lit2idx)
                                  for arg in expr.args) + ")")
    elif isinstance(expr, ExprEqual):
        return "=(" + " ".join(_expr2sat(arg, lit2idx)
                               for arg in expr.args) + ")"
    else:
        fstr = ("expected expr to be a Literal or Not/Or/And/Xor/Equal op, "
                "got {0.__name__}")
        raise TypeError(fstr.format(type(expr)))

def upoint2exprpoint(upoint):
    """Convert an untyped point to an Expression point."""
    point = dict()
    for uniqid in upoint[0]:
        point[EXPRVARIABLES[uniqid]] = 0
    for uniqid in upoint[1]:
        point[EXPRVARIABLES[uniqid]] = 1
    return point

# primitive functions
def Not(arg, simplify=True, factor=False):
    """Factory function for Boolean NOT expression."""
    arg = Expression.box(arg)
    expr = ExprNot(arg)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

def Or(*args, simplify=True, factor=False):
    """Factory function for Boolean OR expression."""
    args = [Expression.box(arg) for arg in args]
    expr = ExprOr(*args)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

def And(*args, simplify=True, factor=False):
    """Factory function for Boolean AND expression."""
    args = [Expression.box(arg) for arg in args]
    expr = ExprAnd(*args)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

def Nor(*args, simplify=True, factor=False):
    """Alias for Not(Or(...))"""
    args = [Expression.box(arg) for arg in args]
    expr = ExprNor(*args)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

def Nand(*args, simplify=True, factor=False):
    """Alias for Not(And(...))"""
    args = [Expression.box(arg) for arg in args]
    expr = ExprNand(*args)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

# secondary functions
def Xor(*args, simplify=True, factor=False, conj=False):
    """Factory function for Boolean XOR expression."""
    args = [Expression.box(arg) for arg in args]
    expr = ExprXor(*args)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def Xnor(*args, simplify=True, factor=False, conj=False):
    """Factory function for Boolean XNOR expression."""
    args = [Expression.box(arg) for arg in args]
    expr = ExprXnor(*args)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def Equal(*args, simplify=True, factor=False, conj=False):
    """Factory function for Boolean EQUAL expression."""
    args = [Expression.box(arg) for arg in args]
    expr = ExprEqual(*args)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def Unequal(*args, simplify=True, factor=False, conj=False):
    """Factory function for Boolean UNEQUAL expression."""
    args = [Expression.box(arg) for arg in args]
    expr = ExprUnequal(*args)
    if factor:
        expr = expr.factor(conj)
    elif simplify:
        expr = expr.simplify()
    return expr

def Implies(p, q, simplify=True, factor=False):
    """Factory function for Boolean implication expression."""
    p = Expression.box(p)
    q = Expression.box(q)
    expr = ExprImplies(p, q)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

def ITE(s, d1, d0, simplify=True, factor=False):
    """Factory function for Boolean If-Then-Else expression."""
    s = Expression.box(s)
    d1 = Expression.box(d1)
    d0 = Expression.box(d0)
    expr = ExprITE(s, d1, d0)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

# high order functions
def OneHot0(*args, simplify=True, factor=False, conj=True):
    """
    Return an expression that means:
        At most one input variable is true.
    """
    terms = list()
    if conj:
        for arg1, arg2 in itertools.combinations(args, 2):
            terms.append(Or(Not(arg1, simplify=False),
                            Not(arg2, simplify=False), simplify=False))
        expr = And(*terms, simplify=False)
    else:
        for comb in itertools.combinations(args, len(args) - 1):
            terms.append(And(*[Not(arg, simplify=False) for arg in comb]))
        expr = Or(*terms, simplify=False)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

def OneHot(*args, simplify=True, factor=False, conj=True):
    """
    Return an expression that means:
        Exactly one input variable is true.
    """
    if conj:
        expr = And(Or(*args, simplify=False), OneHot0(*args, simplify=False),
                   simplify=False)
    else:
        terms = list()
        for i, arg in enumerate(args):
            zeros = [Not(x, simplify=False) for x in args[:i] + args[i+1:]]
            terms.append(And(arg, *zeros, simplify=False))
        expr = Or(*terms, simplify=False)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

def Majority(*args, simplify=True, factor=False, conj=False):
    """
    Return an expression that means:
        The majority of the input variables are true.
    """
    if conj:
        terms = list()
        for comb in itertools.combinations(args, (len(args) + 1) // 2):
            terms.append(Or(*comb, simplify=False))
        expr = And(*terms, simplify=False)
    else:
        terms = list()
        for comb in itertools.combinations(args, len(args) // 2 + 1):
            terms.append(And(*comb, simplify=False))
        expr = Or(*terms, simplify=False)
    if factor:
        expr = expr.factor()
    elif simplify:
        expr = expr.simplify()
    return expr

def ForAll(vs, expr):
    """
    Return an expression that means:
        For all variables in 'vs', the expression is true.
    """
    return And(*expr.cofactors(vs))

def Exists(vs, expr):
    """
    Return an expression that means:
        There exists a variable in 'vs' such that the expression is true.
    """
    return Or(*expr.cofactors(vs))


class Expression(boolfunc.Function):
    """Boolean function represented by a logic expression"""

    ASTOP = NotImplemented
    PRECEDENCE = -1

    def __init__(self):
        self._simplified = False

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return id(self) < id(other)

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
            if PICOSAT_IMPORTED:
                cnf = DimacsCNF(self)
                soln = picosat.satisfy_one(cnf.nvars, cnf.clauses)
                if soln is None:
                    return None
                else:
                    return cnf.soln2point(soln)
            else:
                upoint = sat.dpll(self)
        else:
            upoint = sat.backtrack(self)
        if upoint is None:
            return None
        else:
            return upoint2exprpoint(upoint)

    def satisfy_all(self):
        if self.is_cnf() and PICOSAT_IMPORTED:
            cnf = DimacsCNF(self)
            for soln in picosat.satisfy_all(cnf.nvars, cnf.clauses):
                yield cnf.soln2point(soln)
        else:
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
        if isinstance(arg, Expression):
            return arg
        elif arg in {0, 1}:
            return CONSTANTS[arg]
        elif type(arg) is str:
            return ast2expr(pyeda.parsing.boolexpr.parse(arg))
        else:
            return CONSTANTS[bool(arg)]

    # Specific to Expression
    def invert(self):
        """Return an inverted expression."""
        raise NotImplementedError()

    def simplify(self):
        """Return a simplified expression."""
        raise NotImplementedError()

    def _get_simplified(self):
        """Expression.simplified getter."""
        return self._simplified

    def _set_simplified(self, val):
        """Expression.simplified setter."""
        self._simplified = val

    simplified = property(fget=_get_simplified, fset=_set_simplified)

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

    def to_ast(self):
        """Return the expression converted to an abstract syntax tree."""
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
            return outer(*terms)
        else:
            return self

    def to_dnf(self, flatten=True):
        """Return the expression in disjunctive normal form."""
        if flatten:
            return self.factor().flatten(ExprAnd)
        else:
            terms = list()
            for upnt in _iter_ones(self):
                lits = [-EXPRVARIABLES[uniqid] for uniqid in upnt[0]]
                lits += [EXPRVARIABLES[uniqid] for uniqid in upnt[1]]
                terms.append(And(*lits))
            return Or(*terms)

    def to_cdnf(self, flatten=True):
        """Return the expression in canonical disjunctive normal form."""
        return self.to_dnf(flatten).reduce()

    def is_dnf(self):
        """Return whether this expression is in disjunctive normal form."""
        # pylint: disable=R0201
        return False

    def to_cnf(self, flatten=True):
        """Return the expression in conjunctive normal form."""
        if flatten:
            return self.factor().flatten(ExprOr)
        else:
            terms = list()
            for upnt in _iter_zeros(self):
                lits = [EXPRVARIABLES[uniqid] for uniqid in upnt[0]]
                lits += [-EXPRVARIABLES[uniqid] for uniqid in upnt[1]]
                terms.append(Or(*lits))
            return And(*terms)

    def to_ccnf(self, flatten=True):
        """Return the expression in canonical conjunctive normal form."""
        return self.to_cnf(flatten).reduce()

    def is_cnf(self):
        """Return whether this expression is in conjunctive normal form."""
        # pylint: disable=R0201
        return False

    def tseitin(self, auxvarname='aux'):
        """Convert the expression to Tseitin's encoding."""
        if self.is_cnf():
            return self

        _, cons = _tseitin(self.factor(), auxvarname)
        fst = cons[-1][1]
        rst = [Equal(f, expr).to_cnf() for f, expr in cons[:-1]]
        return And(fst, *rst)

    def complete_sum(self):
        """Return a DNF that contains all prime implicants."""
        if self.is_dnf():
            dnf = self
        else:
            dnf = self.to_dnf(flatten=False)
        return _complete_sum(dnf)

    def equivalent(self, other):
        """Return whether this expression is equivalent to another."""
        other = self.box(other)
        f = Xor(self, other)
        return f.satisfy_one() is None


class ExprConstant(Expression, sat.DPLLInterface):
    """Expression constant"""

    ASTOP = 'const'
    VALUE = NotImplemented

    def __init__(self):
        super(ExprConstant, self).__init__()
        self._simplified = True

    def __bool__(self):
        return bool(self.VALUE)

    def __int__(self):
        return self.VALUE

    def __str__(self):
        return str(self.VALUE)

    # From Function
    @cached_property
    def support(self):
        return frozenset()

    def urestrict(self, upoint):
        return self

    def compose(self, mapping):
        return self

    # From Expression
    def simplify(self):
        return self

    def factor(self, conj=False):
        return self

    @property
    def depth(self):
        return 0

    def to_ast(self):
        return (self.ASTOP, self.VALUE)

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


class _ExprZero(ExprConstant):
    """
    Expression zero

    .. NOTE:: Never use this class. Use EXPRZERO singleton instead.
    """

    VALUE = 0

    def __lt__(self, other):
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    # From Function
    def is_zero(self):
        return True

    # From Expression
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

    VALUE = 1

    def __lt__(self, other):
        if other is EXPRZERO:
            return False
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    # From Function
    def is_one(self):
        return True

    # From Expression
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

CONSTANTS = [EXPRZERO, EXPRONE]


class ExprLiteral(Expression, sat.DPLLInterface):
    """An instance of a variable or of its complement"""

    def __init__(self):
        super(ExprLiteral, self).__init__()
        self._simplified = True

    # From Expression
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

    # FlattenedExpression
    @cached_property
    def arg_set(self):
        """Return the argument set for a normal form term."""
        return frozenset([self])

    def absorb(self):
        """Degenerate form of a flattened expression."""
        return self

    def reduce(self):
        """Degenerate form of a reduced expression."""
        return self

    @cached_property
    def mincover(self):
        """Return the minterm cover."""
        return {self.minterm_index}

    minterm_index = NotImplemented


class ExprVariable(boolfunc.Variable, ExprLiteral):
    """Expression variable"""

    ASTOP = 'var'

    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.names, bvar.indices)
        ExprLiteral.__init__(self)

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
    def invert(self):
        return exprcomp(self)

    def to_ast(self):
        return (self.ASTOP, self.names, self.indices)

    # DPLL IF
    def bcp(self):
        return frozenset(), frozenset([self.uniqid])

    def ple(self):
        return frozenset(), frozenset([self.uniqid])

    minterm_index = 1
    maxterm_index = 0

    @property
    def splitvar(self):
        """Return a good splitting variable."""
        return self


class ExprComplement(ExprLiteral):
    """Expression complement"""

    def __init__(self, exprvar):
        super(ExprComplement, self).__init__()
        self.exprvar = exprvar
        self.uniqid = -exprvar.uniqid

    def __str__(self):
        return str(self.exprvar) + "'"

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
    def invert(self):
        return self.exprvar

    def to_ast(self):
        return (ExprNot.ASTOP, self.exprvar.to_ast())

    # DPLL IF
    def bcp(self):
        return frozenset([self.exprvar.uniqid]), frozenset()

    def ple(self):
        return frozenset([self.exprvar.uniqid]), frozenset()

    minterm_index = 0
    maxterm_index = 1

    @property
    def splitvar(self):
        """Return a good splitting variable."""
        return self.exprvar


class ExprNot(Expression):
    """Expression NOT operator"""

    ASTOP = 'not'

    def __new__(cls, arg):
        if isinstance(arg, ExprConstant) or isinstance(arg, ExprLiteral):
            return arg.invert()
        else:
            return super(ExprNot, cls).__new__(cls)

    def __init__(self, arg):
        super(ExprNot, self).__init__()
        self.arg = arg

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
        if self._simplified:
            return self

        arg = self.arg.simplify()
        obj = self.__class__(arg)
        obj.simplified = True
        return obj

    def factor(self, conj=False):
        return self.arg.invert().factor()

    @cached_property
    def depth(self):
        return self.arg.depth

    def to_ast(self):
        return (self.ASTOP, self.arg.to_ast())

    @property
    def splitvar(self):
        """Return a good splitting variable."""
        return self.arg.splitvar


class _ArgumentContainer(Expression):
    """Common methods for expressions that are argument containers."""

    def __init__(self, *args):
        super(_ArgumentContainer, self).__init__()
        self.args = args

    # From Function
    @cached_property
    def support(self):
        return frozenset.union(*[arg.support for arg in self.args])

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

    # From Expression
    def to_ast(self):
        return (self.ASTOP, ) + tuple(arg.to_ast() for arg in self.args)

    # Specific to _ArgumentContainer
    def args_str(self, sep):
        """Return arguments as a string, joined by a separator."""
        return sep.join(str(arg) for arg in sorted(self.args))

    @cached_property
    def splitvar(self):
        """Return a good splitting variable.

        Heuristic: find the variable that appears in the max # of args.
        """
        cnt = collections.Counter()
        for arg in self.args:
            for v in self.support:
                cnt[v] += (v in arg.support)
        return cnt.most_common(1)[0][0]


class ExprOrAnd(_ArgumentContainer, sat.DPLLInterface):
    """Base class for Expression OR/AND expressions"""

    def __new__(cls, *args):
        # Or() = 0; And() = 1
        if len(args) == 0:
            return cls.IDENTITY
        # Or(a) = a; And(a) = a
        elif len(args) == 1:
            return args[0]
        else:
            return super(ExprOrAnd, cls).__new__(cls)

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
    def simplify(self):
        if self._simplified:
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

        obj = self.__class__(*args)
        obj.simplified = True
        return obj

    def factor(self, conj=False):
        args = [arg.factor() for arg in self.args]
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
        a + (b * c) = (a + b) * (a + c)
        a * (b + c) = (a * b) + (a * c)

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
            self_dual = self.get_dual()
            for i, argi in enumerate(self.args):
                if isinstance(argi, self_dual):
                    others = self.args[:i] + self.args[i+1:]
                    args = [op(arg, *others) for arg in argi.args]
                    expr = op.get_dual()(*args).simplify()
                    return expr.flatten(op).absorb()
            return self
        else:
            args = [arg.flatten(op).absorb() if arg.depth > 1 else arg
                    for arg in self.args]
            return op.get_dual()(*args).simplify()

    # FlattenedExpression
    @cached_property
    def arg_set(self):
        """Return the argument set for a normal form term."""
        return frozenset(self.args)

    def absorb(self):
        """Return the OR/AND expression after absorption.

        a + (a * b) = a
        a * (a + b) = a

        .. NOTE:: This method assumes the expression is already factored and
                  flattened. Do NOT call this method directly -- use the
                  'to_dnf' or 'to_cnf' methods instead.
        """
        dual = self.get_dual()

        # Get rid of all equivalent terms
        temps = {arg.arg_set for arg in self.args}
        args = list()

        # Drop all terms that are a superset of other terms
        while temps:
            fst = temps.pop()
            drop_fst = False
            drop_rst = set()
            for temp in temps:
                if fst > temp:
                    drop_fst = True
                elif fst < temp:
                    drop_rst.add(temp)
            if not drop_fst:
                arg = dual(*fst)
                arg.simplified = True
                args.append(arg)
            temps -= drop_rst

        obj = self.__class__(*args)
        obj.simplified = True
        return obj

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

        obj = self.__class__(*terms)
        obj.simplified = True
        return obj

    def _term_expand(self, term, vs):
        """Return a term expanded by a list of variables."""
        raise NotImplementedError()


class ExprOr(ExprOrAnd):
    """Expression OR operator"""

    ASTOP = 'or'
    PRECEDENCE = 2

    def __str__(self):
        parts = list()
        for arg in sorted(self.args):
            # lower precedence: =>, ?:
            if arg.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        return " + ".join(parts)

    # From Expression
    def invert(self):
        obj = ExprNor(*self.args)
        obj.simplified = self._simplified
        return obj

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


class ExprAnd(ExprOrAnd):
    """Expression AND operator"""

    ASTOP = 'and'
    PRECEDENCE = 0

    def __str__(self):
        parts = list()
        for arg in sorted(self.args):
            # lower precedence: +, xor/xnor, =>, ?:
            if arg.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        return " * ".join(parts)

    # From Expression
    def invert(self):
        obj = ExprNand(*self.args)
        obj.simplified = self._simplified
        return obj

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


class ExprNorNand(_ArgumentContainer):
    """Base class for Expression NOR/NAND expressions"""

    @cached_property
    def depth(self):
        return max(arg.depth + 1 for arg in self.args)


class ExprNor(ExprNorNand):
    """Expression NOR operator"""

    ASTOP = 'nor'
    PRECEDENCE = 2

    def __new__(cls, *args):
        # Nor() = 1
        if len(args) == 0:
            return EXPRONE
        # Nor(a) = -a
        elif len(args) == 1:
            return Not(args[0])
        else:
            return super(ExprNor, cls).__new__(cls)

    # From Function
    def urestrict(self, upoint):
        if self.usupport & (upoint[0] | upoint[1]):
            # speed hack
            if EXPRONE in self.args:
                return EXPRZERO
            else:
                args = {arg.urestrict(upoint) for arg in self.args}
            return self.__class__(*args).simplify()
        else:
            return self.simplify()

    # From Expression
    def invert(self):
        obj = ExprOr(*self.args)
        obj.simplified = self._simplified
        return obj

    def simplify(self):
        if self._simplified:
            return self

        temps, args = set(self.args), set()
        while temps:
            arg = temps.pop()
            arg = arg.simplify()
            if arg is EXPRONE:
                return EXPRZERO
            elif arg is EXPRZERO:
                pass
            # associative
            elif isinstance(arg, ExprOr):
                temps.update(arg.args)
            # complement
            elif isinstance(arg, ExprLiteral) and -arg in args:
                return EXPRZERO
            else:
                args.add(arg)

        obj = self.__class__(*args)
        obj.simplified = True
        return obj

    def factor(self, conj=False):
        args = [arg.invert().factor() for arg in self.args]
        return ExprAnd(*args).simplify()

    def __str__(self):
        parts = list()
        for arg in sorted(self.args):
            # lower precedence:
            if arg.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        # Downwards arrow - U2193
        return " ↓ ".join(parts)


class ExprNand(ExprNorNand):
    """Expression NAND operator"""

    ASTOP = 'nand'
    PRECEDENCE = 0

    def __new__(cls, *args):
        # Nand() = 0
        if len(args) == 0:
            return EXPRZERO
        # Nand(a) = -a
        elif len(args) == 1:
            return Not(args[0])
        else:
            return super(ExprNand, cls).__new__(cls)

    # From Function
    def urestrict(self, upoint):
        if self.usupport & (upoint[0] | upoint[1]):
            # speed hack
            if EXPRZERO in self.args:
                return EXPRONE
            else:
                args = {arg.urestrict(upoint) for arg in self.args}
            return self.__class__(*args).simplify()
        else:
            return self.simplify()

    # From Expression
    def invert(self):
        obj = ExprAnd(*self.args)
        obj.simplified = self._simplified
        return obj

    def simplify(self):
        if self._simplified:
            return self

        temps, args = set(self.args), set()
        while temps:
            arg = temps.pop()
            arg = arg.simplify()
            if arg is EXPRZERO:
                return EXPRONE
            elif arg is EXPRONE:
                pass
            # associative
            elif isinstance(arg, ExprAnd):
                temps.update(arg.args)
            # complement
            elif isinstance(arg, ExprLiteral) and -arg in args:
                return EXPRONE
            else:
                args.add(arg)

        obj = self.__class__(*args)
        obj.simplified = True
        return obj

    def factor(self, conj=False):
        args = [arg.invert().factor() for arg in self.args]
        return ExprOr(*args).simplify()

    def __str__(self):
        parts = list()
        for arg in sorted(self.args):
            # lower precedence: +, xor/xnor, =>, ?:
            if arg.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        # Upwards arrow - U2191
        return " ↑ ".join(parts)


class ExprExclusive(_ArgumentContainer):
    """Expression exclusive (XOR, XNOR) operator"""

    PRECEDENCE = 1

    # From Expression
    def simplify(self):
        if self._simplified:
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
            # Xor(a, a') = 1
            elif isinstance(arg, ExprLiteral) and -arg in args:
                args.remove(-arg)
                par ^= 1
            # Xor(a, a) = 0
            elif arg in args:
                args.remove(arg)
            else:
                args.add(arg)

        obj = EXCLOPS[par](*args)
        obj.simplified = True
        return obj

    def factor(self, conj=False):
        outer, inner = (ExprAnd, ExprOr) if conj else (ExprOr, ExprAnd)
        terms = list()
        # Walk through all entries in the truth table
        for num in range(1 << len(self.args)):
            if conj:
                # Zero outputs
                if parity(num) != self.PARITY:
                    term = list()
                    for i, arg in enumerate(self.args):
                        if bit_on(num, i):
                            term.append(arg.invert().factor())
                        else:
                            term.append(arg.factor())
                    terms.append(inner(*term))
            else:
                # One outputs
                if parity(num) == self.PARITY:
                    term = list()
                    for i, arg in enumerate(self.args):
                        if bit_on(num, i):
                            term.append(arg.factor())
                        else:
                            term.append(arg.invert().factor())
                    terms.append(inner(*term))
        return outer(*terms).simplify()

    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)

    # Specific to ExprExclusive
    PARITY = NotImplemented


class ExprXor(ExprExclusive):
    """Expression Exclusive OR (XOR) operator"""

    ASTOP = 'xor'

    def __new__(cls, *args):
        # Xor() = 0
        if len(args) == 0:
            return EXPRZERO
        # Xor(a) = a
        elif len(args) == 1:
            return args[0]
        else:
            return super(ExprXor, cls).__new__(cls)

    def __str__(self):
        parts = list()
        for arg in sorted(self.args):
            # lower precedence: +, xnor, =>, ?:
            if arg.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        # Circled plus - U2295
        return " ⊕ ".join(parts)

    # From Expression
    def invert(self):
        obj = ExprXnor(*self.args)
        obj.simplified = self._simplified
        return obj

    # Specific to ExprExclusive
    PARITY = 1


class ExprXnor(ExprExclusive):
    """Expression Exclusive NOR (XNOR) operator"""

    ASTOP = 'xnor'

    def __new__(cls, *args):
        # Xnor() = 1
        if len(args) == 0:
            return EXPRONE
        # Xnor(a) = a'
        elif len(args) == 1:
            return ExprNot(args[0]).simplify()
        else:
            return super(ExprXnor, cls).__new__(cls)

    def __str__(self):
        parts = list()
        for arg in sorted(self.args):
            # lower precedence: +, xor, =>, ?:
            if arg.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        # Circled dot - U2299
        return " ⊙ ".join(parts)

    # From Expression
    def invert(self):
        obj = ExprXor(*self.args)
        obj.simplified = self._simplified
        return obj

    # Specific to ExprExclusive
    PARITY = 0


class ExprEqualBase(_ArgumentContainer):
    """Expression equality (EQUAL, UNEQUAL) operators"""

    # From Expression
    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)


class ExprEqual(ExprEqualBase):
    """Expression EQUAL operator"""

    ASTOP = 'equal'

    def __new__(cls, *args):
        # Equal(a) = Equal() = 1
        if len(args) <= 1:
            return EXPRONE
        else:
            return super(ExprEqual, cls).__new__(cls)

    def __str__(self):
        return "Equal(" + self.args_str(", ") + ")"

    # From Expression
    def invert(self):
        obj = ExprUnequal(*self.args)
        obj.simplified = self._simplified
        return obj

    def simplify(self):
        if self._simplified:
            return self

        args = {arg.simplify() for arg in self.args}

        if EXPRZERO in args:
            # Equal(0, 1, ...) = 0
            if EXPRONE in args:
                return EXPRZERO
            # Equal(0, x0, x1, ...) = Nor(x0, x1, ...)
            else:
                args.remove(EXPRZERO)
                return ExprNor(*args).simplify()
        # Equal(1, x0, x1, ...) = And(x0, x1, ...)
        if EXPRONE in args:
            args.remove(EXPRONE)
            return ExprAnd(*args).simplify()

        # no constants; all simplified
        temps, args = args, set()
        while temps:
            arg = temps.pop()
            # Equal(a, -a) = 0
            if isinstance(arg, ExprLiteral) and -arg in args:
                return EXPRZERO
            else:
                args.add(arg)

        obj = self.__class__(*args)
        obj.simplified = True
        return obj

    def factor(self, conj=False):
        if conj:
            args = list()
            for arg1, arg2 in itertools.combinations(self.args, 2):
                args.append(ExprOr(arg1.invert().factor(), arg2.factor()))
                args.append(ExprOr(arg1.factor(), arg2.invert().factor()))
            return ExprAnd(*args).simplify()
        else:
            all0 = ExprAnd(*[arg.invert().factor() for arg in self.args])
            all1 = ExprAnd(*[arg.factor() for arg in self.args])
            return ExprOr(all0, all1).simplify()


class ExprUnequal(ExprEqualBase):
    """Expression UNEQUAL operator"""

    ASTOP = 'unequal'

    def __new__(cls, *args):
        # Unequal(a) = Unequal() = 0
        if len(args) <= 1:
            return EXPRZERO
        else:
            return super(ExprUnequal, cls).__new__(cls)

    def __str__(self):
        return "Unequal(" + self.args_str(", ") + ")"

    # From Expression
    def invert(self):
        obj = ExprEqual(*self.args)
        obj.simplified = self._simplified
        return obj

    def simplify(self):
        if self._simplified:
            return self

        args = {arg.simplify() for arg in self.args}

        if EXPRZERO in args:
            # Unequal(0, 1, ...) = 1
            if EXPRONE in args:
                return EXPRONE
            # Unequal(0, x0, x1, ...) = Or(x0, x1, ...)
            else:
                args.remove(EXPRZERO)
                return ExprOr(*args).simplify()
        # Unequal(1, x0, x1, ...) = Nand(x0, x1, ...)
        if EXPRONE in args:
            args.remove(EXPRONE)
            return ExprNand(*args).simplify()

        # no constants; all simplified
        temps, args = args, set()
        while temps:
            arg = temps.pop()
            # Unequal(a, -a) = 1
            if isinstance(arg, ExprLiteral) and -arg in args:
                return EXPRONE
            else:
                args.add(arg)

        obj = self.__class__(*args)
        obj.simplified = True
        return obj

    def factor(self, conj=False):
        if conj:
            any0 = ExprOr(*[arg.invert().factor() for arg in self.args])
            any1 = ExprOr(*[arg.factor() for arg in self.args])
            return ExprAnd(any0, any1).simplify()
        else:
            args = list()
            for arg1, arg2 in itertools.combinations(self.args, 2):
                args.append(ExprAnd(arg1.invert().factor(), arg2.factor()))
                args.append(ExprAnd(arg1.factor(), arg2.invert().factor()))
            return ExprOr(*args).simplify()


class ExprImplies(_ArgumentContainer):
    """Expression implication operator"""

    ASTOP = 'implies'
    PRECEDENCE = 3

    def __init__(self, p, q):
        super(ExprImplies, self).__init__(p, q)

    def __str__(self):
        parts = list()
        for arg in self.args:
            # lower precedence: ?:
            if arg.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        # Rightwards double arrow - 21D2
        return " ⇒ ".join(parts)

    # From Expression
    def invert(self):
        args = (self.args[0], self.args[1].invert())
        return ExprAnd(*args).simplify()

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
        # p => p = 1
        elif p == q:
            return EXPRONE
        # -p => p = p
        elif isinstance(p, ExprLiteral) and -p == q:
            return q

        obj = self.__class__(p, q)
        obj.simplified = True
        return obj

    def factor(self, conj=False):
        # pylint: disable=W0632
        p, q = self.args
        args = list()
        args.append(p.invert().factor())
        args.append(q.factor())
        return ExprOr(*args).simplify()

    @cached_property
    def depth(self):
        return max(arg.depth + 1 for arg in self.args)


class ExprITE(_ArgumentContainer):
    """Expression if-then-else ternary operator"""

    ASTOP = 'ite'
    PRECEDENCE = 4

    def __init__(self, s, d1, d0):
        super(ExprITE, self).__init__(s, d1, d0)

    def __str__(self):
        parts = list()
        for arg in self.args:
            # lower precedence:
            if arg.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + str(arg) + ')')
            else:
                parts.append(str(arg))
        return "{} ? {} : {}".format(*parts)

    # From Expression
    def invert(self):
        s = self.args[0]
        d1 = self.args[1].invert()
        d0 = self.args[2].invert()
        return ExprITE(s, d1, d0).simplify()

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

        obj = self.__class__(s, d1, d0)
        obj.simplified = True
        return obj

    def factor(self, conj=False):
        # pylint: disable=W0632
        s, d1, d0 = self.args
        if conj:
            arg0 = ExprOr(s.invert().factor(), d1.factor())
            arg1 = ExprOr(s.factor(), d0.factor())
            return ExprAnd(arg0, arg1).simplify()
        else:
            arg0 = ExprAnd(s.factor(), d1.factor())
            arg1 = ExprAnd(s.invert().factor(), d0.factor())
            return ExprOr(arg0, arg1).simplify()

    @cached_property
    def depth(self):
        return max(arg.depth + 2 for arg in self.args)


class DimacsCNF(object):
    """Wrapper class for a DIMACS CNF representation"""

    def __init__(self, expr):
        if not isinstance(expr, Expression):
            fstr = "expected expr to be an Expression, got {0.__name__}"
            raise TypeError(fstr.format(type(expr)))
        if not expr.is_cnf():
            raise ValueError("expected expr to be in conjunctive normal form")

        self.lit2idx = dict()
        self.idx2var = dict()
        for i, v in enumerate(expr.inputs, start=1):
            self.lit2idx[v] = i
            self.lit2idx[-v] = -i
            self.idx2var[i] = v

        if expr is EXPRONE:
            clauses = []
        elif isinstance(expr, ExprLiteral):
            clauses = [[self.lit2idx[expr]]]
        elif isinstance(expr, ExprOr) and expr.depth == 1:
            clauses = [[self.lit2idx[lit] for lit in expr.args]]
        elif isinstance(expr, ExprAnd) and expr.depth == 1:
            clauses = [[self.lit2idx[lit]] for lit in expr.args]
        else:
            clauses = [[self.lit2idx[lit] for lit in arg.arg_set]
                        for arg in expr.args]
        self.clauses = {frozenset(clause) for clause in clauses}

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "p cnf {0.nvars} {0.nclauses}\n{0._formula}".format(self)

    @property
    def nvars(self):
        """Return the count of variables in the CNF."""
        return len(self.idx2var)

    @property
    def nclauses(self):
        """Return the count of clauses in the CNF."""
        return len(self.clauses)

    @property
    def _formula(self):
        """Return the formula string."""
        return "\n".join(" ".join(str(lit) for lit in clause) + " 0"
                         for clause in self.clauses)

    def soln2point(self, soln):
        """Convert a solution vector to a point."""
        return { self.idx2var[i]: int(val > 0)
                 for i, val in enumerate(soln, start=1) }


def _iter_zeros(expr):
    """Iterate through all upoints that map to element zero."""
    if expr is EXPRZERO:
        yield frozenset(), frozenset()
    elif expr is not EXPRONE:
        v = expr.splitvar
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
        v = expr.splitvar
        upnt0 = frozenset([v.uniqid]), frozenset()
        upnt1 = frozenset(), frozenset([v.uniqid])
        for upnt in [upnt0, upnt1]:
            for one_upnt in _iter_ones(expr.urestrict(upnt)):
                yield (upnt[0] | one_upnt[0], upnt[1] | one_upnt[1])

def _tseitin(expr, auxvarname, auxvars=None):
    """
    Convert a factored expression to a literal, and a list of constraints.
    """
    if isinstance(expr, ExprLiteral):
        return expr, list()
    else:
        if auxvars is None:
            auxvars = list()

        fs = list()
        cons = list()
        for arg in expr.args:
            f, subcons = _tseitin(arg, auxvarname, auxvars)
            fs.append(f)
            cons.extend(subcons)

        auxvarindex = len(auxvars)
        auxvar = exprvar(auxvarname, auxvarindex)
        auxvars.append(auxvar)

        cons.append((auxvar, expr.__class__(*fs)))
        return auxvar, cons

def _complete_sum(dnf):
    """
    Recursive complete_sum function implementation.

    CS(f) = ABS([x1 + CS(0, x2, ..., xn)] * [-x1 + CS(1, x2, ..., xn)])
    """
    if dnf.depth <= 1:
        return dnf
    else:
        v = dnf.splitvar
        fv0, fv1 = dnf.cofactors(v)
        f = And(Or(v, _complete_sum(fv0)), Or(-v, _complete_sum(fv1)))
        if isinstance(f, ExprAnd):
            f = Or(*[And(x, y) for x in f.args[0].arg_set
                               for y in f.args[1].arg_set])
        return f.absorb()


# Convenience dictionaries
ASTOPS = {
    ExprNot.ASTOP     : ExprNot,
    ExprOr.ASTOP      : ExprOr,
    ExprAnd.ASTOP     : ExprAnd,
    ExprNor.ASTOP     : ExprNor,
    ExprNand.ASTOP    : ExprNand,
    ExprXor.ASTOP     : ExprXor,
    ExprXnor.ASTOP    : ExprXnor,
    ExprEqual.ASTOP   : ExprEqual,
    ExprUnequal.ASTOP : ExprUnequal,
    ExprImplies.ASTOP : ExprImplies,
    ExprITE.ASTOP     : ExprITE,

    'onehot0'  : OneHot0,
    'onehot'   : OneHot,
    'majority' : Majority,
}

EXCLOPS = {
    ExprXor.PARITY  : ExprXor,
    ExprXnor.PARITY : ExprXnor
}
