"""
Test Module
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved."

# standard library
import random
import unittest

# pyeda
from pyeda.boolalg import (
    Zero, One,
    Variable, Complement,
    Buf, Not,
    Or, Nor, And, Nand,
    Xor, Xnor,
    Implies,
    factor, simplify, notf, orf, norf, andf, nandf, xorf, xnorf, impliesf,
    cube_sop, cube_pos,
    vec, svec, int2vec, uint2vec
)

class TestBoolalg(unittest.TestCase):

    def setUp(self):
        super(TestBoolalg, self).setUp()

    def tearDown(self):
        super(TestBoolalg, self).tearDown()

    def test_number(self):
        a, b = map(Variable, "ab")

        # __str__
        self.assertEqual(str(Zero), "0")
        self.assertEqual(str(One), "1")

        # __eq__
        for val in (Zero, False, 0, 0.0, "0"):
            self.assertEqual(Zero, val)
            self.assertNotEqual(One, val)
        for val in (One, True, 1, 1.0, "1"):
            self.assertNotEqual(Zero, val)
            self.assertEqual(One, val)

        # __lt__
        self.assertLess(Zero, One)
        self.assertGreater(One, Zero)
        self.assertLess(Zero, a)
        self.assertLess(One, a)
        self.assertLess(Zero, a + b)
        self.assertLess(One, a + b)

        # __bool__
        self.assertFalse(Zero)
        self.assertTrue(One)

        # depth
        self.assertEqual(Zero.depth, 1)
        self.assertEqual(One.depth, 1)

        # val
        self.assertEqual(Zero.val, 0)
        self.assertEqual(One.val, 1)

        # get_dual
        self.assertEqual(Zero.get_dual(), One)
        self.assertEqual(One.get_dual(), Zero)

        # subs
        self.assertEqual(Zero.subs({a: 0, b: 1}), 0)
        self.assertEqual(One.subs({a: 0, b: 1}), 1)

        # factor
        self.assertEqual(Zero.factor(), Zero)
        self.assertEqual(One.factor(), One)

        # simplify
        self.assertEqual(Zero.simplify(), Zero)
        self.assertEqual(One.simplify(), One)

    def test_literal(self):
        a, b = map(Variable, "ab")
        c0 = Variable("c", 0)
        c1 = Variable("c", 1)

        # __len__
        self.assertEqual(len(-a), 1)
        self.assertEqual(len(a), 1)

        # __str__
        self.assertEqual(str(-a), "a'")
        self.assertEqual(str(a), "a")
        self.assertEqual(str(c0), "c[0]")
        self.assertEqual(str(-c0), "c[0]'")
        self.assertEqual(str(c1), "c[1]")
        self.assertEqual(str(-c1), "c[1]'")

        # __eq__
        self.assertEqual(-a, -a)
        self.assertNotEqual(a, -a)
        self.assertNotEqual(-a, a)
        self.assertEqual(a, a)

        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        self.assertNotEqual(c0, c1)
        self.assertNotEqual(c1, c0)

        # __lt__
        self.assertLess(Zero, -a)
        self.assertLess(Zero, a)
        self.assertLess(One, -a)
        self.assertLess(One, a)
        self.assertLess(-a, a)
        self.assertLess(a, b)
        self.assertLess(c0, c1)
        self.assertLess(a, a + b)
        self.assertLess(b, a + b)

        # name
        self.assertEqual((-a).name, "a")
        self.assertEqual(a.name, "a")

        # index
        self.assertEqual((-a).index, -1)
        self.assertEqual(a.index, -1)
        self.assertEqual(c0.index, 0)
        self.assertEqual(c1.index, 1)

        # get_dual
        self.assertEqual((-a).get_dual(), a)
        self.assertEqual(a.get_dual(), -a)

        # support
        self.assertEqual((-a).support, {a})
        self.assertEqual(a.support, {a})

        # subs
        self.assertEqual(a.subs({a: 0}), 0)
        self.assertEqual(a.subs({a: 1}), 1)
        self.assertEqual(a.subs({a: -b}), -b)
        self.assertEqual(a.subs({a: b}), b)
        self.assertEqual((-a).subs({a: 0}), 1)
        self.assertEqual((-a).subs({a: 1}), 0)
        self.assertEqual((-a).subs({a: -b}), b)
        self.assertEqual((-a).subs({a: b}), -b)

        # factor
        self.assertEqual((-a).factor(), -a)
        self.assertEqual(a.factor(), a)

        # simplify
        self.assertEqual((-a).simplify(), -a)
        self.assertEqual(a.simplify(), a)

    def test_buf(self):
        a, b, c = map(Variable, "abc")

        self.assertEqual(Buf(0), 0)
        self.assertEqual(Buf(1), 1)
        self.assertEqual(Buf(-a), -a)
        self.assertEqual(Buf(a), a)

        self.assertEqual(Buf(Buf(a)), a)
        self.assertEqual(Buf(Buf(Buf(a))), a)
        self.assertEqual(Buf(Buf(Buf(Buf(a)))), a)

        # __str__
        self.assertEqual(str(Buf(-a + b)), "Buf(a' + b)")
        self.assertEqual(str(Buf(a + -b)), "Buf(a + b')")

        # support
        self.assertEqual(Buf(-a + b).support, {a, b})

        # subs
        self.assertEqual(Buf(-a + b).subs({a: 0}), 1)
        self.assertEqual(Buf(-a + b).subs({a: 1}), b)
        self.assertEqual(str(Buf(-a + b + c).subs({a: 1})), "Buf(b + c)")

        # factor
        self.assertEqual(str(Buf(-a + b).factor()), "a' + b")

        # simplify
        self.assertEqual(simplify(Buf(a + -a)), 1)
        self.assertEqual(simplify(Buf(a * -a)), 0)

    def test_not(self):
        a, b, c = map(Variable, "abc")

        self.assertEqual(Not(0), 1)
        self.assertEqual(Not(1), 0)
        self.assertEqual(Not(-a), a)
        self.assertEqual(Not(a), -a)

        self.assertEqual(-(-a), a)
        self.assertEqual(-(-(-a)), -a)
        self.assertEqual(-(-(-(-a))), a)

        # __str__
        self.assertEqual(str(Not(-a + b)), "Not(a' + b)")
        self.assertEqual(str(Not(a + -b)), "Not(a + b')")

        # support
        self.assertEqual(Not(-a + b).support, {a, b})

        # subs
        self.assertEqual(Not(-a + b).subs({a: 0}), 0)
        self.assertEqual(Not(-a + b).subs({a: 1}), -b)
        self.assertEqual(str(Not(-a + b + c).subs({a: 1})), "Not(b + c)")

        # factor
        self.assertEqual(str(Not(-a + b).factor()), "a * b'")

        # simplify
        self.assertEqual(simplify(Not(a + -a)), 0)
        self.assertEqual(simplify(Not(a * -a)), 1)

    def test_or(self):
        a, b, c, d = map(Variable, "abcd")

        self.assertEqual(Or(), Zero)
        self.assertEqual(Or(a), a)

        # __len__
        self.assertEqual(len(a + b + c), 3)

        # __str__
        self.assertEqual(str(a + b), "a + b")
        self.assertEqual(str(a + b + c), "a + b + c")
        self.assertEqual(str(a + b + c + d), "a + b + c + d")

        # __lt__
        self.assertLess(Zero, a + b)
        self.assertLess(One, a + b)

        self.assertLess(-a, a + b)
        self.assertLess(a, a + b)
        self.assertLess(-b, a + b)
        self.assertLess(b, a + b)

        self.assertLess(a + b, a + -b)   # 00 < 01
        self.assertLess(a + b, -a + b)   # 00 < 10
        self.assertLess(a + b, -a + -b)  # 00 < 11
        self.assertLess(a + -b, -a + b)  # 01 < 10
        self.assertLess(a + -b, -a + -b) # 01 < 11
        self.assertLess(-a + b, -a + -b) # 10 < 11

        self.assertLess(a + b, a + b + c)

        # associative
        self.assertEqual(str((a + b) + c + d),   "a + b + c + d")
        self.assertEqual(str(a + (b + c) + d),   "a + b + c + d")
        self.assertEqual(str(a + b + (c + d)),   "a + b + c + d")
        self.assertEqual(str((a + b) + (c + d)), "a + b + c + d")
        self.assertEqual(str((a + b + c) + d),   "a + b + c + d")
        self.assertEqual(str(a + (b + c + d)),   "a + b + c + d")
        self.assertEqual(str(a + (b + (c + d))), "a + b + c + d")
        self.assertEqual(str(((a + b) + c) + d), "a + b + c + d")

        # depth
        self.assertEqual((a + b).depth, 1)
        self.assertEqual((a + (b * c)).depth, 2)
        self.assertEqual((a + (b * (c + d))).depth, 3)

        # get_dual
        self.assertEqual(Or.get_dual(), And)

        # support
        self.assertEqual((-a + b + (-c * d)).support, {a, b, c, d})

        # subs
        f = -a * b * c + a * -b * c + a * b * -c
        fa0, fa1 = f.subs({a: 0}), f.subs({a: 1})
        self.assertEqual(str(fa0), "b * c")
        self.assertEqual(str(fa1), "b' * c + b * c'")

        self.assertEqual(f.subs({a: 0, b: 0}), 0)
        self.assertEqual(f.subs({a: 0, b: 1}), c)
        self.assertEqual(f.subs({a: 1, b: 0}), c)
        self.assertEqual(f.subs({a: 1, b: 1}), -c)

        # factor
        self.assertEqual(factor(a + 0), a)
        self.assertEqual(factor(a + 1), 1)
        self.assertEqual(str(factor(a + -(b * c))), "a + b' + c'")

        # simplify
        self.assertEqual(simplify(a + 1), 1)
        self.assertEqual(simplify(a + b + 1), 1)
        self.assertEqual(simplify(a + 0), a)
        self.assertEqual(simplify(-a + a), 1)
        self.assertEqual(simplify(-a + a + b), 1)

        self.assertEqual(simplify(a + a), a)
        self.assertEqual(simplify(a + a + a), a)
        self.assertEqual(simplify(a + a + a + a), a)
        self.assertEqual(simplify((a + a) + (a + a)), a)

        # to_csop
        f = a * b + a * c + b * c
        self.assertEqual(str(f.to_csop()), "a' * b * c + a * b' * c + a * b * c' + a * b * c")

    def test_and(self):
        a, b, c, d = map(Variable, "abcd")

        self.assertEqual(And(), One)
        self.assertEqual(And(a), a)

        # __len__
        self.assertEqual(len(a * b * c), 3)

        # __str__
        self.assertEqual(str(a * b), "a * b")
        self.assertEqual(str(a * b * c), "a * b * c")
        self.assertEqual(str(a * b * c * d), "a * b * c * d")

        # __lt__
        self.assertLess(Zero, a * b)
        self.assertLess(One, a * b)

        self.assertLess(-a, a * b)
        self.assertLess(a, a * b)
        self.assertLess(-b, a * b)
        self.assertLess(b, a * b)

        self.assertLess(-a * -b, -a * b) # 00 < 01
        self.assertLess(-a * -b, a * -b) # 00 < 10
        self.assertLess(-a * -b, a * b)  # 00 < 11
        self.assertLess(-a * b, a * -b)  # 01 < 10
        self.assertLess(-a * b, a * b)   # 01 < 11
        self.assertLess(a * -b, a * b)   # 10 < 11

        self.assertLess(a * b, a * b * c)

        # associative
        self.assertEqual(str((a * b) * c * d),   "a * b * c * d")
        self.assertEqual(str(a * (b * c) * d),   "a * b * c * d")
        self.assertEqual(str(a * b * (c * d)),   "a * b * c * d")
        self.assertEqual(str((a * b) * (c * d)), "a * b * c * d")
        self.assertEqual(str((a * b * c) * d),   "a * b * c * d")
        self.assertEqual(str(a * (b * c * d)),   "a * b * c * d")
        self.assertEqual(str(a * (b * (c * d))), "a * b * c * d")
        self.assertEqual(str(((a * b) * c) * d), "a * b * c * d")

        # depth
        self.assertEqual((a * b).depth, 1)
        self.assertEqual((a * (b + c)).depth, 2)
        self.assertEqual((a * (b + (c * d))).depth, 3)

        # get_dual
        self.assertEqual(And.get_dual(), Or)

        # support
        self.assertEqual((-a * b * (-c + d)).support, {a, b, c, d})

        # subs
        f = (-a + b + c) * (a + -b + c) * (a + b + -c)
        fa0, fa1 = f.subs({a: 0}), f.subs({a: 1})
        self.assertEqual(str(fa0), "(b + c') * (b' + c)")
        self.assertEqual(str(fa1), "b + c")

        self.assertEqual(f.subs({a: 0, b: 0}), -c)
        self.assertEqual(f.subs({a: 0, b: 1}), c)
        self.assertEqual(f.subs({a: 1, b: 0}), c)
        self.assertEqual(f.subs({a: 1, b: 1}), 1)

        # factor
        self.assertEqual(factor(a * 0), 0)
        self.assertEqual(factor(a * 1), a)
        self.assertEqual(str(factor(a * -(b + c))), "a * b' * c'")

        # simplify
        self.assertEqual(simplify(a * 0), 0)
        self.assertEqual(simplify(a * b * 0), 0)
        self.assertEqual(simplify(a * 1), a)
        self.assertEqual(simplify(-a * a), 0)
        self.assertEqual(simplify(-a * a * b), 0)

        self.assertEqual(simplify(a * a), a)
        self.assertEqual(simplify(a * a * a), a)
        self.assertEqual(simplify(a * a * a * a), a)
        self.assertEqual(simplify((a * a) + (a * a)), a)

        # to_cpos
        f = a * b + a * c + b * c
        self.assertEqual(str(f.to_cpos()), "(a + b + c) * (a + b + c') * (a + b' + c) * (a' + b + c)")

    def test_implies(self):
        a, b, c, d = map(Variable, "abcd")
        self.assertEqual(str(a >> b), "a => b")
        self.assertEqual(str(-a >> b), "a' => b")
        self.assertEqual(str(a >> -b), "a => b'")
        self.assertEqual(str(-a + b >> a + -b), "a' + b => a + b'")
        self.assertEqual(str((-a >> b) >> (a >> -b)), "(a' => b) => (a => b')")
        self.assertEqual(simplify(a >> a), 1)
        self.assertEqual(simplify(a >> 0), -a)
        self.assertEqual(simplify(a >> 1), 1)
        self.assertEqual(simplify(Zero >> a), 1)
        self.assertEqual(simplify(One >> a), a)
        self.assertEqual(str(impliesf(a, b)), "a' + b")
        self.assertEqual(str(factor(a >> b)), "a' + b")

    def test_nops(self):
        a, b, c, d = map(Variable, "abcd")
        self.assertEqual(str(norf(a, b)), "a' * b'")
        self.assertEqual(str(norf(a, b, c, d)), "a' * b' * c' * d'")
        self.assertEqual(str(nandf(a, b)), "a' + b'")
        self.assertEqual(str(nandf(a, b, c, d)), "a' + b' + c' + d'")

    def test_xor(self):
        a, b, c  = map(Variable, "abc")
        self.assertEqual(str(Xor(a, b).to_sop()),  "a' * b + a * b'")
        self.assertEqual(str(Xnor(a, b).to_sop()), "a' * b' + a * b")
        self.assertEqual(str(Xor(a, b, c).to_sop()),  "a' * b' * c + a' * b * c' + a * b' * c' + a * b * c")
        self.assertEqual(str(Xnor(a, b, c).to_sop()), "a' * b' * c' + a' * b * c + a * b' * c + a * b * c'")

    def test_demorgan(self):
        a, b, c = map(Variable, "abc")

        self.assertEqual(str(notf(a * b)),  "a' + b'")
        self.assertEqual(str(notf(a + b)),  "a' * b'")
        self.assertEqual(str(notf(a * -b)), "a' + b")
        self.assertEqual(str(notf(a * -b)), "a' + b")
        self.assertEqual(str(notf(-a * b)), "a + b'")
        self.assertEqual(str(notf(-a * b)), "a + b'")

        self.assertEqual(str(notf(a * b * c)),  "a' + b' + c'")
        self.assertEqual(str(notf(a + b + c)),  "a' * b' * c'")
        self.assertEqual(str(notf(-a * b * c)), "a + b' + c'")
        self.assertEqual(str(notf(-a + b + c)), "a * b' * c'")
        self.assertEqual(str(notf(a * -b * c)), "a' + b + c'")
        self.assertEqual(str(notf(a + -b + c)), "a' * b * c'")
        self.assertEqual(str(notf(a * b * -c)), "a' + b' + c")
        self.assertEqual(str(notf(a + b + -c)), "a' * b' * c")

    def test_absorb(self):
        a, b, c, d = map(Variable, "abcd")
        self.assertEqual(str(simplify(a * b + a * b)), "a * b")
        self.assertEqual(simplify(a * (a + b)), a)
        self.assertEqual(simplify(-a * (-a + b)), -a)
        self.assertEqual(str(simplify(a * b * (a + c))), "a * b")
        self.assertEqual(str(simplify(a * b * (a + c) * (a + d))), "a * b")
        self.assertEqual(str(simplify(-a * b * (-a + c))), "a' * b")
        self.assertEqual(str(simplify(-a * b * (-a + c) * (-a + d))), "a' * b")
        self.assertEqual(str(simplify(a * -b + a * -b * c)), "a * b'")
        self.assertEqual(str(simplify((a + -b) * (a + -b + c))), "a + b'")

    def test_cofactors(self):
        a, b, c, d = map(Variable, "abcd")
        f = a * b + a * c + b * c
        self.assertEqual(str(f.cofactors()), "[a * b + a * c + b * c]")
        self.assertEqual(str(f.cofactors(a)), "[b * c, b + c + b * c]")
        self.assertEqual(f.cofactors(a, b), [0, c, c, 1])
        self.assertEqual(f.cofactors(a, b, c), [0, 0, 0, 1, 0, 1, 1, 1])
        self.assertEqual(str(f.smoothing(a)), "b + c + b * c + b * c")
        self.assertEqual(str(f.consensus(a)), "b * c * (b + c + b * c)")
        self.assertEqual(str(f.derivative(a).to_sop()), "b' * c + b * c'")

    def test_unate(self):
        a, b, c, d = map(Variable, "abcd")
        f = a + b + -c
        self.assertTrue(f.is_pos_unate(a))
        self.assertTrue(f.is_pos_unate(b))
        self.assertTrue(f.is_neg_unate(c))
        self.assertFalse(f.is_neg_unate(a))
        self.assertFalse(f.is_neg_unate(b))
        self.assertTrue(f.is_neg_unate(c))
        self.assertFalse(f.is_binate(a))
        self.assertFalse(f.is_binate(b))
        self.assertFalse(f.is_binate(c))
        self.assertTrue(f.is_binate())
        g = a * b + a * -c + b * -c
        self.assertTrue(f.is_pos_unate(a))
        self.assertTrue(f.is_pos_unate(b))
        self.assertTrue(f.is_neg_unate(c))

    def test_cube(self):
        a, b, c = map(Variable, "abc")
        self.assertEqual(str(cube_sop(a, b, c)), "a' * b' * c' + a' * b' * c + a' * b * c' + a' * b * c + a * b' * c' + a * b' * c + a * b * c' + a * b * c")
        self.assertEqual(str(cube_pos(a, b, c)), "(a + b + c) * (a + b + c') * (a + b' + c) * (a + b' + c') * (a' + b + c) * (a' + b + c') * (a' + b' + c) * (a' + b' + c')")


class TestBoolvec(unittest.TestCase):

    def setUp(self):
        super(TestBoolvec, self).setUp()
        self.LOOPS = 32

    def tearDown(self):
        super(TestBoolvec, self).tearDown()

    def test_rcadd(self):
        A, B = vec("A", 8), vec("B", 8)
        S, C = A.ripple_carry_add(B)
        S.append(C[-1])
        for i in range(self.LOOPS):
            ra = random.randint(0, 2**8-1)
            rb = random.randint(0, 2**8-1)
            d = {A: uint2vec(ra, 8), B: uint2vec(rb, 8)}
            self.assertEqual(int(A.vsubs(d)), ra)
            self.assertEqual(int(B.vsubs(d)), rb)
            self.assertEqual(int(S.vsubs(d)), ra + rb)

        A, B = svec("A", 8), svec("B", 8)
        S, C = A.ripple_carry_add(B)
        for i in range(self.LOOPS):
            ra = random.randint(-2**6, 2**6-1)
            rb = random.randint(-2**6, 2**6-1)
            d = {A: int2vec(ra, 8), B: int2vec(rb, 8)}
            self.assertEqual(int(A.vsubs(d)), ra)
            self.assertEqual(int(B.vsubs(d)), rb)
            self.assertEqual(int(S.vsubs(d)), ra + rb)


if __name__ == "__main__":
    #import profile, pstats
    #profile.run("unittest.main()", "testprof")
    #p = pstats.Stats("testprof")
    #p.sort_stats('cumulative').print_stats(50)
    unittest.main()
