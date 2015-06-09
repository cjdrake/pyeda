/*
** Filename: test_simple.cpp
**
** Test simplification.
*/


#include "boolexprtest.hpp"


class BX_Simple_Test: public BoolExpr_Test {};


// Test simplification on atoms
TEST_F(BX_Simple_Test, Atoms)
{
    ops[0] = BX_Simplify(&BX_Zero);
    EXPECT_EQ(ops[0], &BX_Zero);

    ops[1] = BX_Simplify(&BX_One);
    EXPECT_EQ(ops[1], &BX_One);

    ops[2] = BX_Simplify(xns[0]);
    EXPECT_EQ(ops[2], xns[0]);

    ops[3] = BX_Simplify(xs[0]);
    EXPECT_EQ(ops[3], xs[0]);
}


// Test all constant inputs to operators
TEST_F(BX_Simple_Test, Constants)
{
    // 0 | 0 <=> 0
    ops[0] = BX_OrN(2, &BX_Zero, &BX_Zero);
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &BX_Zero);

    // 1 | 0 <=> 1
    ops[2] = BX_OrN(2, &BX_One,  &BX_Zero);
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &BX_One);

    // 0 | 1 <=> 1
    ops[4] = BX_OrN(2, &BX_Zero, &BX_One);
    ops[5] = BX_Simplify(ops[4]);
    EXPECT_EQ(ops[5], &BX_One);

    // 1 | 1 <=> 1
    ops[6] = BX_OrN(2, &BX_One,  &BX_One);
    ops[7] = BX_Simplify(ops[6]);
    EXPECT_EQ(ops[7], &BX_One);

    // 0 & 0 <=> 0
    ops[8] = BX_AndN(2, &BX_Zero, &BX_Zero);
    ops[9] = BX_Simplify(ops[8]);
    EXPECT_EQ(ops[9], &BX_Zero);

    // 1 & 0 <=> 0
    ops[10] = BX_AndN(2, &BX_One,  &BX_Zero);
    ops[11] = BX_Simplify(ops[10]);
    EXPECT_EQ(ops[11], &BX_Zero);

    // 0 & 1 <=> 0
    ops[12] = BX_AndN(2, &BX_Zero, &BX_One);
    ops[13] = BX_Simplify(ops[12]);
    EXPECT_EQ(ops[13], &BX_Zero);

    // 1 & 1 <=> 1
    ops[14] = BX_AndN(2, &BX_One,  &BX_One);
    ops[15] = BX_Simplify(ops[14]);
    EXPECT_EQ(ops[15], &BX_One);

    // 0 ^ 0 <=> 0
    ops[16] = BX_XorN(2, &BX_Zero, &BX_Zero);
    ops[17] = BX_Simplify(ops[16]);
    EXPECT_EQ(ops[17], &BX_Zero);

    // 1 ^ 0 <=> 1
    ops[18] = BX_XorN(2, &BX_One,  &BX_Zero);
    ops[19] = BX_Simplify(ops[18]);
    EXPECT_EQ(ops[19], &BX_One);

    // 0 ^ 1 <=> 1
    ops[20] = BX_XorN(2, &BX_Zero, &BX_One);
    ops[21] = BX_Simplify(ops[20]);
    EXPECT_EQ(ops[21], &BX_One);

    // 1 ^ 1 <=> 0
    ops[22] = BX_XorN(2, &BX_One,  &BX_One);
    ops[23] = BX_Simplify(ops[22]);
    EXPECT_EQ(ops[23], &BX_Zero);

    // 0 = 0 <=> 1
    ops[24] = BX_EqualN(2, &BX_Zero, &BX_Zero);
    ops[25] = BX_Simplify(ops[24]);
    EXPECT_EQ(ops[25], &BX_One);

    // 1 = 0 <=> 0
    ops[26] = BX_EqualN(2, &BX_One,  &BX_Zero);
    ops[27] = BX_Simplify(ops[26]);
    EXPECT_EQ(ops[27], &BX_Zero);

    // 0 = 1 <=> 0
    ops[28] = BX_EqualN(2, &BX_Zero, &BX_One);
    ops[29] = BX_Simplify(ops[28]);
    EXPECT_EQ(ops[29], &BX_Zero);

    // 1 = 1 <=> 1
    ops[30] = BX_EqualN(2, &BX_One,  &BX_One);
    ops[31] = BX_Simplify(ops[30]);
    EXPECT_EQ(ops[31], &BX_One);

    // 0 => 0 <=> 1
    ops[32] = BX_Implies(&BX_Zero, &BX_Zero);
    ops[33] = BX_Simplify(ops[32]);
    EXPECT_EQ(ops[33], &BX_One);

    // 1 => 0 <=> 0
    ops[34] = BX_Implies(&BX_One, &BX_Zero);
    ops[35] = BX_Simplify(ops[34]);
    EXPECT_EQ(ops[35], &BX_Zero);

    // 0 => 1 <=> 1
    ops[36] = BX_Implies(&BX_Zero, &BX_One);
    ops[37] = BX_Simplify(ops[36]);
    EXPECT_EQ(ops[37], &BX_One);

    // 1 => 1 <=> 1
    ops[38] = BX_Implies(&BX_One, &BX_One);
    ops[39] = BX_Simplify(ops[38]);
    EXPECT_EQ(ops[39], &BX_One);

    // 0 ? 0 : 0 <=> 0
    ops[40] = BX_ITE(&BX_Zero, &BX_Zero, &BX_Zero);
    ops[41] = BX_Simplify(ops[40]);
    EXPECT_EQ(ops[41], &BX_Zero);

    // 1 ? 0 : 0 <=> 0
    ops[42] = BX_ITE(&BX_One, &BX_Zero, &BX_Zero);
    ops[43] = BX_Simplify(ops[42]);
    EXPECT_EQ(ops[43], &BX_Zero);

    // 0 ? 1 : 0 <=> 0
    ops[44] = BX_ITE(&BX_Zero, &BX_One, &BX_Zero);
    ops[45] = BX_Simplify(ops[44]);
    EXPECT_EQ(ops[45], &BX_Zero);

    // 1 ? 1 : 0 <=> 1
    ops[46] = BX_ITE(&BX_One, &BX_One, &BX_Zero);
    ops[47] = BX_Simplify(ops[46]);
    EXPECT_EQ(ops[47], &BX_One);

    // 0 ? 0 : 1 <=> 1
    ops[48] = BX_ITE(&BX_Zero, &BX_Zero, &BX_One);
    ops[49] = BX_Simplify(ops[48]);
    EXPECT_EQ(ops[49], &BX_One);

    // 1 ? 0 : 1 <=> 0
    ops[50] = BX_ITE(&BX_One, &BX_Zero, &BX_One);
    ops[51] = BX_Simplify(ops[50]);
    EXPECT_EQ(ops[51], &BX_Zero);

    // 0 ? 1 : 1 <=> 1
    ops[52] = BX_ITE(&BX_Zero, &BX_One, &BX_One);
    ops[53] = BX_Simplify(ops[52]);
    EXPECT_EQ(ops[53], &BX_One);

    // 1 ? 1 : 1 <=> 1
    ops[54] = BX_ITE(&BX_One, &BX_One, &BX_One);
    ops[55] = BX_Simplify(ops[54]);
    EXPECT_EQ(ops[55], &BX_One);
}


