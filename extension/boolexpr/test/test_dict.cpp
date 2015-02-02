/*
** Filename: test_dict.cpp
**
** Test the BoolExprDict data type.
*/


#include "boolexprtest.hpp"


class BoolExprDictTest: public BoolExprTest {};


TEST_F(BoolExprDictTest, MinimumSize)
{
    BoolExprDict *dict = BoolExprDict_New(NULL);
    EXPECT_EQ(dict->pridx, 5);

    BoolExprDict_Del(dict);
}


TEST_F(BoolExprDictTest, BasicReadWrite)
{
    BoolExprDict *dict = BoolExprLitMap_New();

    BoolExprDict_Insert(dict, xs[0], &Zero);
    EXPECT_EQ(BoolExprDict_Search(dict, xs[0]), &Zero);
    EXPECT_TRUE(BoolExprDict_Contains(dict, xs[0]));
    EXPECT_EQ(dict->length, 1);

    BoolExprDict_Insert(dict, xs[1], &One);
    EXPECT_EQ(BoolExprDict_Search(dict, xs[1]), &One);
    EXPECT_TRUE(BoolExprDict_Contains(dict, xs[1]));
    EXPECT_EQ(dict->length, 2);

    // Over-write
    BoolExprDict_Insert(dict, xs[0], &One);
    EXPECT_EQ(BoolExprDict_Search(dict, xs[0]), &One);
    EXPECT_EQ(dict->length, 2);

    // Not found
    EXPECT_EQ(BoolExprDict_Search(dict, xs[2]), (BoolExpr *) NULL);
    EXPECT_FALSE(BoolExprDict_Contains(dict, xs[2]));

    BoolExprDict_Del(dict);
}


TEST_F(BoolExprDictTest, Collision)
{
    BoolExprDict *dict = BoolExprVarMap_New();

    // Create a few collisions
    for (int i = 0; i < 64; ++i)
        BoolExprDict_Insert(dict, xs[i], xns[i]);

    // Check Contains/Search on collisions
    for (int i = 0; i < 64; ++i)
        EXPECT_TRUE(BoolExprDict_Contains(dict, xs[i]));
    for (int i = 0; i < 64; ++i)
        EXPECT_EQ(BoolExprDict_Search(dict, xs[i]), xns[i]);

    BoolExprDict_Del(dict);
}


TEST_F(BoolExprDictTest, Resize)
{
    BoolExprDict *dict = BoolExprLitMap_New();

    for (int i = 0; i < 512; ++i)
        BoolExprDict_Insert(dict, xns[i], xs[i]);

    BoolExprDict_Del(dict);
}


TEST_F(BoolExprDictTest, Removal)
{
    BoolExprDict *dict = BoolExprLitMap_New();
    int length = 0;

    for (int i = 0; i < 32; ++i) {
        BoolExprDict_Insert(dict, xns[i], xs[i]);
        EXPECT_EQ(dict->length, ++length);
    }

    // Invalid deletion
    EXPECT_EQ(BoolExprDict_Remove(dict, xs[0]), false);

    for (int i = 0; i < 32; ++i) {
        BoolExprDict_Remove(dict, xns[i]);
        EXPECT_EQ(dict->length, --length);
    }

    for (int i = 0; i < 32; ++i) {
        BoolExprDict_Insert(dict, xns[i], xs[i]);
        EXPECT_EQ(dict->length, ++length);
    }
    for (int i = 0; i < 32; ++i) {
        BoolExprDict_Remove(dict, xns[i]);
        EXPECT_EQ(dict->length, --length);
    }

    for (int i = 0; i < 32; ++i) {
        BoolExprDict_Insert(dict, xns[i], xs[i]);
        EXPECT_EQ(dict->length, ++length);
    }

    for (int i = 0; i < 32; ++i) {
        BoolExprDict_Remove(dict, xns[i]);
        EXPECT_EQ(dict->length, --length);
    }

    BoolExprDict_Del(dict);
}

