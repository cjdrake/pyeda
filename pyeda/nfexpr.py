"""
Normal Form Expressions

Interface Functions:
    expr2dnf
    expr2cnf
    dnf2expr
    cnf2expr

Interface Classes:
    ConjNormalForm
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from pyeda.common import boolify, cached_property
from pyeda.boolfunc import Function
from pyeda.expr import Expression, Or, And
from pyeda.sat import backtrack, dpll

def expr2dnf(expr):
    """Convert an expression into a DNF."""
    if expr.is_dnf():
        int2lit = dict()
        for i, v in enumerate(expr.inputs):
            int2lit[-(i+1)] = -v
            int2lit[i+1] = v
        lit2int = {lit: num for num, lit in int2lit.items()}
        clauses = {tuple(sorted(lit2int[lit] for lit in clause.args))
                   for clause in expr.args}
        return DisjNormalForm(int2lit, clauses)
    else:
        raise TypeError("expression is not a DNF")

def expr2cnf(expr):
    """Convert an expression into a CNF."""
    if expr.is_cnf():
        int2lit = dict()
        for i, v in enumerate(expr.inputs):
            int2lit[-(i+1)] = -v
            int2lit[i+1] = v
        lit2int = {lit: num for num, lit in int2lit.items()}
        clauses = {tuple(sorted(lit2int[lit] for lit in clause.args))
                   for clause in expr.args}
        return ConjNormalForm(int2lit, clauses)
    else:
        raise TypeError("expression is not a CNF")

def dnf2expr(dnf):
    """Convert a DNF into an expression."""
    return Or(*[
              And(*[ dnf.int2lit[num] for num in clause ])
                     for clause in dnf.clauses ])

def cnf2expr(cnf):
    """Convert a CNF into an expression."""
    return And(*[
               Or(*[ cnf.int2lit[num] for num in clause ])
                     for clause in cnf.clauses ])


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
        self.lit2int = {lit: num for num, lit in int2lit.items()}
        self.clauses = frozenset(clauses)

    # From Function
    @cached_property
    def support(self):
        return {self.int2lit[abs(num)]
                for clause in self.clauses for num in clause}

    @cached_property
    def inputs(self):
        return sorted(self.support)

    def restrict(self, mapping):
        idents = set()
        doms = set()
        for v, val in mapping.items():
            low, high = (-v, v) if boolify(val) == self.IDENTITY else (v, -v)
            idents.add(self.lit2int[low])
            doms.add(self.lit2int[high])

        new_clauses = set()
        for clause in self.clauses:
            if not any(n in clause for n in doms):
                new_clause = tuple(n for n in clause if n not in idents)
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

    def __add__(self, other):
        return DNF_Or(self, other)


class ConjNormalForm(NormalForm):
    """
    Conjunctive Normal Form
    """

    IDENTITY = 1
    DOMINATOR = 0

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
        >>> cnf = expr2cnf((a + b + c) * (a + -b + -c))

        Eliminating 'a' results in a true statement.
        >>> cnf.ple()
        (1, {a: 1})

        In this CNF, '-a' is pure: (-a + b) * (-a + c) * (-b + -c)
        >>> cnf = expr2cnf((-a + b) * (-a + c) * (-b + -c))

        Eliminating '-a' results in: -b + -c
        >>> cnf, point = cnf.ple()
        >>> cnf.clauses == {(-3, -2)}, point
        (True, {a: 0})
        """
        counter = dict()
        for clause in self.clauses:
            for num in clause:
                if num in counter:
                    counter[num] += 1
                else:
                    counter[num] = 0

        point = dict()
        while counter:
            num, cnt = counter.popitem()
            if -num in counter:
                counter.pop(-num)
            elif cnt == 1:
                point[self.int2lit[abs(num)]] = int(num > 0)
        if point:
            return self.restrict(point), point
        else:
            return self, {}


def DNF_Or(*args):
    args = [ expr2dnf(arg) if isinstance(arg, Expression) else arg
             for arg in args ]

    support = set()
    for arg in args:
        support |= arg.support
    inputs = sorted(support)

    int2lit = dict()
    for i, v in enumerate(inputs):
        int2lit[-(i+1)] = -v
        int2lit[i+1] = v
    lit2int = {lit: num for num, lit in int2lit.items()}

    clauses = set()
    for arg in args:
        for clause in arg.clauses:
            clauses.add(tuple(lit2int[arg.int2lit[num]] for num in clause))

    return DisjNormalForm(int2lit, clauses)

def CNF_And(*args):
    args = [ expr2cnf(arg) if isinstance(arg, Expression) else arg
             for arg in args ]

    support = set()
    for arg in args:
        support |= arg.support
    inputs = sorted(support)

    int2lit = dict()
    for i, v in enumerate(inputs):
        int2lit[-(i+1)] = -v
        int2lit[i+1] = v
    lit2int = {lit: num for num, lit in int2lit.items()}

    clauses = set()
    for arg in args:
        for clause in arg.clauses:
            clauses.add(tuple(lit2int[arg.int2lit[num]] for num in clause))

    return ConjNormalForm(int2lit, clauses)

def _bcp(cnf):
    """Boolean Constraint Propagation"""
    if cnf in {0, 1}:
        return cnf, {}
    else:
        point = dict()
        for clause in cnf.clauses:
            if len(clause) == 1:
                num = clause[0]
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
