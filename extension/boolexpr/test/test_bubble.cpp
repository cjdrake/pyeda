/*
** Filename: test_bubble.cpp
**
** Test bubbling of NOT operators
**
*/


#include "boolexprtest.hpp"


class BoolExprBubbleTest: public BoolExprTest {};


TEST_F(BoolExprBubbleTest, Atoms)
{
    ops[0] = BoolExpr_PushDownNot(&Zero);
    EXPECT_EQ(ops[0], &Zero);

    ops[1] = BoolExpr_PushDownNot(&One);
    EXPECT_EQ(ops[1], &One);

    ops[2] = BoolExpr_PushDownNot(xns[0]);
    EXPECT_EQ(ops[2], xns[0]);

    ops[3] = BoolExpr_PushDownNot(xs[0]);
    EXPECT_EQ(ops[3], xs[0]);
}


TEST_F(BoolExprBubbleTest, NothingToDo)
{
    // OR/AND with no NOT operators
    ops[0] = AndN(2, xs[0], xs[1]);
    ops[1] = AndN(2, xs[2], xs[3]);
    ops[2] = OrN(2, ops[0], ops[1]);
    ops[3] = BoolExpr_PushDownNot(ops[2]);
    EXPECT_EQ(ops[3], ops[2]);

}


TEST_F(BoolExprBubbleTest, DeMorganL1)
{
    ops[0] = NorN(2, xs[0], xs[1]);
    ops[1] = BoolExpr_PushDownNot(ops[0]);
    exps[0] = AndN(2, xns[0], xns[1]);
    EXPECT_TRUE(Similar(ops[1], exps[0]));

    ops[2] = NandN(2, xs[0], xs[1]);
    ops[3] = BoolExpr_PushDownNot(ops[2]);
    exps[1] = OrN(2, xns[0], xns[1]);
    EXPECT_TRUE(Similar(ops[3], exps[1]));
}


TEST_F(BoolExprBubbleTest, DeMorganL2)
{
    ops[0] = AndN(2, xs[0], xs[1]);
    ops[1] = AndN(2, xs[2], xs[3]);
    ops[2] = OrN(2, ops[0], ops[1]);
    ops[3] = AndN(2, xs[4], xs[5]);
    ops[4] = AndN(2, xs[6], xs[7]);
    ops[5] = OrN(2, ops[3], ops[4]);
    ops[6] = AndN(2, ops[2], ops[5]);
    ops[7] = Not(ops[6]);
    ops[8] = BoolExpr_PushDownNot(ops[7]);

    exps[0] = OrN(2, xns[0], xns[1]);
    exps[1] = OrN(2, xns[2], xns[3]);
    exps[2] = AndN(2, exps[0], exps[1]);
    exps[3] = OrN(2, xns[4], xns[5]);
    exps[4] = OrN(2, xns[6], xns[7]);
    exps[5] = AndN(2, exps[3], exps[4]);
    exps[6] = OrN(2, exps[2], exps[5]);

    EXPECT_TRUE(Similar(ops[8], exps[6]));
}


TEST_F(BoolExprBubbleTest, IfThenElseDuality)
{
    ops[0] = ITE(xs[0], xs[1], xs[2]);
    ops[1] = Not(ops[0]);
    ops[2] = BoolExpr_PushDownNot(ops[1]);
    exps[0] = ITE(xs[0], xns[1], xns[2]);
    EXPECT_TRUE(Similar(ops[2], exps[0]));
}

