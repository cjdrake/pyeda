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

def apply2(op, f1, f2):
    """Recursively apply a binary operator to two Boolean functions.

    NOTE: Both f1 and f2 must implement '-', '*', and '+' operators.
    """
    if f1 in {0, 1}:
        if f2 in {0, 1}:
            return op[f1][f2]
        else:
            x = f2.top
            f1x = (f1, f1)
            f2x = f2.cofactors(x)
    else:
        if f2 in {0, 1}:
            x = f1.top
            f1x = f1.cofactors(x)
            f2x = (f2, f2)
        else:
            x = min(f1.top, f2.top)
            f1x = f1.cofactors(x)
            f2x = f2.cofactors(x)
    return ( -x * apply2(op, f1x[0], f2x[0]) +
              x * apply2(op, f1x[1], f2x[1]) )
