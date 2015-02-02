/*
** Filename: test_flatten.cpp
*/


#include "boolexprtest.hpp"


class BoolExprFlattenTest: public BoolExprTest {};


TEST_F(BoolExprFlattenTest, Atoms)
{
    ops[0] = BoolExpr_ToDNF(&Zero);
    EXPECT_EQ(ops[0], &Zero);

    ops[1] = BoolExpr_ToCNF(&Zero);
    EXPECT_EQ(ops[1], &Zero);

    ops[2] = BoolExpr_ToDNF(xs[0]);
    EXPECT_EQ(ops[2], xs[0]);

    ops[3] = BoolExpr_ToCNF(xs[0]);
    EXPECT_EQ(ops[3], xs[0]);
}


TEST_F(BoolExprFlattenTest, Clauses)
{
    ops[0] = OrN(3, xs[0], xs[1], xs[2]);
    ops[1] = BoolExpr_Simplify(ops[0]);
    ops[2] = BoolExpr_ToDNF(ops[1]);
    EXPECT_EQ(ops[2], ops[1]);
    ops[3] = BoolExpr_ToCNF(ops[1]);
    EXPECT_EQ(ops[3], ops[1]);

    ops[4] = AndN(3, xs[0], xs[1], xs[2]);
    ops[5] = BoolExpr_Simplify(ops[4]);
    ops[6] = BoolExpr_ToDNF(ops[5]);
    EXPECT_EQ(ops[6], ops[5]);
    ops[7] = BoolExpr_ToCNF(ops[5]);
    EXPECT_EQ(ops[7], ops[5]);
}


TEST_F(BoolExprFlattenTest, Basic)
{
    ops[0] = XorN(4, xs[0], xs[1], xs[2], xs[3]);

    ops[1] = BoolExpr_ToDNF(ops[0]);
    EXPECT_EQ(ops[1]->type, OP_OR);
    EXPECT_EQ(ops[1]->data.xs->length, 8);

    ops[2] = BoolExpr_ToCNF(ops[1]);
    EXPECT_EQ(ops[2]->type, OP_AND);
    EXPECT_EQ(ops[2]->data.xs->length, 8);
}


// Only for coverage and memory leak checking
TEST_F(BoolExprFlattenTest, FIXME)
{
    ops[0] = AndN(2, xs[1], xs[2]);
    ops[1] = AndN(3, xs[3], xs[4], xs[5]);
    ops[2] = OrN(3, xs[0], ops[0], ops[1]);
    ops[3] = BoolExpr_ToCNF(ops[2]);
    ops[4] = BoolExpr_CompleteSum(ops[2]);
}

