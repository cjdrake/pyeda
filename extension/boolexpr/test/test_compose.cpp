/*
** Filename: test_compose.cpp
**
** Test function composition
*/


#include "boolexprtest.hpp"


class BoolExprComposeTest: public BoolExprTest {};


// Test composition on atoms
TEST_F(BoolExprComposeTest, Atoms1)
{
    BoolExprDict *var2ex = BoolExprDict_New();

    BoolExprDict_Insert(var2ex, xs[0], &Zero);
    BoolExprDict_Insert(var2ex, xs[1], &One);
    BoolExprDict_Insert(var2ex, xs[2], xs[12]);
    BoolExprDict_Insert(var2ex, xs[3], xs[13]);

    ops[0] = BoolExpr_Compose(&Zero, var2ex);
    EXPECT_EQ(ops[0], &Zero);

    ops[1] = BoolExpr_Compose(&One, var2ex);
    EXPECT_EQ(ops[1], &One);

    ops[2] = BoolExpr_Compose(xs[0], var2ex);
    EXPECT_EQ(ops[2], &Zero);

    ops[3] = BoolExpr_Compose(xns[0], var2ex);
    EXPECT_EQ(ops[3], &One);

    ops[4] = BoolExpr_Compose(xs[2], var2ex);
    EXPECT_EQ(ops[4], xs[12]);

    ops[5] = BoolExpr_Compose(xns[2], var2ex);
    EXPECT_EQ(ops[5], xns[12]);

    ops[6] = BoolExpr_Compose(xs[10], var2ex);
    EXPECT_EQ(ops[6], xs[10]);

    ops[7] = BoolExpr_Compose(xns[10], var2ex);
    EXPECT_EQ(ops[7], xns[10]);

    BoolExprDict_Del(var2ex);
}


// Test restriction on atoms
TEST_F(BoolExprComposeTest, Atoms2)
{
    BoolExprDict *var2const = BoolExprDict_New();

    BoolExprDict_Insert(var2const, xs[0], &Zero);
    BoolExprDict_Insert(var2const, xs[1], &One);
    BoolExprDict_Insert(var2const, xs[2], &Zero);
    BoolExprDict_Insert(var2const, xs[3], &One);

    ops[0] = BoolExpr_Restrict(&Zero, var2const);
    EXPECT_EQ(ops[0], &Zero);

    ops[1] = BoolExpr_Restrict(&One, var2const);
    EXPECT_EQ(ops[1], &One);

    ops[2] = BoolExpr_Restrict(xs[0], var2const);
    EXPECT_EQ(ops[2], &Zero);

    ops[3] = BoolExpr_Restrict(xns[0], var2const);
    EXPECT_EQ(ops[3], &One);

    ops[4] = BoolExpr_Compose(xs[10], var2const);
    EXPECT_EQ(ops[4], xs[10]);

    ops[5] = BoolExpr_Compose(xns[10], var2const);
    EXPECT_EQ(ops[5], xns[10]);

    BoolExprDict_Del(var2const);
}


TEST_F(BoolExprComposeTest, Basic)
{
    ops[0] = AndN(2, xs[0], xs[1]);
    ops[1] = XorN(2, xs[2], xs[3]);
    ops[2] = OrN(2, ops[0], ops[1]);

    BoolExprDict *var2const = BoolExprDict_New();
    BoolExprDict_Insert(var2const, xs[0], &Zero);
    BoolExprDict_Insert(var2const, xs[2], &One);

    ops[3] = BoolExpr_Restrict(ops[2], var2const);
    EXPECT_EQ(ops[3], xns[3]);

    BoolExprDict_Del(var2const);
}


// In which I try to close 100% coverage
TEST_F(BoolExprComposeTest, Misc)
{
    ops[0] = OrN(4, xs[0], xs[1], xs[2], xs[3]);
    ops[1] = BoolExpr_Simplify(ops[0]);

    BoolExprDict *var2const = BoolExprDict_New();
    BoolExprDict_Insert(var2const, xs[8], &Zero);
    BoolExprDict_Insert(var2const, xs[9], &Zero);

    ops[2] = BoolExpr_Compose(ops[1], var2const);
    EXPECT_EQ(ops[2], ops[1]);

    BoolExprDict_Del(var2const);
}

