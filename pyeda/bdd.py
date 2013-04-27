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


class BinaryDecisionDiagram(boolfunc.Function):
    def __new__(cls, node):
        self = super(BinaryDecisionDiagram, cls).__new__(cls)
        self.node = node
        return self

    # Operators
    def __neg__(self):
        raise NotImplementedError()

    def __add__(self, other):
        raise NotImplementedError()

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        raise NotImplementedError()

    def __rsub__(self, other):
        return self.__neg__().__add__(other)

    def __mul__(self, other):
        raise NotImplementedError()

    def __rmul__(self, other):
        return self.__mul__(other)

    def xor(self, *args):
        raise NotImplementedError()

    # From Function
    @cached_property
    def support(self):
        return frozenset(BDDVARIABLES[n.root]
                         for n in self.traverse() if n.root > 0)

    @cached_property
    def inputs(self):
        return tuple(sorted(self.support))

    def iter_zeros(self):
        raise NotImplementedError()

    def iter_ones(self):
        raise NotImplementedError()

    def reduce(self):
        return self

    def restrict(self, point):
        raise NotImplementedError()

    def compose(self, point):
        raise NotImplementedError()

    def satisfy_one(self):
        raise NotImplementedError()

    def satisfy_all(self):
        raise NotImplementedError()

    def satisfy_count(self):
        raise NotImplementedError()

    # Specific to BinaryDecisionDiagram
    def traverse(self):
        visited = set()
        for node in _dfs(self.node, visited):
            visited.add(node)
            yield node

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


def _dfs(node, visited):
    low, high = node.low, node.high
    if low not in visited and low is not None:
        for n in _dfs(low, visited):
            yield n
    if high not in visited and high is not None:
        for n in _dfs(high, visited):
            yield n
    if node not in visited and node is not None:
        yield node
