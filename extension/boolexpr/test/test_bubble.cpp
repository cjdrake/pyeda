/*
** Filename: test_bubble.cpp
**
** Test bubbling of NOT operators
**
*/


#include "boolexprtest.hpp"


class BX_Bubble_Test: public BoolExpr_Test {};


TEST_F(BX_Bubble_Test, Atoms)
{
    ops[0] = BX_PushDownNot(&BX_Zero);
    EXPECT_EQ(ops[0], &BX_Zero);

    ops[1] = BX_PushDownNot(&BX_One);
    EXPECT_EQ(ops[1], &BX_One);

    ops[2] = BX_PushDownNot(xns[0]);
    EXPECT_EQ(ops[2], xns[0]);

    ops[3] = BX_PushDownNot(xs[0]);
    EXPECT_EQ(ops[3], xs[0]);
}


TEST_F(BX_Bubble_Test, NothingToDo)
{
    // OR/AND with no NOT operators
    ops[0] = BX_AndN(2, xs[0], xs[1]);
    ops[1] = BX_AndN(2, xs[2], xs[3]);
    ops[2] = BX_OrN(2, ops[0], ops[1]);
    ops[3] = BX_PushDownNot(ops[2]);
    EXPECT_EQ(ops[3], ops[2]);

}


TEST_F(BX_Bubble_Test, DeMorganL1)
{
    ops[0] = BX_NorN(2, xs[0], xs[1]);
    ops[1] = BX_PushDownNot(ops[0]);
    exps[0] = BX_AndN(2, xns[0], xns[1]);
    EXPECT_TRUE(Similar(ops[1], exps[0]));

    ops[2] = BX_NandN(2, xs[0], xs[1]);
    ops[3] = BX_PushDownNot(ops[2]);
    exps[1] = BX_OrN(2, xns[0], xns[1]);
    EXPECT_TRUE(Similar(ops[3], exps[1]));
}


TEST_F(BX_Bubble_Test, DeMorganL2)
{
    ops[0] = BX_AndN(2, xs[0], xs[1]);
    ops[1] = BX_AndN(2, xs[2], xs[3]);
    ops[2] = BX_OrN(2, ops[0], ops[1]);
    ops[3] = BX_AndN(2, xs[4], xs[5]);
    ops[4] = BX_AndN(2, xs[6], xs[7]);
    ops[5] = BX_OrN(2, ops[3], ops[4]);
    ops[6] = BX_AndN(2, ops[2], ops[5]);
    ops[7] = BX_Not(ops[6]);
    ops[8] = BX_PushDownNot(ops[7]);

    exps[0] = BX_OrN(2, xns[0], xns[1]);
    exps[1] = BX_OrN(2, xns[2], xns[3]);
    exps[2] = BX_AndN(2, exps[0], exps[1]);
    exps[3] = BX_OrN(2, xns[4], xns[5]);
    exps[4] = BX_OrN(2, xns[6], xns[7]);
    exps[5] = BX_AndN(2, exps[3], exps[4]);
    exps[6] = BX_OrN(2, exps[2], exps[5]);

    EXPECT_TRUE(Similar(ops[8], exps[6]));
}


TEST_F(BX_Bubble_Test, IfThenElseDuality)
{
    ops[0] = BX_ITE(xs[0], xs[1], xs[2]);
    ops[1] = BX_Not(ops[0]);
    ops[2] = BX_PushDownNot(ops[1]);
    exps[0] = BX_ITE(xs[0], xns[1], xns[2]);
    EXPECT_TRUE(Similar(ops[2], exps[0]));
}

