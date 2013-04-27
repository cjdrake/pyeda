"""
Binary Decision Diagrams

Globals:
    BDDVARIABLES

Interface Functions:
    expr2bdd
    bdd2expr

Interface Classes:
    BinaryDecisionDiagram
    BDDVariable
"""

import collections

from pyeda import boolfunc
from pyeda.common import cached_property

BDDVARIABLES = dict()
TABLE = dict()

BDDNode = collections.namedtuple('BDDNode', ['root', 'low', 'high'])

BDDZERO = BDDNode(-2, None, None)
BDDONE = BDDNode(-1, None, None)

_NUM2BDD = {0: BDDZERO, 1: BDDONE}


def expr2bdd(expr):
    """Convert an expression into a binary decision diagram."""
    node = _expr2node(expr)
    return BinaryDecisionDiagram(node)

def _expr2node(expr):
    expr_top = expr.top
    bdd_top = BDDVariable(expr_top.name, expr_top.indices, expr_top.namespace)

    fv0, fv1 = expr.cofactors(expr_top)
    try:
        low = _NUM2BDD[fv0]
    except KeyError:
        low = _expr2node(fv0)
    try:
        high = _NUM2BDD[fv1]
    except KeyError:
        high = _expr2node(fv1)
    key = (bdd_top.uniqid, low.root, high.root)
    try:
        node = TABLE[key]
    except KeyError:
        node = BDDNode(bdd_top.uniqid, low, high)
        TABLE[key] = node
    return node

def bdd2expr(bdd):
    """Convert a binary decision diagram into an expression."""
    pass

def traverse(node):
    visited = set()
    for n in _dfs(node, visited):
        visited.add(n)
        yield n

def _dfs(node, visited):
    low, high = node.low, node.high
    if low not in visited and low is not None:
        for n in _dfs(low, visited):
            yield n
    if high not in visited and high is not None:
        for n in _dfs(high, visited):
            yield n
    if node not in visited:
        yield node


class BinaryDecisionDiagram(boolfunc.Function):
    def __new__(cls, node):
        self = super(BinaryDecisionDiagram, cls).__new__(cls)
        self.node = node
        return self

    # Operators

    # From Function
    @cached_property
    def support(self):
        s = set()
        for n in traverse(self.node):
            if n.root > 0:
                s.add(BDDVARIABLES[n.root])
        return frozenset(s)

    @cached_property
    def inputs(self):
        return tuple(sorted(self.support))

    # Specific to BinaryDecisionDiagram
    def equivalent(self, other):
        return self.node == other.node


class BDDVariable(boolfunc.Variable, BinaryDecisionDiagram):
    def __new__(cls, name, indices=None, namespace=None):
        _var = boolfunc.Variable(name, indices, namespace)
        uniqid = _var.uniqid
        try:
            self = BDDVARIABLES[uniqid]
        except KeyError:
            key = (uniqid, -2, -1)
            try:
                node = TABLE[key]
            except KeyError:
                node = BDDNode(uniqid, BDDZERO, BDDONE)
                TABLE[key] = node
            self = super(BinaryDecisionDiagram, cls).__new__(cls)
            self.node = node
            self._var = _var
            BDDVARIABLES[uniqid] = self
        return self

    # From Variable
    @property
    def uniqid(self):
        return self._var.uniqid

    @property
    def namespace(self):
        return self._var.namespace

    @property
    def name(self):
        return self._var.name

    @property
    def indices(self):
        return self._var.indices
