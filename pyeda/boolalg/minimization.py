"""
The :mod:`pyeda.boolalg.minimization` module contains interface functions for
two-level logic minimization.

Interface Functions:

* :func:`espresso_exprs`
* :func:`espresso_tts`
"""


# Disable 'no-name-in-module' error, b/c pylint can't look into C extensions
# pylint: disable=E0611


import os

from pyeda.boolalg import boolfunc
from pyeda.boolalg.expr import And, Expression, Or, exprvar
from pyeda.boolalg.table import PC_DC, PC_ONE, PC_ZERO, TruthTable

# ReadTheDocs doesn't build C extensions
# See http://docs.readthedocs.org/en/latest/faq.html for details
if os.getenv("READTHEDOCS") == "True":
    pass
else:
    from pyeda.boolalg.espresso import (DTYPE, FTYPE, RTYPE, espresso,
                                        set_config)


CONFIG = dict(
    single_expand=False,
    remove_essential=True,
    force_irredundant=True,
    unwrap_onset=True,
    recompute_onset=False,
    use_super_gasp=False,
)


def espresso_exprs(*exprs):
    """Return a tuple of expressions optimized using Espresso.

    The variadic *exprs* argument is a sequence of expressions.

    For example::

       >>> from pyeda.boolalg.expr import exprvar
       >>> a, b, c = map(exprvar, "abc")
       >>> f1 = Or(And(~a, ~b, ~c), And(~a, ~b, c), And(a, ~b, c), And(a, b, c), And(a, b, ~c))
       >>> f2 = Or(And(~a, ~b, c), And(a, ~b, c))
       >>> f1m, f2m = espresso_exprs(f1, f2)
       >>> f1.size, f1m.size
       (21, 10)
       >>> f1m.equivalent(f1)
       True
       >>> f2.size, f2m.size
       (9, 3)
       >>> f2m.equivalent(f2)
       True
    """
    for f in exprs:
        if not (isinstance(f, Expression) and f.is_dnf()):
            raise ValueError("expected a DNF expression")

    support = frozenset.union(*[f.support for f in exprs])
    inputs = sorted(support)

    ninputs = len(inputs)
    noutputs = len(exprs)

    # Gather all cubes in the cover of input functions
    if noutputs == 1:
        fscover = exprs[0].cover
    else:
        fscover = set()
        for f in exprs:
            fscover.update(f.cover)

    invec = [0] * ninputs
    outvec = [0] * noutputs
    cover = set()
    for fscube in fscover:
        for i, v in enumerate(inputs):
            if ~v in fscube:
                invec[i] = 1
            elif v in fscube:
                invec[i] = 2
            else:
                invec[i] = 3
        if noutputs == 1:
            cover.add((tuple(invec), (1,)))
        else:
            for i, f in enumerate(exprs):
                for fcube in f.cover:
                    if fcube <= fscube:
                        outvec[i] = 1
                        break
                else:
                    outvec[i] = 0
            cover.add((tuple(invec), tuple(outvec)))

    set_config(**CONFIG)

    cover = espresso(ninputs, noutputs, cover, intype=FTYPE)
    return _cover2exprs(inputs, noutputs, cover)


def pc_data_index(point, f):
    result = 0
    for key, value in point.items():
        if value:
            index = f.inputs.index(key)
            result |= (1 << index)
    return result


def espresso_tts(*tts):
    """Return a tuple of expressions optimized using Espresso.

    The variadic *tts* argument is a sequence of truth tables.

    For example::

       >>> from pyeda.boolalg.bfarray import exprvars
       >>> from pyeda.boolalg.table import truthtable
       >>> X = exprvars("x", 4)
       >>> f1 = truthtable(X, "0000011111------")
       >>> f2 = truthtable(X, "0001111100------")
       >>> f1m, f2m = espresso_tts(f1, f2)
       >>> f1m.equivalent(X[3] | X[0] & X[2] | X[1] & X[2])
       True
       >>> f2m.equivalent(X[2] | X[0] & X[1])
       True
    """
    for f in tts:
        if not isinstance(f, TruthTable):
            raise ValueError("expected a TruthTable instance")

    support = frozenset.union(*[f.support for f in tts])
    inputs = sorted(support)

    ninputs = len(inputs)
    noutputs = len(tts)

    cover = set()
    for point in boolfunc.iter_points(inputs):
        invec = [2 if point[v] else 1 for v in inputs]
        outvec = []
        for f in tts:
            val = f.pcdata[pc_data_index(point, f)]
            if val == PC_ZERO:
                outvec.append(0)
            elif val == PC_ONE:
                outvec.append(1)
            elif val == PC_DC:
                outvec.append(2)
            else:
                raise ValueError("expected truth table entry in {0, 1, -}")
        cover.add((tuple(invec), tuple(outvec)))

    set_config(**CONFIG)

    cover = espresso(ninputs, noutputs, cover, intype=FTYPE | DTYPE | RTYPE)
    inputs = [exprvar(v.names, v.indices) for v in inputs]
    return _cover2exprs(inputs, noutputs, cover)


def _cover2exprs(inputs, noutputs, cover):
    """Convert a cover to a tuple of Expression instances."""
    fs = []
    for i in range(noutputs):
        terms = []
        for invec, outvec in cover:
            if outvec[i]:
                term = []
                for j, v in enumerate(inputs):
                    if invec[j] == 1:
                        term.append(~v)
                    elif invec[j] == 2:
                        term.append(v)
                terms.append(term)
        fs.append(Or(*[And(*term) for term in terms]))

    return tuple(fs)
