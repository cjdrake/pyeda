/*
** Filename: test_vector.cpp
**
** Test the BX_Vector data type.
*/


#include "boolexprtest.hpp"


class BX_Vector_Test: public BoolExpr_Test {};


TEST_F(BX_Vector_Test, Vector)
{
    struct BX_Vector *vec;

    // Initial length=0, capacity=64
    vec = BX_Vector_New();
    EXPECT_EQ(vec->length, 0);
    EXPECT_EQ(vec->capacity, 64);

    // Resize a couple times
    for (int i = 0; i < N; ++i) {
        BX_Vector_Append(vec, xns[i]);
        BX_Vector_Append(vec, xs[i]);
    }
    EXPECT_EQ(vec->length, 2*N);
    EXPECT_GE(vec->capacity, 2*N);

    BX_Vector_Del(vec);
}

