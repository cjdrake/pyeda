/*
** Filename: test_argset.cpp
**
** Test the BoolExprArgSet data types.
*/


#include "boolexprtest.hpp"


class BX_ArgSet_Test: public BoolExpr_Test {};


TEST_F(BX_ArgSet_Test, OrBasic)
{
    struct BX_OrAndArgSet *a = BX_OrAndArgSet_New(BX_OP_OR);

    EXPECT_EQ(a->kind, BX_OP_OR);
    EXPECT_TRUE(a->min);
    EXPECT_FALSE(a->max);

    BX_OrAndArgSet_Insert(a, xns[0]);
    EXPECT_FALSE(a->min);
    EXPECT_EQ(a->xs->length, 1);

    BX_OrAndArgSet_Insert(a, &BX_Zero);
    EXPECT_EQ(a->xs->length, 1);

    ops[0] = BX_OrN(2, xs[1], xs[2]);
    ops[1] = BX_OrN(2, xs[3], xs[4]);
    ops[2] = BX_OrN(2, ops[0], ops[1]);
    BX_OrAndArgSet_Insert(a, ops[2]);
    EXPECT_EQ(a->xs->length, 5);

    BX_OrAndArgSet_Insert(a, xs[0]);
    EXPECT_FALSE(a->min);
    EXPECT_TRUE(a->max);
    EXPECT_EQ(a->xs->length, 0);

    BX_OrAndArgSet_Del(a);
}


TEST_F(BX_ArgSet_Test, AndBasic)
{
    struct BX_OrAndArgSet *a = BX_OrAndArgSet_New(BX_OP_AND);

    EXPECT_EQ(a->kind, BX_OP_AND);
    EXPECT_TRUE(a->min);
    EXPECT_FALSE(a->max);

    BX_OrAndArgSet_Insert(a, xns[0]);
    EXPECT_FALSE(a->min);
    EXPECT_EQ(a->xs->length, 1);

    BX_OrAndArgSet_Insert(a, &BX_One);
    EXPECT_EQ(a->xs->length, 1);

    ops[0] = BX_AndN(2, xs[1], xs[2]);
    ops[1] = BX_AndN(2, xs[3], xs[4]);
    ops[2] = BX_AndN(2, ops[0], ops[1]);
    BX_OrAndArgSet_Insert(a, ops[2]);
    EXPECT_EQ(a->xs->length, 5);

    BX_OrAndArgSet_Insert(a, &BX_Zero);
    EXPECT_FALSE(a->min);
    EXPECT_TRUE(a->max);
    EXPECT_EQ(a->xs->length, 0);

    BX_OrAndArgSet_Del(a);
}


TEST_F(BX_ArgSet_Test, XorBasic)
{
    struct BX_XorArgSet *a = BX_XorArgSet_New(true);

    BX_XorArgSet_Insert(a, xs[0]);
    BX_XorArgSet_Insert(a, xs[1]);
    EXPECT_TRUE(a->parity);
    EXPECT_EQ(a->xs->length, 2);

    BX_XorArgSet_Insert(a, &BX_Zero);
    EXPECT_TRUE(a->parity);
    EXPECT_EQ(a->xs->length, 2);

    BX_XorArgSet_Insert(a, &BX_One);
    EXPECT_FALSE(a->parity);
    EXPECT_EQ(a->xs->length, 2);

    ops[0] = BX_XorN(2, xs[2], xs[3]);
    ops[1] = BX_XnorN(2, xs[4], xs[5]);
    ops[2] = BX_XorN(2, ops[0], ops[1]);
    BX_XorArgSet_Insert(a, ops[2]);
    EXPECT_TRUE(a->parity);
    EXPECT_EQ(a->xs->length, 6);

    BX_XorArgSet_Insert(a, xs[0]);
    EXPECT_TRUE(a->parity);
    EXPECT_EQ(a->xs->length, 5);

    BX_XorArgSet_Insert(a, xns[1]);
    EXPECT_FALSE(a->parity);
    EXPECT_EQ(a->xs->length, 4);

    BX_XorArgSet_Del(a);
}


