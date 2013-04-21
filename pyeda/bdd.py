"""
Binary Decision Diagrams

Interface Functions:
    expr2bdd
    bdd2expr

Interface Classes:
    BinaryDecisionDiagram
        BDDConstant
            BDDZero
            BDDOne
"""

from pyeda import boolfunc
from pyeda.common import cached_property

TABLE = dict()


def expr2bdd(expr):
    """Convert an expression into a binary decision diagram."""
    root = expr.top.var
    fv0, fv1 = expr.cofactors(expr.top)
    try:
        low = NUM2BDD[fv0]
    except KeyError:
        low = expr2bdd(fv0)
    try:
        high = NUM2BDD[fv1]
    except KeyError:
        high = expr2bdd(fv1)
    key = (root, low.root, high.root)
    try:
        node = TABLE[key]
    except KeyError:
        node = BinaryDecisionDiagram(root, low, high)
        TABLE[key] = node
    return node

def bdd2expr(bdd):
    """Convert a binary decision diagram into an expression."""
    pass


class BinaryDecisionDiagram(boolfunc.Function):
    """Boolean function represented by a binary decision diagram"""
    def __init__(self, root, low, high):
        self.root = root
        self.low = low
        self.high = high

    @cached_property
    def support(self):
        s = set()
        s.update(self.low.support | self.high.support)
        s.add(self.root)
        return frozenset(s)

    @cached_property
    def inputs(self):
        return sorted(self.support)


class BDDConstant(BinaryDecisionDiagram):
    """BDD representation of zero/one"""

    @cached_property
    def support(self):
        return frozenset()


class BDDZero(BDDConstant):
    """BDD representation of the number zero"""
    def __init__(self):
        super(BDDZero, self).__init__(0, None, None)


class BDDOne(BDDConstant):
    """BDD representation of the number one"""
    def __init__(self):
        super(BDDOne, self).__init__(1, None, None)


NUM2BDD = {0: BDDZero(), 1: BDDOne()}
