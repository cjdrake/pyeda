"""
Binary Decision Diagrams

Interface Functions:
    bddvar
    expr2bdd
    bdd2expr

Interface Classes:
    BinaryDecisionDiagram
    BDDConstant
    BDDVariable
"""

import collections

from pyeda import boolfunc
from pyeda.common import cached_property
from pyeda.expr import exprvar, Or, And, EXPRZERO, EXPRONE

# existing BDDVariable references
BDDVARIABLES = dict()

BDDNode = collections.namedtuple('BDDNode', ['root', 'low', 'high'])

BDDNODES = dict()
BDDS = dict()

BDDNODEZERO = BDDNODES[(-2, None, None)] = BDDNode(-2, None, None)
BDDNODEONE = BDDNODES[(-1, None, None)] = BDDNode(-1, None, None)


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
    bvar = boolfunc.var(name, indices, namespace)
    try:
        var = BDDVARIABLES[bvar.uniqid]
    except KeyError:
        var = BDDVARIABLES[bvar.uniqid] = BDDVariable(bvar)
        BDDS[var.node] = var
    return var

def expr2bdd(expr):
    """Convert an expression into a binary decision diagram."""
    return _bdd(_expr2node(expr))

def _expr2node(expr):
    """Convert an expression into a BDD node."""
    if expr is EXPRZERO:
        return BDDNODEZERO
    elif expr is EXPRONE:
        return BDDNODEONE
    else:
        top = expr.top

        # Register this variable
        _ = bddvar(top.name, top.indices, top.namespace)

        root = top.uniqid
        low = _expr2node(expr.restrict({top: 0}))
        high = _expr2node(expr.restrict({top: 1}))
        return _bdd_node(root, low, high)

def bdd2expr(bdd, conj=False):
    """Convert a binary decision diagram into an expression."""
    if bdd.node is BDDNODEZERO:
        return EXPRZERO
    elif bdd.node is BDDNODEONE:
        return EXPRONE
    else:
        if conj:
            outer, inner = (And, Or)
            paths = iter_all_paths(bdd.node, BDDNODEZERO)
        else:
            outer, inner = (Or, And)
            paths = iter_all_paths(bdd.node, BDDNODEONE)
        terms = list()
        for path in paths:
            expr_point = {exprvar(v.name, v.indices, v.namespace): val
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
        return _bdd(neg(self.node))

    def __add__(self, other):
        other_node = self.box(other).node
        # x + y <=> ITE(x, 1, y)
        return _bdd(ite(self.node, BDDNODEONE, other_node))

    def __sub__(self, other):
        other_node = self.box(other).node
        # x - y <=> ITE(x, 1, y')
        return _bdd(ite(self.node, BDDNODEONE, neg(other_node)))

    def __mul__(self, other):
        other_node = self.box(other).node
        # x * y <=> ITE(x, y, 0)
        return _bdd(ite(self.node, other_node, BDDNODEZERO))

    def xor(self, other):
        other_node = self.box(other).node
        # x (xor) y <=> ITE(x, y', y)
        return _bdd(ite(self.node, neg(other_node), other_node))

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
        return _bdd(urestrict(self.node, upoint))

    def compose(self, mapping):
        node = self.node
        for v, g in mapping.items():
            fv0, fv1 = _bdd(node).cofactors(v)
            node = ite(g.node, fv1.node, fv0.node)
        return _bdd(node)

    def satisfy_one(self):
        path = find_path(self.node, BDDNODEONE)
        if path is None:
            return None
        else:
            return path2point(path)

    def satisfy_all(self):
        for path in iter_all_paths(self.node, BDDNODEONE):
            yield path2point(path)

    def satisfy_count(self):
        return sum(1 for _ in self.satisfy_all())

    def is_neg_unate(self, vs=None):
        raise NotImplementedError()

    def is_pos_unate(self, vs=None):
        raise NotImplementedError()

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
            fstr = "argument cannot be converted to BDD: " + str(arg)
            raise TypeError(fstr)

    # Specific to BinaryDecisionDiagram
    def traverse(self):
        """Iterate through all nodes in this BDD in DFS order."""
        visited = set()
        for node in dfs(self.node, visited):
            visited.add(node)
            yield node

    def equivalent(self, other):
        """Return whether this BDD is equivalent to another."""
        other = self.box(other)
        return self.node is other.node


class BDDConstant(BinaryDecisionDiagram):
    """Binary decision diagram constant"""
    pass


class _BDDZero(BDDConstant):
    """Binary decision diagram zero"""

    def __init__(self):
        super(_BDDZero, self).__init__(BDDNODEZERO)

    def __bool__(self):
        return False

    def __int__(self):
        return 0

    def __str__(self):
        return '0'


class _BDDOne(BDDConstant):
    """Binary decision diagram one"""

    def __init__(self):
        super(_BDDOne, self).__init__(BDDNODEONE)

    def __bool__(self):
        return True

    def __int__(self):
        return 1

    def __str__(self):
        return '1'


BDDZERO = BDDS[BDDNODEZERO] = _BDDZero()
BDDONE = BDDS[BDDNODEONE] = _BDDOne()


class BDDVariable(boolfunc.Variable, BinaryDecisionDiagram):
    """Binary decision diagram variable"""

    def __init__(self, bvar):
        boolfunc.Variable.__init__(self, bvar.namespace, bvar.name,
                                   bvar.indices)
        node = _bdd_node(bvar.uniqid, BDDNODEZERO, BDDNODEONE)
        BinaryDecisionDiagram.__init__(self, node)


def neg(node):
    """Return the node that is the inverse of the input node."""
    if node is BDDNODEZERO:
        return BDDNODEONE
    elif node is BDDNODEONE:
        return BDDNODEZERO
    else:
        return _bdd_node(node.root, neg(node.low), neg(node.high))

def ite(f, g, h):
    """Return node that results from recursively applying ITE(f, g, h)."""
    # ITE(f, 1, 0) = f
    if g is BDDNODEONE and h is BDDNODEZERO:
        return f
    # ITE(f, 0, 1) = -f
    elif g is BDDNODEZERO and h is BDDNODEONE:
        return neg(f)
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
        fv0, gv0, hv0 = [urestrict(node, upoint0) for node in (f, g, h)]
        fv1, gv1, hv1 = [urestrict(node, upoint1) for node in (f, g, h)]
        return _bdd_node(root, ite(fv0, gv0, hv0), ite(fv1, gv1, hv1))

def urestrict(node, upoint):
    """Return node that results from untyped point restriction."""
    if node is BDDNODEZERO or node is BDDNODEONE:
        return node
    elif node.root in upoint[0]:
        return urestrict(node.low, upoint)
    elif node.root in upoint[1]:
        return urestrict(node.high, upoint)
    else:
        low = urestrict(node.low, upoint)
        high = urestrict(node.high, upoint)
        return _bdd_node(node.root, low, high)

def find_path(start, end, path=tuple()):
    """Return the path from start to end.

    If no path exists, return None.
    """
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
    """Iterate through all paths from start to end."""
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
    """Iterate through a depth-first traveral starting at node."""
    low, high = node.low, node.high
    if low not in visited and low is not None:
        for _node in dfs(low, visited):
            yield _node
    if high not in visited and high is not None:
        for _node in dfs(high, visited):
            yield _node
    if node not in visited:
        yield node

def _bdd_node(root, low, high):
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

def _bdd(node):
    """Return a unique BDD."""
    try:
        bdd = BDDS[node]
    except KeyError:
        bdd = BDDS[node] = BinaryDecisionDiagram(node)
    return bdd
