"""
Python EDA Package
"""

__version__ = "0.13.0"

# Positional Cube Notation
PC_VOID, PC_ONE, PC_ZERO, PC_DC = range(4)

import pyeda.alphas
import pyeda.arithmetic

from pyeda.util import clog2, boolify

from pyeda.boolfunc import (
    num2point, num2upoint, num2term, point2upoint, point2term,
    iter_points, iter_upoints, iter_terms,
)
from pyeda.expr import (
    exprvar, exprcomp, upoint2exprpoint,
    Or, And, Not, Xor, Xnor, Equal, Implies, ITE,
    Nor, Nand, OneHot0, OneHot,
)
from pyeda.vexpr import (
    bitvec, uint2vec, int2vec, BitVector,
)
from pyeda.nfexpr import (
    expr2dnf, expr2cnf, nf2expr, upoint2nfpoint,
    NF_Not, CNF_And, DNF_Or,
    NormalForm, DisjNormalForm, ConjNormalForm,
)
from pyeda.table import (
    ttvar, truthtable, expr2truthtable, truthtable2expr,
    TruthTable, TTConstant, TTVariable,
)
from pyeda.bdd import (
    bddvar, bddnode, bdd, expr2bddnode, expr2bdd, bdd2expr, upoint2bddpoint,
    BinaryDecisionDiagram, BDDConstant, BDDVariable,
)

from pyeda.parsing.dimacs import (
    load_cnf, dump_cnf, load_sat, dump_sat,
)
from pyeda.parsing.boolexpr import str2expr
