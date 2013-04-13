"""
Normal Form Expressions

Interface Functions:
    expr2nfexpr
    nfexpr2expr

Interface Classes:
    DisjNormalForm
    ConjNormalForm
"""

from collections import Counter

from pyeda.common import boolify, cached_property
from pyeda.boolfunc import Function
from pyeda.expr import Expression, Or, And
from pyeda.sat import backtrack, dpll

B = {0, 1}

def expr2nfexpr(expr):
    """Convert an expression into a normal form representation."""
    if expr.is_dnf():
        cls = DisjNormalForm
    elif expr.is_cnf():
        cls = ConjNormalForm
    else:
        raise TypeError("input is not an expression in normal form")

    int2lit = dict()
    for v in expr.inputs:
        int2lit[-v.gnum] = -v
        int2lit[v.gnum] = v
    clauses = {frozenset(lit.gnum for lit in clause.args)
               for clause in expr.args}
    return cls(int2lit, clauses)

def nfexpr2expr(nfexpr):
    """Convert a normal form representation into an expression."""
    if isinstance(nfexpr, DisjNormalForm):
        outer, inner = Or, And
    elif isinstance(nfexpr, ConjNormalForm):
        outer, inner = And, Or
    else:
        raise TypeError("input is not a NormalForm instance")

    return outer(*[
               inner(*[ nfexpr.int2lit[num] for num in clause ])
                        for clause in nfexpr.clauses ])


class NormalForm(Function):
    """
    Normal Form Representation
    """
    def __new__(cls, int2lit, clauses):
        if clauses:
            return super(NormalForm, cls).__new__(cls)
        else:
            return cls.IDENTITY

    def __init__(self, int2lit, clauses):
        self.int2lit = int2lit
        self.clauses = clauses

    def __repr__(self):
        return self.__str__()

    # From Function
    @cached_property
    def support(self):
        return {self.int2lit[abs(num)]
                for clause in self.clauses for num in clause}

    @cached_property
    def inputs(self):
        return sorted(self.support)

    def restrict(self, point):
        idents = set()
        doms = set()
        for v, val in point.items():
            low, high = (-v, v) if boolify(val) == self.IDENTITY else (v, -v)
            idents.add(low.gnum)
            doms.add(high.gnum)

        new_clauses = set()
        for clause in self.clauses:
            if not any(n in clause for n in doms):
                new_clause = frozenset(n for n in clause if n not in idents)
                if new_clause:
                    new_clauses.add(new_clause)
                else:
                    return self.DOMINATOR

        return self.__class__(self.int2lit, new_clauses)


class DisjNormalForm(NormalForm):
    """
    Disjunctive Normal Form
    """

    IDENTITY = 0
    DOMINATOR = 1

    def __str__(self):
        return str(nfexpr2expr(self))

    def __neg__(self):
        clauses = {frozenset(-arg for arg in clause) for clause in self.clauses}
        return ConjNormalForm(self.int2lit, clauses)

    def __add__(self, other):
        return DNF_Or(self, other)

    def __mul__(self, other):
        f = nfexpr2expr(self)
        g = nfexpr2expr(other)
        return expr2nfexpr((f * g).to_dnf())


class ConjNormalForm(NormalForm):
    """
    Conjunctive Normal Form
    """

    IDENTITY = 1
    DOMINATOR = 0

    def __str__(self):
        return str(nfexpr2expr(self))

    def __neg__(self):
        clauses = {frozenset(-arg for arg in clause) for clause in self.clauses}
        return DisjNormalForm(self.int2lit, clauses)

    def __add__(self, other):
        f = nfexpr2expr(self)
        g = nfexpr2expr(other)
        return expr2nfexpr((f + g).to_cnf())

    def __mul__(self, other):
        return CNF_And(self, other)

    def satisfy_one(self, algorithm='dpll'):
        if algorithm == 'backtrack':
            return backtrack(self)
        elif algorithm == 'dpll':
            return dpll(self)
        else:
            raise ValueError("invalid algorithm")

    def bcp(self):
        """Boolean Constraint Propagation"""
        return _bcp(self)

    def ple(self):
        """Pure Literal Elimination

        A literal is *pure* if it only exists with one polarity in the CNF.

        For example:

        >>> from pyeda import *
        >>> a, b, c = map(var, "abc")

        In this CNF, 'a' is pure: (a + b + c) * (a + -b + -c)
        >>> cnf = expr2nfexpr((a + b + c) * (a + -b + -c))

        Eliminating 'a' results in a true statement.
        >>> cnf.ple()
        (1, {a: 1})

        In this CNF, '-a' is pure: (-a + b) * (-a + c) * (-b + -c)
        >>> cnf = expr2nfexpr((-a + b) * (-a + c) * (-b + -c))

        Eliminating '-a' results in: -b + -c
        >>> cnf, point = cnf.ple()
        >>> nfexpr2expr(cnf), point
        (b' + c', {a: 0})
        """
        cntr = Counter()
        for clause in self.clauses:
            cntr.update(clause)

        point = dict()
        while cntr:
            num, cnt = cntr.popitem()
            if -num in cntr:
                cntr.pop(-num)
            else:
                point[self.int2lit[abs(num)]] = int(num > 0)
        if point:
            return self.restrict(point), point
        else:
            return self, {}


def DNF_Or(*args):
    args = (expr2nfexpr(arg) if isinstance(arg, Expression) else arg
            for arg in args)

    int2lit = dict()
    clauses = set()
    for arg in args:
        int2lit.update(arg.int2lit)
        clauses.update(arg.clauses)

    return DisjNormalForm(int2lit, clauses)

def CNF_And(*args):
    args = (expr2nfexpr(arg) if isinstance(arg, Expression) else arg
            for arg in args)

    int2lit = dict()
    clauses = set()
    for arg in args:
        int2lit.update(arg.int2lit)
        clauses.update(arg.clauses)

    return ConjNormalForm(int2lit, clauses)

def _bcp(cnf):
    """Boolean Constraint Propagation"""
    if cnf in B:
        return cnf, {}
    else:
        point = dict()
        for clause in cnf.clauses:
            if len(clause) == 1:
                num = list(clause)[0]
                if num > 0:
                    point[cnf.int2lit[num]] = 1
                else:
                    point[cnf.int2lit[-num]] = 0
        if point:
            _cnf, _point = _bcp(cnf.restrict(point))
            point.update(_point)
            return _cnf, point
        else:
            return cnf, point
