/*
** Filename: test_simple.cpp
**
** Test simplification.
*/


#include "boolexprtest.hpp"


class BoolExprSimpleTest: public BoolExprTest {};


// Test simplification on atoms
TEST_F(BoolExprSimpleTest, Atoms)
{
    ops[0] = BoolExpr_Simplify(&Zero);
    EXPECT_EQ(ops[0], &Zero);

    ops[1] = BoolExpr_Simplify(&One);
    EXPECT_EQ(ops[1], &One);

    ops[2] = BoolExpr_Simplify(xns[0]);
    EXPECT_EQ(ops[2], xns[0]);

    ops[3] = BoolExpr_Simplify(xs[0]);
    EXPECT_EQ(ops[3], xs[0]);
}


// Test all constant inputs to operators
TEST_F(BoolExprSimpleTest, Constants)
{
    // 0 | 0 <=> 0
    ops[0] = OrN(2, &Zero, &Zero);
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &Zero);

    // 1 | 0 <=> 1
    ops[2] = OrN(2, &One,  &Zero);
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &One);

    // 0 | 1 <=> 1
    ops[4] = OrN(2, &Zero, &One);
    ops[5] = BoolExpr_Simplify(ops[4]);
    EXPECT_EQ(ops[5], &One);

    // 1 | 1 <=> 1
    ops[6] = OrN(2, &One,  &One);
    ops[7] = BoolExpr_Simplify(ops[6]);
    EXPECT_EQ(ops[7], &One);

    // 0 & 0 <=> 0
    ops[8] = AndN(2, &Zero, &Zero);
    ops[9] = BoolExpr_Simplify(ops[8]);
    EXPECT_EQ(ops[9], &Zero);

    // 1 & 0 <=> 0
    ops[10] = AndN(2, &One,  &Zero);
    ops[11] = BoolExpr_Simplify(ops[10]);
    EXPECT_EQ(ops[11], &Zero);

    // 0 & 1 <=> 0
    ops[12] = AndN(2, &Zero, &One);
    ops[13] = BoolExpr_Simplify(ops[12]);
    EXPECT_EQ(ops[13], &Zero);

    // 1 & 1 <=> 1
    ops[14] = AndN(2, &One,  &One);
    ops[15] = BoolExpr_Simplify(ops[14]);
    EXPECT_EQ(ops[15], &One);

    // 0 ^ 0 <=> 0
    ops[16] = XorN(2, &Zero, &Zero);
    ops[17] = BoolExpr_Simplify(ops[16]);
    EXPECT_EQ(ops[17], &Zero);

    // 1 ^ 0 <=> 1
    ops[18] = XorN(2, &One,  &Zero);
    ops[19] = BoolExpr_Simplify(ops[18]);
    EXPECT_EQ(ops[19], &One);

    // 0 ^ 1 <=> 1
    ops[20] = XorN(2, &Zero, &One);
    ops[21] = BoolExpr_Simplify(ops[20]);
    EXPECT_EQ(ops[21], &One);

    // 1 ^ 1 <=> 0
    ops[22] = XorN(2, &One,  &One);
    ops[23] = BoolExpr_Simplify(ops[22]);
    EXPECT_EQ(ops[23], &Zero);

    // 0 = 0 <=> 1
    ops[24] = EqualN(2, &Zero, &Zero);
    ops[25] = BoolExpr_Simplify(ops[24]);
    EXPECT_EQ(ops[25], &One);

    // 1 = 0 <=> 0
    ops[26] = EqualN(2, &One,  &Zero);
    ops[27] = BoolExpr_Simplify(ops[26]);
    EXPECT_EQ(ops[27], &Zero);

    // 0 = 1 <=> 0
    ops[28] = EqualN(2, &Zero, &One);
    ops[29] = BoolExpr_Simplify(ops[28]);
    EXPECT_EQ(ops[29], &Zero);

    // 1 = 1 <=> 1
    ops[30] = EqualN(2, &One,  &One);
    ops[31] = BoolExpr_Simplify(ops[30]);
    EXPECT_EQ(ops[31], &One);

    // 0 => 0 <=> 1
    ops[32] = Implies(&Zero, &Zero);
    ops[33] = BoolExpr_Simplify(ops[32]);
    EXPECT_EQ(ops[33], &One);

    // 1 => 0 <=> 0
    ops[34] = Implies(&One, &Zero);
    ops[35] = BoolExpr_Simplify(ops[34]);
    EXPECT_EQ(ops[35], &Zero);

    // 0 => 1 <=> 1
    ops[36] = Implies(&Zero, &One);
    ops[37] = BoolExpr_Simplify(ops[36]);
    EXPECT_EQ(ops[37], &One);

    // 1 => 1 <=> 1
    ops[38] = Implies(&One, &One);
    ops[39] = BoolExpr_Simplify(ops[38]);
    EXPECT_EQ(ops[39], &One);

    // 0 ? 0 : 0 <=> 0
    ops[40] = ITE(&Zero, &Zero, &Zero);
    ops[41] = BoolExpr_Simplify(ops[40]);
    EXPECT_EQ(ops[41], &Zero);

    // 1 ? 0 : 0 <=> 0
    ops[42] = ITE(&One, &Zero, &Zero);
    ops[43] = BoolExpr_Simplify(ops[42]);
    EXPECT_EQ(ops[43], &Zero);

    // 0 ? 1 : 0 <=> 0
    ops[44] = ITE(&Zero, &One, &Zero);
    ops[45] = BoolExpr_Simplify(ops[44]);
    EXPECT_EQ(ops[45], &Zero);

    // 1 ? 1 : 0 <=> 1
    ops[46] = ITE(&One, &One, &Zero);
    ops[47] = BoolExpr_Simplify(ops[46]);
    EXPECT_EQ(ops[47], &One);

    // 0 ? 0 : 1 <=> 1
    ops[48] = ITE(&Zero, &Zero, &One);
    ops[49] = BoolExpr_Simplify(ops[48]);
    EXPECT_EQ(ops[49], &One);

    // 1 ? 0 : 1 <=> 0
    ops[50] = ITE(&One, &Zero, &One);
    ops[51] = BoolExpr_Simplify(ops[50]);
    EXPECT_EQ(ops[51], &Zero);

    // 0 ? 1 : 1 <=> 1
    ops[52] = ITE(&Zero, &One, &One);
    ops[53] = BoolExpr_Simplify(ops[52]);
    EXPECT_EQ(ops[53], &One);

    // 1 ? 1 : 1 <=> 1
    ops[54] = ITE(&One, &One, &One);
    ops[55] = BoolExpr_Simplify(ops[54]);
    EXPECT_EQ(ops[55], &One);
}


