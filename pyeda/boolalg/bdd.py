"""
The :mod:`pyeda.boolalg.bdd` module implements
Boolean functions represented as binary decision diagrams.

Interface Functions:

* :func:`bddvar`
* :func:`expr2bdd`
* :func:`bdd2expr`
* :func:`upoint2bddpoint`

Interface Classes:

* :class:`BDDNode`
* :class:`BinaryDecisionDiagram`
* :class:`BDDConstant`
* :class:`BDDVariable`
"""

# Disable "redefining name from outer scope"
# pylint: disable=W0621

import collections
import random
import weakref

from pyeda.boolalg import boolfunc
from pyeda.boolalg.expr import exprvar, Or, And
from pyeda.util import cached_property


# existing BDDVariable references
_BDDVARIABLES = dict()

# node/bdd cache
_BDDNODES = weakref.WeakValueDictionary()
_BDDS = weakref.WeakValueDictionary()


class BDDNode(object):
    """Binary decision diagram node

    .. note::
       Never construct a ``BDDNode`` instance directly.
       They will automically be created and destroyed during symbolic
       manipulation.
    """
    def __init__(self, root, lo, hi):
        self.root = root
        self.lo = lo
        self.hi = hi

BDDNODEZERO = _BDDNODES[(-2, None, None)] = BDDNode(-2, None, None)
BDDNODEONE = _BDDNODES[(-1, None, None)] = BDDNode(-1, None, None)


def bddvar(name, index=None):
    r"""Return a unique BDD variable.

    A Boolean *variable* is an abstract numerical quantity that may assume any
    value in the set :math:`B = \{0, 1\}`.
    The ``bddvar`` function returns a unique Boolean variable instance
    represented by a binary decision diagram.
    Variable instances may be used to symbolically construct larger BDDs.

    A variable is defined by one or more *names*,
    and zero or more *indices*.
    Multiple names establish hierarchical namespaces,
    and multiple indices group several related variables.
    If the ``name`` parameter is a single ``str``,
    it will be converted to ``(name, )``.
    The ``index`` parameter is optional;
    when empty, it will be converted to an empty tuple ``()``.
    If the ``index`` parameter is a single ``int``,
    it will be converted to ``(index, )``.

    Given identical names and indices, the ``bddvar`` function will always
    return the same variable:

    >>> bddvar('a', 0) is bddvar('a', 0)
    True

    To create several single-letter variables:

    >>> a, b, c, d = map(bddvar, "abcd")

    To create variables with multiple names (inner-most first):

    >>> fifo_push = bddvar(('push', 'fifo'))
    >>> fifo_pop = bddvar(('pop', 'fifo'))

    .. seealso::
       For creating arrays of variables with incremental indices,
       we recommend using the :func:`bddvars` function.
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
    """Convert an untyped point into a BDD point."""
    point = dict()
    for uniqid in upoint[0]:
        point[_BDDVARIABLES[uniqid]] = 0
    for uniqid in upoint[1]:
        point[_BDDVARIABLES[uniqid]] = 1
    return point

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
    return {_BDDVARIABLES[node.root]: int(node.hi is path[i+1])
            for i, node in enumerate(path[:-1])}


class BinaryDecisionDiagram(boolfunc.Function):
    """Boolean function represented by a binary decision diagram

    .. note::
       Never construct a ``BinaryDecisionDiagram`` instance directly.
       They will automatically be created and destroyed during symbolic
       manipulation.
    """

    def __init__(self, node):
        self.node = node

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
        for node in self.dfs_postorder():
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
    def dfs_preorder(self):
        """Iterate through nodes in DFS pre-order."""
        yield from _dfs_preorder(self.node, set())

    def dfs_postorder(self):
        """Iterate through nodes in DFS post-order."""
        yield from _dfs_postorder(self.node, set())

    def bfs(self):
        """Iterate through nodes in BFS order."""
        yield from _bfs(self.node, set())

    def equivalent(self, other):
        """Return whether this BDD is equivalent to another."""
        other = self.box(other)
        return self.node is other.node

    def to_dot(self, name='BDD'): # pragma: no cover
        """Convert to DOT language representation."""
        parts = ['graph', name, '{']
        for node in self.dfs_postorder():
            if node is BDDNODEZERO:
                parts += ['n' + str(id(node)), '[label=0,shape=box];']
            elif node is BDDNODEONE:
                parts += ['n' + str(id(node)), '[label=1,shape=box];']
            else:
                v = _BDDVARIABLES[node.root]
                parts.append('n' + str(id(node)))
                parts.append('[label="{}",shape=circle];'.format(v))
        for node in self.dfs_postorder():
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
    """Binary decision diagram constant

    .. note::
       Never construct a ``BDDConstant`` instance directly.
       Use the ``int`` values ``0`` and ``1`` instead.
    """

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
    """Binary decision diagram variable

    .. note::
       Never construct a ``BDDVariable`` instance directly.
       Use the :func:`bddvar` function instead.
    """

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
        if rand: # pragma: no cover
            random.shuffle(nodes)
        for node in nodes:
            if node is not None:
                yield from _iter_all_paths(node, end, rand, path)

def _dfs_preorder(node, visited):
    """Iterate through nodes in DFS pre-order."""
    if node not in visited:
        visited.add(node)
        yield node
    if node.lo is not None:
        yield from _dfs_preorder(node.lo, visited)
    if node.hi is not None:
        yield from _dfs_preorder(node.hi, visited)

def _dfs_postorder(node, visited):
    """Iterate through nodes in DFS post-order."""
    if node.lo is not None:
        yield from _dfs_postorder(node.lo, visited)
    if node.hi is not None:
        yield from _dfs_postorder(node.hi, visited)
    if node not in visited:
        visited.add(node)
        yield node

def _bfs(node, visited):
    """Iterate through nodes in BFS order."""
    queue = collections.deque()
    queue.appendleft(node)
    while queue:
        node = queue.pop()
        if node not in visited:
            if node.lo is not None:
                queue.appendleft(node.lo)
            if node.hi is not None:
                queue.appendleft(node.hi)
            visited.add(node)
            yield node

