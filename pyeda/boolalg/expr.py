"""
The :mod:`pyeda.boolalg.expr` module implements
Boolean functions represented as expressions.

Data Types:

abstract syntax tree
   A nested tuple of entries that represents an expression.
   It is defined recursively::

      ast := ('const', bool)
           | ('var', names, indices)
           | ('not', ast)
           | ('implies', ast, ast)
           | ('ite', ast, ast, ast)
           | (func, ast, ...)

      bool := 0 | 1

      names := (name, ...)

      indices := (index, ...)

      func := 'or'
            | 'nor'
            | 'and'
            | 'nand'
            | 'xor'
            | 'xnor'
            | 'equal'
            | 'unequal'
            | 'onehot0'
            | 'onehot'
            | 'majority'
            | 'achillesheel'

Interface Functions:

* :func:`exprvar` --- Return a unique expression variable
* :func:`expr` --- Convert an arbitrary object into an Expression
* :func:`ast2expr` --- Convert an abstract syntax tree to an Expression
* :func:`expr2dimacscnf` --- Convert an expression into an equivalent DIMACS CNF
* :func:`upoint2exprpoint` --- Convert an untyped point to an Expression point

* :func:`Not` --- Expression negation operator
* :func:`Or` --- Expression disjunction (sum, OR) operator
* :func:`And` --- Expression conjunction (product, AND) operator

* :func:`Nor` --- Expression NOR (not OR) operator
* :func:`Nand` --- Expression NAND (not AND) operator
* :func:`Xor` --- Expression exclusive or (XOR) operator
* :func:`Xnor` --- Expression exclusive nor (XNOR) operator
* :func:`Equal` --- Expression equality operator
* :func:`Unequal` --- Expression inequality operator
* :func:`Implies` --- Expression implication operator
* :func:`ITE` --- Expression If-Then-Else (ITE) operator

* :func:`OneHot0`
* :func:`OneHot`
* :func:`Majority`
* :func:`AchillesHeel`
* :func:`Mux`

Interface Classes:

* :class:`Expression`

  * :class:`Atom`

    * :class:`ExprConstant`
    * :class:`ExprLiteral`

      * :class:`ExprVariable`
      * :class:`ExprComplement`

  * :class:`Operator`

    * :class:`NaryOp`

      * :class:`OrAndOp`

        * :class:`ExprOr`
        * :class:`ExprAnd`

      * :class:`ExprXor`
      * :class:`ExprEqual`

    * :class:`ExprNot`
    * :class:`ExprImplies`
    * :class:`ExprITE`

* :class:`NormalForm`

  * :class:`DisjNormalForm`
  * :class:`ConjNormalForm`

    * :class:`DimacsCNF`
"""

# Disable "redefining name from outer scope"
# pylint: disable=W0621

import collections
import itertools
from warnings import warn

import pyeda.parsing.boolexpr
from pyeda.boolalg import boolfunc, sat
from pyeda.util import bit_on, clog2, parity, cached_property

# NOTE: This is a hack for readthedocs Sphinx autodoc
try:
    from pyeda.boolalg import picosat
except ImportError: # pragma: no cover
    pass


# existing ExprVariable/ExprLiteral references
_LITS = dict()

# satisfy_one literal assumptions
_ASSUMPTIONS = set()


def _assume2upoint():
    """Convert global assumptions to an untyped point."""
    return (
        frozenset(lit.v.uniqid for lit in _ASSUMPTIONS
                  if isinstance(lit, ExprComplement)),
        frozenset(lit.uniqid for lit in _ASSUMPTIONS
                  if isinstance(lit, ExprVariable))
    )


def exprvar(name, index=None):
    r"""Return a unique Expression variable.

    A Boolean *variable* is an abstract numerical quantity that may assume any
    value in the set :math:`B = \{0, 1\}`.
    The ``exprvar`` function returns a unique Boolean variable instance
    represented by an expression.
    Variable instances may be used to symbolically construct larger expressions.

    A variable is defined by one or more *names*,
    and zero or more *indices*.
    Multiple names establish hierarchical namespaces,
    and multiple indices group several related variables.
    If the ``name`` parameter is a single ``str``,
    it will be converted to ``(name, )``.
    The ``index`` parameter is optional;
    when empty, it will be converted to an empty tuple ``()``.
    If the ``index`` parameter is a single ``int``,
    it will be converted to ``(index, )``.

    Given identical names and indices, the ``exprvar`` function will always
    return the same variable:

    >>> exprvar('a', 0) is exprvar('a', 0)
    True

    To create several single-letter variables:

    >>> a, b, c, d = map(exprvar, 'abcd')

    To create variables with multiple names (inner-most first):

    >>> fifo_push = exprvar(('push', 'fifo'))
    >>> fifo_pop = exprvar(('pop', 'fifo'))

    .. seealso::
       For creating arrays of variables with incremental indices,
       use the :func:`pyeda.boolalg.bfarray.exprvars` function.
    """
    bvar = boolfunc.var(name, index)
    try:
        var = _LITS[bvar.uniqid]
    except KeyError:
        var = _LITS[bvar.uniqid] = ExprVariable(bvar)
    return var


def _exprcomp(v):
    """Return an Expression Complement."""
    uniqid = -v.uniqid
    try:
        comp = _LITS[uniqid]
    except KeyError:
        comp = _LITS[uniqid] = ExprComplement(v)
    return comp


def expr(obj, simplify=True):
    """Convert an arbitrary object into an Expression."""
    if isinstance(obj, Expression):
        return obj
    # False, True, 0, 1
    elif isinstance(obj, int) and obj in {0, 1}:
        return CONSTANTS[obj]
    elif type(obj) is str:
        ex = ast2expr(pyeda.parsing.boolexpr.parse(obj))
        if simplify:
            ex = ex.simplify()
        return ex
    else:
        return CONSTANTS[bool(obj)]


def ast2expr(ast):
    """Convert an abstract syntax tree to an Expression."""
    if ast[0] == 'const':
        return CONSTANTS[ast[1]]
    elif ast[0] == 'var':
        return exprvar(ast[1], ast[2])
    else:
        xs = [ast2expr(x) for x in ast[1:]]
        return ASTOPS[ast[0]](*xs)


def expr2dimacscnf(expr):
    """Convert an expression into an equivalent DIMACS CNF."""
    if not isinstance(expr, Expression):
        fstr = "expected expr to be an Expression, got {0.__name__}"
        raise TypeError(fstr.format(type(expr)))
    litmap, nvars, clauses = expr.encode_cnf()
    return litmap, DimacsCNF(nvars, clauses)


def expr2dimacssat(expr): # pragma: no cover
    """Convert an expression into an equivalent DIMACS SAT string."""
    if not isinstance(expr, Expression):
        fstr = "expected expr to be an Expression, got {0.__name__}"
        raise TypeError(fstr.format(type(expr)))
    if not expr.simplified:
        raise ValueError("expected expr to be simplified")

    litmap, nvars = expr.encode_inputs()

    formula = _expr2sat(expr, litmap)
    if 'xor' in formula:
        if '=' in formula:
            fmt = 'satex'
        else:
            fmt = 'satx'
    elif '=' in formula:
        fmt = 'sate'
    else:
        fmt = 'sat'

    return "p {} {}\n{}".format(fmt, nvars, formula)


def _expr2sat(expr, litmap): # pragma: no cover
    """Convert an expression to a DIMACS SAT string."""
    if isinstance(expr, ExprLiteral):
        return str(litmap[expr])
    elif isinstance(expr, ExprNot):
        return "-(" + _expr2sat(expr.x, litmap) + ")"
    elif isinstance(expr, ExprOr):
        return "+(" + " ".join(_expr2sat(x, litmap)
                               for x in expr.xs) + ")"
    elif isinstance(expr, ExprAnd):
        return "*(" + " ".join(_expr2sat(x, litmap)
                               for x in expr.xs) + ")"
    elif isinstance(expr, ExprXor):
        return ("xor(" + " ".join(_expr2sat(x, litmap)
                                  for x in expr.xs) + ")")
    elif isinstance(expr, ExprEqual):
        return "=(" + " ".join(_expr2sat(x, litmap)
                               for x in expr.xs) + ")"
    else:
        fstr = ("expected expr to be a Literal or Not/Or/And/Xor/Equal op, "
                "got {0.__name__}")
        raise ValueError(fstr.format(type(expr)))