TEST_F(BoolExprSimpleTest, Identity)
{
    // x | 0 <=> x
    ops[0] = OrN(2, xs[0], &Zero);
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_EQ(ops[1], xs[0]);

    // 0 | x <=> x0
    ops[2] = OrN(2, &Zero, xs[0]);
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_EQ(ops[3], xs[0]);

    // x & 1 <=> x
    ops[4] = AndN(2, xs[0], &One);
    ops[5] = BoolExpr_Simplify(ops[4]);
    EXPECT_EQ(ops[5], xs[0]);

    // 1 & x <=> x
    ops[6] = AndN(2, &One, xs[0]);
    ops[7] = BoolExpr_Simplify(ops[6]);
    EXPECT_EQ(ops[7], xs[0]);

    // x ^ 0 <=> x
    ops[8] = XorN(2, xs[0], &Zero);
    ops[9] = BoolExpr_Simplify(ops[8]);
    EXPECT_EQ(ops[9], xs[0]);

    // 0 ^ x <=> x
    ops[10] = XorN(2, &Zero, xs[0]);
    ops[11] = BoolExpr_Simplify(ops[10]);
    EXPECT_EQ(ops[11], xs[0]);

    // x = 1 <=> x
    ops[12] = EqualN(2, xs[0], &One);
    ops[13] = BoolExpr_Simplify(ops[12]);
    EXPECT_EQ(ops[13], xs[0]);

    // 1 = x <=> x
    ops[14] = EqualN(2, &One, xs[0]);
    ops[15] = BoolExpr_Simplify(ops[14]);
    EXPECT_EQ(ops[15], xs[0]);
}


TEST_F(BoolExprSimpleTest, Domination)
{
    // x | 1 <=> 1
    ops[0] = OrN(2, xs[0], &One);
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &One);

    // 1 | x <=> 1
    ops[2] = OrN(2, &One, xs[0]);
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &One);

    // x & 0 <=> 0
    ops[4] = AndN(2, xs[0], &Zero);
    ops[5] = BoolExpr_Simplify(ops[4]);
    EXPECT_EQ(ops[5], &Zero);

    // 0 & x <=> 0
    ops[6] = AndN(2, &Zero, xs[0]);
    ops[7] = BoolExpr_Simplify(ops[6]);
    EXPECT_EQ(ops[7], &Zero);
}


