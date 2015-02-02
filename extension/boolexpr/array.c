/*
** Filename: array.c
*/


#include "boolexpr.h"


BoolExprArray *
BoolExprArray_New(size_t length, BoolExpr **items)
{
    BoolExprArray *array;

    array = (BoolExprArray *) malloc(sizeof(BoolExprArray));

    /* LCOV_EXCL_START */
    if (array == NULL)
        return NULL;
    /* LCOV_EXCL_STOP */

    array->items = (BoolExpr **) malloc(length * sizeof(BoolExpr *));

    /* LCOV_EXCL_START */
    if (array->items == NULL) {
        free(array);
        return NULL;
    }
    /* LCOV_EXCL_STOP */

    array->length = length;

    for (size_t i = 0; i < length; ++i)
        array->items[i] = BoolExpr_IncRef(items[i]);

    return array;
}


void
BoolExprArray_Del(BoolExprArray *array)
{
    for (size_t i = 0; i < array->length; ++i)
        BoolExpr_DecRef(array->items[i]);

    free(array->items);
    free(array);
}


bool
BoolExprArray_Equal(BoolExprArray *self, BoolExprArray *other)
{
    if (self->length != other->length)
        return false;

    for (size_t i = 0; i < self->length; ++i)
        if (self->items[i] != other->items[i])
            return false;

    return true;
}

