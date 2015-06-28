/*
** Filename: test_set.cpp
**
** Test the BX_Set data type.
*/


#include "boolexprtest.hpp"


class BX_Set_Test: public BoolExpr_Test {};


TEST_F(BX_Set_Test, MinimumSize)
{
    struct BX_Set *set = BX_Set_New();
    EXPECT_EQ(set->_pridx, 4);

    BX_Set_Del(set);
}


TEST_F(BX_Set_Test, BasicReadWrite)
{
    struct BX_Set *set = BX_Set_New();

    BX_Set_Insert(set, xs[0]);
    EXPECT_TRUE(BX_Set_Contains(set, xs[0]));
    EXPECT_EQ(set->length, 1);

    BX_Set_Insert(set, xs[1]);
    EXPECT_TRUE(BX_Set_Contains(set, xs[1]));
    EXPECT_EQ(set->length, 2);

    // Over-write
    BX_Set_Insert(set, xs[0]);
    EXPECT_EQ(set->length, 2);

    // Not found
    EXPECT_FALSE(BX_Set_Contains(set, xs[2]));

    BX_Set_Del(set);
}


TEST_F(BX_Set_Test, Iteration)
{
    struct BX_Set *set = BX_Set_New();

    bool mark[N];
    for (int i = 0; i < N; ++i) {
        BX_Set_Insert(set, xs[i]);
        mark[i-1] = false;
    }

    struct BX_SetIter it;
    for (BX_SetIter_Init(&it, set); !it.done; BX_SetIter_Next(&it))
        mark[it.item->key->data.lit.uniqid-1] = true;

    // Using Next method should have no effect
    struct BX_SetItem *prev_item = it.item;
    BX_SetIter_Next(&it);
    EXPECT_TRUE(it.done);
    EXPECT_EQ(it.item, prev_item);

    for (size_t i = 0; i < N; ++i)
        EXPECT_TRUE(mark[i]);

    BX_Set_Del(set);
}


TEST_F(BX_Set_Test, Collision)
{
    struct BX_Set *set = BX_Set_New();

    // Create a few collisions
    for (int i = 0; i < 64; ++i)
        BX_Set_Insert(set, xs[i]);

    // Check Contains on collisions
    for (int i = 0; i < 64; ++i)
        EXPECT_TRUE(BX_Set_Contains(set, xs[i]));

    BX_Set_Del(set);
}


TEST_F(BX_Set_Test, Resize)
{
    struct BX_Set *set = BX_Set_New();

    for (int i = 0; i < 512; ++i)
        BX_Set_Insert(set, xns[i]);

    BX_Set_Del(set);
}


TEST_F(BX_Set_Test, Removal)
{
    struct BX_Set *set = BX_Set_New();
    int length = 0;

    for (int i = 0; i < 32; ++i) {
        BX_Set_Insert(set, xns[i]);
        EXPECT_EQ(set->length, ++length);
    }

    // Invalid deletion
    EXPECT_EQ(BX_Set_Remove(set, xs[0]), false);

    for (int i = 0; i < 32; ++i) {
        BX_Set_Remove(set, xns[i]);
        EXPECT_EQ(set->length, --length);
    }

    for (int i = 0; i < 32; ++i) {
        BX_Set_Insert(set, xns[i]);
        EXPECT_EQ(set->length, ++length);
    }
    for (int i = 0; i < 32; ++i) {
        BX_Set_Remove(set, xns[i]);
        EXPECT_EQ(set->length, --length);
    }

    for (int i = 0; i < 32; ++i) {
        BX_Set_Insert(set, xns[i]);
        EXPECT_EQ(set->length, ++length);
    }
    for (int i = 0; i < 32; ++i) {
        BX_Set_Remove(set, xns[i]);
        EXPECT_EQ(set->length, --length);
    }

    BX_Set_Del(set);
}


