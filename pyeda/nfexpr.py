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

from pyeda.common import cached_property
from pyeda.boolfunc import Function
from pyeda.expr import EXPRVARIABLES, EXPRCOMPLEMENTS
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

    clauses = {frozenset(lit.uniqid for lit in clause.args)
               for clause in expr.args}
    return cls(clauses)

def nfexpr2expr(nfexpr):
    """Convert a normal form representation into an expression."""
    if isinstance(nfexpr, DisjNormalForm):
        outer, inner = Or, And
    elif isinstance(nfexpr, ConjNormalForm):
        outer, inner = And, Or
    else:
        raise TypeError("input is not a NormalForm instance")

    terms = list()
    for clause in nfexpr.clauses:
        term = list()
        for num in clause:
            if num < 0:
                lit = EXPRCOMPLEMENTS[num]
            else:
                lit = EXPRVARIABLES[num]
            term.append(lit)
        terms.append(term)

    return outer(*[inner(*term) for term in terms])


class NormalForm(Function):
    """
    Normal Form Representation
    """
    def __new__(cls, clauses):
        if clauses:
            return super(NormalForm, cls).__new__(cls)
        else:
            return cls.IDENTITY

    def __init__(self, clauses):
        self.clauses = clauses

    def __str__(self):
        return str(nfexpr2expr(self))

    def __repr__(self):
        return self.__str__()

    # From Function
    @cached_property
    def support(self):
        return frozenset(EXPRVARIABLES[abs(num)]
                         for clause in self.clauses for num in clause)

    @cached_property
    def inputs(self):
        return sorted(self.support)

    def urestrict(self, upoint):
        idents = set()
        idents.update(upoint[self.DOMINATOR])
        idents.update(-n for n in upoint[self.IDENTITY])

        doms = set()
        doms.update(upoint[self.IDENTITY])
        doms.update(-n for n in upoint[self.DOMINATOR])

        new_clauses = set()
        for clause in self.clauses:
            if not clause & doms:
                new_clause = clause - idents
                if new_clause:
                    new_clauses.add(new_clause)
                else:
                    return self.DOMINATOR

        return self.__class__(new_clauses)

    # Specific to NormalForm
    IDENTITY = NotImplemented
    DOMINATOR = NotImplemented


class DisjNormalForm(NormalForm):
    """
    Disjunctive Normal Form
    """
    def __neg__(self):
        clauses = {frozenset(-arg for arg in clause) for clause in self.clauses}
        return ConjNormalForm(clauses)

    def __add__(self, other):
        return DNF_Or(self, other)

    def __mul__(self, other):
        f = nfexpr2expr(self)
        g = nfexpr2expr(other)
        return expr2nfexpr((f * g).to_dnf())

    # Specific to NormalForm
    IDENTITY = 0
    DOMINATOR = 1


class ConjNormalForm(NormalForm):
    """
    Conjunctive Normal Form
    """
    def __neg__(self):
        clauses = {frozenset(-arg for arg in clause) for clause in self.clauses}
        return DisjNormalForm(clauses)

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

    # DPLL IF
    def bcp(self):
        """Boolean Constraint Propagation"""
        return _bcp(self)

    def ple(self):
        """Pure Literal Elimination"""
        cntr = Counter()
        for clause in self.clauses:
            cntr.update(clause)

        point = dict()
        while cntr:
            num, _ = cntr.popitem()
            if -num in cntr:
                cntr.pop(-num)
            else:
                point[EXPRVARIABLES[abs(num)]] = int(num > 0)
        if point:
            return self.restrict(point), point
        else:
            return self, {}

    # Specific to NormalForm
    IDENTITY = 1
    DOMINATOR = 0


def DNF_Or(*args):
    args = (expr2nfexpr(arg) if isinstance(arg, Expression) else arg
            for arg in args)

    clauses = set()
    for arg in args:
        clauses.update(arg.clauses)

    return DisjNormalForm(clauses)

def CNF_And(*args):
    args = (expr2nfexpr(arg) if isinstance(arg, Expression) else arg
            for arg in args)

    clauses = set()
    for arg in args:
        clauses.update(arg.clauses)

    return ConjNormalForm(clauses)

def _bcp(cnf):
    """Boolean Constraint Propagation"""
    if cnf in B:
        return cnf, {}
    else:
        point = dict()
        for clause in cnf.clauses:
            if len(clause) == 1:
                num = list(clause)[0]
                point[EXPRVARIABLES[abs(num)]] = int(num > 0)
        if point:
            _cnf, _point = _bcp(cnf.restrict(point))
            point.update(_point)
            return _cnf, point
        else:
            return cnf, point
