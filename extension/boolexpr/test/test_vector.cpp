/*
** Filename: test_vector.cpp
**
** Test the BoolExprVector data type.
*/


#include "boolexprtest.hpp"


class BoolExprVectorTest: public BoolExprTest {};


TEST_F(BoolExprVectorTest, Vector)
{
    BoolExprVector *vec;

    // Initial length=0, capacity=64
    vec = BoolExprVector_New();
    EXPECT_EQ(vec->length, 0);
    EXPECT_EQ(vec->capacity, 64);

    // Resize a couple times
    for (int i = 0; i < N; ++i) {
        BoolExprVector_Append(vec, xns[i]);
        BoolExprVector_Append(vec, xs[i]);
    }
    EXPECT_EQ(vec->length, 2*N);
    EXPECT_GE(vec->capacity, 2*N);

    BoolExprVector_Del(vec);
}

