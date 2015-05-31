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
    struct BoolExprEqArgSet *b = BoolExprEqArgSet_New();
    struct BoolExprEqArgSet *c = BoolExprEqArgSet_New();

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

    BoolExprEqArgSet_Insert(b, xs[0]);
    BoolExprEqArgSet_Insert(b, xs[1]);
    EXPECT_FALSE(b->zero);
    EXPECT_FALSE(b->one);
    EXPECT_EQ(b->xs->length, 2);

    BoolExprEqArgSet_Insert(b, &One);
    BoolExprEqArgSet_Insert(b, &Zero);
    EXPECT_TRUE(b->zero);
    EXPECT_TRUE(b->one);
    EXPECT_EQ(b->xs->length, 0);

    BoolExprEqArgSet_Insert(b, xs[2]);
    BoolExprEqArgSet_Insert(b, xs[3]);
    EXPECT_TRUE(b->zero);
    EXPECT_TRUE(b->one);
    EXPECT_EQ(b->xs->length, 0);

    BoolExprEqArgSet_Insert(c, xs[0]);
    BoolExprEqArgSet_Insert(c, xs[1]);
    BoolExprEqArgSet_Insert(c, xs[2]);
    EXPECT_FALSE(c->zero);
    EXPECT_FALSE(c->one);
    EXPECT_EQ(c->xs->length, 3);
    BoolExprEqArgSet_Insert(c, xns[1]);
    EXPECT_TRUE(c->zero);
    EXPECT_TRUE(c->one);
    EXPECT_EQ(c->xs->length, 0);

    BoolExprEqArgSet_Del(a);
    BoolExprEqArgSet_Del(b);
    BoolExprEqArgSet_Del(c);
}


TEST_F(BoolExprArgSetTest, OrReduce)
{
    struct BoolExprOrAndArgSet *a = BoolExprOrAndArgSet_New(OP_OR);
    struct BoolExprOrAndArgSet *b = BoolExprOrAndArgSet_New(OP_OR);
    struct BoolExprOrAndArgSet *c = BoolExprOrAndArgSet_New(OP_OR);
    struct BoolExprOrAndArgSet *d = BoolExprOrAndArgSet_New(OP_OR);

    EXPECT_EQ(BoolExprOrAndArgSet_Reduce(a), &Zero);

    BoolExprOrAndArgSet_Insert(b, xs[0]);
    BoolExprOrAndArgSet_Insert(b, xs[1]);
    BoolExprOrAndArgSet_Insert(b, xs[2]);
    BoolExprOrAndArgSet_Insert(b, xns[0]);
    EXPECT_EQ(BoolExprOrAndArgSet_Reduce(b), &One);

    BoolExprOrAndArgSet_Insert(c, xs[0]);
    BoolExprOrAndArgSet_Insert(c, xs[0]);
    BoolExprOrAndArgSet_Insert(c, xs[1]);
    BoolExprOrAndArgSet_Insert(c, xs[1]);
    ops[0] = BoolExprOrAndArgSet_Reduce(c);
    EXPECT_EQ(ops[0]->kind, OP_OR);
    EXPECT_EQ(ops[0]->data.xs->length, 2);

    BoolExprOrAndArgSet_Insert(d, xs[0]);
    ops[1] = BoolExprOrAndArgSet_Reduce(d);
    EXPECT_EQ(ops[1], xs[0]);

    BoolExprOrAndArgSet_Del(a);
    BoolExprOrAndArgSet_Del(b);
    BoolExprOrAndArgSet_Del(c);
    BoolExprOrAndArgSet_Del(d);
}


TEST_F(BoolExprArgSetTest, AndReduce)
{
    struct BoolExprOrAndArgSet *a = BoolExprOrAndArgSet_New(OP_AND);
    struct BoolExprOrAndArgSet *b = BoolExprOrAndArgSet_New(OP_AND);
    struct BoolExprOrAndArgSet *c = BoolExprOrAndArgSet_New(OP_AND);

    EXPECT_EQ(BoolExprOrAndArgSet_Reduce(a), &One);

    BoolExprOrAndArgSet_Insert(b, xs[0]);
    BoolExprOrAndArgSet_Insert(b, xs[1]);
    BoolExprOrAndArgSet_Insert(b, xs[2]);
    BoolExprOrAndArgSet_Insert(b, xns[0]);
    EXPECT_EQ(BoolExprOrAndArgSet_Reduce(b), &Zero);

    BoolExprOrAndArgSet_Insert(c, xs[0]);
    BoolExprOrAndArgSet_Insert(c, xs[0]);
    BoolExprOrAndArgSet_Insert(c, xs[1]);
    BoolExprOrAndArgSet_Insert(c, xs[1]);
    ops[0] = BoolExprOrAndArgSet_Reduce(c);
    EXPECT_EQ(ops[0]->kind, OP_AND);
    EXPECT_EQ(ops[0]->data.xs->length, 2);

    BoolExprOrAndArgSet_Del(a);
    BoolExprOrAndArgSet_Del(b);
    BoolExprOrAndArgSet_Del(c);
}


