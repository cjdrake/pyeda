/*
** Filename: test_array2.cpp
**
** Test the BoolExprArray2 data type.
*/


#include "boolexprtest.hpp"


class BoolExprArray2Test: public BoolExprTest {};


TEST_F(BoolExprArray2Test, Basic)
{
    BoolExpr *A[] = {xs[0]};
    BoolExpr *B[] = {xs[1], xs[2]};
    BoolExpr *C[] = {xs[3], xs[4], xs[5]};

    size_t lengths[] = {1, 2, 3};
    BoolExpr **items[] = {A, B, C};

    BoolExprArray2 *array2 = BoolExprArray2_New(3, lengths, items);

    // BoolExprArray2_Length
    EXPECT_EQ(array2->length, 3);

    // BoolExprArray2_GetItem
    for (int i = 0; i < array2->length; ++i)
        for (int j = 0; j < array2->items[i]->length; ++j)
            EXPECT_EQ(array2->items[i]->items[j], items[i][j]);

    BoolExprArray2_Del(array2);
}


TEST_F(BoolExprArray2Test, Equal)
{
    BoolExpr *A[] = {xs[0]};
    BoolExpr *B[] = {xs[1], xs[2]};
    BoolExpr *C[] = {xs[3], xs[4], xs[5]};

    size_t lengths[] = {1, 2, 3};
    BoolExpr **itemsA[] = {A, B, C};
    BoolExpr **itemsB[] = {A, B, C};

    BoolExprArray2 *a = BoolExprArray2_New(3, lengths, itemsA);
    BoolExprArray2 *b = BoolExprArray2_New(3, lengths, itemsB);

    EXPECT_TRUE(BoolExprArray2_Equal(a, b));

    BoolExprArray2_Del(a);
    BoolExprArray2_Del(b);
}


TEST_F(BoolExprArray2Test, NotEqual)
{
    BoolExpr *A[] = {xs[0]};
    BoolExpr *B[] = {xs[1], xs[2]};
    BoolExpr *C[] = {xs[3], xs[4], xs[5]};
    BoolExpr *D[] = {xs[6], xs[7], xs[8]};

    size_t lengthsA[] = {1, 2, 3};
    BoolExpr **itemsA[] = {A, B, C};

    size_t lengthsB[] = {1, 2, 3};
    BoolExpr **itemsB[] = {A, B, D};

    size_t lengthsC[] = {1, 2};
    BoolExpr **itemsC[] = {A, B};

    BoolExprArray2 *a = BoolExprArray2_New(3, lengthsA, itemsA);
    BoolExprArray2 *b = BoolExprArray2_New(3, lengthsB, itemsB);
    BoolExprArray2 *c = BoolExprArray2_New(2, lengthsC, itemsC);

    // Unequal items
    EXPECT_FALSE(BoolExprArray2_Equal(a, b));
    // Unequal lengths
    EXPECT_FALSE(BoolExprArray2_Equal(a, c));

    BoolExprArray2_Del(a);
    BoolExprArray2_Del(b);
    BoolExprArray2_Del(c);
}


TEST_F(BoolExprArray2Test, Product)
{
    BoolExpr *A[] = {xs[0]};
    BoolExpr *B[] = {xs[1], xs[2]};
    BoolExpr *C[] = {xs[3], xs[4], xs[5]};

    size_t lengths[] = {1, 2, 3};
    BoolExpr **items[] = {A, B, C};

    BoolExprArray2 *array2 = BoolExprArray2_New(3, lengths, items);

    BoolExprArray *prod = BoolExprArray2_Product(array2, OP_OR);

    EXPECT_EQ(prod->length, 1 * 2 * 3);

    for (int i = 0; i < prod->length; ++i)
        EXPECT_EQ(prod->items[i]->type, OP_OR);

    // [x0+x1+x3, x0+x2+x3, x0+x1+x4, x0+x2+x4, x0+x1+x5, x0+x2+x5]
    int p[6][3] = {{0, 1, 3}, {0, 2, 3}, {0, 1, 4},
                   {0, 2, 4}, {0, 1, 5}, {0, 2, 5}};

    for (int i = 0; i < 6; ++i) {
        EXPECT_EQ(prod->items[i]->data.xs->items[1]->data.xs->items[1]->data.xs->items[1], &Zero);
        EXPECT_EQ(prod->items[i]->data.xs->items[1]->data.xs->items[1]->data.xs->items[0], xs[p[i][0]]);
        EXPECT_EQ(prod->items[i]->data.xs->items[1]->data.xs->items[0], xs[p[i][1]]);
        EXPECT_EQ(prod->items[i]->data.xs->items[0], xs[p[i][2]]);
    }

    BoolExprArray_Del(prod);

    BoolExprArray2_Del(array2);
}


TEST_F(BoolExprArray2Test, Identity)
{
    size_t lengths[] = {};
    BoolExpr **items[] = {};
    BoolExprArray2 *array2 = BoolExprArray2_New(0, lengths, items);

    BoolExprArray *prod = BoolExprArray2_Product(array2, OP_AND);

    EXPECT_EQ(prod->length, 1);
    // [1]
    EXPECT_EQ(prod->items[0], &One);

    BoolExprArray_Del(prod);

    BoolExprArray2_Del(array2);
}

