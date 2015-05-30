/*
** Filename: test_set.cpp
**
** Test the BoolExprSet data type.
*/


#include "boolexprtest.hpp"


class BoolExprSetTest: public BoolExprTest {};


TEST_F(BoolExprSetTest, MinimumSize)
{
    BoolExprSet *set = BoolExprSet_New();
    EXPECT_EQ(set->_pridx, 4);

    BoolExprSet_Del(set);
}


TEST_F(BoolExprSetTest, BasicReadWrite)
{
    BoolExprSet *set = BoolExprSet_New();

    BoolExprSet_Insert(set, xs[0]);
    EXPECT_TRUE(BoolExprSet_Contains(set, xs[0]));
    EXPECT_EQ(set->length, 1);

    BoolExprSet_Insert(set, xs[1]);
    EXPECT_TRUE(BoolExprSet_Contains(set, xs[1]));
    EXPECT_EQ(set->length, 2);

    // Over-write
    BoolExprSet_Insert(set, xs[0]);
    EXPECT_EQ(set->length, 2);

    // Not found
    EXPECT_FALSE(BoolExprSet_Contains(set, xs[2]));

    BoolExprSet_Del(set);
}


TEST_F(BoolExprSetTest, Iteration)
{
    BoolExprSet *set = BoolExprSet_New();

    bool mark[N];
    for (int i = 0; i < N; ++i) {
        BoolExprSet_Insert(set, xs[i]);
        mark[i-1] = false;
    }

    struct BoolExprSetIter *it;
    for (it = BoolExprSetIter_New(set); !it->done; BoolExprSetIter_Next(it))
        mark[it->item->key->data.lit.uniqid-1] = true;

    // Using Next method should have no effect
    struct BoolExprSetItem *item = it->item;
    BoolExprSetIter_Next(it);
    EXPECT_TRUE(it->done);
    EXPECT_EQ(it->item, item);

    BoolExprSetIter_Del(it);

    for (size_t i = 0; i < N; ++i)
        EXPECT_TRUE(mark[i]);

    BoolExprSet_Del(set);
}


TEST_F(BoolExprSetTest, Collision)
{
    BoolExprSet *set = BoolExprSet_New();

    // Create a few collisions
    for (int i = 0; i < 64; ++i)
        BoolExprSet_Insert(set, xs[i]);

    // Check Contains on collisions
    for (int i = 0; i < 64; ++i)
        EXPECT_TRUE(BoolExprSet_Contains(set, xs[i]));

    BoolExprSet_Del(set);
}


TEST_F(BoolExprSetTest, Resize)
{
    BoolExprSet *set = BoolExprSet_New();

    for (int i = 0; i < 512; ++i)
        BoolExprSet_Insert(set, xns[i]);

    BoolExprSet_Del(set);
}


TEST_F(BoolExprSetTest, Removal)
{
    BoolExprSet *set = BoolExprSet_New();
    int length = 0;

    for (int i = 0; i < 32; ++i) {
        BoolExprSet_Insert(set, xns[i]);
        EXPECT_EQ(set->length, ++length);
    }

    // Invalid deletion
    EXPECT_EQ(BoolExprSet_Remove(set, xs[0]), false);

    for (int i = 0; i < 32; ++i) {
        BoolExprSet_Remove(set, xns[i]);
        EXPECT_EQ(set->length, --length);
    }

    for (int i = 0; i < 32; ++i) {
        BoolExprSet_Insert(set, xns[i]);
        EXPECT_EQ(set->length, ++length);
    }
    for (int i = 0; i < 32; ++i) {
        BoolExprSet_Remove(set, xns[i]);
        EXPECT_EQ(set->length, --length);
    }

    for (int i = 0; i < 32; ++i) {
        BoolExprSet_Insert(set, xns[i]);
        EXPECT_EQ(set->length, ++length);
    }
    for (int i = 0; i < 32; ++i) {
        BoolExprSet_Remove(set, xns[i]);
        EXPECT_EQ(set->length, --length);
    }

    BoolExprSet_Del(set);
}


