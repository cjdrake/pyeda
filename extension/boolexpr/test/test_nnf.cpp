/*
** Filename: test_nnf.cpp
*/


#include "boolexprtest.hpp"


class BoolExprNNFTest: public BoolExprTest {};


TEST_F(BoolExprNNFTest, Basic)
{
    ops[0] = NorN(2, xs[0], xs[1]);
    ops[1] = BoolExpr_ToNNF(ops[0]);
    exps[0] = AndN(2, xns[0], xns[1]);
    EXPECT_TRUE(Similar(ops[1], exps[0]));

    ops[2] = NandN(2, xs[0], xs[1]);
    ops[3] = BoolExpr_ToNNF(ops[2]);
    exps[1] = OrN(2, xns[0], xns[1]);
    EXPECT_TRUE(Similar(ops[3], exps[1]));

    ops[4] = XorN(2, xs[0], xs[1]);
    ops[5] = BoolExpr_ToNNF(ops[4]);
    exps[2] = AndN(2, xns[0], xs[1]);
    exps[3] = AndN(2, xs[0], xns[1]);
    exps[4] = OrN(2, exps[2], exps[3]);
    EXPECT_TRUE(Similar(ops[5], exps[4]));

    ops[6] = EqualN(3, xs[0], xs[1], xs[2]);
    ops[7] = BoolExpr_ToNNF(ops[6]);
    exps[5] = AndN(3, xns[0], xns[1], xns[2]);
    exps[6] = AndN(3, xs[0], xs[1], xs[2]);
    exps[7] = OrN(2, exps[5], exps[6]);
    EXPECT_TRUE(Similar(ops[7], exps[7]));

    ops[8] = Implies(xs[0], xs[1]);
    ops[9] = BoolExpr_ToNNF(ops[8]);
    exps[8] = OrN(2, xns[0], xs[1]);
    EXPECT_TRUE(Similar(ops[9], exps[8]));

    ops[10] = ITE(xs[0], xs[1], xs[2]);
    ops[11] = BoolExpr_ToNNF(ops[10]);
    exps[9] = AndN(2, xs[0], xs[1]);
    exps[10] = AndN(2, xns[0], xs[2]);
    exps[11] = OrN(2, exps[9], exps[10]);
    EXPECT_TRUE(Similar(ops[11], exps[11]));
}

