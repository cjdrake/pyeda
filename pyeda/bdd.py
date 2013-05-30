"""
Binary Decision Diagrams

Globals:
    BDDVARIABLES

Interface Functions:
    bddvar
    expr2bdd
    bdd2expr

Interface Classes:
    BDDNode
    BinaryDecisionDiagram
    BDDVariable
"""

import collections
import functools

from pyeda import boolfunc
from pyeda.common import cached_property
from pyeda.expr import EXPRVARIABLES, Or, And

# existing BDDVariable references
BDDVARIABLES = dict()

BDDNode = collections.namedtuple('BDDNode', ['root', 'low', 'high'])

BDDZERO = BDDNode(-2, None, None)
BDDONE = BDDNode(-1, None, None)

_NUM2BDDNODE = {
    0: BDDZERO,
    1: BDDONE,
}

_BDDNODE2NUM = {
    BDDZERO: 0,
    BDDONE: 1,
}

# { (int, int, int) : BDDNode }
BDD_NODES = dict()

def get_bdd_node(root, low, high):
    key = (root, low, high)
    try:
        node = BDD_NODES[key]
    except KeyError:
        node = BDD_NODES[key] = BDDNode(*key)
    return node

def bddvar(name, indices=None, namespace=None):
    """Return a BDD variable.

    Parameters
    ----------
    name : str
        The variable's identifier string.
    indices : int or tuple[int], optional
        One or more integer suffixes for variables that are part of a
        multi-dimensional bit-vector, eg x[1], x[1][2][3]
    namespace : str or tuple[str], optional
        A container for a set of variables. Since a Variable instance is global,
        a namespace can be used for local scoping.
    """
    return BDDVariable(name, indices, namespace)

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
        return BinaryDecisionDiagram(node)

def _expr2node(expr):
    top = expr.top
    fv0, fv1 = expr.cofactors(top)

    top = BDDVariable(top.name, top.indices, top.namespace)

    root = top.uniqid
    try:
        low = _NUM2BDDNODE[fv0]
    except KeyError:
        low = _expr2node(fv0)
    try:
        high = _NUM2BDDNODE[fv1]
    except KeyError:
        high = _expr2node(fv1)

    if low is high:
        return low
    else:
        return get_bdd_node(root, low, high)

def bdd2expr(bdd, conj=False):
    """Convert a binary decision diagram into an expression."""
    if bdd.node is BDDZERO:
        return 0
    elif bdd.node is BDDONE:
        return 1
    else:
        if conj:
            outer, inner = (And, Or)
            points = bdd.iter_zeros()
        else:
            outer, inner = (Or, And)
            points = bdd.iter_ones()
        points = [{EXPRVARIABLES[v.uniqid]: val for v, val in point.items()}
                  for point in points]
        terms = [boolfunc.point2term(point, conj) for point in points]
        return outer(*[inner(*term) for term in terms])


# existing BinaryDecisionDiagram references
_BDDS = dict()

