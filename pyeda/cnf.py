"""
Conjunctive Normal Form

Interface Functions:
    expr2cnf
    cnf2expr

Interface Classes:
    CompactCNF
"""

from pyeda.common import cached_property
from pyeda.constant import boolify
from pyeda.boolfunc import Function
from pyeda.expr import Or, And

__copyright__ = "Copyright (c) 2012, Chris Drake"

def expr2cnf(expr):
    """Convert an expression into a compact CNF."""
    if expr.is_pos():
        int2lit = dict()
        for i, v in enumerate(expr.inputs):
            int2lit[-(i+1)] = -v
            int2lit[i+1] = v
        lit2int = {lit: num for num, lit in int2lit.items()}
        terms = {tuple(sorted(lit2int[lit] for lit in term.args))
                 for term in expr.args}
        return CompactCNF(int2lit, terms)
    else:
        raise TypeError("expression is not in CNF")

def cnf2expr(cnf):
    """Convert a compact CNF into an expression."""
    return And(*[Or(*[cnf.int2lit[num] for num in term]) for term in cnf.terms])

class CompactCNF(Function):
    """
    Compact CNF representation
    """
    def __new__(cls, int2lit, terms):
        if not terms:
            return 1
        else:
            return super(CompactCNF, cls).__new__(cls)

    def __init__(self, int2lit, terms):
        self.int2lit = int2lit
        self.lit2int = {lit: num for num, lit in int2lit.items()}
        self.terms = terms

    # From Function
    @cached_property
    def support(self):
        return {v for i, v in self.int2lit.items() if i > 0}

    @cached_property
    def inputs(self):
        return sorted(self.support)

    def __mul__(self, other):
        inputs = sorted(self.support | other.support)
        int2lit = dict()
        for i, v in enumerate(inputs):
            int2lit[-(i+1)] = -v
            int2lit[i+1] = v
        lit2int = {lit: num for num, lit in int2lit.items()}

        sterms = {tuple(lit2int[self.int2lit[num]] for num in term)
                  for term in self.terms}
        oterms = {tuple(lit2int[other.int2lit[num]] for num in term)
                  for term in other.terms}

        return CompactCNF(int2lit, sterms | oterms)

    def restrict(self, mapping):
        zeros, ones = set(), set()
        for v, val in mapping.items():
            low, high = (-v, v) if boolify(val) else (v, -v)
            zeros.add(self.lit2int[low])
            ones.add(self.lit2int[high])

        terms = set()
        for term in self.terms:
            if not any(one in term for one in ones):
                nums = [n for n in term if n not in zeros]
                if nums:
                    terms.add(tuple(nums))
                else:
                    return 0

        return CompactCNF(self.int2lit, terms)
