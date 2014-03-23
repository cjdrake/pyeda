"""
Test the Espresso interface
"""

import os
from multiprocessing import Pool

from pyeda.boolalg import espresso
from pyeda.boolalg.table import truthtable2expr, truthtable
from pyeda.boolalg.bfarray import exprvars
from pyeda.boolalg.minimization import espresso_exprs, espresso_tts
from pyeda.logic.addition import ripple_carry_add
from pyeda.parsing.pla import parse_pla

from pyeda.inter import exprvar

from nose.tools import assert_raises

BOOM_PLAS = [
    'bb_50x5x50_20%_0.pla',
    'bb_50x5x50_20%_1.pla',
    'bb_50x5x50_20%_2.pla',
    'bb_50x5x50_20%_3.pla',
    'bb_50x5x50_20%_4.pla',
    'bb_50x5x50_20%_5.pla',
    'bb_50x5x50_20%_6.pla',
    'bb_50x5x50_20%_7.pla',
]

def test_espresso():
    assert espresso.FTYPE == 1
    assert espresso.DTYPE == 2
    assert espresso.RTYPE == 4

    A = exprvars('a', 16)
    B = exprvars('b', 16)
    S, C = ripple_carry_add(A, B)
    s0, s1, s2, s3 = espresso_exprs(S[0].to_dnf(), S[1].to_dnf(),
                                    S[2].to_dnf(), S[3].to_dnf())
    assert s0.equivalent(S[0])
    assert s1.equivalent(S[1])
    assert s2.equivalent(S[2])
    assert s3.equivalent(S[3])

    X = exprvars('x', 4)
    f1 = truthtable(X, "0000011111------")
    f2 = truthtable(X, "0001111100------")
    f1m, f2m = espresso_tts(f1, f2)
    truthtable2expr(f1).equivalent(f1m)
    truthtable2expr(f2).equivalent(f2m)

def test_issue75():
    """Reference: https://github.com/cjdrake/pyeda/issues/75"""
    b, x = map(exprvar, "bx")

    f_out = ~(b | ~x)
    f_out_dnf = f_out.to_dnf()
    assert f_out.equivalent(f_out_dnf)
    f_out_r, = espresso_exprs(f_out_dnf)
    assert f_out.equivalent(f_out_r)

def _do_espresso(fname):
    fpath = os.path.join('extension', 'espresso', 'test', 'bb_all', fname)
    with open(fpath) as fin:
        pla = parse_pla(fin)
    return espresso.espresso(pla['ninputs'], pla['noutputs'], pla['cover'], intype=pla['intype'])

def test_boom():
    p = Pool(4)
    # Espresso has an internal 'verify' function
    p.map(_do_espresso, BOOM_PLAS)

def test_errors():
    assert_raises(ValueError, espresso_exprs, "bad input")
    assert_raises(ValueError, espresso_tts, "bad input")

    # expected row vector of length 2
    assert_raises(ValueError, espresso.espresso, 2, 2, {(1, 2, 3)})
    # expected N inputs
    assert_raises(ValueError, espresso.espresso, 2, 2, {((1, 2, 3), (0, 0))})
    # expected input to be an int
    assert_raises(TypeError, espresso.espresso, 2, 2, {(('1', '2'), (0, 0))})
    # expected input in range
    assert_raises(ValueError, espresso.espresso, 2, 2, {(1, 4), (0, 0)})
    # expected N outputs
    assert_raises(ValueError, espresso.espresso, 2, 2, {((1, 2), (0, 0, 0))})
    # expected output to be an int
    assert_raises(TypeError, espresso.espresso, 2, 2, {((1, 2), ('0', '0'))})
    # expected output in {0, 1, 2}
    assert_raises(ValueError, espresso.espresso, 2, 2, {((1, 2), (0, 3))})
    # expected ninputs > 0
    assert_raises(ValueError, espresso.espresso, 0, 2, {((), (0, 0))})
    # expected noutputs > 0
    assert_raises(ValueError, espresso.espresso, 2, 0, {((1, 2), ())})
    # expected intype in {f, r, fd, fr, dr, fdr}
    assert_raises(ValueError, espresso.espresso, 2, 2, {((1, 2), (0, 1))}, intype=0)

