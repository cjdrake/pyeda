"""
Conjunctive Normal Form

Interface Functions:
    expr2cnf
    cnf2expr

Interface Classes:
    CNF
"""

from pyeda.common import cached_property
from pyeda.constant import boolify
from pyeda.boolfunc import Function
from pyeda.expr import Expression, Or, And

__copyright__ = "Copyright (c) 2012, Chris Drake"

def expr2cnf(expr):
    """Convert an expression into a CNF."""
    if expr.is_pos():
        int2lit = dict()
        for i, v in enumerate(expr.inputs):
            int2lit[-(i+1)] = -v
            int2lit[i+1] = v
        lit2int = { lit: num for num, lit in int2lit.items() }
        clauses = { tuple(sorted(lit2int[lit] for lit in clause.args))
                    for clause in expr.args }
        return CNF(int2lit, clauses)
    else:
        raise TypeError("expression is not in CNF")

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
        self.lit2int = { lit: num for num, lit in int2lit.items() }
        self.clauses = frozenset(clauses)

    # From Function
    @cached_property
    def support(self):
        return { self.int2lit[abs(num)]
                 for clause in self.clauses for num in clause }

    @cached_property
    def inputs(self):
        return sorted(self.support)

    # Specific to NormalForm
    def copy(self):
        return self.__class__(self.int2lit, self.clauses)


class CNF(NormalForm):
    """
    Conjunctive Normal Form
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

        scls = { tuple(lit2int[self.int2lit[num]] for num in clause)
                 for clause in self.clauses }
        ocls = { tuple(lit2int[other.int2lit[num]] for num in clause)
                 for clause in other.clauses }

        return CNF(int2lit, scls | ocls)

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

        return CNF(self.int2lit, new_clauses)

    def satisfy_one(self):
        constraints, cnf = self.bcp()
        if cnf == 0:
            return None
        elif cnf == 1:
            return constraints

        # FIXME -- variable selection heuristic
        var = cnf.top
        cfs = {p[var]: cf for p, cf in cnf.iter_cofactors(var)}
        if cfs[0] == 1:
            if cfs[1] == 1:
                # tautology
                point = {}
            else:
                # var=0 satisfies the formula
                point = {var: 0}
        elif cfs[1] == 1:
            # var=1 satisfies the formula
            point = {var: 1}
        else:
            for num, cf in cfs.items():
                if cf != 0:
                    point = cf.satisfy_one()
                    if point is not None:
                        point[var] = num
                        break
            else:
                point = None

        if point is not None:
            point.update(constraints)

        return point

    def bcp(self):
        """Boolean Constraint Propagation"""
        constraints = dict()
        for clause in self.clauses:
            if len(clause) == 1:
                num = clause[0]
                if num > 0:
                    constraints[self.int2lit[num]] = 1
                else:
                    constraints[self.int2lit[-num]] = 0
        if constraints:
            cnf = self.restrict(constraints)
            if cnf == 0:
                return None, cnf
            elif cnf == 1:
                return constraints, cnf
            else:
                _constraints, _cnf = cnf.bcp()
                if _cnf == 0:
                    return None, _cnf
                else:
                    constraints.update(_constraints)
                    return constraints, _cnf
        else:
            return constraints, self
