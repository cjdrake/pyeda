/*
** Filename: test_compose.cpp
**
** Test function composition
*/


#include "boolexprtest.hpp"


class BX_Compose_Test: public BoolExpr_Test {};


// Test composition on atoms
TEST_F(BX_Compose_Test, Atoms1)
{
    struct BX_Dict *var2ex = BX_Dict_New();

    BX_Dict_Insert(var2ex, xs[0], &BX_Zero);
    BX_Dict_Insert(var2ex, xs[1], &BX_One);
    BX_Dict_Insert(var2ex, xs[2], xs[12]);
    BX_Dict_Insert(var2ex, xs[3], xs[13]);

    ops[0] = BX_Compose(&BX_Zero, var2ex);
    EXPECT_EQ(ops[0], &BX_Zero);

    ops[1] = BX_Compose(&BX_One, var2ex);
    EXPECT_EQ(ops[1], &BX_One);

    ops[2] = BX_Compose(xs[0], var2ex);
    EXPECT_EQ(ops[2], &BX_Zero);

    ops[3] = BX_Compose(xns[0], var2ex);
    EXPECT_EQ(ops[3], &BX_One);

    ops[4] = BX_Compose(xs[2], var2ex);
    EXPECT_EQ(ops[4], xs[12]);

    ops[5] = BX_Compose(xns[2], var2ex);
    EXPECT_EQ(ops[5], xns[12]);

    ops[6] = BX_Compose(xs[10], var2ex);
    EXPECT_EQ(ops[6], xs[10]);

    ops[7] = BX_Compose(xns[10], var2ex);
    EXPECT_EQ(ops[7], xns[10]);

    BX_Dict_Del(var2ex);
}


// Test restriction on atoms
TEST_F(BX_Compose_Test, Atoms2)
{
    struct BX_Dict *var2const = BX_Dict_New();

    BX_Dict_Insert(var2const, xs[0], &BX_Zero);
    BX_Dict_Insert(var2const, xs[1], &BX_One);
    BX_Dict_Insert(var2const, xs[2], &BX_Zero);
    BX_Dict_Insert(var2const, xs[3], &BX_One);

    ops[0] = BX_Restrict(&BX_Zero, var2const);
    EXPECT_EQ(ops[0], &BX_Zero);

    ops[1] = BX_Restrict(&BX_One, var2const);
    EXPECT_EQ(ops[1], &BX_One);

    ops[2] = BX_Restrict(xs[0], var2const);
    EXPECT_EQ(ops[2], &BX_Zero);

    ops[3] = BX_Restrict(xns[0], var2const);
    EXPECT_EQ(ops[3], &BX_One);

    ops[4] = BX_Compose(xs[10], var2const);
    EXPECT_EQ(ops[4], xs[10]);

    ops[5] = BX_Compose(xns[10], var2const);
    EXPECT_EQ(ops[5], xns[10]);

    BX_Dict_Del(var2const);
}


TEST_F(BX_Compose_Test, Basic)
{
    ops[0] = BX_AndN(2, xs[0], xs[1]);
    ops[1] = BX_XorN(2, xs[2], xs[3]);
    ops[2] = BX_OrN(2, ops[0], ops[1]);

    struct BX_Dict *var2const = BX_Dict_New();
    BX_Dict_Insert(var2const, xs[0], &BX_Zero);
    BX_Dict_Insert(var2const, xs[2], &BX_One);

    ops[3] = BX_Restrict(ops[2], var2const);
    EXPECT_EQ(ops[3], xns[3]);

    BX_Dict_Del(var2const);
}


// In which I try to close 100% coverage
TEST_F(BX_Compose_Test, Misc)
{
    ops[0] = BX_OrN(4, xs[0], xs[1], xs[2], xs[3]);
    ops[1] = BX_Simplify(ops[0]);

    struct BX_Dict *var2const = BX_Dict_New();
    BX_Dict_Insert(var2const, xs[8], &BX_Zero);
    BX_Dict_Insert(var2const, xs[9], &BX_Zero);

    ops[2] = BX_Compose(ops[1], var2const);
    EXPECT_EQ(ops[2], ops[1]);

    BX_Dict_Del(var2const);
}

