/*
** Filename: boolexprtest.hpp
*/


#include <gtest/gtest.h>

#include "boolexpr.h"


/*
** Return true if two expressions are similar.
**
** This is just a cheap way to check expression transformations against
** expected values.
** It does not check function equality or isomorphism.
*/
bool Similar(BoolExpr * const, BoolExpr * const);


class BoolExpr_Test: public ::testing::Test
{

protected:

    virtual void SetUp();
    virtual void TearDown();

    static const int N = 1024;

    struct BX_Vector *lits;

    BoolExpr *xns[N];
    BoolExpr *xs[N];

    BoolExpr *ops[N];

    BoolExpr *exps[N];
};