def upoint2exprpoint(upoint):
    """Convert an untyped point to an Expression point."""
    point = dict()
    for uniqid in upoint[0]:
        point[_LITS[uniqid]] = 0
    for uniqid in upoint[1]:
        point[_LITS[uniqid]] = 1
    return point


# primitive functions
def Not(x, simplify=True):
    """Expression negation operator

    If *simplify* is ``True``, return a simplified expression.
    """
    x = Expression.box(x)
    expr = ExprNot(x)
    if simplify:
        expr = expr.simplify()
    return expr


def Or(*xs, simplify=True):
    """Expression disjunction (sum, OR) operator

    If *simplify* is ``True``, return a simplified expression.
    """
    xs = [Expression.box(x) for x in xs]
    expr = ExprOr(*xs)
    if simplify:
        expr = expr.simplify()
    return expr


def And(*xs, simplify=True):
    """Expression conjunction (product, AND) operator

    If *simplify* is ``True``, return a simplified expression.
    """
    xs = [Expression.box(x) for x in xs]
    expr = ExprAnd(*xs)
    if simplify:
        expr = expr.simplify()
    return expr


# secondary functions
def Xor(*xs, simplify=True):
    """Expression exclusive or (XOR) operator

    If *simplify* is ``True``, return a simplified expression.
    """
    xs = [Expression.box(x) for x in xs]
    expr = ExprXor(*xs)
    if simplify:
        expr = expr.simplify()
    return expr


def Equal(*xs, simplify=True):
    """Expression equality operator

    If *simplify* is ``True``, return a simplified expression.
    """
    xs = [Expression.box(x) for x in xs]
    expr = ExprEqual(*xs)
    if simplify:
        expr = expr.simplify()
    return expr


def Implies(p, q, simplify=True):
    """Expression implication operator

    If *simplify* is ``True``, return a simplified expression.
    """
    p = Expression.box(p)
    q = Expression.box(q)
    expr = ExprImplies(p, q)
    if simplify:
        expr = expr.simplify()
    return expr


def ITE(s, d1, d0, simplify=True):
    """Expression If-Then-Else (ITE) operator

    If *simplify* is ``True``, return a simplified expression.
    """
    s = Expression.box(s)
    d1 = Expression.box(d1)
    d0 = Expression.box(d0)
    expr = ExprITE(s, d1, d0)
    if simplify:
        expr = expr.simplify()
    return expr


# high order functions
def Nor(*xs, simplify=True):
    """Expression NOR (not OR) operator

    If *simplify* is ``True``, return a simplified expression.
    """
    xs = [Expression.box(x) for x in xs]
    expr = ExprNot(ExprOr(*xs))
    if simplify:
        expr = expr.simplify()
    return expr


def Nand(*xs, simplify=True):
    """Expression NAND (not AND) operator

    If *simplify* is ``True``, return a simplified expression.
    """
    xs = [Expression.box(x) for x in xs]
    expr = ExprNot(ExprAnd(*xs))
    if simplify:
        expr = expr.simplify()
    return expr


def Xnor(*xs, simplify=True):
    """Expression exclusive nor (XNOR) operator

    If *simplify* is ``True``, return a simplified expression.
    """
    xs = [Expression.box(x) for x in xs]
    expr = ExprNot(ExprXor(*xs))
    if simplify:
        expr = expr.simplify()
    return expr


def Unequal(*xs, simplify=True):
    """Expression inequality operator

    If *simplify* is ``True``, return a simplified expression.
    """
    xs = [Expression.box(x) for x in xs]
    expr = ExprNot(ExprEqual(*xs))
    if simplify:
        expr = expr.simplify()
    return expr


def OneHot0(*xs, simplify=True, conj=True):
    """
    Return an expression that means
    "at most one input function is true".

    If *simplify* is ``True``, return a simplified expression.

    If *conj* is ``True``, return a CNF.
    Otherwise, return a DNF.
    """
    xs = [Expression.box(x) for x in xs]
    terms = list()
    if conj:
        for x0, x1 in itertools.combinations(xs, 2):
            terms.append(ExprOr(ExprNot(x0), ExprNot(x1)))
        expr = ExprAnd(*terms)
    else:
        for _xs in itertools.combinations(xs, len(xs) - 1):
            terms.append(ExprAnd(*[ExprNot(x) for x in _xs]))
        expr = ExprOr(*terms)
    if simplify:
        expr = expr.simplify()
    return expr


def OneHot(*xs, simplify=True, conj=True):
    """
    Return an expression that means
    "exactly one input function is true".

    If *simplify* is ``True``, return a simplified expression.

    If *conj* is ``True``, return a CNF.
    Otherwise, return a DNF.
    """
    xs = [Expression.box(x) for x in xs]
    terms = list()
    if conj:
        for x0, x1 in itertools.combinations(xs, 2):
            terms.append(ExprOr(ExprNot(x0), ExprNot(x1)))
        terms.append(ExprOr(*xs))
        expr = ExprAnd(*terms)
    else:
        for i, xi in enumerate(xs):
            zeros = [ExprNot(x) for x in xs[:i] + xs[i+1:]]
            terms.append(ExprAnd(xi, *zeros))
        expr = ExprOr(*terms)
    if simplify:
        expr = expr.simplify()
    return expr


