"""
Binary Decision Diagrams

Interface Functions:
    bddvar
    expr2bdd
    bdd2expr

Interface Classes:
    BinaryDecisionDiagram
        BDDVariable
"""

from pyeda import boolfunc

UNIQUE_TABLE = dict()

def bddvar(name, indices=None, namespace=None):
    """Return a variable binary decision diagram."""
    return BDDVariable(name, indices, namespace)

def expr2bdd(expr):
    """Convert an expression into a binary decision diagram."""
    pass

def bdd2expr(bdd):
    """Convert a binary decision diagram into an expression."""
    pass


class BinaryDecisionDiagram(boolfunc.Function):
    """Boolean function represented by a binary decision diagram"""
    def __new__(cls, root, low, high):
        pass


class BDDVariable(BinaryDecisionDiagram):
    """Binary decision diagram variable"""

    _MEM = dict()

    def __new__(cls, name, indices=None, namespace=None):
        _var = boolfunc.Variable(name, indices, namespace)

    def __str__(self):
        return str(self._var)
