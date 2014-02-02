"""
Test the Espresso interface
"""

from pyeda.boolalg.vexpr import bitvec
from pyeda.boolalg.minimization import espresso_exprs
from pyeda.logic.addition import ripple_carry_add

def test_espresso():
    A = bitvec('a', 16)
    B = bitvec('b', 16)
    S, C = ripple_carry_add(A, B)
    s0, s1, s2, s3 = espresso_exprs(S[0].to_dnf(), S[1].to_dnf(),
                                    S[2].to_dnf(), S[3].to_dnf())

    assert s0.equivalent(S[0])
    assert s1.equivalent(S[1])
    assert s2.equivalent(S[2])
    assert s3.equivalent(S[3])

