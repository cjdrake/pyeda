"""
Interactive Use

To prepare a terminal for interactive use:

    >>> from pyeda.inter import *
"""

# Disable "unused import"
# pylint: disable=W0611

from pyeda.util import clog2, parity, boolify

from pyeda.boolalg.boolfunc import (
    num2point, num2upoint, num2term,
    point2upoint, point2term,
    iter_points, iter_upoints, iter_terms,
    Variable, Function, VectorFunction,
)

from pyeda.boolalg.bdd import (
    bddvar, bddnode, bdd, expr2bddnode, expr2bdd, bdd2expr,
    BinaryDecisionDiagram, BDDConstant, BDDVariable,
)

from pyeda.boolalg.expr import (
    exprvar, exprcomp, expr,
    ast2expr, expr2dimacssat, upoint2exprpoint,
    Not, Or, And, Nor, Nand, Xor, Xnor, Equal, Unequal, Implies, ITE,
    Nor, Nand, OneHot0, OneHot, Majority,
    ForAll, Exists,
    Expression, ExprConstant, ExprLiteral, ExprVariable, ExprComplement,
    ExprNot, ExprOrAnd, ExprOr, ExprAnd, ExprNor, ExprNand,
    ExprExclusive, ExprXor, ExprXnor, ExprEqual, ExprUnequal,
    ExprImplies, ExprITE,
    DimacsCNF,
)

from pyeda.boolalg.table import (
    ttvar, truthtable, expr2truthtable, truthtable2expr,
    TruthTable, TTConstant, TTVariable,
)

from pyeda.boolalg.vexpr import bitvec, uint2vec, int2vec, BitVector

from pyeda.parsing.lex import LexRunError

from pyeda.parsing.boolexpr import BoolExprParseError
from pyeda.parsing.boolexpr import parse as parse_expr

from pyeda.parsing.dimacs import DIMACSError, parse_cnf, parse_sat
