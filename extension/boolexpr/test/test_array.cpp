/*
** Filename: test_array.cpp
**
** Test the BoolExprArray data type.
*/


#include "boolexprtest.hpp"


class BoolExprArrayTest: public BoolExprTest {};


TEST_F(BoolExprArrayTest, Basic)
{
    BoolExpr *items[] = {xs[0], xs[1], xs[2], xs[3]};

    BoolExprArray *array = BoolExprArray_New(4, items);

    // BoolExprArray_Length
    EXPECT_EQ(array->length, 4);

    // BoolExprArray_GetItem
    for (int i = 0; i < array->length; ++i)
        EXPECT_EQ(array->items[i], xs[i]);

    BoolExprArray_Del(array);
}


TEST_F(BoolExprArrayTest, Equal)
{
    BoolExpr *itemsA[] = {xs[0], xs[1], xs[2], xs[3]};
    BoolExpr *itemsB[] = {xs[0], xs[1], xs[2], xs[3]};

    BoolExprArray *a = BoolExprArray_New(4, itemsA);
    BoolExprArray *b = BoolExprArray_New(4, itemsB);

    EXPECT_TRUE(BoolExprArray_Equal(a, b));

    BoolExprArray_Del(a);
    BoolExprArray_Del(b);
}


TEST_F(BoolExprArrayTest, NotEqual)
{
    BoolExpr *itemsA[] = {xs[0], xs[1], xs[2], xs[3]};
    BoolExpr *itemsB[] = {xs[0], xs[1], xs[3], xs[2]};
    BoolExpr *itemsC[] = {xs[0], xs[1]};

    BoolExprArray *a = BoolExprArray_New(4, itemsA);
    BoolExprArray *b = BoolExprArray_New(4, itemsB);
    BoolExprArray *c = BoolExprArray_New(2, itemsC);

    // Unequal items
    EXPECT_FALSE(BoolExprArray_Equal(a, b));
    // Unequal lengths
    EXPECT_FALSE(BoolExprArray_Equal(a, c));

    BoolExprArray_Del(a);
    BoolExprArray_Del(b);
    BoolExprArray_Del(c);
}

