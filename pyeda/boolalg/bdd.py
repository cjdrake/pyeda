"""
Binary Decision Diagrams

Interface Functions:
    bddvar
    expr2bdd
    bdd2expr
    upoint2bddpoint

Interface Classes:
    BDDNode
        BDDNODEZERO
        BDDNODEONE
    BinaryDecisionDiagram
        BDDConstant
            BDDZERO
            BDDONE
        BDDVariable
"""

# Disable "redefining name from outer scope"
# pylint: disable=W0621

import random
import weakref

from pyeda.boolalg import boolfunc
from pyeda.boolalg.expr import exprvar, Or, And
from pyeda.util import cached_property


# existing BDDVariable references
_BDDVARIABLES = weakref.WeakValueDictionary()

# node/bdd cache
_BDDNODES = weakref.WeakValueDictionary()
_BDDS = weakref.WeakValueDictionary()


class BDDNode(object):
    """Binary Decision Diagram Node"""
    def __init__(self, root, lo, hi):
        self.root = root
        self.lo = lo
        self.hi = hi

BDDNODEZERO = _BDDNODES[(-2, None, None)] = BDDNode(-2, None, None)
BDDNODEONE = _BDDNODES[(-1, None, None)] = BDDNode(-1, None, None)


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
        var = _BDDVARIABLES[bvar.uniqid]
    except KeyError:
        var = _BDDVARIABLES[bvar.uniqid] = BDDVariable(bvar)
        _BDDS[var.node] = var
    return var

def _expr2bddnode(expr):
    """Convert an expression into a BDD node."""
    if expr.is_zero():
        return BDDNODEZERO
    elif expr.is_one():
        return BDDNODEONE
    else:
        top = expr.top

        # Register this variable
        _ = bddvar(top.names, top.indices)

        root = top.uniqid
        lo = _expr2bddnode(expr.restrict({top: 0}))
        hi = _expr2bddnode(expr.restrict({top: 1}))
        return _bddnode(root, lo, hi)

def expr2bdd(expr):
    """Convert an expression into a binary decision diagram."""
    return _bdd(_expr2bddnode(expr))

def bdd2expr(bdd, conj=False):
    """Convert a binary decision diagram into an expression."""
    if conj:
        outer, inner = (And, Or)
        paths = _iter_all_paths(bdd.node, BDDNODEZERO)
    else:
        outer, inner = (Or, And)
        paths = _iter_all_paths(bdd.node, BDDNODEONE)
    terms = list()
    for path in paths:
        expr_point = {exprvar(v.names, v.indices): val
                      for v, val in _path2point(path).items()}
        terms.append(boolfunc.point2term(expr_point, conj))
    return outer(*[inner(*term) for term in terms])

def upoint2bddpoint(upoint):
    """Convert an untyped point to a BDD point."""
    point = dict()
    for uniqid in upoint[0]:
        point[_BDDVARIABLES[uniqid]] = 0
    for uniqid in upoint[1]:
        point[_BDDVARIABLES[uniqid]] = 1

def _bddnode(root, lo, hi):
    """Return a unique BDD node."""
    if lo is hi:
        node = lo
    else:
        key = (root, lo, hi)
        try:
            node = _BDDNODES[key]
        except KeyError:
            node = _BDDNODES[key] = BDDNode(*key)
    return node

def _bdd(node):
    """Return a unique BDD."""
    try:
        bdd = _BDDS[node]
    except KeyError:
        bdd = _BDDS[node] = BinaryDecisionDiagram(node)
    return bdd

def _path2point(path):
    """Convert a BDD path to a BDD point."""
    point = dict()
    for i, node in enumerate(path[:-1]):
        if node.lo is path[i+1]:
            point[_BDDVARIABLES[node.root]] = 0
        elif node.hi is path[i+1]:
            point[_BDDVARIABLES[node.root]] = 1
    return point


