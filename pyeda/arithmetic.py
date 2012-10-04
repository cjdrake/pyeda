"""
Arithmetic Module
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved."

# pyeda
from pyeda.boolfunc import VectorFunction as VF
from pyeda.expr import Xor
from pyeda.vexpr import BitVector

def ripple_carry_add(A, B, cin=0):
    """Return symbolic logic for an N-bit ripple carry adder."""
    assert isinstance(B, BitVector) and len(A) == len(B)
    if A.bnr == VF.TWOS_COMPLEMENT or B.bnr == VF.TWOS_COMPLEMENT:
        sum_bnr = VF.TWOS_COMPLEMENT
    else:
        sum_bnr = VF.UNSIGNED
    S = list()
    C = list()
    for i, ai in enumerate(A):
        carry = (cin if i == 0 else C[i-1])
        S.append(Xor(ai, B.getifz(i), carry))
        C.append(ai * B.getifz(i) + ai * carry + B.getifz(i) * carry)
    return BitVector(S, bnr=sum_bnr), BitVector(C)