TEST_F(BoolExprSimpleTest, Idempotent)
{
    // ~x3 | x2 | ~x1 | x2 | ~x1 | x0 <=> x0 | ~x1 | x2 | ~x3
    ops[0] = OrN(6, xns[3], xs[2], xns[1], xs[2], xns[1], xs[0]);
    ops[1] = BoolExpr_Simplify(ops[0]);
    exps[0] = OrN(4, xs[0], xns[1], xs[2], xns[3]);
    EXPECT_TRUE(Similar(ops[1], exps[0]));

    // ~x3 & x2 & ~x1 & x2 & ~x1 & x0 <=> x0 & ~x1 & x2 & ~x3
    ops[2] = AndN(6, xns[3], xs[2], xns[1], xs[2], xns[1], xs[0]);
    ops[3] = BoolExpr_Simplify(ops[2]);
    exps[1] = AndN(4, xs[0], xns[1], xs[2], xns[3]);
    EXPECT_TRUE(Similar(ops[3], exps[1]));
}


TEST_F(BoolExprSimpleTest, Inverse)
{
    // ~x | x <=> 1
    ops[0] = OrN(2, xns[0], xs[0]);
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &One);

    // x | ~x <=> 1
    ops[2] = OrN(2, xs[0], xns[0]);
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &One);

    // ~x & x <=> 0
    ops[4] = AndN(2, xns[0], xs[0]);
    ops[5] = BoolExpr_Simplify(ops[4]);
    EXPECT_EQ(ops[5], &Zero);

    // x & ~x <=> 0
    ops[6] = AndN(2, xs[0], xns[0]);
    ops[7] = BoolExpr_Simplify(ops[6]);
    EXPECT_EQ(ops[7], &Zero);
}


TEST_F(BoolExprSimpleTest, Associative)
{
    // (x0 | x1) | (x2 | x3) <=> x0 | x1 | x2 | x3
    ops[0] = OrN(2, xs[0], xs[1]);
    ops[1] = OrN(2, xs[2], xs[3]);
    ops[2] = OrN(2, ops[0], ops[1]);
    ops[3] = BoolExpr_Simplify(ops[2]);
    exps[0] = OrN(4, xs[0], xs[1], xs[2], xs[3]);
    EXPECT_TRUE(Similar(ops[3], exps[0]));

    // (x0 & x1) & (x2 & x3) <=> x0 & x1 & x2 & x3
    ops[4] = AndN(2, xs[0], xs[1]);
    ops[5] = AndN(2, xs[2], xs[3]);
    ops[6] = AndN(2, ops[4], ops[5]);
    ops[7] = BoolExpr_Simplify(ops[6]);
    exps[1] = AndN(4, xs[0], xs[1], xs[2], xs[3]);
    EXPECT_TRUE(Similar(ops[7], exps[1]));

    // (x0 ^ x1) ^ (x2 ^ x3) <=> x0 ^ x1 ^ x2 ^ x3
    ops[8] = XorN(2, xs[0], xs[1]);
    ops[9] = XorN(2, xs[2], xs[3]);
    ops[10] = XorN(2, ops[8], ops[9]);
    ops[11] = BoolExpr_Simplify(ops[10]);
    exps[2] = XorN(4, xs[0], xs[1], xs[2], xs[3]);
    EXPECT_TRUE(Similar(ops[11], exps[2]));
}


TEST_F(BoolExprSimpleTest, XorCases)
{
    // ~x ^ x <=> 1
    ops[0] = XorN(2, xns[0], xs[0]);
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &One);

    // x ^ ~x <=> 1
    ops[2] = XorN(2, xs[0], xns[0]);
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &One);

    // x ^ x <=> 0
    ops[4] = XorN(2, xs[0], xs[0]);
    ops[5] = BoolExpr_Simplify(ops[4]);
    EXPECT_EQ(ops[5], &Zero);
}


TEST_F(BoolExprSimpleTest, EqualCases)
{
    // ~x = x <=> 0
    ops[0] = EqualN(2, xns[0], xs[0]);
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &Zero);

    // x = ~x <=> 0
    ops[2] = EqualN(2, xs[0], xns[0]);
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &Zero);

    // 0 = x <=> ~x
    ops[4] = EqualN(2, &Zero, xs[0]);
    ops[5] = BoolExpr_Simplify(ops[4]);
    EXPECT_EQ(ops[5], xns[0]);

    // eq(0, x0, x1) <=> Nor(x0, x1)
    ops[6] = EqualN(3, &Zero, xs[0], xs[1]);
    ops[7] = BoolExpr_Simplify(ops[6]);
    exps[0] = NorN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[7], exps[0]));

    // eq(1, x0, x1) <=> And(x0, x1)
    ops[8] = EqualN(3, &One, xs[0], xs[1]);
    ops[9] = BoolExpr_Simplify(ops[8]);
    exps[1] = AndN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[9], exps[1]));

    // eq(x1, x0, x1, x0) <=> x0 = x1
    ops[12] = EqualN(4, xs[1], xs[0], xs[1], xs[0]);
    ops[13] = BoolExpr_Simplify(ops[12]);
    exps[2] = EqualN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[13], exps[2]));
}