class BinaryDecisionDiagram(boolfunc.Function):
    def __new__(cls, node):
        try:
            self = _BDDS[node]
        except KeyError:
            self = super(BinaryDecisionDiagram, cls).__new__(cls)
            self.node = node
            _BDDS[node] = self
        return self

    # Operators
    def __neg__(self):
        node = neg(self.node)
        return BinaryDecisionDiagram(node)

    def __add__(self, other):
        try:
            other_node = _NUM2BDDNODE[other]
        except KeyError:
            other_node = other.node
        node = ite(self.node, BDDONE, other_node)
        try:
            return _BDDNODE2NUM[node]
        except KeyError:
            return BinaryDecisionDiagram(node)

    def __sub__(self, other):
        try:
            other_node = _NUM2BDDNODE[other]
        except KeyError:
            other_node = other.node
        node = ite(self.node, BDDONE, neg(other_node))
        try:
            return _BDDNODE2NUM[node]
        except KeyError:
            return BinaryDecisionDiagram(node)

    def __mul__(self, other):
        try:
            other_node = _NUM2BDDNODE[other]
        except KeyError:
            other_node = other.node
        node = ite(self.node, other_node, BDDZERO)
        try:
            return _BDDNODE2NUM[node]
        except KeyError:
            return BinaryDecisionDiagram(node)

    def xor(self, other):
        try:
            other_node = _NUM2BDDNODE[other]
        except KeyError:
            other_node = other.node
        node = ite(self.node, neg(other_node), other_node)
        try:
            return _BDDNODE2NUM[node]
        except KeyError:
            return BinaryDecisionDiagram(node)

    # From Function
    @cached_property
    def support(self):
        return frozenset(BDDVARIABLES[n.root]
                         for n in self.traverse() if n.root > 0)

    @cached_property
    def inputs(self):
        return tuple(sorted(self.support))

    def iter_zeros(self):
        for path in iter_all_paths(self.node, BDDZERO):
            point = dict()
            for i, node in enumerate(path[:-1]):
                if node.low is path[i+1]:
                    point[BDDVARIABLES[node.root]] = 0
                elif node.high is path[i+1]:
                    point[BDDVARIABLES[node.root]] = 1
            yield point

    def iter_ones(self):
        for path in iter_all_paths(self.node, BDDONE):
            point = dict()
            for i, node in enumerate(path[:-1]):
                if node.low is path[i+1]:
                    point[BDDVARIABLES[node.root]] = 0
                elif node.high is path[i+1]:
                    point[BDDVARIABLES[node.root]] = 1
            yield point

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
            return BinaryDecisionDiagram(node)

    def compose(self, mapping):
        raise NotImplementedError()

    def satisfy_one(self):
        path = find_path(self.node, BDDONE)
        if path is None:
            return None
        else:
            point = dict()
            for i, node in enumerate(path[:-1]):
                if node.low is path[i+1]:
                    point[BDDVARIABLES[node.root]] = 0
                elif node.high is path[i+1]:
                    point[BDDVARIABLES[node.root]] = 1
            return point

    def satisfy_all(self):
        return self.iter_ones()

    def satisfy_count(self):
        return sum(1 for _ in self.satisfy_all())

    #def is_neg_unate(self, vs=None):
    #    raise NotImplementedError()

    #def is_pos_unate(self, vs=None):
    #    raise NotImplementedError()

    def smoothing(self, vs=None):
        return functools.reduce(self.__class__.__add__, self.cofactors(vs))

    def consensus(self, vs=None):
        return functools.reduce(self.__class__.__mul__, self.cofactors(vs))

    def derivative(self, vs=None):
        return functools.reduce(self.__class__.xor, self.cofactors(vs))

    # Specific to BinaryDecisionDiagram
    def traverse(self):
        visited = set()
        for node in dfs(self.node, visited):
            visited.add(node)
            yield node

    def equivalent(self, other):
        try:
            other_node = _NUM2BDDNODE[other]
        except KeyError:
            other_node = other.node
        return self.node is other_node


class BDDVariable(boolfunc.Variable, BinaryDecisionDiagram):
    def __new__(cls, name, indices=None, namespace=None):
        _var = boolfunc.Variable(name, indices, namespace)
        root = _var.uniqid
        try:
            self = BDDVARIABLES[root]
        except KeyError:
            node = get_bdd_node(root, BDDZERO, BDDONE)
            self = BinaryDecisionDiagram.__new__(cls, node)
            self._var = _var
            BDDVARIABLES[root] = self
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
        return get_bdd_node(node.root, neg(node.low), neg(node.high))

def ite(nf, ng, nh):
    if ng is BDDONE and nh is BDDZERO:
        return nf
    elif ng is BDDZERO and nh is BDDONE:
        return neg(nf)
    elif nf is BDDONE:
        return ng
    elif nf is BDDZERO:
        return nh
    elif ng is nh:
        return ng
    else:
        root = min(node.root for node in (nf, ng, nh) if node.root > 0)
        upoint0 = (frozenset([root]), frozenset())
        upoint1 = (frozenset(), frozenset([root]))
        nf0, ng0, nh0 = [urestrict(node, upoint0) for node in (nf, ng, nh)]
        nf1, ng1, nh1 = [urestrict(node, upoint1) for node in (nf, ng, nh)]
        return get_bdd_node(root, ite(nf0, ng0, nh0), ite(nf1, ng1, nh1))

def urestrict(node, upoint):
    if node is BDDZERO or node is BDDONE:
        return node
    elif node.root in upoint[0]:
        return urestrict(node.low, upoint)
    elif node.root in upoint[1]:
        return urestrict(node.high, upoint)
    else:
        low = urestrict(node.low, upoint)
        high = urestrict(node.high, upoint)
        if low is not node.low or high is not node.high:
            if low is high:
                return low
            else:
                return get_bdd_node(node.root, low, high)
        else:
            return node

def find_path(start, end, path=tuple()):
    path = path + (start, )
    if start is end:
        return path
    else:
        ret = None
        if start.low is not None:
            ret = find_path(start.low, end, path)
        if ret is None and start.high is not None:
            ret = find_path(start.high, end, path)
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
    if node not in visited:
        yield node
