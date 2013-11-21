"""
Binary Decision Diagrams

Interface Functions:
    bddvar
    bddnode
    bdd
    expr2bddnode
    expr2bdd
    bdd2expr

Interface Classes:
    BinaryDecisionDiagram
    BDDConstant
    BDDVariable
"""

# Disable "redefining name from outer scope"
# pylint: disable=W0621

import random
import weakref

from pyeda.boolalg import boolfunc
from pyeda.boolalg.expr import exprvar, Or, And, EXPRZERO, EXPRONE
from pyeda.util import cached_property

# existing BDDVariable references
BDDVARIABLES = dict()

BDDNODES = weakref.WeakValueDictionary()
BDDS = weakref.WeakValueDictionary()
_RESTRICT_CACHE = weakref.WeakValueDictionary()


class BDDNode(object):
    """Binary Decision Diagram Node"""
    def __init__(self, root, low, high):
        self.root = root
        self.low = low
        self.high = high

BDDNODEZERO = BDDNODES[(-2, None, None)] = BDDNode(-2, None, None)
BDDNODEONE = BDDNODES[(-1, None, None)] = BDDNode(-1, None, None)


def bddvar(name, index=None):
    """Return a BDD variable.

    Parameters
    ----------
    name : str
        The variable's identifier string.
    index : int or tuple[int], optional
        One or more integer suffixes for variables that are part of a
        multi-dimensional bit-vector, eg x[1], x[1][2][3]
    """
    bvar = boolfunc.var(name, index)
    try:
        var = BDDVARIABLES[bvar.uniqid]
    except KeyError:
        var = BDDVARIABLES[bvar.uniqid] = BDDVariable(bvar)
        BDDS[var.node] = var
    return var

def bddnode(root, low, high):
    """Return a unique BDD node."""
    if low is high:
        node = low
    else:
        key = (root, low, high)
        try:
            node = BDDNODES[key]
        except KeyError:
            node = BDDNODES[key] = BDDNode(*key)
    return node

def bdd(node):
    """Return a unique BDD."""
    try:
        _bdd = BDDS[node]
    except KeyError:
        _bdd = BDDS[node] = BinaryDecisionDiagram(node)
    return _bdd

def expr2bddnode(expr):
    """Convert an expression into a BDD node."""
    if expr is EXPRZERO:
        return BDDNODEZERO
    elif expr is EXPRONE:
        return BDDNODEONE
    else:
        top = expr.top

        # Register this variable
        _ = bddvar(top.names, top.indices)

        root = top.uniqid
        low = expr2bddnode(expr.restrict({top: 0}))
        high = expr2bddnode(expr.restrict({top: 1}))
        return bddnode(root, low, high)

def expr2bdd(expr):
    """Convert an expression into a binary decision diagram."""
    return bdd(expr2bddnode(expr))

def bdd2expr(bdd, conj=False):
    """Convert a binary decision diagram into an expression."""
    if bdd.node is BDDNODEZERO:
        return EXPRZERO
    elif bdd.node is BDDNODEONE:
        return EXPRONE
    else:
        if conj:
            outer, inner = (And, Or)
            paths = _iter_all_paths(bdd.node, BDDNODEZERO)
        else:
            outer, inner = (Or, And)
            paths = _iter_all_paths(bdd.node, BDDNODEONE)
        terms = list()
        for path in paths:
            expr_point = {exprvar(v.names, v.indices): val
                          for v, val in path2point(path).items()}
            terms.append(boolfunc.point2term(expr_point, conj))
        return outer(*[inner(*term) for term in terms])

def path2point(path):
    """Convert a BDD path to a BDD point."""
    point = dict()
    for i, node in enumerate(path[:-1]):
        if node.low is path[i+1]:
            point[BDDVARIABLES[node.root]] = 0
        elif node.high is path[i+1]:
            point[BDDVARIABLES[node.root]] = 1
    return point

