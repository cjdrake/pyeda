/*
** Filename: test_argset.cpp
**
** Test the BoolExprArgSet data types.
*/


#include "boolexprtest.hpp"


class BoolExprArgSetTest: public BoolExprTest {};


TEST_F(BoolExprArgSetTest, OrBasic)
{
    BoolExprOrAndArgSet *a = BoolExprOrAndArgSet_New(OP_OR);

    EXPECT_EQ(a->kind, OP_OR);
    EXPECT_TRUE(a->min);
    EXPECT_FALSE(a->max);

    BoolExprOrAndArgSet_Insert(a, xns[0]);
    EXPECT_FALSE(a->min);
    EXPECT_EQ(a->xs->length, 1);

    BoolExprOrAndArgSet_Insert(a, &Zero);
    EXPECT_EQ(a->xs->length, 1);

    ops[0] = OrN(2, xs[1], xs[2]);
    ops[1] = OrN(2, xs[3], xs[4]);
    ops[2] = OrN(2, ops[0], ops[1]);
    BoolExprOrAndArgSet_Insert(a, ops[2]);
    EXPECT_EQ(a->xs->length, 5);

    BoolExprOrAndArgSet_Insert(a, xs[0]);
    EXPECT_FALSE(a->min);
    EXPECT_TRUE(a->max);
    EXPECT_EQ(a->xs->length, 0);

    BoolExprOrAndArgSet_Del(a);
}


TEST_F(BoolExprArgSetTest, AndBasic)
{
    BoolExprOrAndArgSet *a = BoolExprOrAndArgSet_New(OP_AND);

    EXPECT_EQ(a->kind, OP_AND);
    EXPECT_TRUE(a->min);
    EXPECT_FALSE(a->max);

    BoolExprOrAndArgSet_Insert(a, xns[0]);
    EXPECT_FALSE(a->min);
    EXPECT_EQ(a->xs->length, 1);

    BoolExprOrAndArgSet_Insert(a, &One);
    EXPECT_EQ(a->xs->length, 1);

    ops[0] = AndN(2, xs[1], xs[2]);
    ops[1] = AndN(2, xs[3], xs[4]);
    ops[2] = AndN(2, ops[0], ops[1]);
    BoolExprOrAndArgSet_Insert(a, ops[2]);
    EXPECT_EQ(a->xs->length, 5);

    BoolExprOrAndArgSet_Insert(a, &Zero);
    EXPECT_FALSE(a->min);
    EXPECT_TRUE(a->max);
    EXPECT_EQ(a->xs->length, 0);

    BoolExprOrAndArgSet_Del(a);
}