TEST_F(BX_Simple_Test, Identity)
{
    // x | 0 <=> x
    ops[0] = BX_OrN(2, xs[0], &BX_Zero);
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_EQ(ops[1], xs[0]);

    // 0 | x <=> x0
    ops[2] = BX_OrN(2, &BX_Zero, xs[0]);
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_EQ(ops[3], xs[0]);

    // x & 1 <=> x
    ops[4] = BX_AndN(2, xs[0], &BX_One);
    ops[5] = BX_Simplify(ops[4]);
    EXPECT_EQ(ops[5], xs[0]);

    // 1 & x <=> x
    ops[6] = BX_AndN(2, &BX_One, xs[0]);
    ops[7] = BX_Simplify(ops[6]);
    EXPECT_EQ(ops[7], xs[0]);

    // x ^ 0 <=> x
    ops[8] = BX_XorN(2, xs[0], &BX_Zero);
    ops[9] = BX_Simplify(ops[8]);
    EXPECT_EQ(ops[9], xs[0]);

    // 0 ^ x <=> x
    ops[10] = BX_XorN(2, &BX_Zero, xs[0]);
    ops[11] = BX_Simplify(ops[10]);
    EXPECT_EQ(ops[11], xs[0]);

    // x = 1 <=> x
    ops[12] = BX_EqualN(2, xs[0], &BX_One);
    ops[13] = BX_Simplify(ops[12]);
    EXPECT_EQ(ops[13], xs[0]);

    // 1 = x <=> x
    ops[14] = BX_EqualN(2, &BX_One, xs[0]);
    ops[15] = BX_Simplify(ops[14]);
    EXPECT_EQ(ops[15], xs[0]);
}