def upoint2bddpoint(upoint):
    """Convert an untyped point to a BDD point."""
    point = dict()
    for uniqid in upoint[0]:
        point[BDDVARIABLES[uniqid]] = 0
    for uniqid in upoint[1]:
        point[BDDVARIABLES[uniqid]] = 1


class BinaryDecisionDiagram(boolfunc.Function):
    """Boolean function represented by a binary decision diagram."""

    def __init__(self, node):
        self.node = node

    def __str__(self):
        return "BDD({0.root}, {0.low}, {0.high})".format(self.node)

    def __repr__(self):
        return str(self)

    # Operators
    def __neg__(self):
        return bdd(_neg(self.node))

    def __add__(self, other):
        other_node = self.box(other).node
        # x + y <=> ITE(x, 1, y)
        return bdd(_ite(self.node, BDDNODEONE, other_node))

    def __sub__(self, other):
        other_node = self.box(other).node
        # x - y <=> ITE(x, 1, y')
        return bdd(_ite(self.node, BDDNODEONE, _neg(other_node)))

    def __mul__(self, other):
        other_node = self.box(other).node
        # x * y <=> ITE(x, y, 0)
        return bdd(_ite(self.node, other_node, BDDNODEZERO))

    def xor(self, other):
        other_node = self.box(other).node
        # x (xor) y <=> ITE(x, y', y)
        return bdd(_ite(self.node, _neg(other_node), other_node))

    # From Function
    @cached_property
    def support(self):
        return frozenset(self.inputs)

    @cached_property
    def inputs(self):
        _inputs = list()
        for node in self.traverse():
            if node.root > 0:
                v = BDDVARIABLES[node.root]
                if v not in _inputs:
                    _inputs.append(v)
        return tuple(reversed(_inputs))

    def urestrict(self, upoint):
        return bdd(_urestrict(self.node, upoint))

    def compose(self, mapping):
        node = self.node
        for v, g in mapping.items():
            fv0, fv1 = bdd(node).cofactors(v)
            node = _ite(g.node, fv1.node, fv0.node)
        return bdd(node)

    def satisfy_one(self):
        path = _find_path(self.node, BDDNODEONE)
        if path is None:
            return None
        else:
            return path2point(path)

    def satisfy_all(self):
        for path in _iter_all_paths(self.node, BDDNODEONE):
            yield path2point(path)

    def satisfy_count(self):
        return sum(1 for _ in self.satisfy_all())

    def is_neg_unate(self, vs=None):
        return bdd2expr(self).is_neg_unate(vs)

    def is_pos_unate(self, vs=None):
        return bdd2expr(self).is_pos_unate(vs)

    def is_zero(self):
        return self.node is BDDNODEZERO

    def is_one(self):
        return self.node is BDDNODEONE

    @staticmethod
    def box(arg):
        if isinstance(arg, BinaryDecisionDiagram):
            return arg
        elif arg == 0 or arg == '0':
            return BDDZERO
        elif arg == 1 or arg == '1':
            return BDDONE
        else:
            return CONSTANTS[bool(arg)]

    # Specific to BinaryDecisionDiagram
    def traverse(self):
        """Iterate through all nodes in this BDD in DFS order."""
        visited = set()
        for node in _dfs(self.node, visited):
            visited.add(node)
            yield node

    def equivalent(self, other):
        """Return whether this BDD is equivalent to another."""
        other = self.box(other)
        return self.node is other.node


class BDDConstant(BinaryDecisionDiagram):
    """Binary decision diagram constant"""

    VAL = NotImplemented

    def __bool__(self):
        return bool(self.VAL)

    def __int__(self):
        return self.VAL

    def __str__(self):
        return str(self.VAL)


class _BDDZero(BDDConstant):
    """Binary decision diagram zero"""

    VAL = 0

    def __init__(self):
        super(_BDDZero, self).__init__(BDDNODEZERO)