def Majority(*xs, simplify=True, conj=False):
    """
    Return an expression that means
    "the majority of input functions are true".

    If *simplify* is ``True``, return a simplified expression.

    If *conj* is ``True``, return a CNF.
    Otherwise, return a DNF.
    """
    xs = [Expression.box(x) for x in xs]
    if conj:
        terms = list()
        for _xs in itertools.combinations(xs, (len(xs) + 1) // 2):
            terms.append(ExprOr(*_xs))
        expr = ExprAnd(*terms)
    else:
        terms = list()
        for _xs in itertools.combinations(xs, len(xs) // 2 + 1):
            terms.append(ExprAnd(*_xs))
        expr = ExprOr(*terms)
    if simplify:
        expr = expr.simplify()
    return expr


def AchillesHeel(*xs, simplify=True):
    r"""
    Return the Achille's Heel function, defined as:
    :math:`\prod_{i=0}^{n/2-1}{X_{2i} + X_{2i+1}}`.

    If *simplify* is ``True``, return a simplified expression.
    """
    nargs = len(xs)
    if nargs & 1:
        fstr = "expected an even number of arguments, got {}"
        raise ValueError(fstr.format(nargs))
    xs = [Expression.box(x) for x in xs]
    expr = ExprAnd(*[ExprOr(xs[2*i], xs[2*i+1]) for i in range(nargs // 2)])
    if simplify:
        expr = expr.simplify()
    return expr


def Mux(fs, sel, simplify=True):
    """
    Return an expression that multiplexes a sequence of input functions over a
    sequence of select functions.
    """
    # convert Mux([a, b], x) to Mux([a, b], [x])
    if isinstance(sel, Expression):
        sel = [sel]

    if len(sel) < clog2(len(fs)):
        fstr = "expected at least {} select bits, got {}"
        raise ValueError(fstr.format(clog2(len(fs)), len(sel)))

    it = boolfunc.iter_terms(sel)
    expr = ExprOr(*[ExprAnd(f, *next(it)) for f in fs])
    if simplify:
        expr = expr.simplify()
    return expr


def ForAll(vs, expr): # pragma: no cover
    """
    Return an expression that means
    "for all variables in *vs*, *expr* is true".
    """
    return And(*expr.cofactors(vs))


def Exists(vs, expr): # pragma: no cover
    """
    Return an expression that means
    "there exists a variable in *vs* such that *expr* is true".
    """
    return Or(*expr.cofactors(vs))


class Expression(boolfunc.Function):
    """Boolean function represented by a logic expression

    .. seealso::
       This is a subclass of :class:`pyeda.boolalg.boolfunc.Function`

    An expression is a tree data structure with operators at the branches,
    and constants/literals at the leaves.
    A literal is a variable or its complement.

    There are two ways to construct an expression:

    * Convert another function representation.
    * Use operators on existing expressions.

    Use the ``exprvar`` function to create expression variables,
    and use the Python ``~|&^`` operators for NOT, OR, AND, XOR.
    Additionally, expressions overload ``>>`` for IMPLIES.

    For example::

       >>> a, b, c, d, p, q = map(exprvar, 'abcdpq')
       >>> f = ~a | b & c ^ d
       >>> g = p >> q

    To create unsimplified expressions, use class constructors::

       >>> ExprOr(0, a)
       Or(0, a)

    To create simplified expressions,
    use function form operators with ``simplify=True``,
    or Python ``~|&^`` operators::

       >>> Or(0, a)
       a
       >>> 0 | a
       a
    """
    ASTOP = NotImplemented
    PRECEDENCE = -1

    def __init__(self):
        self._simplified = False
        self._inverse = None

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other): # pragma: no cover
        return id(self) < id(other)

    def to_unicode(self):
        """Return a string representation using Unicode symbols."""
        raise NotImplementedError()

    def to_latex(self):
        """Return a string representation using Latex."""
        raise NotImplementedError()

    # Operators
    def __invert__(self):
        return self.simplify()._inv

    def __or__(self, g):
        return ExprOr(self, self.box(g)).simplify()

    def __and__(self, g):
        return ExprAnd(self, self.box(g)).simplify()

    def __xor__(self, g):
        return ExprXor(self, self.box(g)).simplify()

    def __rshift__(self, g):
        r"""Boolean implication operator

        +-----------+-----------+----------------------+
        | :math:`f` | :math:`g` | :math:`f \implies g` |
        +===========+===========+======================+
        |         0 |         0 |                    1 |
        +-----------+-----------+----------------------+
        |         0 |         1 |                    1 |
        +-----------+-----------+----------------------+
        |         1 |         0 |                    0 |
        +-----------+-----------+----------------------+
        |         1 |         1 |                    1 |
        +-----------+-----------+----------------------+
        """
        return ExprImplies(self, self.box(g)).simplify()

    def __rrshift__(self, g):
        """Reverse Boolean implication operator"""
        return ExprImplies(self.box(g), self).simplify()

    # From Function
    @cached_property
    def inputs(self):
        return tuple(sorted(self.support))

    def urestrict(self, upoint):
        intersect = upoint[0] & upoint[1]
        if intersect:
            parts = list()
            for uniqid in intersect:
                v = _LITS[uniqid]
                parts += [str(v), str(~v)]
            raise ValueError("conflicting constraints: " + ", ".join(parts))
        return self._urestrict2(upoint)

    def _urestrict1(self, upoint):
        """Implementation of restrict after error-checking."""
        raise NotImplementedError()

    def _urestrict2(self, upoint):
        """Implementation of restrict after error-checking."""
        return self._urestrict1(upoint).simplify()

    def satisfy_one(self):
        if self.is_cnf():
            litmap, cnf = expr2dimacscnf(self)
            assumptions = [litmap[lit] for lit in _ASSUMPTIONS]
            soln = cnf.satisfy_one(assumptions)
            if soln is None:
                return None
            else:
                return cnf.soln2point(soln, litmap)
        else:
            if _ASSUMPTIONS:
                aupnt = _assume2upoint()
                upoint = sat.backtrack(self.urestrict(aupnt))
                upoint = (upoint[0] | aupnt[0], upoint[1] | aupnt[1])
            else:
                upoint = sat.backtrack(self)
        if upoint is None:
            return None
        else:
            return upoint2exprpoint(upoint)

    def satisfy_all(self):
        if self.is_cnf():
            litmap, cnf = expr2dimacscnf(self)
            for soln in cnf.satisfy_all():
                yield cnf.soln2point(soln, litmap)
        else:
            for upoint in sat.iter_backtrack(self):
                yield upoint2exprpoint(upoint)

    def is_zero(self):
        return False

    def is_one(self):
        return False

    @staticmethod
    def box(obj):
        if isinstance(obj, Expression):
            return obj
        # False, True, 0, 1
        elif isinstance(obj, int) and obj in {0, 1}:
            return CONSTANTS[obj]
        elif type(obj) is str:
            return ast2expr(pyeda.parsing.boolexpr.parse(obj))
        else:
            return CONSTANTS[bool(obj)]

    # Specific to Expression
    def traverse(self):
        """Iterate through all nodes in this expression in DFS order."""
        yield from self._traverse(set())

    def _traverse(self, visited):
        """Iterate through all nodes in this expression in DFS order."""
        raise NotImplementedError()

    @property
    def _inv(self):
        if self._inverse is None:
            self._inverse = ExprNot(self)
        return self._inverse

    def simplify(self):
        """Return a simplified expression."""
        raise NotImplementedError()

    @property
    def simplified(self):
        """Return True if the expression is simplified."""
        return self._simplified

    @property
    def depth(self):
        """Return the depth of the expression tree.

        Expression depth is defined recursively:

        1. A leaf node (constant or literal) has zero depth.
        2. A branch node (operator) has depth equal to the maximum depth of
           its children (arguments) plus one.
        """
        raise NotImplementedError()

    def to_ast(self):
        """Return the expression converted to an abstract syntax tree."""
        raise NotImplementedError()

    def expand(self, vs=None, conj=False):
        """Return the Shannon expansion with respect to a list of variables."""
        vs = self._expect_vars(vs)
        if vs:
            outer, inner = (ExprAnd, ExprOr) if conj else (ExprOr, ExprAnd)
            terms = [inner(self.restrict(p),
                           *boolfunc.point2term(p, conj)).simplify()
                     for p in boolfunc.iter_points(vs)]
            if conj:
                terms = [term for term in terms if term is not EXPRONE]
            else:
                terms = [term for term in terms if term is not EXPRZERO]
            return outer(*terms)
        else:
            return self

    def to_nnf(self, conj=False):
        """Return the expression in negation normal form (NNF).

        An NNF expression is one of the following:

        * A literal.
        * A disjunction / conjunction of NNF expressions.

        Parameters

        conj : bool
            Always choose a conjunctive form when there's a choice
        """
        raise NotImplementedError()

    def _inv_nnf(self, conj=False):
        """Return an inverted factored expression."""
        raise NotImplementedError()

    def _flatten(self, op):
        """Return a factored, flattened expression."""
        raise NotImplementedError()

    def flatten(self, op):
        r"""Return a factored, flattened expression.

        Use the distributive law to flatten all nested expressions:

        .. math::
           a + (b \cdot c) = (a + b) \cdot (a + c)

           a \cdot (b + c) = (a \cdot b) + (a \cdot c)

        op : ExprOr or ExprAnd
            The operator you want to flatten. For example, if you want to
            produce an ExprOr expression, flatten all the nested ExprAnds.
        """
        if op is ExprOr or op is ExprAnd:
            return self.to_nnf()._flatten(op)
        else:
            raise ValueError("expected op to be ExprOr or ExprAnd")

    def to_dnf(self, flatten=True):
        """Return the expression in disjunctive normal form."""
        if flatten:
            return self.to_nnf()._flatten(ExprAnd)
        else:
            terms = list()
            for upnt in _iter_ones(self):
                lits = [~_LITS[uniqid] for uniqid in upnt[0]]
                lits += [_LITS[uniqid] for uniqid in upnt[1]]
                terms.append(ExprAnd(*lits).simplify())
            return ExprOr(*terms).simplify()

    def to_cdnf(self, flatten=True):
        """Return the expression in canonical disjunctive normal form."""
        return self.to_dnf(flatten)._reduce()

    def is_dnf(self):
        """Return True if this expression is in disjunctive normal form."""
        # pylint: disable=R0201
        return False

    def to_cnf(self, flatten=True):
        """Return the expression in conjunctive normal form."""
        if flatten:
            return self.to_nnf()._flatten(ExprOr)
        else:
            terms = list()
            for upnt in _iter_zeros(self):
                lits = [_LITS[uniqid] for uniqid in upnt[0]]
                lits += [~_LITS[uniqid] for uniqid in upnt[1]]
                terms.append(ExprOr(*lits).simplify())
            return ExprAnd(*terms).simplify()

    def to_ccnf(self, flatten=True):
        """Return the expression in canonical conjunctive normal form."""
        return self.to_cnf(flatten)._reduce()

    def is_cnf(self):
        """Return True if this expression is in conjunctive normal form."""
        # pylint: disable=R0201
        return False

    @cached_property
    def _cover(self):
        """Return the cover representation."""
        raise NotImplementedError()

    @property
    def cover(self):
        """Return the DNF expression as a cover of cubes."""
        if self.is_dnf():
            return self._cover
        else:
            raise ValueError("expected a DNF expression")

    def _absorb(self):
        """Return the DNF/CNF expression after absorption."""
        raise NotImplementedError()

    def absorb(self):
        r"""Return the DNF/CNF expression after absorption.

        .. math::
           a + (a \cdot b) = a

           a \cdot (a + b) = a
        """
        if self.is_dnf() or self.is_cnf():
            return self._absorb()
        else:
            raise ValueError("expected expression to be in normal form")

    def _reduce(self):
        """Reduce the DNF/CNF expression to a canonical form."""
        raise NotImplementedError

    def reduce(self):
        """Reduce the DNF/CNF expression to a canonical form."""
        if self.is_dnf() or self.is_cnf():
            return self._reduce()
        else:
            raise ValueError("expected expression to be in normal form")

    def encode_inputs(self):
        """Return a compact encoding for input variables."""
        litmap = dict()
        nvars = 0
        for i, v in enumerate(self.inputs, start=1):
            litmap[v] = i
            litmap[~v] = -i
            litmap[i] = v
            litmap[-i] = ~v
            nvars += 1
        return litmap, nvars

    def _encode_clause(self, litmap):
        """Encode as a compact DNF/CNF clause."""
        raise NotImplementedError()

    def _encode_dnf(self):
        """Encode as a compact DNF."""
        raise NotImplementedError()

    def _encode_cnf(self):
        """Encode as a compact CNF."""
        raise NotImplementedError()

    def encode_dnf(self):
        """Encode as a compact DNF."""
        if self.is_dnf():
            return self._encode_dnf()
        else:
            raise ValueError("expected a DNF expression")

    def encode_cnf(self):
        """Encode as a compact CNF."""
        if self.is_cnf():
            return self._encode_cnf()
        else:
            raise ValueError("expected a CNF expression")

    def tseitin(self, auxvarname='aux'):
        """Convert the expression to Tseitin's encoding."""
        if self.is_cnf():
            return self

        _, constraints = _tseitin(self.to_nnf(), auxvarname)
        fst = constraints[-1][1]
        rst = [ExprEqual(f, expr).to_cnf() for f, expr in constraints[:-1]]
        return ExprAnd(fst, *rst).simplify()

    def complete_sum(self):
        """Return a DNF that contains all prime implicants."""
        if self.is_dnf():
            dnf = self
        else:
            dnf = self.to_dnf(flatten=False)
        return _complete_sum(dnf)

    def equivalent(self, other):
        """Return True if this expression is equivalent to other."""
        f = ExprXor(self, self.box(other)).simplify()
        return f.satisfy_one() is None

    def to_dot(self, name='EXPR'): # pragma: no cover
        """Convert to DOT language representation."""
        parts = ['graph', name, '{', 'rankdir=BT;']
        for expr in self.traverse():
            if expr is EXPRZERO:
                parts += ['n' + str(id(expr)), '[label=0,shape=box]']
            elif expr is EXPRONE:
                parts += ['n' + str(id(expr)), '[label=1,shape=box]']
            elif isinstance(expr, ExprLiteral):
                parts += ['n' + str(id(expr)),
                          '[label="{}",shape=box]'.format(expr)]
            else:
                parts.append('n' + str(id(expr)))
                parts.append("[label={0.ASTOP},shape=circle]".format(expr))
        for expr in self.traverse():
            if isinstance(expr, ExprNot):
                parts += ['n' + str(id(expr.x)), '--',
                          'n' + str(id(expr))]
            elif isinstance(expr, ExprImplies):
                parts += ['n' + str(id(expr.p)), '--',
                          'n' + str(id(expr)), '[label=p]']
                parts += ['n' + str(id(expr.q)), '--',
                          'n' + str(id(expr)), '[label=q]']
            elif isinstance(expr, ExprITE):
                parts += ['n' + str(id(expr.s)), '--',
                          'n' + str(id(expr)), '[label=s]']
                parts += ['n' + str(id(expr.d1)), '--',
                          'n' + str(id(expr)), '[label=d1]']
                parts += ['n' + str(id(expr.d0)), '--',
                          'n' + str(id(expr)), '[label=d0]']
            elif isinstance(expr, NaryOp):
                for x in expr.xs:
                    parts += ['n' + str(id(x)), '--', 'n' + str(id(expr))]
        parts.append('}')
        return " ".join(parts)


class Atom(Expression):
    """Atomic Expression"""

    # From Expression
    def _traverse(self, visited):
        if self not in visited:
            visited.add(self)
            yield self

    def simplify(self):
        return self

    @property
    def depth(self):
        return 0

    def to_nnf(self, conj=False):
        return self

    def _inv_nnf(self, conj=False):
        return self._inv

    # FactoredExpression
    def _flatten(self, op):
        return self

    def _absorb(self):
        return self

    def _reduce(self):
        return self


class ExprConstant(Atom):
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

    def _urestrict1(self, upoint):
        return self

    def compose(self, mapping):
        return self

    # From Expression
    def to_ast(self):
        return (self.ASTOP, self.VALUE)


class _ExprZero(ExprConstant):
    """
    Expression zero

    .. note:: Never use this class. Use EXPRZERO singleton instead.
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
    def is_dnf(self):
        return True

    @cached_property
    def _cover(self):
        return set()

    def _encode_dnf(self):
        litmap, nvars = self.encode_inputs()
        clauses = set()
        return litmap, nvars, clauses


class _ExprOne(ExprConstant):
    """
    Expression one

    .. note:: Never use this class. Use EXPRONE singleton instead.
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
    def is_cnf(self):
        return True

    def _encode_cnf(self):
        litmap, nvars = self.encode_inputs()
        clauses = set()
        return litmap, nvars, clauses


EXPRZERO = _ExprZero()
EXPRONE = _ExprOne()

EXPRZERO._inverse = EXPRONE
EXPRONE._inverse = EXPRZERO

CONSTANTS = [EXPRZERO, EXPRONE]


class ExprLiteral(Atom):
    """An instance of a variable or of its complement"""
    def __init__(self):
        super(ExprLiteral, self).__init__()
        self._simplified = True

    def __enter__(self):
        _ASSUMPTIONS.add(self)

    def __exit__(self, exc_type, exc_val, traceback):
        _ASSUMPTIONS.discard(self)

    # From Expression
    def is_dnf(self):
        return True

    def is_cnf(self):
        return True

    # FlattenedExpression
    @cached_property
    def _lits(self):
        """Return a frozenset of literals."""
        return frozenset([self])

    @cached_property
    def _cube(self):
        """Return the cube representation."""
        return frozenset([self])

    @cached_property
    def _cover(self):
        return {self._cube}

    def _encode_clause(self, litmap):
        return frozenset([litmap[self]])

    def _encode_dnf(self):
        litmap, nvars = self.encode_inputs()
        clauses = {self._encode_clause(litmap)}
        return litmap, nvars, clauses

    def _encode_cnf(self):
        litmap, nvars = self.encode_inputs()
        clauses = {self._encode_clause(litmap)}
        return litmap, nvars, clauses

    minterm_index = NotImplemented


class ExprVariable(boolfunc.Variable, ExprLiteral):
    """Expression variable"""
    ASTOP = 'var'

    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.names, bvar.indices)
        ExprLiteral.__init__(self)
        self._inverse = _exprcomp(self)

    def to_unicode(self):
        return self.__str__()

    def to_latex(self):
        suffix = ", ".join(str(idx) for idx in self.indices)
        return self.qualname + "_{" + suffix + "}"

    def __lt__(self, other):
        if isinstance(other, ExprConstant):
            return False
        if isinstance(other, ExprVariable):
            return boolfunc.Variable.__lt__(self, other)
        if isinstance(other, ExprComplement):
            return boolfunc.Variable.__lt__(self, other.v)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    # From Function
    @cached_property
    def support(self):
        return frozenset([self, ])

    def _urestrict1(self, upoint):
        if self.uniqid in upoint[0]:
            return EXPRZERO
        elif self.uniqid in upoint[1]:
            return EXPRONE
        else:
            return self

    def compose(self, mapping):
        try:
            return mapping[self].simplify()
        except KeyError:
            return self

    # From Expression
    def to_ast(self):
        return (self.ASTOP, self.names, self.indices)

    minterm_index = 1
    maxterm_index = 0

    @property
    def splitvar(self):
        """Return a good splitting variable."""
        return self


class ExprComplement(ExprLiteral):
    """Expression complement"""
    # Prime - U2032
    SYMBOL = '′'

    def __init__(self, v):
        super(ExprComplement, self).__init__()
        self._inverse = v
        self.v = v
        self.uniqid = -v.uniqid

    def __str__(self):
        return '~' + str(self.v)

    def to_unicode(self):
        return str(self.v) + self.SYMBOL

    def to_latex(self):
        return "\\bar{" + self.v.to_latex() + "}"

    def __lt__(self, other):
        if isinstance(other, ExprConstant):
            return False
        if isinstance(other, ExprVariable):
            return (self.v.names < other.names or
                    self.v.names == other.names and
                    self.v.indices <= other.indices)
        if isinstance(other, ExprComplement):
            return boolfunc.Variable.__lt__(self.v, other.v)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    # From Function
    @cached_property
    def support(self):
        return frozenset([self.v, ])

    def _urestrict1(self, upoint):
        if self.v.uniqid in upoint[0]:
            return EXPRONE
        elif self.v.uniqid in upoint[1]:
            return EXPRZERO
        else:
            return self

    def compose(self, mapping):
        try:
            return mapping[self.v].simplify()._inv
        except KeyError:
            return self

    # From Expression
    def to_ast(self):
        return (ExprNot.ASTOP, self.v.to_ast())

    minterm_index = 0
    maxterm_index = 1

    @property
    def splitvar(self):
        """Return a good splitting variable."""
        return self.v


class Operator(Expression):
    """Operator Expression"""
    STROP = NotImplemented
    ASTOP = NotImplemented

    def __init__(self, *xs):
        super(Operator, self).__init__()
        self.xs = xs

    def __str__(self):
        return self.STROP + "(" + self._joinargs(", ") + ")"

    @property
    def args(self):
        warn("Operator.args is deprecated. Use Operator.xs instead.")
        return self.xs

    # From Function
    @cached_property
    def support(self):
        return frozenset.union(*[x.support for x in self.xs])

    def _urestrict1(self, upoint):
        modified = False
        ys = list()
        for x in self.xs:
            y = x._urestrict1(upoint)
            if y is not x:
                modified = True
            ys.append(y)
        if modified:
            return self.__class__(*ys)
        else:
            return self

    def compose(self, mapping):
        modified = False
        ys = list()
        for x in self.xs:
            y = x.compose(mapping)
            if y is not x:
                modified = True
            ys.append(y)
        if modified:
            return self.__class__(*ys).simplify()
        else:
            return self.simplify()

    # From Expression
    def _traverse(self, visited):
        for x in self.xs:
            yield from x._traverse(visited)
        if self not in visited:
            visited.add(self)
            yield self

    @cached_property
    def depth(self):
        return max(x.depth for x in self.xs) + 1

    def to_ast(self):
        return (self.ASTOP, ) + tuple(x.to_ast() for x in self.xs)

    @cached_property
    def splitvar(self):
        """Return a good splitting variable.

        Heuristic: find the variable that appears in the max # of xs.
        """
        cnt = collections.Counter()
        for x in self.xs:
            for v in self.support:
                cnt[v] += (v in x.support)
        return cnt.most_common(1)[0][0]

    # Specific to Operator
    def _joinargs(self, sep):
        """Return arguments as a string, joined by a separator."""
        return sep.join(str(x) for x in self.xs)


class NaryOp(Operator):
    """Common methods for N-ary expression operators."""
    def _joinargs(self, sep):
        """Return arguments as a string, joined by a separator."""
        return sep.join(str(x) for x in sorted(self.xs))


class ExprOrAnd(NaryOp):
    """Base class for Expression OR/AND expressions"""
    IDENTITY = NotImplemented
    DOMINATOR = NotImplemented

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
    def _urestrict1(self, upoint):
        modified = False
        ys = set()
        for x in self.xs:
            y = x._urestrict1(upoint)
            # speed hack
            if y is self.DOMINATOR:
                return self.DOMINATOR
            elif y is not x:
                modified = True
            ys.add(y)
        if modified:
            return self.__class__(*ys)
        else:
            return self

    # From Expression
    def simplify(self):
        if self._simplified:
            return self

        temps, xs = set(self.xs), set()
        while temps:
            x = temps.pop().simplify()
            if x is self.DOMINATOR:
                return x
            elif x is self.IDENTITY:
                pass
            # associative
            elif isinstance(x, self.__class__):
                temps.update(x.xs)
            # complement
            elif x._inv in xs:
                return self.DOMINATOR
            else:
                xs.add(x)

        # Or() = 0; And() = 1
        if len(xs) == 0:
            obj = self.IDENTITY
        # Or(x) = x, And(x) = x
        elif len(xs) == 1:
            obj = xs.pop()
        else:
            obj = self.__class__(*xs)
            obj._simplified = True
        return obj

    def to_nnf(self, conj=False):
        xs = [x.to_nnf() for x in self.xs]
        return self.__class__(*xs).simplify()

    def _inv_nnf(self, conj=False):
        xs = [x._inv_nnf() for x in self.xs]
        return self.get_dual()(*xs).simplify()

    # Specific to ExprOrAnd
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
        | ~a & ~b & ~c | 000   |
        |  a &  b & ~c | 110   |
        |  a &  b &  c | 111   |
        +--------------+-------+
        | ~a | ~b | ~c | 111   |
        |  a |  b | ~c | 001   |
        |  a |  b |  c | 000   |
        +==============+=======+
        """
        raise NotImplementedError()

    # FactoredExpression
    def _flatten(self, op):
        if isinstance(self, op):
            self_dual = self.get_dual()
            for i, xi in enumerate(self.xs):
                if isinstance(xi, self_dual):
                    others = self.xs[:i] + self.xs[i+1:]
                    xs = [op(x, *others) for x in xi.xs]
                    expr = op.get_dual()(*xs).simplify()
                    return expr._flatten(op)._absorb()
            return self
        else:
            xs = [x._flatten(op)._absorb() if x.depth > 1 else x
                  for x in self.xs]
            return op.get_dual()(*xs).simplify()

    # FlattenedExpression
    @cached_property
    def _lits(self):
        """Return a frozenset of literals."""
        return frozenset(self.xs)

    def _absorb(self):
        dual = self.get_dual()

        # Get rid of all equivalent terms
        temps = {x._lits for x in self.xs}
        xs = list()

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
                x = dual(*fst).simplify()
                xs.append(x)
            temps -= drop_rst

        return self.__class__(*xs).simplify()

    def _reduce(self):
        if self.depth == 1:
            return self

        terms = list()
        indices = set()
        for term in self.xs:
            vs = list(self.support - term.support)
            eterms = self._term_expand(term, vs) if vs else (term, )
            for eterm in eterms:
                if eterm.term_index not in indices:
                    terms.append(eterm)
                    indices.add(eterm.term_index)

        return self.__class__(*terms).simplify()

    def _encode_clause(self, litmap):
        return frozenset(litmap[x] for x in self.xs)

    @staticmethod
    def _term_expand(term, vs):
        """Return a term expanded by a list of variables."""
        raise NotImplementedError()


class ExprOr(ExprOrAnd):
    """Expression OR operator"""
    STROP = 'Or'
    ASTOP = 'or'
    SYMBOL = '+'
    LATEX_SYMBOL = '+'
    PRECEDENCE = 2

    IDENTITY = EXPRZERO
    DOMINATOR = EXPRONE

    def to_unicode(self):
        parts = list()
        for x in sorted(self.xs):
            # lower precedence: implies, equal
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_unicode() + ')')
            else:
                parts.append(x.to_unicode())
        sep = " " + self.SYMBOL + " "
        return sep.join(parts)

    def to_latex(self):
        parts = list()
        for x in sorted(self.xs):
            # lower precedence: implies, equal
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_latex() + ')')
            else:
                parts.append(x.to_latex())
        sep = " " + self.LATEX_SYMBOL + " "
        return sep.join(parts)

    # From Expression
    def is_dnf(self):
        # a | b
        if self.depth == 1:
            return all(isinstance(x, ExprLiteral) for x in self.xs)
        # a | b & c
        elif self.depth == 2:
            return all(isinstance(x, ExprLiteral) or
                       isinstance(x, ExprAnd) and x.is_cnf()
                       for x in self.xs)
        else:
            return False

    def is_cnf(self):
        # a & b
        if self.depth == 1:
            return all(isinstance(x, ExprLiteral) for x in self.xs)
        else:
            return False

    def _encode_dnf(self):
        litmap, nvars = self.encode_inputs()
        clauses = {x._encode_clause(litmap) for x in self.xs}
        return litmap, nvars, clauses

    def _encode_cnf(self):
        litmap, nvars = self.encode_inputs()
        clauses = {self._encode_clause(litmap)}
        return litmap, nvars, clauses

    # Specific to ExprOrAnd
    @staticmethod
    def get_dual():
        return ExprAnd

    # FlattenedExpression
    @cached_property
    def _cover(self):
        return {x._cube for x in self.xs}

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
            if ~v in self.xs:
                index |= 1 << (num - i)
        return index

    @staticmethod
    def _term_expand(term, vs):
        return term.expand(vs, conj=False).xs


class ExprAnd(ExprOrAnd):
    """Expression AND operator"""
    STROP = 'And'
    ASTOP = 'and'
    # Middle dot - U00B7
    SYMBOL = '·'
    LATEX_SYMBOL = '\\cdot'
    PRECEDENCE = 0

    IDENTITY = EXPRONE
    DOMINATOR = EXPRZERO

    def __enter__(self):
        for x in self.xs:
            if isinstance(x, ExprLiteral):
                _ASSUMPTIONS.add(x)
            else:
                raise ValueError("expected assumption to be a literal")

    def __exit__(self, exc_type, exc_val, traceback):
        for x in self.xs:
            if isinstance(x, ExprLiteral):
                _ASSUMPTIONS.discard(x)
            else:
                raise ValueError("expected assumption to be a literal")

    def to_unicode(self):
        parts = list()
        for x in sorted(self.xs):
            # lower precedence: or, xor, implies, equal
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_unicode() + ')')
            else:
                parts.append(x.to_unicode())
        sep = " " + self.SYMBOL + " "
        return sep.join(parts)

    def to_latex(self):
        parts = list()
        for x in sorted(self.xs):
            # lower precedence: or, xor, implies, equal
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_latex() + ')')
            else:
                parts.append(x.to_latex())
        sep = " " + self.LATEX_SYMBOL + " "
        return sep.join(parts)

    # From Expression
    def is_dnf(self):
        # a & b
        if self.depth == 1:
            return all(isinstance(x, ExprLiteral) for x in self.xs)
        else:
            return False

    def is_cnf(self):
        # a & b
        if self.depth == 1:
            return all(isinstance(x, ExprLiteral) for x in self.xs)
        # a & (b | c)
        elif self.depth == 2:
            return all(isinstance(x, ExprLiteral) or
                       isinstance(x, ExprOr) and x.is_dnf()
                       for x in self.xs)
        else:
            return False

    def _encode_dnf(self):
        litmap, nvars = self.encode_inputs()
        clauses = {self._encode_clause(litmap)}
        return litmap, nvars, clauses

    def _encode_cnf(self):
        litmap, nvars = self.encode_inputs()
        clauses = {x._encode_clause(litmap) for x in self.xs}
        return litmap, nvars, clauses

    # From ExprOrAnd
    @staticmethod
    def get_dual():
        return ExprOr

    # FlattenedExpression
    @cached_property
    def _cube(self):
        """Return the cube representation."""
        return frozenset(self.xs)

    @cached_property
    def _cover(self):
        return {self._cube}

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
            if v in self.xs:
                index |= 1 << (num - i)
        return index

    @staticmethod
    def _term_expand(term, vs):
        return term.expand(vs, conj=True).xs


class ExprXor(NaryOp):
    """Expression exclusive OR (XOR) operator"""
    STROP = 'Xor'
    ASTOP = 'xor'
    # Circled plus - U2295
    SYMBOL = '⊕'
    LATEX_SYMBOL = '\\oplus'
    PRECEDENCE = 1
    IDENTITY = EXPRZERO

    def to_unicode(self):
        parts = list()
        for x in sorted(self.xs):
            # lower precedence: or, implies, equal
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_unicode() + ')')
            else:
                parts.append(x.to_unicode())
        sep = " " + self.SYMBOL + " "
        return sep.join(parts)

    def to_latex(self):
        parts = list()
        for x in sorted(self.xs):
            # lower precedence: or, implies, equal
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_latex() + ')')
            else:
                parts.append(x.to_latex())
        sep = " " + self.LATEX_SYMBOL + " "
        return sep.join(parts)

    # From Expression
    def simplify(self):
        if self._simplified:
            return self

        par = 1
        temps, xs = list(self.xs), set()
        while temps:
            x = temps.pop().simplify()
            if isinstance(x, ExprConstant):
                par ^= int(x)
            # associative
            elif isinstance(x, self.__class__):
                temps.extend(x.xs)
            # (x, ~x) is either (0, 1) or (1, 0)
            elif x._inv in xs:
                xs.remove(x._inv)
                par ^= 1
            # (x, x) is either (0, 0) or (1, 1)
            elif x in xs:
                xs.remove(x)
            else:
                xs.add(x)

        # Xor() = 0
        if len(xs) == 0:
            obj = self.IDENTITY
        # Xor(x) = x; Xnor(x) = ~x
        elif len(xs) == 1:
            obj = xs.pop()
        else:
            obj = ExprXor(*xs)
            obj._simplified = True
        return obj if par else obj._inv

    def to_nnf(self, conj=False):
        outer, inner = (ExprAnd, ExprOr) if conj else (ExprOr, ExprAnd)
        terms = list()
        # Walk through all entries in the truth table
        for num in range(1 << len(self.xs)):
            if conj:
                if parity(num) == 0:
                    term = list()
                    for i, xi in enumerate(self.xs):
                        if bit_on(num, i):
                            term.append(xi._inv_nnf())
                        else:
                            term.append(xi.to_nnf())
                    terms.append(inner(*term))
            else:
                if parity(num) == 1:
                    term = list()
                    for i, xi in enumerate(self.xs):
                        if bit_on(num, i):
                            term.append(xi.to_nnf())
                        else:
                            term.append(xi._inv_nnf())
                    terms.append(inner(*term))
        return outer(*terms).simplify()

    def _inv_nnf(self, conj=False):
        outer, inner = (ExprAnd, ExprOr) if conj else (ExprOr, ExprAnd)
        terms = list()
        # Walk through all entries in the truth table
        for num in range(1 << len(self.xs)):
            if conj:
                if parity(num) == 1:
                    term = list()
                    for i, xi in enumerate(self.xs):
                        if bit_on(num, i):
                            term.append(xi._inv_nnf())
                        else:
                            term.append(xi.to_nnf())
                    terms.append(inner(*term))
            else:
                if parity(num) == 0:
                    term = list()
                    for i, xi in enumerate(self.xs):
                        if bit_on(num, i):
                            term.append(xi.to_nnf())
                        else:
                            term.append(xi._inv_nnf())
                    terms.append(inner(*term))
        return outer(*terms).simplify()


class ExprEqual(NaryOp):
    """Expression EQUAL operator"""
    STROP = 'Equal'
    ASTOP = 'equal'
    # Left right double arrow - 21D4
    SYMBOL = '⇔'
    LATEX_SYMBOL = '\\Leftrightarrow'
    PRECEDENCE = 4

    IDENTITY = EXPRONE

    def to_unicode(self):
        parts = list()
        for x in self.xs:
            # lower precedence:
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_unicode() + ')')
            else:
                parts.append(x.to_unicode())
        sep = " " + self.SYMBOL + " "
        return sep.join(parts)

    def to_latex(self):
        parts = list()
        for x in self.xs:
            # lower precedence:
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_latex() + ')')
            else:
                parts.append(x.to_latex())
        sep = " " + self.LATEX_SYMBOL + " "
        return sep.join(parts)

    # From Expression
    def simplify(self):
        if self._simplified:
            return self

        xs = {x.simplify() for x in self.xs}

        if EXPRZERO in xs:
            # Equal(0, 1, ...) = 0
            if EXPRONE in xs:
                return EXPRZERO
            # Equal(0, x0, x1, ...) = Nor(x0, x1, ...)
            else:
                xs.remove(EXPRZERO)
                return ExprOr(*xs).simplify()._inv
        # Equal(1, x0, x1, ...) = And(x0, x1, ...)
        if EXPRONE in xs:
            xs.remove(EXPRONE)
            return ExprAnd(*xs).simplify()

        # no constants; all simplified
        temps, xs = xs, set()
        while temps:
            x = temps.pop()
            # Equal(x, ~x) = 0
            if x._inv in xs:
                return EXPRZERO
            else:
                xs.add(x)

        # Equal(x) = Equal() = 1
        if len(xs) <= 1:
            obj = self.IDENTITY
        else:
            obj = self.__class__(*xs)
            obj._simplified = True
        return obj

    def to_nnf(self, conj=False):
        if conj:
            xs = list()
            for x0, x1 in itertools.combinations(self.xs, 2):
                xs.append(ExprOr(x0._inv_nnf(), x1.to_nnf()))
                xs.append(ExprOr(x0.to_nnf(), x1._inv_nnf()))
            return ExprAnd(*xs).simplify()
        else:
            all0 = ExprAnd(*[x._inv_nnf() for x in self.xs])
            all1 = ExprAnd(*[x.to_nnf() for x in self.xs])
            return ExprOr(all0, all1).simplify()

    def _inv_nnf(self, conj=False):
        if conj:
            any0 = ExprOr(*[x._inv_nnf() for x in self.xs])
            any1 = ExprOr(*[x.to_nnf() for x in self.xs])
            return ExprAnd(any0, any1).simplify()
        else:
            xs = list()
            for x0, x1 in itertools.combinations(self.xs, 2):
                xs.append(ExprAnd(x0._inv_nnf(), x1.to_nnf()))
                xs.append(ExprAnd(x0.to_nnf(), x1._inv_nnf()))
            return ExprOr(*xs).simplify()


class ExprNot(Operator):
    """Expression NOT operator"""
    STROP = 'Not'
    ASTOP = 'not'
    # Logical NOT - U00AC
    SYMBOL = '¬'

    def __new__(cls, x):
        # Primitives
        if isinstance(x, ExprConstant) or isinstance(x, ExprLiteral):
            return x._inv
        # Auto-eliminate double negatives
        elif isinstance(x, ExprNot):
            return x.x
        else:
            return super(ExprNot, cls).__new__(cls)

    def __init__(self, x):
        super(ExprNot, self).__init__(x)
        self._simplified = x._simplified
        self._inverse = x
        self.x = x

    @property
    def arg(self):
        warn("Not.arg is deprecated. Use Not.x instead.")
        return self.xs

    def to_unicode(self):
        return self.SYMBOL + "(" + str(self.x.to_unicode()) + ")"

    def to_latex(self):
        return "\\overline{" + self.x.to_latex() + "}"

    # From Expression
    def simplify(self):
        if self._simplified:
            return self

        return self.x.simplify()._inv

    def to_nnf(self, conj=False):
        return self.x._inv_nnf()

    def _inv_nnf(self, conj=False):
        return self.x.to_nnf()

    def to_ast(self):
        return (self.ASTOP, self.x.to_ast())


class ExprImplies(Operator):
    """Expression implication operator"""
    STROP = 'Implies'
    ASTOP = 'implies'
    # Rightwards double arrow - 21D2
    SYMBOL = '⇒'
    LATEX_SYMBOL = '\\Rightarrow'
    PRECEDENCE = 3

    def __init__(self, p, q):
        super(ExprImplies, self).__init__(p, q)
        self.p = p
        self.q = q

    def to_unicode(self):
        parts = list()
        for x in (self.p, self.q):
            # lower precedence: equal
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_unicode() + ')')
            else:
                parts.append(x.to_unicode())
        sep = " " + self.SYMBOL + " "
        return sep.join(parts)

    def to_latex(self):
        parts = list()
        for x in (self.p, self.q):
            # lower precedence: equal
            if x.PRECEDENCE >= self.PRECEDENCE:
                parts.append('(' + x.to_latex() + ')')
            else:
                parts.append(x.to_latex())
        sep = " " + self.LATEX_SYMBOL + " "
        return sep.join(parts)

    # From Expression
    def simplify(self):
        p = self.p.simplify()
        q = self.q.simplify()

        # 0 => q = 1; p => 1 = 1
        if p is EXPRZERO or q is EXPRONE:
            return EXPRONE
        # 1 => q = q
        elif p is EXPRONE:
            return q
        # p => 0 = ~p
        elif q is EXPRZERO:
            return p._inv
        # p => p = 1
        elif p is q:
            return EXPRONE
        # ~p => p = p
        elif p._inv is q:
            return q

        obj = self.__class__(p, q)
        obj._simplified = True
        return obj

    def to_nnf(self, conj=False):
        return ExprOr(self.p._inv_nnf(), self.q.to_nnf()).simplify()

    def _inv_nnf(self, conj=False):
        return ExprAnd(self.p.to_nnf(), self.q._inv_nnf()).simplify()


class ExprITE(Operator):
    """Expression if-then-else ternary operator"""
    STROP = 'ITE'
    ASTOP = 'ite'

    def __init__(self, s, d1, d0):
        super(ExprITE, self).__init__(s, d1, d0)
        self.s = s
        self.d1 = d1
        self.d0 = d0

    def to_unicode(self):
        unicode_args = [self.s.to_unicode(),
                        self.d1.to_unicode(), self.d0.to_unicode()]
        return "ite({}, {}, {})".format(*unicode_args)

    def to_latex(self):
        latex_args = [self.s.to_latex(), self.d1.to_latex(), self.d0.to_latex()]
        return "ite({}, {}, {})".format(*latex_args)

    # From Expression
    def simplify(self):
        s = self.s.simplify()
        d1 = self.d1.simplify()
        d0 = self.d0.simplify()

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
            # s ? 0 : 1 = ~s
            elif d0 is EXPRONE:
                return s._inv
            # s ? 0 : d0 = ~s & d0
            else:
                return ExprAnd(s._inv, d0).simplify()
        elif d1 is EXPRONE:
            # s ? 1 : 0 = s
            if d0 is EXPRZERO:
                return s
            # s ? 1 : 1 = 1
            elif d0 is EXPRONE:
                return EXPRONE
            # s ? 1 : d0 = s | d0
            else:
                return ExprOr(s, d0).simplify()
        # s ? d1 : 0 = s & d1
        elif d0 is EXPRZERO:
            return ExprAnd(s, d1).simplify()
        # s ? d1 : 1 = ~s | d1
        elif d0 is EXPRONE:
            return ExprOr(s._inv, d1).simplify()
        # s ? d1 : d1 = d1
        elif d1 is d0:
            return d1
        # s ? s : d0 = s | d0
        elif s is d1:
            return ExprOr(s, d0).simplify()
        # s ? d1 : s = s & d1
        elif s is d0:
            return ExprAnd(s, d1).simplify()

        obj = self.__class__(s, d1, d0)
        obj._simplified = True
        return obj

    def to_nnf(self, conj=False):
        if conj:
            # (~s | d1) & (s | d0)
            x0 = ExprOr(self.s._inv_nnf(), self.d1.to_nnf())
            x1 = ExprOr(self.s.to_nnf(), self.d0.to_nnf())
            return ExprAnd(x0, x1).simplify()
        else:
            # s & d1 | ~s & d0
            x0 = ExprAnd(self.s.to_nnf(), self.d1.to_nnf())
            x1 = ExprAnd(self.s._inv_nnf(), self.d0.to_nnf())
            return ExprOr(x0, x1).simplify()

    def _inv_nnf(self, conj=False):
        if conj:
            # (~s | ~d1) & (s | ~d1)
            x0 = ExprOr(self.s._inv_nnf(), self.d1._inv_nnf())
            x1 = ExprOr(self.s.to_nnf(), self.d0._inv_nnf())
            return ExprAnd(x0, x1).simplify()
        else:
            # s & ~d1 | ~s & ~d0
            x0 = ExprAnd(self.s.to_nnf(), self.d1._inv_nnf())
            x1 = ExprAnd(self.s._inv_nnf(), self.d0._inv_nnf())
            return ExprOr(x0, x1).simplify()


class NormalForm:
    """Normal form expression"""
    def __init__(self, nvars, clauses):
        self.nvars = nvars
        self.clauses = clauses

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "\n".join(" ".join(str(idx) for idx in clause) + " 0"
                         for clause in self.clauses)

    @cached_property
    def nclauses(self):
        """Return the count of clauses in the CNF."""
        return len(self.clauses)

    def invert(self):
        """Return the inverse normal form expression."""
        raise NotImplementedError()

    def reduce(self):
        """Reduce to a canonical form."""
        support = frozenset(range(1, self.nvars+1))
        new_clauses = set()
        for clause in self.clauses:
            vs = list(support - {abs(uniqid) for uniqid in clause})
            if vs:
                for num in range(1 << len(vs)):
                    new_part = {v if bit_on(num, i) else ~v
                                for i, v in enumerate(vs)}
                    new_clauses.add(clause | new_part)
            else:
                new_clauses.add(clause)
        return self.__class__(self.nvars, new_clauses)


class DisjNormalForm(NormalForm):
    """Disjunctive normal form expression"""
    def decode(self, litmap):
        """Convert the DNF to an expression."""
        return Or(*[And(*[litmap[idx] for idx in clause])
                    for clause in self.clauses])

    def invert(self):
        clauses = {frozenset(-idx for idx in clause) for clause in self.clauses}
        return ConjNormalForm(self.nvars, clauses)


class ConjNormalForm(NormalForm):
    """Conjunctive normal form expression"""
    def decode(self, litmap):
        """Convert the CNF to an expression."""
        return And(*[Or(*[litmap[idx] for idx in clause])
                     for clause in self.clauses])

    def invert(self):
        clauses = {frozenset(-idx for idx in clause) for clause in self.clauses}
        return DisjNormalForm(self.nvars, clauses)

    def satisfy_one(self, assumptions=None):
        """
        If the input CNF is satisfiable, return a satisfying input point.
        A contradiction will return None.
        """
        return picosat.satisfy_one(self.nvars, self.clauses,
                                   assumptions=assumptions)

    def satisfy_all(self):
        """Iterate through all satisfying input points."""
        yield from picosat.satisfy_all(self.nvars, self.clauses)

    @staticmethod
    def soln2point(soln, litmap):
        """Convert a solution vector to a point."""
        return {litmap[i]: int(val > 0)
                for i, val in enumerate(soln, start=1)}


class DimacsCNF(ConjNormalForm):
    """Wrapper class for a DIMACS CNF representation"""
    def __str__(self):
        formula = super(DimacsCNF, self).__str__()
        return "p cnf {0.nvars} {0.nclauses}\n{1}".format(self, formula)


def _iter_zeros(expr):
    """Iterate through all upoints that map to element zero."""
    if expr is EXPRZERO:
        yield frozenset(), frozenset()
    elif expr is not EXPRONE:
        v = expr.splitvar
        upnt0 = frozenset([v.uniqid]), frozenset()
        upnt1 = frozenset(), frozenset([v.uniqid])
        for upnt in [upnt0, upnt1]:
            for zero_upnt in _iter_zeros(expr._urestrict2(upnt)):
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
            for one_upnt in _iter_ones(expr._urestrict2(upnt)):
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
        constraints = list()
        for x in expr.xs:
            f, subcons = _tseitin(x, auxvarname, auxvars)
            fs.append(f)
            constraints.extend(subcons)

        auxvarindex = len(auxvars)
        auxvar = exprvar(auxvarname, auxvarindex)
        auxvars.append(auxvar)

        constraints.append((auxvar, expr.__class__(*fs)))
        return auxvar, constraints

def _complete_sum(dnf):
    """
    Recursive complete_sum function implementation.

    CS(f) = ABS([x1 | CS(0, x2, ..., xn)] & [~x1 | CS(1, x2, ..., xn)])
    """
    if dnf.depth <= 1:
        return dnf
    else:
        v = dnf.splitvar
        fv0, fv1 = dnf.cofactors(v)
        f = And(Or(v, _complete_sum(fv0)), Or(~v, _complete_sum(fv1)))
        if isinstance(f, ExprAnd):
            f = Or(*[And(x, y)
                     for x in f.xs[0]._lits
                     for y in f.xs[1]._lits])
        return f._absorb()


# Convenience dictionaries
ASTOPS = {
    ExprNot.ASTOP     : ExprNot,
    ExprOr.ASTOP      : ExprOr,
    ExprAnd.ASTOP     : ExprAnd,
    ExprXor.ASTOP     : ExprXor,
    ExprEqual.ASTOP   : ExprEqual,
    ExprImplies.ASTOP : ExprImplies,
    ExprITE.ASTOP     : ExprITE,

    'nor': Nor,
    'nand': Nand,
    'xnor': Xnor,
    'unequal': Unequal,

    'onehot0'  : OneHot0,
    'onehot'   : OneHot,
    'majority' : Majority,
    'achillesheel' : AchillesHeel,
}

