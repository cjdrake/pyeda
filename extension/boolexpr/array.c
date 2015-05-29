/*
** Filename: array.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


struct BoolExprArray *
BoolExprArray_New(size_t length, struct BoolExpr **items)
{
    struct BoolExprArray *array;

    array = (struct BoolExprArray *) malloc(sizeof(struct BoolExprArray));
    if (array == NULL)
        return NULL; // LCOV_EXCL_LINE

    array->items = (struct BoolExpr **) malloc(length * sizeof(struct BoolExpr *));
    if (array->items == NULL) {
        free(array); // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    array->length = length;

    for (size_t i = 0; i < length; ++i)
        array->items[i] = BoolExpr_IncRef(items[i]);

    return array;
}


void
BoolExprArray_Del(struct BoolExprArray *array)
{
    for (size_t i = 0; i < array->length; ++i)
        BoolExpr_DecRef(array->items[i]);

    free(array->items);
    free(array);
}


bool
BoolExprArray_Equal(struct BoolExprArray *self, struct BoolExprArray *other)
{
    if (self->length != other->length)
        return false;

    for (size_t i = 0; i < self->length; ++i) {
        if (self->items[i] != other->items[i])
            return false;
    }

    return true;
}

