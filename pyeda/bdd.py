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
from pyeda.expr import EXPRVARIABLES, And, Or

# existing BDDVariable references
BDDVARIABLES = dict()

# existing BinaryDecisionDiagram references
BDDS = dict()

# { (int, int, int) : BDDNode }
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
    if node is BDDZERO:
        return 0
    elif node is BDDONE:
        return 1
    elif node.low is BDDZERO and node.high is BDDONE:
        return BDDVARIABLES[node.root]
    else:
        try:
            ret = BDDS[node]
        except KeyError:
            ret = BDDS[node] = BinaryDecisionDiagram(node)
        return ret

def _expr2node(expr):
    top = expr.top
    fv0, fv1 = expr.cofactors(top)

    top = BDDVariable(top.name, top.indices, top.namespace)

    root = top.uniqid
    try:
        low = _NUM2BDD[fv0]
    except KeyError:
        low = _expr2node(fv0)
    try:
        high = _NUM2BDD[fv1]
    except KeyError:
        high = _expr2node(fv1)

    if low is high:
        node = low
    else:
        key = (root, low, high)
        try:
            node = TABLE[key]
        except KeyError:
            node = TABLE[key] = BDDNode(*key)

    return node

def bdd2expr(bdd):
    """Convert a binary decision diagram into an expression."""
    if bdd.node is BDDZERO:
        return 0
    elif bdd.node is BDDONE:
        return 1
    else:
        terms = list()
        paths = [path for path in iter_all_paths(bdd.node, BDDONE)]
        for path in paths:
            term = list()
            for i, node in enumerate(path[:-1]):
                if node.low is path[i+1]:
                    term.append(-EXPRVARIABLES[node.root])
                elif node.high is path[i+1]:
                    term.append(EXPRVARIABLES[node.root])
            terms.append(term)
        return Or(*[And(*term) for term in terms])


class BinaryDecisionDiagram(boolfunc.Function):
    def __new__(cls, node):
        self = super(BinaryDecisionDiagram, cls).__new__(cls)
        self.node = node
        return self

    # Operators
    def __neg__(self):
        node = neg(self.node)
        try:
            ret = BDDS[node]
        except KeyError:
            ret = BDDS[node] = BinaryDecisionDiagram(node)
        return ret

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
        if node is BDDZERO:
            return 0
        elif node is BDDONE:
            return 1
        elif node is self.node:
            return self
        elif node.low is BDDZERO and node.high is BDDONE:
            return BDDVARIABLES[node.root]
        else:
            try:
                ret = BDDS[node]
            except KeyError:
                ret = BDDS[node] = BinaryDecisionDiagram(node)
            return ret

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
        for node in dfs(self.node, visited):
            visited.add(node)
            yield node

    def equivalent(self, other):
        return self.node is other.node


class BDDVariable(boolfunc.Variable, BinaryDecisionDiagram):
    def __new__(cls, name, indices=None, namespace=None):
        _var = boolfunc.Variable(name, indices, namespace)
        uniqid = _var.uniqid
        try:
            self = BDDVARIABLES[uniqid]
        except KeyError:
            key = (uniqid, BDDZERO, BDDONE)
            try:
                node = TABLE[key]
            except KeyError:
                node = TABLE[key] = BDDNode(*key)
            self = BinaryDecisionDiagram.__new__(cls, node)
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


def neg(node):
    if node is BDDZERO:
        return BDDONE
    elif node is BDDONE:
        return BDDZERO
    else:
        low = neg(node.low)
        high = neg(node.high)
        key = (node.root, low, high)
        try:
            ret = TABLE[key]
        except KeyError:
            ret = TABLE[key] = BDDNode(*key)
        return ret

def urestrict(node, upoint):
    if node is BDDZERO or node is BDDONE:
        ret = node
    elif node.root in upoint[0]:
        ret = urestrict(node.low, upoint)
    elif node.root in upoint[1]:
        ret = urestrict(node.high, upoint)
    else:
        low = urestrict(node.low, upoint)
        high = urestrict(node.high, upoint)
        if low is not node.low or high is not node.high:
            if low is high:
                ret = low
            else:
                key = (node.root, low, high)
                try:
                    ret = TABLE[key]
                except KeyError:
                    ret = TABLE[key] = BDDNode(*key)
        else:
            ret = node
    return ret

def iter_all_paths(start, end, path=tuple()):
    path = path + (start, )
    if start is end:
        yield path
    else:
        if start.low is not None:
            for _path in iter_all_paths(start.low, end, path):
                yield _path
        if start.high is not None:
            for _path in iter_all_paths(start.high, end, path):
                yield _path

def dfs(node, visited):
    low, high = node.low, node.high
    if low not in visited and low is not None:
        for n in dfs(low, visited):
            yield n
    if high not in visited and high is not None:
        for n in dfs(high, visited):
            yield n
    if node not in visited and node is not None:
        yield node
