/*
** Filename: test_set.cpp
**
** Test the BoolExprSet data type.
*/


#include "boolexprtest.hpp"


class BoolExprSetTest: public BoolExprTest {};


TEST_F(BoolExprSetTest, MinimumSize)
{
    BoolExprSet *set = BoolExprSet_New(NULL);
    EXPECT_EQ(set->pridx, 5);

    BoolExprSet_Del(set);
}


TEST_F(BoolExprSetTest, BasicReadWrite)
{
    BoolExprSet *set = BoolExprLitSet_New();

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


TEST_F(BoolExprSetTest, Collision)
{
    BoolExprSet *set = BoolExprVarSet_New();

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
    BoolExprSet *set = BoolExprLitSet_New();

    for (int i = 0; i < 512; ++i)
        BoolExprSet_Insert(set, xns[i]);

    BoolExprSet_Del(set);
}


TEST_F(BoolExprSetTest, Removal)
{
    BoolExprSet *set = BoolExprLitSet_New();
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

