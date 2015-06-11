/*
** Filename: test_product.cpp
**
** Test BoolExpr cross products.
*/


#include "boolexprtest.hpp"


class BX_Product_Test: public BoolExpr_Test {};


TEST_F(BX_Product_Test, Product)
{
    struct BoolExpr *A[] = {xs[0]};
    struct BoolExpr *B[] = {xs[1], xs[2]};
    struct BoolExpr *C[] = {xs[3], xs[4], xs[5]};

    struct BX_Array *arrays[3];

    arrays[0] = BX_Array_New(1, A);
    arrays[1] = BX_Array_New(2, B);
    arrays[2] = BX_Array_New(3, C);

    struct BX_Array *prod = BX_Product(BX_OP_OR, 3, arrays);

    EXPECT_EQ(prod->length, 1 * 2 * 3);

    for (int i = 0; i < prod->length; ++i)
        EXPECT_EQ(prod->items[i]->kind, BX_OP_OR);

    // [x0+x1+x3, x0+x2+x3, x0+x1+x4, x0+x2+x4, x0+x1+x5, x0+x2+x5]
    int p[6][3] = {
        {0, 1, 3}, {0, 2, 3}, {0, 1, 4},
        {0, 2, 4}, {0, 1, 5}, {0, 2, 5}
    };

    for (int i = 0; i < 6; ++i) {
        EXPECT_EQ(prod->items[i]->data.xs->items[1]->data.xs->items[1]->data.xs->items[1], &BX_Zero);
        EXPECT_EQ(prod->items[i]->data.xs->items[1]->data.xs->items[1]->data.xs->items[0], xs[p[i][0]]);
        EXPECT_EQ(prod->items[i]->data.xs->items[1]->data.xs->items[0], xs[p[i][1]]);
        EXPECT_EQ(prod->items[i]->data.xs->items[0], xs[p[i][2]]);
    }

    BX_Array_Del(prod);

    for (int i = 0; i < 3; ++i)
        BX_Array_Del(arrays[i]);
}


TEST_F(BX_Product_Test, Identity)
{
    struct BX_Array **arrays;

    struct BX_Array *prod_and = BX_Product(BX_OP_AND, 0, arrays);

    EXPECT_EQ(prod_and->length, 1);
    EXPECT_EQ(prod_and->items[0], &BX_One);

    BX_Array_Del(prod_and);

    struct BX_Array *prod_or = BX_Product(BX_OP_OR, 0, arrays);

    EXPECT_EQ(prod_or->length, 1);
    EXPECT_EQ(prod_or->items[0], &BX_Zero);

    BX_Array_Del(prod_or);
}

