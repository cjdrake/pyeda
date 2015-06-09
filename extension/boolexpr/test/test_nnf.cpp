/*
** Filename: test_nnf.cpp
*/


#include "boolexprtest.hpp"


class BX_NNF_Test: public BoolExpr_Test {};


TEST_F(BX_NNF_Test, Basic)
{
    ops[0] = BX_NorN(2, xs[0], xs[1]);
    ops[1] = BX_ToNNF(ops[0]);
    exps[0] = BX_AndN(2, xns[0], xns[1]);
    EXPECT_TRUE(Similar(ops[1], exps[0]));

    ops[2] = BX_NandN(2, xs[0], xs[1]);
    ops[3] = BX_ToNNF(ops[2]);
    exps[1] = BX_OrN(2, xns[0], xns[1]);
    EXPECT_TRUE(Similar(ops[3], exps[1]));

    ops[4] = BX_XorN(2, xs[0], xs[1]);
    ops[5] = BX_ToNNF(ops[4]);
    exps[2] = BX_AndN(2, xns[0], xs[1]);
    exps[3] = BX_AndN(2, xs[0], xns[1]);
    exps[4] = BX_OrN(2, exps[2], exps[3]);
    EXPECT_TRUE(Similar(ops[5], exps[4]));

    ops[6] = BX_EqualN(3, xs[0], xs[1], xs[2]);
    ops[7] = BX_ToNNF(ops[6]);
    exps[5] = BX_AndN(3, xns[0], xns[1], xns[2]);
    exps[6] = BX_AndN(3, xs[0], xs[1], xs[2]);
    exps[7] = BX_OrN(2, exps[5], exps[6]);
    EXPECT_TRUE(Similar(ops[7], exps[7]));

    ops[8] = BX_Implies(xs[0], xs[1]);
    ops[9] = BX_ToNNF(ops[8]);
    exps[8] = BX_OrN(2, xns[0], xs[1]);
    EXPECT_TRUE(Similar(ops[9], exps[8]));

    ops[10] = BX_ITE(xs[0], xs[1], xs[2]);
    ops[11] = BX_ToNNF(ops[10]);
    exps[9] = BX_AndN(2, xs[0], xs[1]);
    exps[10] = BX_AndN(2, xns[0], xs[2]);
    exps[11] = BX_OrN(2, exps[9], exps[10]);
    EXPECT_TRUE(Similar(ops[11], exps[11]));
}