TEST_F(BX_Simple_Test, Domination)
{
    // x | 1 <=> 1
    ops[0] = BX_OrN(2, xs[0], &BX_One);
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &BX_One);

    // 1 | x <=> 1
    ops[2] = BX_OrN(2, &BX_One, xs[0]);
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &BX_One);

    // x & 0 <=> 0
    ops[4] = BX_AndN(2, xs[0], &BX_Zero);
    ops[5] = BX_Simplify(ops[4]);
    EXPECT_EQ(ops[5], &BX_Zero);

    // 0 & x <=> 0
    ops[6] = BX_AndN(2, &BX_Zero, xs[0]);
    ops[7] = BX_Simplify(ops[6]);
    EXPECT_EQ(ops[7], &BX_Zero);
}


TEST_F(BX_Simple_Test, Idempotent)
{
    // ~x3 | x2 | ~x1 | x2 | ~x1 | x0 <=> x0 | ~x1 | x2 | ~x3
    ops[0] = BX_OrN(6, xns[3], xs[2], xns[1], xs[2], xns[1], xs[0]);
    ops[1] = BX_Simplify(ops[0]);
    exps[0] = BX_OrN(4, xs[0], xns[1], xs[2], xns[3]);
    EXPECT_TRUE(Similar(ops[1], exps[0]));

    // ~x3 & x2 & ~x1 & x2 & ~x1 & x0 <=> x0 & ~x1 & x2 & ~x3
    ops[2] = BX_AndN(6, xns[3], xs[2], xns[1], xs[2], xns[1], xs[0]);
    ops[3] = BX_Simplify(ops[2]);
    exps[1] = BX_AndN(4, xs[0], xns[1], xs[2], xns[3]);
    EXPECT_TRUE(Similar(ops[3], exps[1]));
}


TEST_F(BX_Simple_Test, Inverse)
{
    // ~x | x <=> 1
    ops[0] = BX_OrN(2, xns[0], xs[0]);
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &BX_One);

    // x | ~x <=> 1
    ops[2] = BX_OrN(2, xs[0], xns[0]);
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &BX_One);

    // ~x & x <=> 0
    ops[4] = BX_AndN(2, xns[0], xs[0]);
    ops[5] = BX_Simplify(ops[4]);
    EXPECT_EQ(ops[5], &BX_Zero);

    // x & ~x <=> 0
    ops[6] = BX_AndN(2, xs[0], xns[0]);
    ops[7] = BX_Simplify(ops[6]);
    EXPECT_EQ(ops[7], &BX_Zero);
}


