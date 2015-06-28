/*
** Filename: test_dict.cpp
**
** Test the BX_Dict data type.
*/


#include "boolexprtest.hpp"


class BX_Dict_Test: public BoolExpr_Test {};


TEST_F(BX_Dict_Test, MinimumSize)
{
    struct BX_Dict *dict = BX_Dict_New();
    EXPECT_EQ(dict->_pridx, 4);

    BX_Dict_Del(dict);
}


TEST_F(BX_Dict_Test, BasicReadWrite)
{
    struct BX_Dict *dict = BX_Dict_New();

    BX_Dict_Insert(dict, xs[0], &BX_Zero);
    EXPECT_EQ(BX_Dict_Search(dict, xs[0]), &BX_Zero);
    EXPECT_TRUE(BX_Dict_Contains(dict, xs[0]));
    EXPECT_EQ(dict->length, 1);

    BX_Dict_Insert(dict, xs[1], &BX_One);
    EXPECT_EQ(BX_Dict_Search(dict, xs[1]), &BX_One);
    EXPECT_TRUE(BX_Dict_Contains(dict, xs[1]));
    EXPECT_EQ(dict->length, 2);

    // Over-write
    BX_Dict_Insert(dict, xs[0], &BX_One);
    EXPECT_EQ(BX_Dict_Search(dict, xs[0]), &BX_One);
    EXPECT_EQ(dict->length, 2);

    // Not found
    EXPECT_EQ(BX_Dict_Search(dict, xs[2]), (BoolExpr *) NULL);
    EXPECT_FALSE(BX_Dict_Contains(dict, xs[2]));

    BX_Dict_Del(dict);
}


TEST_F(BX_Dict_Test, Iteration)
{
    struct BX_Dict *dict = BX_Dict_New();

    bool mark[N];
    for (int i = 0; i < N; ++i) {
        BX_Dict_Insert(dict, xs[i], xns[i]);
        mark[i-1] = false;
    }

    struct BX_DictIter it;
    for (BX_DictIter_Init(&it, dict); !it.done; BX_DictIter_Next(&it))
        mark[it.item->key->data.lit.uniqid-1] = true;

    // Using Next method should have no effect
    struct BX_DictItem *prev_item = it.item;
    BX_DictIter_Next(&it);
    EXPECT_TRUE(it.done);
    EXPECT_EQ(it.item, prev_item);

    for (size_t i = 0; i < N; ++i)
        EXPECT_TRUE(mark[i]);

    BX_Dict_Del(dict);
}


TEST_F(BX_Dict_Test, Collision)
{
    struct BX_Dict *dict = BX_Dict_New();

    // Create a few collisions
    for (int i = 0; i < 64; ++i)
        BX_Dict_Insert(dict, xs[i], xns[i]);

    // Check Contains/Search on collisions
    for (int i = 0; i < 64; ++i)
        EXPECT_TRUE(BX_Dict_Contains(dict, xs[i]));
    for (int i = 0; i < 64; ++i)
        EXPECT_EQ(BX_Dict_Search(dict, xs[i]), xns[i]);

    BX_Dict_Del(dict);
}


TEST_F(BX_Dict_Test, Resize)
{
    struct BX_Dict *dict = BX_Dict_New();

    for (int i = 0; i < 512; ++i)
        BX_Dict_Insert(dict, xns[i], xs[i]);

    BX_Dict_Del(dict);
}


TEST_F(BX_Dict_Test, Removal)
{
    struct BX_Dict *dict = BX_Dict_New();
    int length = 0;

    for (int i = 0; i < 32; ++i) {
        BX_Dict_Insert(dict, xns[i], xs[i]);
        EXPECT_EQ(dict->length, ++length);
    }

    // Invalid deletion
    EXPECT_EQ(BX_Dict_Remove(dict, xs[0]), false);

    for (int i = 0; i < 32; ++i) {
        BX_Dict_Remove(dict, xns[i]);
        EXPECT_EQ(dict->length, --length);
    }

    for (int i = 0; i < 32; ++i) {
        BX_Dict_Insert(dict, xns[i], xs[i]);
        EXPECT_EQ(dict->length, ++length);
    }
    for (int i = 0; i < 32; ++i) {
        BX_Dict_Remove(dict, xns[i]);
        EXPECT_EQ(dict->length, --length);
    }

    for (int i = 0; i < 32; ++i) {
        BX_Dict_Insert(dict, xns[i], xs[i]);
        EXPECT_EQ(dict->length, ++length);
    }

    for (int i = 0; i < 32; ++i) {
        BX_Dict_Remove(dict, xns[i]);
        EXPECT_EQ(dict->length, --length);
    }

    BX_Dict_Del(dict);
}


TEST_F(BX_Dict_Test, Clear)
{
    struct BX_Dict *dict = BX_Dict_New();
    int length = 0;

    for (int i = 0; i < 32; ++i) {
        BX_Dict_Insert(dict, xns[i], xs[i]);
        EXPECT_EQ(dict->length, ++length);
    }

    BX_Dict_Clear(dict);
    EXPECT_EQ(dict->length, 0);

    BX_Dict_Del(dict);
}


TEST_F(BX_Dict_Test, Equal)
{
    struct BX_Dict *A = BX_Dict_New();
    struct BX_Dict *B = BX_Dict_New();

    for (size_t i = 0; i < 8; ++i) {
        BX_Dict_Insert(A, xs[i], xns[i]);
        BX_Dict_Insert(B, xs[i], xns[i]);
    }

    EXPECT_TRUE(BX_Dict_Equal(A, B));

    BX_Dict_Remove(B, xs[4]);

    EXPECT_FALSE(BX_Dict_Equal(A, B));

    BX_Dict_Remove(A, xs[5]);

    EXPECT_FALSE(BX_Dict_Equal(A, B));

    BX_Dict_Del(A);
    BX_Dict_Del(B);
}


TEST_F(BX_Dict_Test, Update)
{
    struct BX_Dict *a = BX_Dict_New();
    struct BX_Dict *b = BX_Dict_New();
    struct BX_Dict *c = BX_Dict_New();

    BX_Dict_Insert(a, xs[0], xns[0]);
    BX_Dict_Insert(a, xs[1], xns[1]);
    BX_Dict_Insert(a, xs[2], xns[2]);

    BX_Dict_Insert(b, xs[3], xns[3]);
    BX_Dict_Insert(b, xs[4], xns[4]);
    BX_Dict_Insert(b, xs[5], xns[5]);

    for (int i = 0; i < 6; ++i)
        BX_Dict_Insert(c, xs[i], xns[i]);

    BX_Dict_Update(a, b);
    ASSERT_TRUE(BX_Dict_Equal(a, c));

    BX_Dict_Del(a);
    BX_Dict_Del(b);
    BX_Dict_Del(c);
}
