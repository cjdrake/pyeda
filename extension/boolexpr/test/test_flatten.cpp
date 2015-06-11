/*
** Filename: test_flatten.cpp
*/


#include "boolexprtest.hpp"


class BX_Flatten_Test: public BoolExpr_Test {};


TEST_F(BX_Flatten_Test, Atoms)
{
    ops[0] = BX_ToDNF(&BX_Zero);
    EXPECT_EQ(ops[0], &BX_Zero);

    ops[1] = BX_ToCNF(&BX_Zero);
    EXPECT_EQ(ops[1], &BX_Zero);

    ops[2] = BX_ToDNF(xs[0]);
    EXPECT_EQ(ops[2], xs[0]);

    ops[3] = BX_ToCNF(xs[0]);
    EXPECT_EQ(ops[3], xs[0]);
}


TEST_F(BX_Flatten_Test, Clauses)
{
    ops[0] = BX_OrN(3, xs[0], xs[1], xs[2]);
    ops[1] = BX_Simplify(ops[0]);
    ops[2] = BX_ToDNF(ops[1]);
    EXPECT_EQ(ops[2], ops[1]);
    ops[3] = BX_ToCNF(ops[1]);
    EXPECT_EQ(ops[3], ops[1]);

    ops[4] = BX_AndN(3, xs[0], xs[1], xs[2]);
    ops[5] = BX_Simplify(ops[4]);
    ops[6] = BX_ToDNF(ops[5]);
    EXPECT_EQ(ops[6], ops[5]);
    ops[7] = BX_ToCNF(ops[5]);
    EXPECT_EQ(ops[7], ops[5]);
}


TEST_F(BX_Flatten_Test, Basic)
{
    ops[0] = BX_XorN(4, xs[0], xs[1], xs[2], xs[3]);

    ops[1] = BX_ToDNF(ops[0]);
    EXPECT_EQ(ops[1]->kind, BX_OP_OR);
    EXPECT_EQ(ops[1]->data.xs->length, 8);

    ops[2] = BX_ToCNF(ops[1]);
    EXPECT_EQ(ops[2]->kind, BX_OP_AND);
    EXPECT_EQ(ops[2]->data.xs->length, 8);
}


// Only for coverage and memory leak checking
TEST_F(BX_Flatten_Test, FIXME)
{
    ops[0] = BX_AndN(2, xs[1], xs[2]);
    ops[1] = BX_AndN(3, xs[3], xs[4], xs[5]);
    ops[2] = BX_OrN(3, xs[0], ops[0], ops[1]);
    ops[3] = BX_ToCNF(ops[2]);
    ops[4] = BX_CompleteSum(ops[2]);
}

