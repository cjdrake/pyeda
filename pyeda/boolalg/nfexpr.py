"""
Boolean Normal Form Expressions

Interface Functions:
    expr2dnf
    expr2cnf
    nf2expr
    upoint2nfpoint
    NF_Not
    DNF_Or
    CNF_And

Interface Classes:
    NormalForm
    DisjNormalForm
    ConjNormalForm

.. NOTE:: Unlike other Boolean function representations, normal form
          expressions do not have their own Variable implementation. It uses
          the ExprVariable implementation wherever required.
"""

from pyeda.boolalg import boolfunc
from pyeda.boolalg import sat
from pyeda.boolalg.expr import EXPRVARIABLES
from pyeda.boolalg.expr import (
    Expression, ExprLiteral, ExprOr, ExprAnd
)
from pyeda.util import bit_on, cached_property

def expr2dnf(expr):
    """Convert an expression into a disjunctive normal form representation."""
    if not isinstance(expr, Expression):
        raise TypeError("input is not an Expression: " + str(expr))

    if expr.is_zero():
        return DisjNormalForm()
    elif expr.is_dnf():
        # a
        if expr.depth == 0:
            clauses = {frozenset([expr.uniqid])}
            return DisjNormalForm(clauses)
        elif expr.depth == 1:
            # a + b
            if isinstance(expr, ExprOr):
                clauses = {frozenset([lit.uniqid]) for lit in expr.args}
            # a * b
            elif isinstance(expr, ExprAnd):
                clauses = {frozenset(lit.uniqid for lit in expr.args)}
            return DisjNormalForm(clauses)
        elif expr.depth == 2:
            clauses = set()
            # a + (b * c)
            if isinstance(expr, ExprOr):
                for arg in expr.args:
                    if isinstance(arg, ExprLiteral):
                        clauses.add(frozenset([arg.uniqid]))
                    elif isinstance(arg, ExprAnd):
                        clauses.add(frozenset(lit.uniqid for lit in arg.args))
                return DisjNormalForm(clauses)

    raise ValueError("Expression cannot be converted to DNF: " + str(expr))

def expr2cnf(expr):
    """Convert an expression into a conjunctive normal form representation."""
    if not isinstance(expr, Expression):
        raise TypeError("input is not an Expression: " + str(expr))

    if expr.is_one():
        return ConjNormalForm()
    elif expr.is_cnf():
        # a
        if expr.depth == 0:
            clauses = {frozenset([expr.uniqid])}
            return ConjNormalForm(clauses)
        elif expr.depth == 1:
            # a + b
            if isinstance(expr, ExprOr):
                clauses = {frozenset(lit.uniqid for lit in expr.args)}
            # a * b
            elif isinstance(expr, ExprAnd):
                clauses = {frozenset([lit.uniqid]) for lit in expr.args}
            return ConjNormalForm(clauses)
        elif expr.depth == 2:
            clauses = set()
            # a * (b + c)
            if isinstance(expr, ExprAnd):
                for arg in expr.args:
                    if isinstance(arg, ExprLiteral):
                        clauses.add(frozenset([arg.uniqid]))
                    elif isinstance(arg, ExprOr):
                        clauses.add(frozenset(lit.uniqid for lit in arg.args))
                return ConjNormalForm(clauses)

    raise ValueError("Expression cannot be converted to CNF: " + str(expr))

def nf2expr(nf):
    """Convert a normal form representation into an expression."""
    if isinstance(nf, DisjNormalForm):
        outer, inner = ExprOr, ExprAnd
    elif isinstance(nf, ConjNormalForm):
        outer, inner = ExprAnd, ExprOr
    else:
        raise TypeError("input is not a NormalForm instance: " + str(nf))

    terms = list()
    for clause in nf.clauses:
        term = list()
        for uniqid in clause:
            if uniqid < 0:
                lit = -EXPRVARIABLES[-uniqid]
            else:
                lit = EXPRVARIABLES[uniqid]
            term.append(lit)
        terms.append(term)

    return outer(*[inner(*term) for term in terms])

def upoint2nfpoint(upoint):
    """Convert an untyped point to a NormalForm point."""
    point = dict()
    for uniqid in upoint[0]:
        point[EXPRVARIABLES[uniqid]] = 0
    for uniqid in upoint[1]:
        point[EXPRVARIABLES[uniqid]] = 1
    return point

def NF_Not(arg):
    """Return an inverted normal form expression."""
    nf = _nfify(arg)
    clauses = { frozenset(-uniqid for uniqid in clause)
                for clause in nf.clauses }
    return nf.get_dual()(clauses)

def DNF_Or(*args):
    """Return the disjunction of normal form expressions."""
    args = tuple(_dnfify(arg) for arg in args)

    clauses = set()
    for arg in args:
        clauses.update(arg.clauses)
    return DisjNormalForm(clauses)

def CNF_And(*args):
    """Return the conjunction of normal form expression."""
    args = tuple(_cnfify(arg) for arg in args)

    clauses = set()
    for arg in args:
        clauses.update(arg.clauses)
    return ConjNormalForm(clauses)