TEST_F(BoolExprSetTest, Comparison)
{
    BoolExprSet *A = BoolExprSet_New();
    BoolExprSet *B = BoolExprSet_New();
    BoolExprSet *C = BoolExprSet_New();
    BoolExprSet *D = BoolExprSet_New();
    BoolExprSet *E = BoolExprSet_New();
    BoolExprSet *F = BoolExprSet_New();

    BoolExprSet_Insert(A, xs[0]);
    BoolExprSet_Insert(A, xs[1]);
    BoolExprSet_Insert(A, xs[2]);

    // equal to A
    BoolExprSet_Insert(B, xs[0]);
    BoolExprSet_Insert(B, xs[1]);
    BoolExprSet_Insert(B, xs[2]);

    // fully contained by A
    BoolExprSet_Insert(C, xs[0]);
    BoolExprSet_Insert(C, xs[1]);

    // partially contained by A
    BoolExprSet_Insert(D, xs[2]);
    BoolExprSet_Insert(D, xs[3]);

    // disjoint with A
    BoolExprSet_Insert(E, xs[3]);
    BoolExprSet_Insert(E, xs[4]);

    // disjoint with A
    BoolExprSet_Insert(F, xs[3]);
    BoolExprSet_Insert(F, xs[4]);
    BoolExprSet_Insert(F, xs[5]);
    BoolExprSet_Insert(F, xs[6]);

    EXPECT_TRUE (BoolExprSet_EQ (A, B));
    EXPECT_FALSE(BoolExprSet_NE (A, B));
    EXPECT_FALSE(BoolExprSet_LT (A, B));
    EXPECT_TRUE (BoolExprSet_LTE(A, B));
    EXPECT_FALSE(BoolExprSet_GT (A, B));
    EXPECT_TRUE (BoolExprSet_GTE(A, B));

    EXPECT_FALSE(BoolExprSet_EQ (A, C));
    EXPECT_TRUE (BoolExprSet_NE (A, C));
    EXPECT_FALSE(BoolExprSet_LT (A, C));
    EXPECT_FALSE(BoolExprSet_LTE(A, C));
    EXPECT_TRUE (BoolExprSet_GT (A, C));
    EXPECT_TRUE (BoolExprSet_GTE(A, C));

    EXPECT_FALSE(BoolExprSet_EQ (A, D));
    EXPECT_TRUE (BoolExprSet_NE (A, D));
    EXPECT_FALSE(BoolExprSet_LT (A, D));
    EXPECT_FALSE(BoolExprSet_LTE(A, D));
    EXPECT_FALSE(BoolExprSet_GT (A, D));
    EXPECT_FALSE(BoolExprSet_GTE(A, D));

    EXPECT_FALSE(BoolExprSet_EQ (A, E));
    EXPECT_TRUE (BoolExprSet_NE (A, E));
    EXPECT_FALSE(BoolExprSet_LT (A, E));
    EXPECT_FALSE(BoolExprSet_LTE(A, E));
    EXPECT_FALSE(BoolExprSet_GT (A, E));
    EXPECT_FALSE(BoolExprSet_GTE(A, E));

    EXPECT_FALSE(BoolExprSet_EQ (A, F));
    EXPECT_TRUE (BoolExprSet_NE (A, F));
    EXPECT_FALSE(BoolExprSet_LT (A, F));
    EXPECT_FALSE(BoolExprSet_LTE(A, F));
    EXPECT_FALSE(BoolExprSet_GT (A, F));
    EXPECT_FALSE(BoolExprSet_GTE(A, F));

    BoolExprSet_Del(A);
    BoolExprSet_Del(B);
    BoolExprSet_Del(C);
    BoolExprSet_Del(D);
    BoolExprSet_Del(E);
    BoolExprSet_Del(F);
}


TEST_F(BoolExprSetTest, Clear)
{
    BoolExprSet *a = BoolExprSet_New();

    BoolExprSet_Insert(a, xns[0]);
    BoolExprSet_Insert(a, xs[1]);
    BoolExprSet_Insert(a, xns[2]);
    BoolExprSet_Insert(a, xs[3]);

    ASSERT_EQ(a->length, 4);
    BoolExprSet_Clear(a);
    ASSERT_EQ(a->length, 0);

    BoolExprSet_Del(a);
}

