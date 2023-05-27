"""
The :mod:`pyeda.boolalg.bdd` module implements
Boolean functions represented as binary decision diagrams.

Interface Functions:

* :func:`bddvar` --- Return a unique BDD variable
* :func:`expr2bdd` --- Convert an expression into a binary decision diagram
* :func:`bdd2expr` --- Convert a binary decision diagram into an expression
* :func:`upoint2bddpoint` --- Convert an untyped point into a BDD point
* :func:`ite` --- BDD if-then-else operator

Interface Classes:

* :class:`BDDNode`
* :class:`BinaryDecisionDiagram`

  * :class:`BDDConstant`
  * :class:`BDDVariable`
"""

import collections
import random
import weakref
from functools import cached_property

from pyeda.boolalg import boolfunc
from pyeda.boolalg.expr import And, Or, exprvar

# existing BDDVariable references
_VARS = {}

# node/bdd cache
_NODES = weakref.WeakValueDictionary()
_BDDS = weakref.WeakValueDictionary()


class BDDNode:
    """Binary decision diagram node

    A BDD node represents one cofactor in the decomposition of a Boolean
    function.
    Nodes are uniquely identified by a ``root`` integer,
    ``lo`` child node, and ``hi`` child node:

    * ``root`` is the cofactor variable's ``uniqid`` attribute
    * ``lo`` is the zero cofactor node
    * ``hi`` is the one cofactor node

    The ``root`` of the zero node is -1,
    and the ``root`` of the one node is -2.
    Both zero/one nodes have ``lo=None`` and ``hi=None``.

    Do **NOT** create BDD nodes using the ``BDDNode`` constructor.
    BDD node instances are managed internally.
    """
    def __init__(self, root, lo, hi):
        self.root = root
        self.lo = lo
        self.hi = hi


BDDNODEZERO = _NODES[(-1, None, None)] = BDDNode(-1, None, None)
BDDNODEONE = _NODES[(-2, None, None)] = BDDNode(-2, None, None)


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

    >>> bddvar("a", 0) is bddvar("a", 0)
    True

    To create several single-letter variables:

    >>> a, b, c, d = map(bddvar, "abcd")

    To create variables with multiple names (inner-most first):

    >>> fifo_push = bddvar(("push", "fifo"))
    >>> fifo_pop = bddvar(("pop", "fifo"))

    .. seealso::
       For creating arrays of variables with incremental indices,
       use the :func:`pyeda.boolalg.bfarray.bddvars` function.
    """
    bvar = boolfunc.var(name, index)
    try:
        var = _VARS[bvar.uniqid]
    except KeyError:
        var = _VARS[bvar.uniqid] = BDDVariable(bvar)
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
    """Convert a binary decision diagram into an expression.

    This function will always return an expression in two-level form.
    If *conj* is ``False``, return a sum of products (SOP).
    Otherwise, return a product of sums (POS).

    For example::

       >>> a, b = map(bddvar, "ab")
       >>> bdd2expr(~a | b)
       Or(~a, And(a, b))
    """
    if conj:
        outer, inner = (And, Or)
        paths = _iter_all_paths(bdd.node, BDDNODEZERO)
    else:
        outer, inner = (Or, And)
        paths = _iter_all_paths(bdd.node, BDDNODEONE)
    terms = []
    for path in paths:
        expr_point = {exprvar(v.names, v.indices): val
                      for v, val in _path2point(path).items()}
        terms.append(boolfunc.point2term(expr_point, conj))
    return outer(*[inner(*term) for term in terms])


def upoint2bddpoint(upoint):
    """Convert an untyped point into a BDD point.

    .. seealso::
       For definitions of points and untyped points,
       see the :mod:`pyeda.boolalg.boolfunc` module.
    """
    point = {}
    for uniqid in upoint[0]:
        point[_VARS[uniqid]] = 0
    for uniqid in upoint[1]:
        point[_VARS[uniqid]] = 1
    return point


def ite(f, g, h):
    r"""BDD if-then-else (ITE) operator

    The *f*, *g*, and *h* arguments are BDDs.

    The ITE(f, g, h) operator means
    "if *f* is true, return *g*, else return *h*".

    It is equivalent to:

    * DNF form: ``f & g | ~f & h``
    * CNF form: ``(~f | g) & (f | h)``
    """
    f, g, h = map(BinaryDecisionDiagram.box, (f, g, h))
    return _bdd(_ite(f.node, g.node, h.node))


def _bddnode(root, lo, hi):
    """Return a unique BDD node."""
    if lo is hi:
        node = lo
    else:
        key = (root, lo, hi)
        try:
            node = _NODES[key]
        except KeyError:
            node = _NODES[key] = BDDNode(*key)
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
    return {_VARS[node.root]: int(node.hi is path[i+1])
            for i, node in enumerate(path[:-1])}


class BinaryDecisionDiagram(boolfunc.Function):
    """Boolean function represented by a binary decision diagram

    .. seealso::
       This is a subclass of :class:`pyeda.boolalg.boolfunc.Function`

    BDDs have a single attribute, ``node``,
    that points to a node in the managed unique table.

    There are two ways to construct a BDD:

    * Convert an expression using the ``expr2bdd`` function.
    * Use operators on existing BDDs.

    Use the ``bddvar`` function to create BDD variables,
    and use the Python ``~|&^`` operators for NOT, OR, AND, XOR.

    For example::

       >>> a, b, c, d = map(bddvar, "abcd")
       >>> f = ~a | b & c ^ d

    The ``BinaryDecisionDiagram`` class is useful for type checking,
    e.g. ``isinstance(f, BinaryDecisionDiagram)``.

    Do **NOT** create a BDD using the ``BinaryDecisionDiagram`` constructor.
    BDD instances are managed internally,
    and you will not be able to use the Python ``is`` operator to establish
    formal equivalence with manually constructed BDDs.
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

    def __rshift__(self, other):
        other_node = self.box(other).node
        # f => g <=> ITE(f', 1, g)
        return _bdd(_ite(_neg(self.node), BDDNODEONE, other_node))

    def __rrshift__(self, other):
        other_node = self.box(other).node
        # f => g <=> ITE(f', 1, g)
        return _bdd(_ite(_neg(other_node), BDDNODEONE, self.node))

    # From Function
    @cached_property
    def support(self):
        return frozenset(self.inputs)

    @cached_property
    def inputs(self):
        inputs_ = []
        for node in self.dfs_postorder():
            if node.root > 0:
                v = _VARS[node.root]
                if v not in inputs_:
                    inputs_.append(v)
        return tuple(reversed(inputs_))

    def restrict(self, point):
        npoint = {v.node.root: self.box(val).node for v, val in point.items()}
        return _bdd(_restrict(self.node, npoint))

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
        elif obj in (0, "0"):
            return BDDZERO
        elif obj in (1, "1"):
            return BDDONE
        else:
            return BDDONE if bool(obj) else BDDZERO

    # Specific to BinaryDecisionDiagram
    def dfs_preorder(self):
        """Iterate through nodes in depth first search (DFS) pre-order."""
        yield from _dfs_preorder(self.node, set())

    def dfs_postorder(self):
        """Iterate through nodes in depth first search (DFS) post-order."""
        yield from _dfs_postorder(self.node, set())

    def bfs(self):
        """Iterate through nodes in breadth first search (BFS) order."""
        yield from _bfs(self.node, set())

    def equivalent(self, other):
        """Return whether this BDD is equivalent to *other*.

        You can also use Python's ``is`` operator for BDD equivalency testing.

        For example::

           >>> a, b, c = map(bddvar, "abc")
           >>> f1 = a ^ b ^ c
           >>> f2 = a & ~b & ~c | ~a & b & ~c | ~a & ~b & c | a & b & c
           >>> f1 is f2
           True
        """
        other = self.box(other)
        return self.node is other.node

    def to_dot(self, name="BDD"):  # pragma: no cover
        """Convert to DOT language representation.

        See the
        `DOT language reference <http://www.graphviz.org/content/dot-language>`_
        for details.
        """
        parts = ["graph", name, "{"]
        for node in self.dfs_postorder():
            if node is BDDNODEZERO:
                parts += ["n" + str(id(node)), "[label=0,shape=box];"]
            elif node is BDDNODEONE:
                parts += ["n" + str(id(node)), "[label=1,shape=box];"]
            else:
                v = _VARS[node.root]
                parts.append("n" + str(id(node)))
                parts.append(f"[label=\"{v}\",shape=circle];")
        for node in self.dfs_postorder():
            if node is not BDDNODEZERO and node is not BDDNODEONE:
                parts += ["n" + str(id(node)), "--",
                          "n" + str(id(node.lo)),
                          "[label=0,style=dashed];"]
                parts += ["n" + str(id(node)), "--",
                          "n" + str(id(node.hi)),
                          "[label=1];"]
        parts.append("}")
        return " ".join(parts)


