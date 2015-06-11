/*
** Filename: boolexprtest.cpp
**
** Entry point for all unit tests.
*/


#include "boolexprtest.hpp"


bool
Similar(BoolExpr * const self, BoolExpr * const other)
{
    if (self->kind != other->kind)
        return false;

    if (BX_IS_CONST(self)) {
        return true;
    }
    else if (BX_IS_LIT(self)) {
        return (self->data.lit.lits == other->data.lit.lits) &&
               (self->data.lit.uniqid == other->data.lit.uniqid);
    }
    else {
        if (self->data.xs->length == other->data.xs->length) {
            for (size_t i = 0; i < self->data.xs->length; ++i) {
                if (!Similar(self->data.xs->items[i],
                                other->data.xs->items[i]))
                    return false;
            }
            return true;
        }
        else {
            return false;
        }
    }
}


void
BoolExpr_Test::SetUp()
{
    lits = BX_Vector_New();

    // Initialize local literals
    for (int i = 0; i < N; ++i) {
        long uniqid = (long) (i + 1);
        xns[i] = BX_Literal(lits, -uniqid);
        xs[i] = BX_Literal(lits, uniqid);
    }

    // Initialize scratchpad operators
    for (int i = 0; i < N; ++i)
        ops[i] = (BoolExpr *) NULL;

    // Initialize expected operators
    for (int i = 0; i < N; ++i)
        exps[i] = (BoolExpr *) NULL;
}


void
BoolExpr_Test::TearDown()
{
    // Clear local literals
    for (int i = 0; i < N; ++i) {
        BX_DecRef(xns[i]);
        BX_DecRef(xs[i]);
    }
    BX_Vector_Del(lits);

    // Clear scratchpad operators
    for (int i = 0; i < N; ++i) {
        if (ops[i] != (BoolExpr *) NULL)
            BX_DecRef(ops[i]);
    }

    // Clear expected operators
    for (int i = 0; i < N; ++i) {
        if (exps[i] != (BoolExpr *) NULL)
            BX_DecRef(exps[i]);
    }
}

