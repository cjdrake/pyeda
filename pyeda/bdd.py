"""
Binary Decision Diagrams

Interface Functions:
    expr2bdd
    bdd2expr

Interface Classes:
    BinaryDecisionDiagram
        BDDZero
        BDDOne
"""

from pyeda import boolfunc

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

class BDDZero(BinaryDecisionDiagram):
    def __init__(self):
        self.root = 0
        self.low = None
        self.high = None

class BDDOne(BinaryDecisionDiagram):
    def __init__(self):
        self.root = 1
        self.low = None
        self.high = None


NUM2BDD = {0: BDDZero(), 1: BDDOne()}
