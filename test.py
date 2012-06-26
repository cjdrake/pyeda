"""
Test Module
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved"

# standard library
import random
import unittest

# pyeda
from pyeda.boolalg import (
    Zero, One,
    Variable, Complement,
    Not, NotF,
    Or, OrF, And, AndF,
    Nor, NorF, Nand, NandF,
    Xor, Xnor,
    Implies, ImpliesF,
    factor, simplify,
    vec, svec, int2vec, uint2vec
)

class TestBoolalg(unittest.TestCase):

    def setUp(self):
        super(TestBoolalg, self).setUp()

    def tearDown(self):
        super(TestBoolalg, self).tearDown()

    def test_variable(self):
        a, b = map(Variable, "ab")
        self.assertEqual(str(a), "a")
        self.assertEqual(a, a)
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)

    def test_complement(self):
        a, b = map(Variable, "ab")
        self.assertEqual(str(Not(a)), "a'")
        self.assertEqual(str(-a), "a'")
        self.assertEqual(Not(a), Not(a))
        self.assertEqual(-a, -a)
        self.assertEqual(id(-a), id(-a))
        self.assertNotEqual(-a, -b)
        self.assertNotEqual(-b, -a)
        self.assertNotEqual(a, -a)

        self.assertEqual(Not(Not(a)), a)
        self.assertEqual(-(-a), a)
        self.assertEqual(Not(Not(Not(a))), Not(a))
        self.assertEqual(-(-(-a)), -a)
        self.assertEqual(Not(Not(Not(Not(a)))), a)
        self.assertEqual(-(-(-(-a))), a)

    def test_not(self):
        self.assertEqual(Not(Zero), One)
        self.assertEqual(-Zero, One)
        self.assertEqual(Not(One), Zero)
        self.assertEqual(-One, Zero)

    def test_or(self):
        a, b, c, d = map(Variable, "abcd")

        self.assertEqual(a + b, a + b)
        self.assertEqual(a + b + c, a + b + c)
        self.assertEqual(a + b + c + d, a + b + c + d)

        self.assertEqual(str(a + b), "a + b")
        self.assertEqual(str(a + b + c), "a + b + c")
        self.assertEqual(str(a + b + c + d), "a + b + c + d")

        self.assertEqual(OrF(a, True), One)
        self.assertEqual(OrF(a, 1), One)
        self.assertEqual(OrF(a, "1"), One)

        self.assertEqual(factor(a + True), One)
        self.assertEqual(factor(a + 1), One)
        self.assertEqual(factor(a + "1"), One)

        self.assertEqual(OrF(a, False), a)
        self.assertEqual(OrF(a, 0), a)
        self.assertEqual(OrF(a, "0"), a)

        self.assertEqual(factor(a + False), a)
        self.assertEqual(factor(a + 0), a)
        self.assertEqual(factor(a + "0"), a)

        self.assertEqual(OrF(a, -a), One)
        self.assertEqual(factor(a + -a), One)

        self.assertEqual(Or(a, a), a)
        self.assertEqual(Or(a, a, a), a)
        self.assertEqual(Or(a, a, a, a), a)
        self.assertEqual(Or(Or(a, a), Or(a, a)), a)

        self.assertEqual(a + a, a)
        self.assertEqual(a + a + a, a)
        self.assertEqual(a + a + a + a, a)
        self.assertEqual((a + a) + (a + a), a)

        self.assertEqual((a + b) + c + d, a + b + c + d)
        self.assertEqual(a + (b + c) + d, a + b + c + d)
        self.assertEqual(a + b + (c + d), a + b + c + d)
        self.assertEqual((a + b) + (c + d), a + b + c + d)
        self.assertEqual((a + b + c) + d, a + b + c + d)
        self.assertEqual(a + (b + c + d), a + b + c + d)
        self.assertEqual(a + (b + (c + d)), a + b + c + d)
        self.assertEqual(((a + b) + c) + d, a + b + c + d)

    def test_and(self):
        a, b, c, d = map(Variable, "abcd")

        self.assertEqual(a * b, a * b)
        self.assertEqual(a * b * c, a * b * c)
        self.assertEqual(a * b * c * d, a * b * c * d)

        self.assertEqual(str(a * b), "a * b")
        self.assertEqual(str(a * b * c), "a * b * c")
        self.assertEqual(str(a * b * c * d), "a * b * c * d")

        self.assertEqual(AndF(a, False), Zero)
        self.assertEqual(AndF(a, 0), Zero)
        self.assertEqual(AndF(a, "0"), Zero)

        self.assertEqual(factor(a * False), Zero)
        self.assertEqual(factor(a * 0), Zero)
        self.assertEqual(factor(a * "0"), Zero)

        self.assertEqual(AndF(a, True), a)
        self.assertEqual(AndF(a, 1), a)
        self.assertEqual(AndF(a, "1"), a)

        self.assertEqual(factor(a * True), a)
        self.assertEqual(factor(a * 1), a)
        self.assertEqual(factor(a * "1"), a)

        self.assertEqual(AndF(a, -a), Zero)
        self.assertEqual(factor(a * -a), Zero)

        self.assertEqual(And(a, a), a)
        self.assertEqual(And(a, a, a), a)
        self.assertEqual(And(a, a, a, a), a)
        self.assertEqual(And(And(a, a), And(a, a)), a)

        self.assertEqual(a * a, a)
        self.assertEqual(a * a * a, a)
        self.assertEqual(a * a * a * a, a)
        self.assertEqual((a * a) * (a * a), a)

        self.assertEqual((a * b) * c * d, a * b * c * d)
        self.assertEqual(a * (b * c) * d, a * b * c * d)
        self.assertEqual(a * b * (c * d), a * b * c * d)
        self.assertEqual((a * b) * (c * d), a * b * c * d)
        self.assertEqual((a * b * c) * d, a * b * c * d)
        self.assertEqual(a * (b * c * d), a * b * c * d)
        self.assertEqual(a * (b * (c * d)), a * b * c * d)
        self.assertEqual(((a * b) * c) * d, a * b * c * d)

    def test_cmp(self):
        a, b = map(Variable, "ab")
        A = vec("a", 11)
        self.assertLess(-a, a)
        self.assertLess(a, b)
        self.assertLess(-a, -b)
        self.assertLess(a, a + b)
        self.assertLess(a, a * b)
        self.assertLess(-a * b, a * b)
        self.assertLess(-a * -b, -a * b)
        self.assertLess(a, A[0])
        self.assertLess(A[0], A[1])
        self.assertLess(A[1], A[10])
        self.assertLess(A[0], -A[1])
        self.assertLess(A[1], -A[10])
        self.assertLess(-A[0], -A[1])
        self.assertLess(-A[1], -A[10])
        self.assertLess(-A[0], A[0])
        self.assertLess(-A[0], A[1])
        self.assertLess(-A[1], A[10])

    def test_implies(self):
        a, b, c, d = map(Variable, "abcd")
        self.assertEqual(str(a >> b), "a => b")
        self.assertEqual(str(-a >> b), "a' => b")
        self.assertEqual(str(a >> -b), "a => b'")
        self.assertEqual(str(-a + b >> a + -b), "a' + b => a + b'")
        self.assertEqual(str((-a >> b) >> (a >> -b)), "(a' => b) => (a => b')")
        self.assertEqual(simplify(a >> 0), -a)
        self.assertEqual(simplify(a >> 1), 1)
        self.assertEqual(simplify(Zero >> a), 1)
        self.assertEqual(simplify(One >> a), a)
        self.assertEqual(ImpliesF(a, b), -a + b)
        self.assertEqual(factor(a >> b), -a + b)

    def test_nops(self):
        a, b, c, d = map(Variable, "abcd")
        self.assertEqual(NorF(a, b), -a * -b)
        self.assertEqual(NorF(a, b, c, d), -a * -b * -c * -d)
        self.assertEqual(NandF(a, b), -a + -b)
        self.assertEqual(NandF(a, b, c, d), -a + -b + -c + -d)

    def test_xor(self):
        a, b, c  = map(Variable, "abc")
        self.assertEqual(Xor(a, b).to_sop(), a * -b + -a * b)
        self.assertEqual(Xnor(a, b).to_sop(), -a * -b + a * b)
        self.assertEqual(Xor(a, b, c).to_sop(),  -a * -b * c + -a * b * -c + a * -b * -c + a * b * c)
        self.assertEqual(Xnor(a, b, c).to_sop(),  -a * -b * -c + -a * b * c + a * -b * c + a * b * -c)

    def test_factor(self):
        a, b, c, d = map(Variable, "abcd")
        self.assertEqual(factor(a * -(b + c)), a * -b * -c)
        self.assertEqual(factor(a + -(b * c)), a + -b + -c)

    def test_demorgan(self):
        a, b, c = map(Variable, "abc")

        self.assertEqual(NotF(a * b), -a + -b)
        self.assertEqual(NotF(a + b), -a * -b)
        self.assertEqual(factor(-(a * b)), -a + -b)
        self.assertEqual(factor(-(a + b)), -a * -b)

        self.assertEqual(NotF(a * -b), -a + b)
        self.assertEqual(NotF(a * -b), -a + b)
        self.assertEqual(factor(-(a + -b)), -a * b)
        self.assertEqual(factor(-(a + -b)), -a * b)

        self.assertEqual(NotF(-a * b), a + -b)
        self.assertEqual(NotF(-a * b), a + -b)
        self.assertEqual(factor(-(-a + b)), a * -b)
        self.assertEqual(factor(-(-a + b)), a * -b)

        self.assertEqual(NotF(a * b * c), -a + -b + -c)
        self.assertEqual(NotF(a + b + c), -a * -b * -c)
        self.assertEqual(factor(-(a * b * c)), -a + -b + -c)
        self.assertEqual(factor(-(a + b + c)), -a * -b * -c)

        self.assertEqual(NotF(-a * b * c), a + -b + -c)
        self.assertEqual(NotF(-a + b + c), a * -b * -c)
        self.assertEqual(factor(-(-a * b * c)), a + -b + -c)
        self.assertEqual(factor(-(-a + b + c)), a * -b * -c)

        self.assertEqual(NotF(a * -b * c), -a + b + -c)
        self.assertEqual(NotF(a + -b + c), -a * b * -c)
        self.assertEqual(factor(-(a * -b * c)), -a + b + -c)
        self.assertEqual(factor(-(a + -b + c)), -a * b * -c)

        self.assertEqual(NotF(a * b * -c), -a + -b + c)
        self.assertEqual(NotF(a + b + -c), -a * -b * c)
        self.assertEqual(factor(-(a * b * -c)), -a + -b + c)
        self.assertEqual(factor(-(a + b + -c)), -a * -b * c)

    def test_absorb(self):
        a, b, c, d = map(Variable, "abcd")
        self.assertEqual(simplify(a * (a + b)), a)
        self.assertEqual(simplify(a * b * (a + c)), a * b)
        self.assertEqual(simplify(a * b * (a + c) * (a + d)), a * b)
        self.assertEqual(simplify(-a * (-a + b)), -a)
        self.assertEqual(simplify(-a * b * (-a + c)), -a * b)
        self.assertEqual(simplify(-a * b * (-a + c) * (-a + d)), -a * b)
        self.assertEqual(simplify(a * -b + a * -b * c), a * -b)
        self.assertEqual(simplify((a + -b) * (a + -b + c)), a + -b)

    def test_subs(self):
        a, b, c = map(Variable, "abc")
        f = -a * b * c + a * -b * c + a * b * -c
        self.assertEqual(f.subs({a: False}), b * c)
        self.assertEqual(f.subs({a: 0}), b * c)
        self.assertEqual(f.subs({a: "0"}), b * c)

        self.assertEqual(f.subs({a: True}), -b * c + b * -c)
        self.assertEqual(f.subs({a: 1}), -b * c + b * -c)
        self.assertEqual(f.subs({a: "1"}), -b * c + b * -c)

        self.assertEqual(f.subs({a: 0, b: 0}), 0)
        self.assertEqual(f.subs({a: 0, b: 1}), c)
        self.assertEqual(f.subs({a: 1, b: 0}), c)
        self.assertEqual(f.subs({a: 1, b: 1}), -c)

        g = (a + b) * (a + c) * (b + c)
        self.assertEqual(g.subs({a: False}), b * c)
        self.assertEqual(g.subs({a: 0}), b * c)
        self.assertEqual(g.subs({a: "0"}), b * c)

        self.assertEqual(g.subs({a: True}), b + c)
        self.assertEqual(g.subs({a: 1}), b + c)
        self.assertEqual(g.subs({a: "1"}), b + c)

        self.assertEqual(g.subs({a: 0, b: 0}), 0)
        self.assertEqual(g.subs({a: 0, b: 1}), c)
        self.assertEqual(g.subs({a: 1, b: 0}), c)
        self.assertEqual(g.subs({a: 1, b: 1}), 1)

    def test_sop(self):
        a, b, c, d = map(Variable, "abcd")
        self.assertEqual(Xor(a, b, c).to_sop(), -a * -b * c + -a * b * -c + a * -b * -c + a * b * c)
        self.assertEqual(Xor(a, b, c, d).to_sop(), -a * -b * -c * d + -a * -b * c * -d + -a * b * -c * -d + -a * b * c * d + a * -b * -c * -d + a * -b * c * d + a * b * -c * d + a * b * c * -d)

    def test_pos(self):
        a, b, c, d = map(Variable, "abcd")
        self.assertEqual(Xor(a, b, c).to_pos(),
                         (-a + -b + c) * (-a + b + -c) * (a + -b + -c) * (a + b + c))
        self.assertEqual(Xor(a, b, c, d).to_pos(),
                         (-a + -b + -c + -d) * (-a + -b + c + d) * (-a + b + -c + d) * (-a + b + c + -d) * (a + -b + -c + d) * (a + -b + c + -d) * (a + b + -c + -d) * (a + b + c + d))

    def test_cofactors(self):
        a, b, c, d = map(Variable, "abcd")
        f = a * b + a * c + b * c
        self.assertEqual(f.cofactors(), [a * b + a * c + b * c])
        self.assertEqual(f.cofactors(a), [b * c, b + c])
        self.assertEqual(f.cofactors(a, b), [0, c, c, 1])
        self.assertEqual(f.cofactors(a, b, c), [0, 0, 0, 1, 0, 1, 1, 1])
        self.assertEqual(f.derivative(a).to_sop(), -b * c + b * -c)
        self.assertEqual(f.consensus(a), b * c * (b + c))
        self.assertEqual(f.smoothing(a), b + c + (b * c))

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
