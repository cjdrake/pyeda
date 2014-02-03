"""
Boolean Minimization

Interface Functions:
    espresso_exprs
"""

from pyeda.boolalg.espresso import (
    FTYPE, DTYPE, RTYPE,
    espresso,
)
from pyeda.boolalg.expr import Expression, Or, And

def espresso_exprs(*exprs):
    """Return a list of expressions optimized using Espresso."""
    support = frozenset.union(*[f.support for f in exprs])
    inputs = sorted(support)

    # Gather all cubes in the cover of input functions
    fscover = set()
    for f in exprs:
        if not (isinstance(f, Expression) and f.is_dnf()):
            raise ValueError("expected a DNF expression, got " + str(f))
        fscover |= f.cover

    num_inputs = len(inputs)
    num_outputs = len(exprs)

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

    cover = espresso(num_inputs, num_outputs, cover, intype=FTYPE)

    fs = list()
    for i in range(num_outputs):
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