TEST_F(BX_ArgSet_Test, EqBasic)
{
    struct BX_EqArgSet *a = BX_EqArgSet_New();
    struct BX_EqArgSet *b = BX_EqArgSet_New();
    struct BX_EqArgSet *c = BX_EqArgSet_New();

    BX_EqArgSet_Insert(a, xs[0]);
    BX_EqArgSet_Insert(a, xs[1]);
    EXPECT_FALSE(a->zero);
    EXPECT_FALSE(a->one);
    EXPECT_EQ(a->xs->length, 2);

    BX_EqArgSet_Insert(a, &BX_Zero);
    BX_EqArgSet_Insert(a, &BX_One);
    EXPECT_TRUE(a->zero);
    EXPECT_TRUE(a->one);
    EXPECT_EQ(a->xs->length, 0);

    BX_EqArgSet_Insert(a, xs[2]);
    BX_EqArgSet_Insert(a, xs[3]);
    EXPECT_TRUE(a->zero);
    EXPECT_TRUE(a->one);
    EXPECT_EQ(a->xs->length, 0);

    BX_EqArgSet_Insert(b, xs[0]);
    BX_EqArgSet_Insert(b, xs[1]);
    EXPECT_FALSE(b->zero);
    EXPECT_FALSE(b->one);
    EXPECT_EQ(b->xs->length, 2);

    BX_EqArgSet_Insert(b, &BX_One);
    BX_EqArgSet_Insert(b, &BX_Zero);
    EXPECT_TRUE(b->zero);
    EXPECT_TRUE(b->one);
    EXPECT_EQ(b->xs->length, 0);

    BX_EqArgSet_Insert(b, xs[2]);
    BX_EqArgSet_Insert(b, xs[3]);
    EXPECT_TRUE(b->zero);
    EXPECT_TRUE(b->one);
    EXPECT_EQ(b->xs->length, 0);

    BX_EqArgSet_Insert(c, xs[0]);
    BX_EqArgSet_Insert(c, xs[1]);
    BX_EqArgSet_Insert(c, xs[2]);
    EXPECT_FALSE(c->zero);
    EXPECT_FALSE(c->one);
    EXPECT_EQ(c->xs->length, 3);
    BX_EqArgSet_Insert(c, xns[1]);
    EXPECT_TRUE(c->zero);
    EXPECT_TRUE(c->one);
    EXPECT_EQ(c->xs->length, 0);

    BX_EqArgSet_Del(a);
    BX_EqArgSet_Del(b);
    BX_EqArgSet_Del(c);
}


TEST_F(BX_ArgSet_Test, OrReduce)
{
    struct BX_OrAndArgSet *a = BX_OrAndArgSet_New(BX_OP_OR);
    struct BX_OrAndArgSet *b = BX_OrAndArgSet_New(BX_OP_OR);
    struct BX_OrAndArgSet *c = BX_OrAndArgSet_New(BX_OP_OR);
    struct BX_OrAndArgSet *d = BX_OrAndArgSet_New(BX_OP_OR);

    EXPECT_EQ(BX_OrAndArgSet_Reduce(a), &BX_Zero);

    BX_OrAndArgSet_Insert(b, xs[0]);
    BX_OrAndArgSet_Insert(b, xs[1]);
    BX_OrAndArgSet_Insert(b, xs[2]);
    BX_OrAndArgSet_Insert(b, xns[0]);
    EXPECT_EQ(BX_OrAndArgSet_Reduce(b), &BX_One);

    BX_OrAndArgSet_Insert(c, xs[0]);
    BX_OrAndArgSet_Insert(c, xs[0]);
    BX_OrAndArgSet_Insert(c, xs[1]);
    BX_OrAndArgSet_Insert(c, xs[1]);
    ops[0] = BX_OrAndArgSet_Reduce(c);
    EXPECT_EQ(ops[0]->kind, BX_OP_OR);
    EXPECT_EQ(ops[0]->data.xs->length, 2);

    BX_OrAndArgSet_Insert(d, xs[0]);
    ops[1] = BX_OrAndArgSet_Reduce(d);
    EXPECT_EQ(ops[1], xs[0]);

    BX_OrAndArgSet_Del(a);
    BX_OrAndArgSet_Del(b);
    BX_OrAndArgSet_Del(c);
    BX_OrAndArgSet_Del(d);
}


TEST_F(BX_ArgSet_Test, AndReduce)
{
    struct BX_OrAndArgSet *a = BX_OrAndArgSet_New(BX_OP_AND);
    struct BX_OrAndArgSet *b = BX_OrAndArgSet_New(BX_OP_AND);
    struct BX_OrAndArgSet *c = BX_OrAndArgSet_New(BX_OP_AND);

    EXPECT_EQ(BX_OrAndArgSet_Reduce(a), &BX_One);

    BX_OrAndArgSet_Insert(b, xs[0]);
    BX_OrAndArgSet_Insert(b, xs[1]);
    BX_OrAndArgSet_Insert(b, xs[2]);
    BX_OrAndArgSet_Insert(b, xns[0]);
    EXPECT_EQ(BX_OrAndArgSet_Reduce(b), &BX_Zero);

    BX_OrAndArgSet_Insert(c, xs[0]);
    BX_OrAndArgSet_Insert(c, xs[0]);
    BX_OrAndArgSet_Insert(c, xs[1]);
    BX_OrAndArgSet_Insert(c, xs[1]);
    ops[0] = BX_OrAndArgSet_Reduce(c);
    EXPECT_EQ(ops[0]->kind, BX_OP_AND);
    EXPECT_EQ(ops[0]->data.xs->length, 2);

    BX_OrAndArgSet_Del(a);
    BX_OrAndArgSet_Del(b);
    BX_OrAndArgSet_Del(c);
}


