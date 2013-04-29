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

ZERO_ROOT = -2
ONE_ROOT = -1

BDDZERO = BDDNode(ZERO_ROOT, None, None)
BDDONE = BDDNode(ONE_ROOT, None, None)

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
        node = TABLE[key] = BDDNode(bdd_top.uniqid, low, high)
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

    def urestrict(self, upoint):
        node = urestrict(self.node, upoint)
        if node == BDDZERO:
            return 0
        elif node == BDDONE:
            return 1
        elif node == self.node:
            return self
        else:
            if node.low == BDDZERO and node.high == BDDONE:
                return BDDVARIABLES[node.root]
            else:
                return BinaryDecisionDiagram(node)

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
            key = (uniqid, ZERO_ROOT, ONE_ROOT)
            try:
                node = TABLE[key]
            except KeyError:
                node = TABLE[key] = BDDNode(uniqid, BDDZERO, BDDONE)
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


def urestrict(node, upoint):
    if node.root in {ZERO_ROOT, ONE_ROOT}:
        ret = node
    elif node.root in upoint[0]:
        ret = urestrict(node.low, upoint)
    elif node.root in upoint[1]:
        ret = urestrict(node.high, upoint)
    else:
        low = urestrict(node.low, upoint)
        high = urestrict(node.high, upoint)
        if low != node.low or high != node.high:
            if low == high:
                ret = low
            else:
                key = (node.root, low.root, high.root)
                try:
                    ret = TABLE[key]
                except KeyError:
                    ret = TABLE[key] = BDDNode(node.root, low, high)
        else:
            ret = node
    return ret

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