TEST_F(BX_Simple_Test, Associative)
{
    // (x0 | x1) | (x2 | x3) <=> x0 | x1 | x2 | x3
    ops[0] = BX_OrN(2, xs[0], xs[1]);
    ops[1] = BX_OrN(2, xs[2], xs[3]);
    ops[2] = BX_OrN(2, ops[0], ops[1]);
    ops[3] = BX_Simplify(ops[2]);
    exps[0] = BX_OrN(4, xs[0], xs[1], xs[2], xs[3]);
    EXPECT_TRUE(Similar(ops[3], exps[0]));

    // (x0 & x1) & (x2 & x3) <=> x0 & x1 & x2 & x3
    ops[4] = BX_AndN(2, xs[0], xs[1]);
    ops[5] = BX_AndN(2, xs[2], xs[3]);
    ops[6] = BX_AndN(2, ops[4], ops[5]);
    ops[7] = BX_Simplify(ops[6]);
    exps[1] = BX_AndN(4, xs[0], xs[1], xs[2], xs[3]);
    EXPECT_TRUE(Similar(ops[7], exps[1]));

    // (x0 ^ x1) ^ (x2 ^ x3) <=> x0 ^ x1 ^ x2 ^ x3
    ops[8] = BX_XorN(2, xs[0], xs[1]);
    ops[9] = BX_XorN(2, xs[2], xs[3]);
    ops[10] = BX_XorN(2, ops[8], ops[9]);
    ops[11] = BX_Simplify(ops[10]);
    exps[2] = BX_XorN(4, xs[0], xs[1], xs[2], xs[3]);
    EXPECT_TRUE(Similar(ops[11], exps[2]));
}


TEST_F(BX_Simple_Test, XorCases)
{
    // ~x ^ x <=> 1
    ops[0] = BX_XorN(2, xns[0], xs[0]);
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &BX_One);

    // x ^ ~x <=> 1
    ops[2] = BX_XorN(2, xs[0], xns[0]);
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &BX_One);

    // x ^ x <=> 0
    ops[4] = BX_XorN(2, xs[0], xs[0]);
    ops[5] = BX_Simplify(ops[4]);
    EXPECT_EQ(ops[5], &BX_Zero);
}


TEST_F(BX_Simple_Test, EqualCases)
{
    // ~x = x <=> 0
    ops[0] = BX_EqualN(2, xns[0], xs[0]);
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &BX_Zero);

    // x = ~x <=> 0
    ops[2] = BX_EqualN(2, xs[0], xns[0]);
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_EQ(ops[3], &BX_Zero);

    // 0 = x <=> ~x
    ops[4] = BX_EqualN(2, &BX_Zero, xs[0]);
    ops[5] = BX_Simplify(ops[4]);
    EXPECT_EQ(ops[5], xns[0]);

    // eq(0, x0, x1) <=> Nor(x0, x1)
    ops[6] = BX_EqualN(3, &BX_Zero, xs[0], xs[1]);
    ops[7] = BX_Simplify(ops[6]);
    exps[0] = BX_NorN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[7], exps[0]));

    // eq(1, x0, x1) <=> And(x0, x1)
    ops[8] = BX_EqualN(3, &BX_One, xs[0], xs[1]);
    ops[9] = BX_Simplify(ops[8]);
    exps[1] = BX_AndN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[9], exps[1]));

    // eq(x1, x0, x1, x0) <=> x0 = x1
    ops[12] = BX_EqualN(4, xs[1], xs[0], xs[1], xs[0]);
    ops[13] = BX_Simplify(ops[12]);
    exps[2] = BX_EqualN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[13], exps[2]));
}


TEST_F(BX_Simple_Test, NotCases)
{
    ops[0] = BX_NorN(3, xs[0], &BX_One, xs[1]);
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &BX_Zero);

    ops[2] = BX_NandN(3, xs[0], xs[1], xs[2]);
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_TRUE(Similar(ops[2], ops[3]));
}


