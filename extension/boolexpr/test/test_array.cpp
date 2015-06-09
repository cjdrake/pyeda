/*
** Filename: test_array.cpp
**
** Test the BX_Array data type.
*/


#include "boolexprtest.hpp"


class BX_Array_Test: public BoolExpr_Test {};


TEST_F(BX_Array_Test, Basic)
{
    struct BoolExpr *items[] = {xs[0], xs[1], xs[2], xs[3]};

    struct BX_Array *array = BX_Array_New(4, items);

    // BX_Array_Length
    EXPECT_EQ(array->length, 4);

    // BX_Array_GetItem
    for (int i = 0; i < array->length; ++i)
        EXPECT_EQ(array->items[i], xs[i]);

    BX_Array_Del(array);
}


TEST_F(BX_Array_Test, Equal)
{
    struct BoolExpr *itemsA[] = {xs[0], xs[1], xs[2], xs[3]};
    struct BoolExpr *itemsB[] = {xs[0], xs[1], xs[2], xs[3]};

    struct BX_Array *a = BX_Array_New(4, itemsA);
    struct BX_Array *b = BX_Array_New(4, itemsB);

    EXPECT_TRUE(BX_Array_Equal(a, b));

    BX_Array_Del(a);
    BX_Array_Del(b);
}


TEST_F(BX_Array_Test, NotEqual)
{
    struct BoolExpr *itemsA[] = {xs[0], xs[1], xs[2], xs[3]};
    struct BoolExpr *itemsB[] = {xs[0], xs[1], xs[3], xs[2]};
    struct BoolExpr *itemsC[] = {xs[0], xs[1]};

    struct BX_Array *a = BX_Array_New(4, itemsA);
    struct BX_Array *b = BX_Array_New(4, itemsB);
    struct BX_Array *c = BX_Array_New(2, itemsC);

    // Unequal items
    EXPECT_FALSE(BX_Array_Equal(a, b));
    // Unequal lengths
    EXPECT_FALSE(BX_Array_Equal(a, c));

    BX_Array_Del(a);
    BX_Array_Del(b);
    BX_Array_Del(c);
}