class BDDConstant(BinaryDecisionDiagram):
    """Binary decision diagram constant zero/one

    The ``BDDConstant`` class is useful for type checking,
    e.g. ``isinstance(f, BDDConstant)``.

    Do **NOT** create a BDD using the ``BDDConstant`` constructor.
    BDD instances are managed internally,
    and the BDD zero/one instances are singletons.
    """
    def __init__(self, node, value):
        super().__init__(node)
        self.value = value

    def __bool__(self):
        return bool(self.value)

    def __int__(self):
        return self.value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.value)


BDDZERO = _BDDS[BDDNODEZERO] = BDDConstant(BDDNODEZERO, 0)
BDDONE = _BDDS[BDDNODEONE] = BDDConstant(BDDNODEONE, 1)


class BDDVariable(boolfunc.Variable, BinaryDecisionDiagram):
    """Binary decision diagram variable

    The ``BDDVariable`` class is useful for type checking,
    e.g. ``isinstance(f, BDDVariable)``.

    Do **NOT** create a BDD using the ``BDDVariable`` constructor.
    Use the :func:`bddvar` function instead.
    """
    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.names, bvar.indices)
        node = _bddnode(bvar.uniqid, BDDNODEZERO, BDDNODEONE)
        BinaryDecisionDiagram.__init__(self, node)


def _neg(node):
    """Return the inverse of *node*."""
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
        npoint0 = {root: BDDNODEZERO}
        npoint1 = {root: BDDNODEONE}
        fv0, gv0, hv0 = [_restrict(node, npoint0) for node in (f, g, h)]
        fv1, gv1, hv1 = [_restrict(node, npoint1) for node in (f, g, h)]
        return _bddnode(root, _ite(fv0, gv0, hv0), _ite(fv1, gv1, hv1))


def _restrict(node, npoint, cache=None):
    """Restrict a subset of support variables to {0, 1}."""
    if node is BDDNODEZERO or node is BDDNODEONE:
        return node

    if cache is None:
        cache = {}

    try:
        ret = cache[node]
    except KeyError:
        try:
            val = npoint[node.root]
        except KeyError:
            lo = _restrict(node.lo, npoint, cache)
            hi = _restrict(node.hi, npoint, cache)
            ret = _bddnode(node.root, lo, hi)
        else:
            child = {BDDNODEZERO: node.lo, BDDNODEONE: node.hi}[val]
            ret = _restrict(child, npoint, cache)
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
        if rand:  # pragma: no cover
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