TEST_F(BX_ArgSet_Test, XorReduce)
{
    struct BX_XorArgSet *a = BX_XorArgSet_New(true);
    struct BX_XorArgSet *b = BX_XorArgSet_New(false);
    struct BX_XorArgSet *c = BX_XorArgSet_New(true);
    struct BX_XorArgSet *d = BX_XorArgSet_New(true);

    EXPECT_EQ(BX_XorArgSet_Reduce(a), &BX_Zero);
    EXPECT_EQ(BX_XorArgSet_Reduce(b), &BX_One);

    BX_XorArgSet_Insert(c, xs[0]);
    BX_XorArgSet_Insert(c, xs[1]);
    BX_XorArgSet_Insert(c, xs[2]);
    ops[0] = BX_XorArgSet_Reduce(c);
    EXPECT_EQ(ops[0]->kind, BX_OP_XOR);
    EXPECT_EQ(ops[0]->data.xs->length, 3);

    BX_XorArgSet_Insert(d, xs[0]);
    ops[1] = BX_XorArgSet_Reduce(d);
    EXPECT_EQ(ops[1], xs[0]);

    BX_XorArgSet_Del(a);
    BX_XorArgSet_Del(b);
    BX_XorArgSet_Del(c);
    BX_XorArgSet_Del(d);
}


TEST_F(BX_ArgSet_Test, EqReduce)
{
    struct BX_EqArgSet *a = BX_EqArgSet_New();
    struct BX_EqArgSet *b = BX_EqArgSet_New();
    struct BX_EqArgSet *c = BX_EqArgSet_New();
    struct BX_EqArgSet *d = BX_EqArgSet_New();
    struct BX_EqArgSet *e = BX_EqArgSet_New();
    struct BX_EqArgSet *f = BX_EqArgSet_New();
    struct BX_EqArgSet *g = BX_EqArgSet_New();

    EXPECT_EQ(BX_EqArgSet_Reduce(a), &BX_One);
    BX_EqArgSet_Insert(a, &BX_Zero);
    EXPECT_EQ(BX_EqArgSet_Reduce(a), &BX_One);
    BX_EqArgSet_Insert(a, &BX_One);
    EXPECT_EQ(BX_EqArgSet_Reduce(a), &BX_Zero);

    BX_EqArgSet_Insert(b, xs[0]);
    BX_EqArgSet_Insert(b, xs[1]);
    BX_EqArgSet_Insert(b, xs[2]);
    BX_EqArgSet_Insert(b, xns[0]);
    EXPECT_EQ(BX_EqArgSet_Reduce(b), &BX_Zero);

    BX_EqArgSet_Insert(c, &BX_Zero);
    BX_EqArgSet_Insert(c, xs[0]);
    ops[0] = BX_EqArgSet_Reduce(c);
    EXPECT_EQ(ops[0], xns[0]);

    BX_EqArgSet_Insert(d, &BX_One);
    BX_EqArgSet_Insert(d, xs[0]);
    ops[1] = BX_EqArgSet_Reduce(d);
    EXPECT_EQ(ops[1], xs[0]);

    BX_EqArgSet_Insert(e, &BX_Zero);
    BX_EqArgSet_Insert(e, xs[0]);
    BX_EqArgSet_Insert(e, xs[1]);
    ops[2] = BX_EqArgSet_Reduce(e);
    EXPECT_EQ(ops[2]->kind, BX_OP_NOT);
    EXPECT_EQ(ops[2]->data.xs->items[0]->kind, BX_OP_OR);

    BX_EqArgSet_Insert(f, &BX_One);
    BX_EqArgSet_Insert(f, xs[0]);
    BX_EqArgSet_Insert(f, xs[1]);
    ops[3] = BX_EqArgSet_Reduce(f);
    EXPECT_EQ(ops[3]->kind, BX_OP_AND);

    BX_EqArgSet_Insert(g, xs[0]);
    BX_EqArgSet_Insert(g, xs[1]);
    ops[4] = BX_EqArgSet_Reduce(g);
    EXPECT_EQ(ops[4]->kind, BX_OP_EQ);

    BX_EqArgSet_Del(a);
    BX_EqArgSet_Del(b);
    BX_EqArgSet_Del(c);
    BX_EqArgSet_Del(d);
    BX_EqArgSet_Del(e);
    BX_EqArgSet_Del(f);
    BX_EqArgSet_Del(g);
}