class NormalForm(sat.DPLLInterface):
    """
    Normal Form Representation
    """
    def __init__(self, clauses=None):
        if clauses is None:
            self.clauses = set()
        else:
            self.clauses = clauses

    def __str__(self):
        if not self.clauses:
            return str(self.IDENTITY)
        else:
            return str(nf2expr(self))

    def __repr__(self):
        return self.__str__()

    # Operators
    def __neg__(self):
        return NF_Not(self)

    def __add__(self, other):
        return DNF_Or(self, other)

    def __sub__(self, other):
        return DNF_Or(self, NF_Not(other))

    def __mul__(self, other):
        return CNF_And(self, other)

    # From Function
    @cached_property
    def support(self):
        return frozenset(EXPRVARIABLES[abs(uniqid)]
                         for clause in self.clauses for uniqid in clause)

    @cached_property
    def inputs(self):
        return sorted(self.support)

    def restrict(self, point):
        return self.urestrict(boolfunc.point2upoint(point))

    def urestrict(self, upoint):
        idents = set()
        idents.update(upoint[self.DOMINATOR])
        idents.update(-n for n in upoint[self.IDENTITY])

        doms = set()
        doms.update(upoint[self.IDENTITY])
        doms.update(-n for n in upoint[self.DOMINATOR])

        new_clauses = set()
        for clause in self.clauses:
            if not clause & doms:
                new_clause = clause - idents
                if new_clause:
                    new_clauses.add(new_clause)
                else:
                    dual = self.get_dual()
                    return dual()
        return self.__class__(new_clauses)

    def is_zero(self):
        return False

    def is_one(self):
        return False

    # Specific to NormalForm
    def get_dual(self):
        """Return the dual function.

        The dual or Or is And, and the dual of Or is And.
        """
        raise NotImplementedError()

    def absorb(self):
        """Return the OR/AND expression after absorption.

        x * (x * y) = x
        x * (x + y) = x
        """
        temps = list(self.clauses)
        new_clauses = set()

        # Drop all terms that are a superset of other terms
        while temps:
            fst, rst, temps = temps[0], temps[1:], list()
            drop_fst = False
            for term in rst:
                drop_term = False
                if fst <= term:
                    drop_term = True
                elif fst > term:
                    drop_fst = True
                if not drop_term:
                    temps.append(term)
            if not drop_fst:
                new_clauses.add(fst)

        return self.__class__(new_clauses)

    def reduce(self):
        """Reduce this expression to a canonical form."""
        support = frozenset(abs(uniqid) for clause in self.clauses
                            for uniqid in clause)
        new_clauses = set()
        for clause in self.clauses:
            vs = list(support - {abs(uniqid) for uniqid in clause})
            if vs:
                for num in range(1 << len(vs)):
                    new_part = {v if bit_on(num, i) else -v
                                for i, v in enumerate(vs)}
                    new_clauses.add(clause | new_part)
            else:
                new_clauses.add(clause)
        return self.__class__(new_clauses)

    IDENTITY = NotImplemented
    DOMINATOR = NotImplemented


class DisjNormalForm(NormalForm):
    """
    Disjunctive Normal Form
    """
    def is_zero(self):
        return not self.clauses

    # Specific to NormalForm
    def get_dual(self):
        return ConjNormalForm

    # DPLL IF
    def bcp(self):
        return None

    def ple(self):
        return None

    IDENTITY = 0
    DOMINATOR = 1


class ConjNormalForm(NormalForm):
    """
    Conjunctive Normal Form
    """
    def satisfy_one(self):
        solution = sat.dpll(self)
        if solution is None:
            return None
        else:
            return upoint2nfpoint(solution)

    def satisfy_all(self):
        for upoint in sat.iter_backtrack(self):
            yield upoint2nfpoint(upoint)

    def is_one(self):
        return not self.clauses

    # DPLL IF
    def bcp(self):
        zeros, ones = set(), set()
        for clause in self.clauses:
            if len(clause) == 1:
                uniqid = list(clause)[0]
                if uniqid < 0:
                    zeros.add(-uniqid)
                else:
                    ones.add(uniqid)
        if zeros or ones:
            upnt = frozenset(zeros), frozenset(ones)
            bcp_upnt = self.urestrict(upnt).bcp()
            if bcp_upnt is None:
                return None
            else:
                return (upnt[0] | bcp_upnt[0], upnt[1] | bcp_upnt[1])
        else:
            return frozenset(), frozenset()

    def ple(self):
        zeros, ones = set(), set()
        for clause in self.clauses:
            for uniqid in clause:
                if uniqid < 0:
                    zeros.add(-uniqid)
                else:
                    ones.add(uniqid)
        return frozenset(zeros - ones), frozenset(ones - zeros)

    # Specific to NormalForm
    def get_dual(self):
        return DisjNormalForm

    IDENTITY = 1
    DOMINATOR = 0


def _nfify(arg):
    """Convert input argument to normal form expression."""
    if isinstance(arg, NormalForm):
        return arg
    elif arg == 0 or arg == '0':
        return DisjNormalForm()
    elif arg == 1 or arg == '1':
        return ConjNormalForm()
    elif isinstance(arg, Expression):
        if arg.is_cnf():
            return expr2cnf(arg)
        elif arg.is_dnf():
            return expr2dnf(arg)
        else:
            raise ValueError("Expression is not in normal form: " + str(arg))
    else:
        raise TypeError("input cannot be converted to NormalForm: " + str(arg))

def _dnfify(arg):
    """Convert input argument to disjunctive normal form expression."""
    if arg == 0 or arg == '0':
        return DisjNormalForm()
    elif isinstance(arg, DisjNormalForm):
        return arg
    elif isinstance(arg, Expression):
        return expr2dnf(arg)
    else:
        fstr = "input cannot be converted to DisjNormalForm: " + str(arg)
        raise TypeError(fstr)

def _cnfify(arg):
    """Convert input argument to conjunctive normal form expression."""
    if arg == 1 or arg == '1':
        return ConjNormalForm()
    elif isinstance(arg, ConjNormalForm):
        return arg
    elif isinstance(arg, Expression):
        return expr2cnf(arg)
    else:
        fstr = "input cannot be converted to ConjNormalForm: " + str(arg)
        raise TypeError(fstr)
