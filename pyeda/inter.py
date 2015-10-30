"""
Interactive Use

To prepare a terminal for interactive use:

    >>> from pyeda.inter import *
"""


# Disable "unused-import", since that's basically all this module is for.
# pylint: disable=W0611


from pyeda.util import clog2, parity

from pyeda.boolalg.boolfunc import (
    num2point, num2upoint, num2term,
    point2upoint, point2term,
    iter_points, iter_upoints, iter_terms,
    vpoint2point,
    Variable, Function,
)

from pyeda.boolalg.bdd import (
    bddvar, expr2bdd, bdd2expr, upoint2bddpoint, ite,
    BDDNode, BinaryDecisionDiagram, BDDConstant, BDDVariable,
)

from pyeda.boolalg.expr import (
    exprvar, expr,
    ast2expr, expr2dimacscnf, expr2dimacssat, upoint2exprpoint,
    Not, Or, And, Nor, Nand, Xor, Xnor, Equal, Unequal, Implies, ITE,
    Nor, Nand, OneHot0, OneHot, NHot,
    AtMostN, AtLeastN, ExactlyN,
    Majority, AchillesHeel,
    Mux, ForAll, Exists,
    Expression,
    NormalForm, DisjNormalForm, ConjNormalForm, DimacsCNF,
)

from pyeda.boolalg.table import (
    ttvar, truthtable, expr2truthtable, truthtable2expr,
    TruthTable, TTConstant, TTVariable,
)

from pyeda.boolalg.bfarray import (
    bddzeros, bddones, bddvars,
    exprzeros, exprones, exprvars,
    ttzeros, ttones, ttvars,
    uint2bdds, uint2exprs, uint2tts,
    int2bdds, int2exprs, int2tts,
    fcat,
    farray,
)

from pyeda.boolalg.minimization import espresso_exprs, espresso_tts

from pyeda.parsing.boolexpr import parse as parse_expr

from pyeda.parsing.dimacs import parse_cnf, parse_sat