TEST_F(BoolExprSimpleTest, NotCases)
{
    ops[0] = NorN(3, xs[0], &One, xs[1]);
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &Zero);

    ops[2] = NandN(3, xs[0], xs[1], xs[2]);
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_TRUE(Similar(ops[2], ops[3]));
}


TEST_F(BoolExprSimpleTest, ImpliesCases)
{
    ops[0] = Implies(&Zero, xs[0]);
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &One);

    ops[2] = Implies(&One, xs[0]);
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_EQ(ops[3], xs[0]);

    ops[4] = Implies(xs[0], &Zero);
    ops[5] = BoolExpr_Simplify(ops[4]);
    EXPECT_EQ(ops[5], xns[0]);

    ops[6] = Implies(xs[0], &One);
    ops[7] = BoolExpr_Simplify(ops[6]);
    EXPECT_EQ(ops[7], &One);

    ops[8] = Implies(xs[0], xs[0]);
    ops[9] = BoolExpr_Simplify(ops[8]);
    EXPECT_EQ(ops[7], &One);

    ops[10] = Implies(xns[0], xs[0]);
    ops[11] = BoolExpr_Simplify(ops[10]);
    EXPECT_EQ(ops[11], xs[0]);

    ops[12] = Implies(xs[1], xs[2]);
    ops[13] = BoolExpr_Simplify(ops[12]);
    EXPECT_TRUE(Similar(ops[12], ops[13]));
}


TEST_F(BoolExprSimpleTest, ITECases)
{
    // ITE(s, 0, 0) <=> 0
    ops[0] = ITE(xs[0], &Zero, &Zero);
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &Zero);

    // ITE(s, 0, 1) <=> ~s
    ops[2] = ITE(xs[0], &Zero, &One);
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_EQ(ops[3], xns[0]);

    // ITE(s, 0, d0) <=> ~s & d0
    ops[4] = ITE(xs[0], &Zero, xs[1]);
    ops[5] = BoolExpr_Simplify(ops[4]);
    exps[0] = AndN(2, xns[0], xs[1]);
    EXPECT_TRUE(Similar(ops[5], exps[0]));

    // ITE(s, 1, 0) <=> s
    ops[6] = ITE(xs[0], &One, &Zero);
    ops[7] = BoolExpr_Simplify(ops[6]);
    EXPECT_EQ(ops[7], xs[0]);

    // ITE(s, 1, 1) <=> 1
    ops[8] = ITE(xs[0], &One, &One);
    ops[9] = BoolExpr_Simplify(ops[8]);
    EXPECT_EQ(ops[9], &One);

    // ITE(s, 1, d0) <=> s | d0
    ops[10] = ITE(xs[0], &One, xs[1]);
    ops[11] = BoolExpr_Simplify(ops[10]);
    exps[1] = OrN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[11], exps[1]));

    // ITE(s, d1, 0) <=> s & d1
    ops[12] = ITE(xs[0], xs[1], &Zero);
    ops[13] = BoolExpr_Simplify(ops[12]);
    exps[2] = AndN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[13], exps[2]));

    // ITE(s, d1, 1) <=> ~s | d1
    ops[14] = ITE(xs[0], xs[1], &One);
    ops[15] = BoolExpr_Simplify(ops[14]);
    exps[3] = OrN(2, xns[0], xs[1]);
    EXPECT_TRUE(Similar(ops[15], exps[3]));

    // ITE(s, d1, d1) <=> d1
    ops[16] = ITE(xs[0], xs[1], xs[1]);
    ops[17] = BoolExpr_Simplify(ops[16]);
    EXPECT_EQ(ops[17], xs[1]);

    // ITE(s, s, d0) <=> s | d0
    ops[18] = ITE(xs[0], xs[0], xs[1]);
    ops[19] = BoolExpr_Simplify(ops[18]);
    exps[4] = OrN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[19], exps[4]));

    // ITE(s, d1, s) <=> s & d1
    ops[20] = ITE(xs[0], xs[1], xs[0]);
    ops[21] = BoolExpr_Simplify(ops[20]);
    exps[5] = AndN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[21], exps[5]));

    ops[22] = ITE(xs[0], xs[1], xs[2]);
    ops[23] = BoolExpr_Simplify(ops[22]);
    EXPECT_TRUE(Similar(ops[22], ops[23]));
}

