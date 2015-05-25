/*
** Filename: test_argset.cpp
**
** Test the BoolExprArgSet data types.
*/


#include "boolexprtest.hpp"


class BoolExprArgSetTest: public BoolExprTest {};


TEST_F(BoolExprArgSetTest, OrBasic)
{
    struct BoolExprOrAndArgSet *a = BoolExprOrAndArgSet_New(OP_OR);

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
    struct BoolExprOrAndArgSet *a = BoolExprOrAndArgSet_New(OP_AND);

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


TEST_F(BoolExprArgSetTest, XorBasic)
{
    struct BoolExprXorArgSet *a = BoolExprXorArgSet_New(true);

    BoolExprXorArgSet_Insert(a, xs[0]);
    BoolExprXorArgSet_Insert(a, xs[1]);
    EXPECT_TRUE(a->parity);
    EXPECT_EQ(a->xs->length, 2);

    BoolExprXorArgSet_Insert(a, &Zero);
    EXPECT_TRUE(a->parity);
    EXPECT_EQ(a->xs->length, 2);

    BoolExprXorArgSet_Insert(a, &One);
    EXPECT_FALSE(a->parity);
    EXPECT_EQ(a->xs->length, 2);

    ops[0] = XorN(2, xs[2], xs[3]);
    ops[1] = XnorN(2, xs[4], xs[5]);
    ops[2] = XorN(2, ops[0], ops[1]);
    BoolExprXorArgSet_Insert(a, ops[2]);
    EXPECT_TRUE(a->parity);
    EXPECT_EQ(a->xs->length, 6);

    BoolExprXorArgSet_Insert(a, xs[0]);
    EXPECT_TRUE(a->parity);
    EXPECT_EQ(a->xs->length, 5);

    BoolExprXorArgSet_Insert(a, xns[1]);
    EXPECT_FALSE(a->parity);
    EXPECT_EQ(a->xs->length, 4);

    BoolExprXorArgSet_Del(a);
}


TEST_F(BoolExprArgSetTest, EqBasic)
{
    struct BoolExprEqArgSet *a = BoolExprEqArgSet_New();

    BoolExprEqArgSet_Insert(a, xs[0]);
    BoolExprEqArgSet_Insert(a, xs[1]);
    EXPECT_FALSE(a->zero);
    EXPECT_FALSE(a->one);
    EXPECT_EQ(a->xs->length, 2);

    BoolExprEqArgSet_Insert(a, &Zero);
    BoolExprEqArgSet_Insert(a, &One);
    EXPECT_TRUE(a->zero);
    EXPECT_TRUE(a->one);
    EXPECT_EQ(a->xs->length, 0);

    BoolExprEqArgSet_Insert(a, xs[2]);
    BoolExprEqArgSet_Insert(a, xs[3]);
    EXPECT_TRUE(a->zero);
    EXPECT_TRUE(a->one);
    EXPECT_EQ(a->xs->length, 0);

    BoolExprEqArgSet_Del(a);

    struct BoolExprEqArgSet *b = BoolExprEqArgSet_New();

    BoolExprEqArgSet_Insert(b, xs[0]);
    BoolExprEqArgSet_Insert(b, xs[1]);
    BoolExprEqArgSet_Insert(b, xs[2]);
    EXPECT_FALSE(b->zero);
    EXPECT_FALSE(b->one);
    EXPECT_EQ(b->xs->length, 3);
    BoolExprEqArgSet_Insert(b, xns[1]);
    EXPECT_TRUE(b->zero);
    EXPECT_TRUE(b->one);
    EXPECT_EQ(b->xs->length, 0);

    BoolExprEqArgSet_Del(b);
}