class BinaryDecisionDiagram(boolfunc.Function):
    """Boolean function represented by a binary decision diagram."""

    def __init__(self, node):
        self.node = node

    def __str__(self):
        return "BDD({0.root}, {0.lo}, {0.hi})".format(self.node)

    def __repr__(self):
        return str(self)

    # Operators
    def __invert__(self):
        return _bdd(_neg(self.node))

    def __or__(self, other):
        other_node = self.box(other).node
        # f | g <=> ITE(f, 1, g)
        return _bdd(_ite(self.node, BDDNODEONE, other_node))

    def __and__(self, other):
        other_node = self.box(other).node
        # f & g <=> ITE(f, g, 0)
        return _bdd(_ite(self.node, other_node, BDDNODEZERO))

    def __xor__(self, other):
        other_node = self.box(other).node
        # f ^ g <=> ITE(f, g', g)
        return _bdd(_ite(self.node, _neg(other_node), other_node))

    # From Function
    @cached_property
    def support(self):
        return frozenset(self.inputs)

    @cached_property
    def inputs(self):
        _inputs = list()
        for node in self.traverse():
            if node.root > 0:
                v = _BDDVARIABLES[node.root]
                if v not in _inputs:
                    _inputs.append(v)
        return tuple(reversed(_inputs))

    def urestrict(self, upoint):
        return _bdd(_urestrict(self.node, upoint))

    def compose(self, mapping):
        node = self.node
        for v, g in mapping.items():
            fv0, fv1 = _bdd(node).cofactors(v)
            node = _ite(g.node, fv1.node, fv0.node)
        return _bdd(node)

    def satisfy_one(self):
        path = _find_path(self.node, BDDNODEONE)
        if path is None:
            return None
        else:
            return _path2point(path)

    def satisfy_all(self):
        for path in _iter_all_paths(self.node, BDDNODEONE):
            yield _path2point(path)

    def is_zero(self):
        return self.node is BDDNODEZERO

    def is_one(self):
        return self.node is BDDNODEONE

    @staticmethod
    def box(obj):
        if isinstance(obj, BinaryDecisionDiagram):
            return obj
        elif obj == 0 or obj == '0':
            return BDDZERO
        elif obj == 1 or obj == '1':
            return BDDONE
        else:
            return CONSTANTS[bool(obj)]

    # Specific to BinaryDecisionDiagram
    def traverse(self):
        """Iterate through all nodes in this BDD in DFS order."""
        yield from _dfs(self.node, set())

    def equivalent(self, other):
        """Return whether this BDD is equivalent to another."""
        other = self.box(other)
        return self.node is other.node

    def to_dot(self, name='BDD'):
        """Convert to DOT language representation."""
        parts = ['graph', name, '{']
        for node in self.traverse():
            if node is BDDNODEZERO:
                parts += ['n' + str(id(node)), '[label=0,shape=box];']
            elif node is BDDNODEONE:
                parts += ['n' + str(id(node)), '[label=1,shape=box];']
            else:
                v = _BDDVARIABLES[node.root]
                parts.append('n' + str(id(node)))
                parts.append('[label="{}",shape=circle];'.format(v))
        for node in self.traverse():
            if node is not BDDNODEZERO and node is not BDDNODEONE:
                parts += ['n' + str(id(node)), '--',
                          'n' + str(id(node.lo)),
                          '[label=0,style=dashed];']
                parts += ['n' + str(id(node)), '--',
                          'n' + str(id(node.hi)),
                          '[label=1];']
        parts.append('}')
        return " ".join(parts)


class BDDConstant(BinaryDecisionDiagram):
    """Binary decision diagram constant"""

    VALUE = NotImplemented

    def __bool__(self):
        return bool(self.VALUE)

    def __int__(self):
        return self.VALUE

    def __str__(self):
        return str(self.VALUE)


class _BDDZero(BDDConstant):
    """Binary decision diagram zero"""

    VALUE = 0

    def __init__(self):
        super(_BDDZero, self).__init__(BDDNODEZERO)


class _BDDOne(BDDConstant):
    """Binary decision diagram one"""

    VALUE = 1

    def __init__(self):
        super(_BDDOne, self).__init__(BDDNODEONE)


BDDZERO = _BDDS[BDDNODEZERO] = _BDDZero()
BDDONE = _BDDS[BDDNODEONE] = _BDDOne()

CONSTANTS = [BDDZERO, BDDONE]


class BDDVariable(boolfunc.Variable, BinaryDecisionDiagram):
    """Binary decision diagram variable"""

    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.names, bvar.indices)
        node = _bddnode(bvar.uniqid, BDDNODEZERO, BDDNODEONE)
        BinaryDecisionDiagram.__init__(self, node)


def _neg(node):
    """Return the node that is the inverse of the input node."""
    if node is BDDNODEZERO:
        return BDDNODEONE
    elif node is BDDNODEONE:
        return BDDNODEZERO
    else:
        return _bddnode(node.root, _neg(node.lo), _neg(node.hi))

def _ite(f, g, h):
    """Return node that results from recursively applying ITE(f, g, h)."""
    # ITE(f, 1, 0) = f
    if g is BDDNODEONE and h is BDDNODEZERO:
        return f
    # ITE(f, 0, 1) = f'
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
        return _bddnode(root, _ite(fv0, gv0, hv0), _ite(fv1, gv1, hv1))

def _urestrict(node, upoint, cache=None):
    """Return node that results from untyped point restriction."""
    if node is BDDNODEZERO or node is BDDNODEONE:
        return node

    if cache is None:
        cache = dict()

    try:
        ret = cache[node]
    except KeyError:
        if node.root in upoint[0]:
            ret = _urestrict(node.lo, upoint, cache)
        elif node.root in upoint[1]:
            ret = _urestrict(node.hi, upoint, cache)
        else:
            lo = _urestrict(node.lo, upoint, cache)
            hi = _urestrict(node.hi, upoint, cache)
            ret = _bddnode(node.root, lo, hi)
        cache[node] = ret
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
        if start.lo is not None:
            ret = _find_path(start.lo, end, path)
        if ret is None and start.hi is not None:
            ret = _find_path(start.hi, end, path)
        return ret

def _iter_all_paths(start, end, rand=False, path=tuple()):
    """Iterate through all paths from start to end."""
    path = path + (start, )
    if start is end:
        yield path
    else:
        nodes = [start.lo, start.hi]
        if rand:
            random.shuffle(nodes)
        for node in nodes:
            if node is not None:
                yield from _iter_all_paths(node, end, rand, path)

def _dfs(node, visited):
    """Iterate through a depth-first traveral starting at node."""
    lo, hi = node.lo, node.hi
    if lo is not None:
        yield from _dfs(lo, visited)
    if hi is not None:
        yield from _dfs(hi, visited)
    if node not in visited:
        visited.add(node)
        yield node