TEST_F(BX_Set_Test, Comparison)
{
    struct BX_Set *A = BX_Set_New();
    struct BX_Set *B = BX_Set_New();
    struct BX_Set *C = BX_Set_New();
    struct BX_Set *D = BX_Set_New();
    struct BX_Set *E = BX_Set_New();
    struct BX_Set *F = BX_Set_New();

    BX_Set_Insert(A, xs[0]);
    BX_Set_Insert(A, xs[1]);
    BX_Set_Insert(A, xs[2]);

    // equal to A
    BX_Set_Insert(B, xs[0]);
    BX_Set_Insert(B, xs[1]);
    BX_Set_Insert(B, xs[2]);

    // fully contained by A
    BX_Set_Insert(C, xs[0]);
    BX_Set_Insert(C, xs[1]);

    // partially contained by A
    BX_Set_Insert(D, xs[2]);
    BX_Set_Insert(D, xs[3]);

    // disjoint with A
    BX_Set_Insert(E, xs[3]);
    BX_Set_Insert(E, xs[4]);

    // disjoint with A
    BX_Set_Insert(F, xs[3]);
    BX_Set_Insert(F, xs[4]);
    BX_Set_Insert(F, xs[5]);
    BX_Set_Insert(F, xs[6]);

    EXPECT_TRUE (BX_Set_EQ (A, B));
    EXPECT_FALSE(BX_Set_NE (A, B));
    EXPECT_FALSE(BX_Set_LT (A, B));
    EXPECT_TRUE (BX_Set_LTE(A, B));
    EXPECT_FALSE(BX_Set_GT (A, B));
    EXPECT_TRUE (BX_Set_GTE(A, B));

    EXPECT_FALSE(BX_Set_EQ (A, C));
    EXPECT_TRUE (BX_Set_NE (A, C));
    EXPECT_FALSE(BX_Set_LT (A, C));
    EXPECT_FALSE(BX_Set_LTE(A, C));
    EXPECT_TRUE (BX_Set_GT (A, C));
    EXPECT_TRUE (BX_Set_GTE(A, C));

    EXPECT_FALSE(BX_Set_EQ (A, D));
    EXPECT_TRUE (BX_Set_NE (A, D));
    EXPECT_FALSE(BX_Set_LT (A, D));
    EXPECT_FALSE(BX_Set_LTE(A, D));
    EXPECT_FALSE(BX_Set_GT (A, D));
    EXPECT_FALSE(BX_Set_GTE(A, D));

    EXPECT_FALSE(BX_Set_EQ (A, E));
    EXPECT_TRUE (BX_Set_NE (A, E));
    EXPECT_FALSE(BX_Set_LT (A, E));
    EXPECT_FALSE(BX_Set_LTE(A, E));
    EXPECT_FALSE(BX_Set_GT (A, E));
    EXPECT_FALSE(BX_Set_GTE(A, E));

    EXPECT_FALSE(BX_Set_EQ (A, F));
    EXPECT_TRUE (BX_Set_NE (A, F));
    EXPECT_FALSE(BX_Set_LT (A, F));
    EXPECT_FALSE(BX_Set_LTE(A, F));
    EXPECT_FALSE(BX_Set_GT (A, F));
    EXPECT_FALSE(BX_Set_GTE(A, F));

    BX_Set_Del(A);
    BX_Set_Del(B);
    BX_Set_Del(C);
    BX_Set_Del(D);
    BX_Set_Del(E);
    BX_Set_Del(F);
}


TEST_F(BX_Set_Test, Clear)
{
    struct BX_Set *a = BX_Set_New();

    BX_Set_Insert(a, xns[0]);
    BX_Set_Insert(a, xs[1]);
    BX_Set_Insert(a, xns[2]);
    BX_Set_Insert(a, xs[3]);

    ASSERT_EQ(a->length, 4);
    BX_Set_Clear(a);
    ASSERT_EQ(a->length, 0);

    BX_Set_Del(a);
}


TEST_F(BX_Set_Test, Update)
{
    struct BX_Set *a = BX_Set_New();
    struct BX_Set *b = BX_Set_New();
    struct BX_Set *c = BX_Set_New();

    BX_Set_Insert(a, xs[0]);
    BX_Set_Insert(a, xs[1]);
    BX_Set_Insert(a, xs[2]);

    BX_Set_Insert(b, xs[3]);
    BX_Set_Insert(b, xs[4]);
    BX_Set_Insert(b, xs[5]);

    for (int i = 0; i < 6; ++i)
        BX_Set_Insert(c, xs[i]);

    BX_Set_Update(a, b);
    ASSERT_TRUE(BX_Set_EQ(a, c));

    BX_Set_Del(a);
    BX_Set_Del(b);
    BX_Set_Del(c);
}

