"""
Interactive Use

To prepare a terminal for interactive use:

    >>> from pyeda.inter import *
"""

# Disable "unused import"
# pylint: disable=W0611

from pyeda.util import clog2, parity, boolify

from pyeda.boolfunc import (
    num2point, num2upoint, num2term,
    point2upoint, point2term,
    iter_points, iter_upoints, iter_terms,
    Variable, Function, VectorFunction,
)

from pyeda.bdd import (
    bddvar, bddnode, bdd, expr2bddnode, expr2bdd, bdd2expr,
    BinaryDecisionDiagram, BDDConstant, BDDVariable,
)

from pyeda.expr import (
    exprvar, exprcomp, expr,
    ast2expr, expr2dimacscnf, expr2dimacssat, upoint2exprpoint,
    Or, And, Not, Xor, Xnor, Equal, Implies, ITE,
    Nor, Nand, OneHot0, OneHot,
    Expression, ExprConstant, ExprLiteral, ExprVariable, ExprComplement,
    ExprOrAnd, ExprOr, ExprAnd, ExprNot,
    ExprExclusive, ExprXor, ExprXnor, ExprEqual, ExprImplies, ExprITE,
)

from pyeda.table import (
    ttvar, truthtable, expr2truthtable, truthtable2expr,
    TruthTable, TTConstant, TTVariable,
)

from pyeda.vexpr import bitvec, uint2vec, int2vec, BitVector

from pyeda.parsing.lex import LexRunError

from pyeda.parsing.dimacs import DIMACSError, parse_cnf, parse_sat
