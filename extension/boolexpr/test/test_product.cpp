/*
** Filename: test_product.cpp
**
** Test BoolExpr cross products.
*/


#include "boolexprtest.hpp"


class BoolExprProductTest: public BoolExprTest {};


TEST_F(BoolExprProductTest, Product)
{
    struct BoolExpr *A[] = {xs[0]};
    struct BoolExpr *B[] = {xs[1], xs[2]};
    struct BoolExpr *C[] = {xs[3], xs[4], xs[5]};

    struct BoolExprArray *arrays[3];

    arrays[0] = BoolExprArray_New(1, A);
    arrays[1] = BoolExprArray_New(2, B);
    arrays[2] = BoolExprArray_New(3, C);

    struct BoolExprArray *prod = BoolExpr_Product(OP_OR, 3, arrays);

    EXPECT_EQ(prod->length, 1 * 2 * 3);

    for (int i = 0; i < prod->length; ++i)
        EXPECT_EQ(prod->items[i]->kind, OP_OR);

    // [x0+x1+x3, x0+x2+x3, x0+x1+x4, x0+x2+x4, x0+x1+x5, x0+x2+x5]
    int p[6][3] = {
        {0, 1, 3}, {0, 2, 3}, {0, 1, 4},
        {0, 2, 4}, {0, 1, 5}, {0, 2, 5}
    };

    for (int i = 0; i < 6; ++i) {
        EXPECT_EQ(prod->items[i]->data.xs->items[1]->data.xs->items[1]->data.xs->items[1], &Zero);
        EXPECT_EQ(prod->items[i]->data.xs->items[1]->data.xs->items[1]->data.xs->items[0], xs[p[i][0]]);
        EXPECT_EQ(prod->items[i]->data.xs->items[1]->data.xs->items[0], xs[p[i][1]]);
        EXPECT_EQ(prod->items[i]->data.xs->items[0], xs[p[i][2]]);
    }

    BoolExprArray_Del(prod);

    for (int i = 0; i < 3; ++i)
        BoolExprArray_Del(arrays[i]);
}


TEST_F(BoolExprProductTest, Identity)
{
    struct BoolExprArray **arrays;

    struct BoolExprArray *prod_and = BoolExpr_Product(OP_AND, 0, arrays);

    EXPECT_EQ(prod_and->length, 1);
    EXPECT_EQ(prod_and->items[0], &One);

    BoolExprArray_Del(prod_and);

    struct BoolExprArray *prod_or = BoolExpr_Product(OP_OR, 0, arrays);

    EXPECT_EQ(prod_or->length, 1);
    EXPECT_EQ(prod_or->items[0], &Zero);

    BoolExprArray_Del(prod_or);
}

