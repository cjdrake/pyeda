"""
Boolean Binary Operators

Constants:
    OP_ZERO
    OP_AND
    OP_GT
    OP_FST
    OP_LT
    OP_SND
    OP_XOR
    OP_OR
    OP_NOR
    OP_XNOR
    OP_NSND
    OP_GTE
    OP_NFST
    OP_LTE
    OP_NAND
    OP_ONE

Interface Functions:
    apply2
"""

# FST (OP) SND
OP_ZERO = ((0, 0), (0, 0))
OP_AND  = ((0, 0), (0, 1))
OP_GT   = ((0, 0), (1, 0))
OP_FST  = ((0, 0), (1, 1))
OP_LT   = ((0, 1), (0, 0))
OP_SND  = ((0, 1), (0, 1))
OP_XOR  = ((0, 1), (1, 0))
OP_OR   = ((0, 1), (1, 1))
OP_NOR  = ((1, 0), (0, 0))
OP_XNOR = ((1, 0), (0, 1))
OP_NSND = ((1, 0), (1, 0))
OP_GTE  = ((1, 0), (1, 1))
OP_NFST = ((1, 1), (0, 0))
OP_LTE  = ((1, 1), (0, 1))
OP_NAND = ((1, 1), (1, 0))
OP_ONE  = ((1, 1), (1, 1))

def apply2(op, f, g):
    """Recursively apply a binary operator to two Boolean functions.

    NOTE: Both f and g must implement '-', '*', and '+' operators.
    """
    if f in {0, 1}:
        if g in {0, 1}:
            return op[f][g]
        else:
            v = g.top
            fv0, fv1 = (f, f)
            gv0, gv1 = g.cofactors(v)
    else:
        if g in {0, 1}:
            v = f.top
            fv0, fv1 = f.cofactors(v)
            gv0, gv1 = (g, g)
        else:
            v = min(f.top, g.top)
            fv0, fv1 = f.cofactors(v)
            gv0, gv1 = g.cofactors(v)
    return ( -v * apply2(op, fv0, gv0) +
              v * apply2(op, fv1, gv1) )
