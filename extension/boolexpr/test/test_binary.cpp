/*
** Filename: test_binary.cpp
**
** Test conversion of Nary operators to binary operators
*/


#include "boolexprtest.hpp"


class BX_Binary_Test: public BoolExpr_Test {};


TEST_F(BX_Binary_Test, BinifyAtoms)
{
    ops[0] = BX_ToBinary(&BX_Zero);
    EXPECT_EQ(ops[0], &BX_Zero);

    ops[1] = BX_ToBinary(xs[0]);
    EXPECT_EQ(ops[1], xs[0]);
}


TEST_F(BX_Binary_Test, BinifyFixed)
{
    ops[0] = BX_NorN(2, xs[0], xs[1]);
    ops[1] = BX_ToBinary(ops[0]);
    EXPECT_EQ(ops[0], ops[1]);

    ops[2] = BX_Implies(xs[0], xs[1]);
    ops[3] = BX_ToBinary(ops[2]);
    EXPECT_EQ(ops[2], ops[3]);

    ops[4] = BX_ITE(xs[0], xs[1], xs[2]);
    ops[5] = BX_ToBinary(ops[4]);
    EXPECT_EQ(ops[4], ops[5]);
}


TEST_F(BX_Binary_Test, BinifyCommutativeOdd)
{
    // Or(x0, x1, x2) <=> Or(x0, Or(x1, x2))
    ops[0] = BX_OrN(3, xs[0], xs[1], xs[2]);
    ops[1] = BX_ToBinary(ops[0]);
    exps[0] = BX_OrN(2, xs[1], xs[2]);
    exps[1] = BX_OrN(2, xs[0], exps[0]);
    EXPECT_TRUE(Similar(ops[1], exps[1]));

    // And(x0, x1, x2) <=> And(x0, And(x1, x2))
    ops[2] = BX_AndN(3, xs[0], xs[1], xs[2]);
    ops[3] = BX_ToBinary(ops[2]);
    exps[2] = BX_AndN(2, xs[1], xs[2]);
    exps[3] = BX_AndN(2, xs[0], exps[2]);
    EXPECT_TRUE(Similar(ops[3], exps[3]));

    // Xor(x0, x1, x2) <=> Xor(x0, Xor(x1, x2))
    ops[4] = BX_XorN(3, xs[0], xs[1], xs[2]);
    ops[5] = BX_ToBinary(ops[4]);
    exps[4] = BX_XorN(2, xs[1], xs[2]);
    exps[5] = BX_XorN(2, xs[0], exps[4]);
    EXPECT_TRUE(Similar(ops[5], exps[5]));
}


TEST_F(BX_Binary_Test, BinifyCommutativeEven)
{
    // Or(x0, x1, x2, x3) <=> Or(Or(x0, x1), Or(x2, x3))
    ops[0] = BX_OrN(4, xs[0], xs[1], xs[2], xs[3]);
    ops[1] = BX_ToBinary(ops[0]);
    exps[0] = BX_OrN(2, xs[0], xs[1]);
    exps[1] = BX_OrN(2, xs[2], xs[3]);
    exps[2] = BX_OrN(2, exps[0], exps[1]);
    EXPECT_TRUE(Similar(ops[1], exps[2]));

    // And(x0, x1, x2, x3) <=> And(And(x0, x1), And(x2, x3))
    ops[2] = BX_AndN(4, xs[0], xs[1], xs[2], xs[3]);
    ops[3] = BX_ToBinary(ops[2]);
    exps[3] = BX_AndN(2, xs[0], xs[1]);
    exps[4] = BX_AndN(2, xs[2], xs[3]);
    exps[5] = BX_AndN(2, exps[3], exps[4]);
    EXPECT_TRUE(Similar(ops[3], exps[5]));

    // Xor(x0, x1, x2, x3) <=> Xor(Xor(x0, x1), Xor(x2, x3))
    ops[4] = BX_XorN(4, xs[0], xs[1], xs[2], xs[3]);
    ops[5] = BX_ToBinary(ops[4]);
    exps[6] = BX_XorN(2, xs[0], xs[1]);
    exps[7] = BX_XorN(2, xs[2], xs[3]);
    exps[8] = BX_XorN(2, exps[6], exps[7]);
    EXPECT_TRUE(Similar(ops[5], exps[8]));
}


TEST_F(BX_Binary_Test, BinifyEqual2)
{
    ops[0] = BX_EqualN(2, xs[0], xs[1]);
    ops[1] = BX_ToBinary(ops[0]);
    EXPECT_EQ(ops[0], ops[1]);
}


TEST_F(BX_Binary_Test, BinifyEqualN)
{
    // Equal(x0, x1, x2) <=> (x0 = x1) & (x0 = x2) & (x1 = x2)
    ops[0] = BX_EqualN(3, xs[0], xs[1], xs[2]);
    ops[1] = BX_ToBinary(ops[0]);
    exps[0] = BX_EqualN(2, xs[0], xs[1]);
    exps[1] = BX_EqualN(2, xs[0], xs[2]);
    exps[2] = BX_EqualN(2, xs[1], xs[2]);
    exps[3] = BX_AndN(2, exps[1], exps[2]);
    exps[4] = BX_AndN(2, exps[0], exps[3]);
    EXPECT_TRUE(Similar(ops[1], exps[4]));
}

