"""
Conjunctive Normal Form

Interface Functions:
    expr2cnf
    cnf2expr

Interface Classes:
    CompactCNF
    CompactDNF
"""

from pyeda.common import cached_property
from pyeda.constant import boolify
from pyeda.boolfunc import Function
from pyeda.expr import Expression, Or, And

__copyright__ = "Copyright (c) 2012, Chris Drake"

def expr2cnf(expr):
    """Convert an expression into a compact CNF."""
    if expr.is_pos():
        int2lit = dict()
        for i, v in enumerate(expr.inputs):
            int2lit[-(i+1)] = -v
            int2lit[i+1] = v
        lit2int = {lit: num for num, lit in int2lit.items()}
        clauses = {tuple(sorted(lit2int[lit] for lit in clause.args))
                   for clause in expr.args}
        return CompactCNF(int2lit, clauses)
    else:
        raise TypeError("expression is not in CNF")

def cnf2expr(cnf):
    """Convert a compact CNF into an expression."""
    return And(*[
               Or(*[ cnf.int2lit[num] for num in clause ])
                     for clause in cnf.clauses ])

class CompactNF(Function):
    """
    Compact Normal Form Representation
    """
    def __new__(cls, int2lit, clauses):
        if clauses:
            return super(CompactNF, cls).__new__(cls)
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

    # Specific to CompactNF
    def copy(self):
        return self.__class__(self.int2lit, self.clauses)


class CompactCNF(CompactNF):
    """
    Compact CNF representation
    """

    IDENTITY = 1
    DOMINATOR = 0

    def __mul__(self, other):
        if isinstance(other, Expression):
            other = expr2cnf(other)

        inputs = sorted(self.support | other.support)
        int2lit = dict()
        for i, v in enumerate(inputs):
            int2lit[-(i+1)] = -v
            int2lit[i+1] = v
        lit2int = {lit: num for num, lit in int2lit.items()}

        scls = {tuple(lit2int[self.int2lit[num]] for num in clause)
                for clause in self.clauses}
        ocls = {tuple(lit2int[other.int2lit[num]] for num in clause)
                for clause in other.clauses}

        return CompactCNF(int2lit, scls | ocls)

    def restrict(self, mapping):
        zeros, ones = set(), set()
        for v, val in mapping.items():
            low, high = (-v, v) if boolify(val) else (v, -v)
            zeros.add(self.lit2int[low])
            ones.add(self.lit2int[high])

        new_clauses = set()
        for clause in self.clauses:
            if not any(one in clause for one in ones):
                new_clause = tuple(n for n in clause if n not in zeros)
                if new_clause:
                    new_clauses.add(new_clause)
                else:
                    return self.DOMINATOR

        return CompactCNF(self.int2lit, new_clauses)

    def satisfy_one(self):
        pass

    def bcp(self):
        point = dict()
        for clause in self.clauses:
            if len(clause) == 1:
                num = clause[0]
                if num > 0:
                    point[self.int2lit[num]] = 1
                else:
                    point[self.int2lit[-num]] = 0
        if point:
            cnf = self.restrict(point)
            if cnf != 1:
                _point, cnf = cnf.bcp()
                point.update(_point)
            return point, cnf
        else:
            return point, self
