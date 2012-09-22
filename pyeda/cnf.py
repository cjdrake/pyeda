"""
Conjunctive Normal Form

Interface Functions:
    expr2cnf
    cnf2expr

Interface Classes:
    ConjNormalForm
"""

import random

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
        lit2int = {lit: num for num, lit in int2lit.items()}
        clauses = {tuple(sorted(lit2int[lit] for lit in clause.args))
                   for clause in expr.args}
        return ConjNormalForm(int2lit, clauses)
    else:
        raise TypeError("expression is not a CNF")

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

    # Specific to NormalForm
    def copy(self):
        return self.__class__(self.int2lit, self.clauses)


class ConjNormalForm(NormalForm):
    """
    Conjunctive Normal Form
    """

    IDENTITY = 1
    DOMINATOR = 0

    def __mul__(self, other):
        return CNF_AND(self, other)

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

        return ConjNormalForm(self.int2lit, new_clauses)

    def satisfy_one(self):
        # Boolean constraint propagation
        cnf, point = bcp(self)

        # Pure literal elimination
        if isinstance(cnf, ConjNormalForm):
            cnf, pure_point = cnf.eliminate_pure()
            point.update(pure_point)

        if cnf == 0:
            return None
        elif cnf == 1:
            return point

        # variable selection heuristic
        #var = cnf.top
        var = random.choice(cnf.inputs)

        # backtracking
        cfs = {p[var]: cf for p, cf in cnf.iter_cofactors(var)}
        if cfs[0] == 1:
            if cfs[1] == 1:
                # tautology
                bt_point = {}
            else:
                # var=0 satisfies the formula
                bt_point = {var: 0}
        elif cfs[1] == 1:
            # var=1 satisfies the formula
            bt_point = {var: 1}
        else:
            for num, cf in cfs.items():
                if cf != 0:
                    bt_point = cf.satisfy_one()
                    if bt_point is not None:
                        bt_point[var] = num
                        break
            else:
                bt_point = None

        if bt_point is not None:
            bt_point.update(point)

        return bt_point

    def eliminate_pure(self):
        """Return a CNF with no clauses that contain pure literals.

        A literal is *pure* if it only exists with one polarity in the CNF.

        For example:

        >>> from pyeda import *
        >>> a, b, c = map(var, "abc")

        In this CNF, 'a' is pure: (a + b + c) * (a + -b + -c)
        >>> cnf = expr2cnf((a + b + c) * (a + -b + -c))

        Eliminating 'a' results in a true statement.
        >>> cnf.eliminate_pure()
        (1, {a: 1})

        In this CNF, 'a' is pure: (a + b) * (a + c) * (-b + -c)
        >>> cnf = expr2cnf((a + b) * (a + c) * (-b + -c))

        Eliminating 'a' results in: -b + -c
        >>> cnf, point = cnf.eliminate_pure()
        >>> cnf.clauses, point
        (frozenset({(-3, -2)}), {a: 1})
        """
        counter = dict()
        for clause in self.clauses:
            for num in clause:
                if num in counter:
                    counter[num] += 1
                else:
                    counter[num] = 0

        pures = list()
        while counter:
            num, cnt = counter.popitem()
            if -num in counter:
                counter.pop(-num)
            elif cnt == 1:
                pures.append(num)

        if pures:
            point = {self.int2lit[num]: (0 if num < 0 else 1) for num in pures}
            new_clauses = list()
            for clause in self.clauses:
                if not any(num in clause for num in pures):
                    new_clauses.append(clause)
            return ConjNormalForm(self.int2lit, new_clauses), point
        else:
            return self, {}


def bcp(cnf):
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
            _cnf, _point = bcp(cnf.restrict(point))
            point.update(_point)
            return _cnf, point
        else:
            return cnf, point

def CNF_AND(*args):
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