TEST_F(BoolExprArgSetTest, XorReduce)
{
    struct BoolExprXorArgSet *a = BoolExprXorArgSet_New(true);
    struct BoolExprXorArgSet *b = BoolExprXorArgSet_New(false);
    struct BoolExprXorArgSet *c = BoolExprXorArgSet_New(true);
    struct BoolExprXorArgSet *d = BoolExprXorArgSet_New(true);

    EXPECT_EQ(BoolExprXorArgSet_Reduce(a), &Zero);
    EXPECT_EQ(BoolExprXorArgSet_Reduce(b), &One);

    BoolExprXorArgSet_Insert(c, xs[0]);
    BoolExprXorArgSet_Insert(c, xs[1]);
    BoolExprXorArgSet_Insert(c, xs[2]);
    ops[0] = BoolExprXorArgSet_Reduce(c);
    EXPECT_EQ(ops[0]->kind, OP_XOR);
    EXPECT_EQ(ops[0]->data.xs->length, 3);

    BoolExprXorArgSet_Insert(d, xs[0]);
    ops[1] = BoolExprXorArgSet_Reduce(d);
    EXPECT_EQ(ops[1], xs[0]);

    BoolExprXorArgSet_Del(a);
    BoolExprXorArgSet_Del(b);
    BoolExprXorArgSet_Del(c);
    BoolExprXorArgSet_Del(d);
}


TEST_F(BoolExprArgSetTest, EqReduce)
{
    struct BoolExprEqArgSet *a = BoolExprEqArgSet_New();
    struct BoolExprEqArgSet *b = BoolExprEqArgSet_New();
    struct BoolExprEqArgSet *c = BoolExprEqArgSet_New();
    struct BoolExprEqArgSet *d = BoolExprEqArgSet_New();
    struct BoolExprEqArgSet *e = BoolExprEqArgSet_New();
    struct BoolExprEqArgSet *f = BoolExprEqArgSet_New();
    struct BoolExprEqArgSet *g = BoolExprEqArgSet_New();

    EXPECT_EQ(BoolExprEqArgSet_Reduce(a), &One);
    BoolExprEqArgSet_Insert(a, &Zero);
    EXPECT_EQ(BoolExprEqArgSet_Reduce(a), &One);
    BoolExprEqArgSet_Insert(a, &One);
    EXPECT_EQ(BoolExprEqArgSet_Reduce(a), &Zero);

    BoolExprEqArgSet_Insert(b, xs[0]);
    BoolExprEqArgSet_Insert(b, xs[1]);
    BoolExprEqArgSet_Insert(b, xs[2]);
    BoolExprEqArgSet_Insert(b, xns[0]);
    EXPECT_EQ(BoolExprEqArgSet_Reduce(b), &Zero);

    BoolExprEqArgSet_Insert(c, &Zero);
    BoolExprEqArgSet_Insert(c, xs[0]);
    ops[0] = BoolExprEqArgSet_Reduce(c);
    EXPECT_EQ(ops[0], xns[0]);

    BoolExprEqArgSet_Insert(d, &One);
    BoolExprEqArgSet_Insert(d, xs[0]);
    ops[1] = BoolExprEqArgSet_Reduce(d);
    EXPECT_EQ(ops[1], xs[0]);

    BoolExprEqArgSet_Insert(e, &Zero);
    BoolExprEqArgSet_Insert(e, xs[0]);
    BoolExprEqArgSet_Insert(e, xs[1]);
    ops[2] = BoolExprEqArgSet_Reduce(e);
    EXPECT_EQ(ops[2]->kind, OP_NOT);
    EXPECT_EQ(ops[2]->data.xs->items[0]->kind, OP_OR);

    BoolExprEqArgSet_Insert(f, &One);
    BoolExprEqArgSet_Insert(f, xs[0]);
    BoolExprEqArgSet_Insert(f, xs[1]);
    ops[3] = BoolExprEqArgSet_Reduce(f);
    EXPECT_EQ(ops[3]->kind, OP_NOT);
    EXPECT_EQ(ops[3]->data.xs->items[0]->kind, OP_AND);

    BoolExprEqArgSet_Insert(g, xs[0]);
    BoolExprEqArgSet_Insert(g, xs[1]);
    ops[4] = BoolExprEqArgSet_Reduce(g);
    EXPECT_EQ(ops[4]->kind, OP_EQ);

    BoolExprEqArgSet_Del(a);
    BoolExprEqArgSet_Del(b);
    BoolExprEqArgSet_Del(c);
    BoolExprEqArgSet_Del(d);
    BoolExprEqArgSet_Del(e);
    BoolExprEqArgSet_Del(f);
    BoolExprEqArgSet_Del(g);
}