TEST_F(BX_Simple_Test, ImpliesCases)
{
    ops[0] = BX_Implies(&BX_Zero, xs[0]);
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &BX_One);

    ops[2] = BX_Implies(&BX_One, xs[0]);
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_EQ(ops[3], xs[0]);

    ops[4] = BX_Implies(xs[0], &BX_Zero);
    ops[5] = BX_Simplify(ops[4]);
    EXPECT_EQ(ops[5], xns[0]);

    ops[6] = BX_Implies(xs[0], &BX_One);
    ops[7] = BX_Simplify(ops[6]);
    EXPECT_EQ(ops[7], &BX_One);

    ops[8] = BX_Implies(xs[0], xs[0]);
    ops[9] = BX_Simplify(ops[8]);
    EXPECT_EQ(ops[7], &BX_One);

    ops[10] = BX_Implies(xns[0], xs[0]);
    ops[11] = BX_Simplify(ops[10]);
    EXPECT_EQ(ops[11], xs[0]);

    ops[12] = BX_Implies(xs[1], xs[2]);
    ops[13] = BX_Simplify(ops[12]);
    EXPECT_TRUE(Similar(ops[12], ops[13]));
}


TEST_F(BX_Simple_Test, ITECases)
{
    // ITE(s, 0, 0) <=> 0
    ops[0] = BX_ITE(xs[0], &BX_Zero, &BX_Zero);
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_EQ(ops[1], &BX_Zero);

    // ITE(s, 0, 1) <=> ~s
    ops[2] = BX_ITE(xs[0], &BX_Zero, &BX_One);
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_EQ(ops[3], xns[0]);

    // ITE(s, 0, d0) <=> ~s & d0
    ops[4] = BX_ITE(xs[0], &BX_Zero, xs[1]);
    ops[5] = BX_Simplify(ops[4]);
    exps[0] = BX_AndN(2, xns[0], xs[1]);
    EXPECT_TRUE(Similar(ops[5], exps[0]));

    // ITE(s, 1, 0) <=> s
    ops[6] = BX_ITE(xs[0], &BX_One, &BX_Zero);
    ops[7] = BX_Simplify(ops[6]);
    EXPECT_EQ(ops[7], xs[0]);

    // ITE(s, 1, 1) <=> 1
    ops[8] = BX_ITE(xs[0], &BX_One, &BX_One);
    ops[9] = BX_Simplify(ops[8]);
    EXPECT_EQ(ops[9], &BX_One);

    // ITE(s, 1, d0) <=> s | d0
    ops[10] = BX_ITE(xs[0], &BX_One, xs[1]);
    ops[11] = BX_Simplify(ops[10]);
    exps[1] = BX_OrN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[11], exps[1]));

    // ITE(s, d1, 0) <=> s & d1
    ops[12] = BX_ITE(xs[0], xs[1], &BX_Zero);
    ops[13] = BX_Simplify(ops[12]);
    exps[2] = BX_AndN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[13], exps[2]));

    // ITE(s, d1, 1) <=> ~s | d1
    ops[14] = BX_ITE(xs[0], xs[1], &BX_One);
    ops[15] = BX_Simplify(ops[14]);
    exps[3] = BX_OrN(2, xns[0], xs[1]);
    EXPECT_TRUE(Similar(ops[15], exps[3]));

    // ITE(s, d1, d1) <=> d1
    ops[16] = BX_ITE(xs[0], xs[1], xs[1]);
    ops[17] = BX_Simplify(ops[16]);
    EXPECT_EQ(ops[17], xs[1]);

    // ITE(s, s, d0) <=> s | d0
    ops[18] = BX_ITE(xs[0], xs[0], xs[1]);
    ops[19] = BX_Simplify(ops[18]);
    exps[4] = BX_OrN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[19], exps[4]));

    // ITE(s, d1, s) <=> s & d1
    ops[20] = BX_ITE(xs[0], xs[1], xs[0]);
    ops[21] = BX_Simplify(ops[20]);
    exps[5] = BX_AndN(2, xs[0], xs[1]);
    EXPECT_TRUE(Similar(ops[21], exps[5]));

    ops[22] = BX_ITE(xs[0], xs[1], xs[2]);
    ops[23] = BX_Simplify(ops[22]);
    EXPECT_TRUE(Similar(ops[22], ops[23]));
}