class _BDDOne(BDDConstant):
    """Binary decision diagram one"""

    VAL = 1

    def __init__(self):
        super(_BDDOne, self).__init__(BDDNODEONE)


BDDZERO = BDDS[BDDNODEZERO] = _BDDZero()
BDDONE = BDDS[BDDNODEONE] = _BDDOne()

CONSTANTS = [BDDZERO, BDDONE]


class BDDVariable(boolfunc.Variable, BinaryDecisionDiagram):
    """Binary decision diagram variable"""

    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.names, bvar.indices)
        node = bddnode(bvar.uniqid, BDDNODEZERO, BDDNODEONE)
        BinaryDecisionDiagram.__init__(self, node)


def _neg(node):
    """Return the node that is the inverse of the input node."""
    if node is BDDNODEZERO:
        return BDDNODEONE
    elif node is BDDNODEONE:
        return BDDNODEZERO
    else:
        return bddnode(node.root, _neg(node.low), _neg(node.high))

def _ite(f, g, h):
    """Return node that results from recursively applying ITE(f, g, h)."""
    # ITE(f, 1, 0) = f
    if g is BDDNODEONE and h is BDDNODEZERO:
        return f
    # ITE(f, 0, 1) = -f
    elif g is BDDNODEZERO and h is BDDNODEONE:
        return _neg(f)
    # ITE(1, g, h) = g
    elif f is BDDNODEONE:
        return g
    # ITE(0, g, h) = h
    elif f is BDDNODEZERO:
        return h
    # ITE(f, g, g) = g
    elif g is h:
        return g
    else:
        # ITE(f, g, h) = ITE(x, ITE(fx', gx', hx'), ITE(fx, gx, hx))
        root = min(node.root for node in (f, g, h) if node.root > 0)
        upoint0 = frozenset([root]), frozenset()
        upoint1 = frozenset(), frozenset([root])
        fv0, gv0, hv0 = [_urestrict(node, upoint0) for node in (f, g, h)]
        fv1, gv1, hv1 = [_urestrict(node, upoint1) for node in (f, g, h)]
        return bddnode(root, _ite(fv0, gv0, hv0), _ite(fv1, gv1, hv1))

def _urestrict(node, upoint):
    """Return node that results from untyped point restriction."""
    if node is BDDNODEZERO or node is BDDNODEONE:
        return node

    key = (node, upoint)
    try:
        ret = _RESTRICT_CACHE[key]
    except KeyError:
        if node.root in upoint[0]:
            ret = _urestrict(node.low, upoint)
        elif node.root in upoint[1]:
            ret = _urestrict(node.high, upoint)
        else:
            low = _urestrict(node.low, upoint)
            high = _urestrict(node.high, upoint)
            ret = bddnode(node.root, low, high)
        _RESTRICT_CACHE[key] = ret
    return ret

def _find_path(start, end, path=tuple()):
    """Return the path from start to end.

    If no path exists, return None.
    """
    path = path + (start, )
    if start is end:
        return path
    else:
        ret = None
        if start.low is not None:
            ret = _find_path(start.low, end, path)
        if ret is None and start.high is not None:
            ret = _find_path(start.high, end, path)
        return ret

def _iter_all_paths(start, end, rand=False, path=tuple()):
    """Iterate through all paths from start to end."""
    path = path + (start, )
    if start is end:
        yield path
    else:
        nodes = [start.low, start.high]
        if rand:
            random.shuffle(nodes)
        for node in nodes:
            if node is not None:
                for _path in _iter_all_paths(node, end, rand, path):
                    yield _path

def _dfs(node, visited):
    """Iterate through a depth-first traveral starting at node."""
    low, high = node.low, node.high
    if low not in visited and low is not None:
        for _node in _dfs(low, visited):
            yield _node
    if high not in visited and high is not None:
        for _node in _dfs(high, visited):
            yield _node
    if node not in visited:
        yield node
