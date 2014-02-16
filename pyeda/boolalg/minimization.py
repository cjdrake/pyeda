"""
Boolean Minimization

Interface Functions:
    espresso_exprs
"""

from pyeda.boolalg import boolfunc
from pyeda.boolalg.espresso import (
    FTYPE, DTYPE, RTYPE,
    set_config, espresso, EspressoError,
)
from pyeda.boolalg.expr import exprvar, Expression, Or, And
from pyeda.boolalg.table import TruthTable, PC_ZERO, PC_ONE, PC_DC

CONFIG = dict(
    single_expand=False,
    remove_essential=True,
    force_irredundant=True,
    unwrap_onset=True,
    recompute_onset=False,
    use_super_gasp=False,
)

def espresso_exprs(*exprs):
    """Return a tuple of expressions optimized using Espresso."""
    for f in exprs:
        if not (isinstance(f, Expression) and f.is_dnf()):
            raise ValueError("expected a DNF expression")

    support = frozenset.union(*[f.support for f in exprs])
    inputs = sorted(support)

    # Gather all cubes in the cover of input functions
    fscover = set()
    for f in exprs:
        fscover |= f.cover

    ninputs = len(inputs)
    noutputs = len(exprs)

    cover = set()
    for fscube in fscover:
        invec = list()
        for v in inputs:
            if ~v in fscube:
                invec.append(1)
            elif v in fscube:
                invec.append(2)
            else:
                invec.append(3)
        outvec = list()
        for f in exprs:
            for fcube in f.cover:
                if fcube <= fscube:
                    outvec.append(1)
                    break
            else:
                outvec.append(0)

        cover.add((tuple(invec), tuple(outvec)))

    set_config(**CONFIG)

    cover = espresso(ninputs, noutputs, cover, intype=FTYPE)
    return _cover2exprs(inputs, noutputs, cover)

def espresso_tts(*tts):
    """Return a tuple of expressions optimized using Espresso."""
    for f in tts:
        if not isinstance(f, TruthTable):
            raise ValueError("expected a TruthTable instance")

    support = frozenset.union(*[f.support for f in tts])
    inputs = sorted(support)

    ninputs = len(inputs)
    noutputs = len(tts)

    cover = set()
    for i, point in enumerate(boolfunc.iter_points(inputs)):
        invec = [2 if point[v] else 1 for v in inputs]
        outvec = list()
        for f in tts:
            val = f.pcdata[i]
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

    cover = espresso(ninputs, noutputs, cover, intype=FTYPE|DTYPE|RTYPE)
    inputs = [exprvar(v.names, v.indices) for v in inputs]
    return _cover2exprs(inputs, noutputs, cover)

def _cover2exprs(inputs, noutputs, cover):
    """Convert a cover to a tuple of Expression instances."""
    fs = list()
    for i in range(noutputs):
        terms = list()
        for invec, outvec in cover:
            if outvec[i]:
                term = list()
                for j, v in enumerate(inputs):
                    if invec[j] == 1:
                        term.append(~v)
                    elif invec[j] == 2:
                        term.append(v)
                terms.append(term)
        fs.append(Or(*[And(*term) for term in terms]))

    return tuple(fs)

