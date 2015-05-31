/*
** Filename: array.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


struct BoolExprArray *
_bx_array_from(size_t length, struct BoolExpr **items)
{
    struct BoolExprArray *array;

    array = malloc(sizeof(struct BoolExprArray));
    if (array == NULL)
        return NULL; // LCOV_EXCL_LINE

    array->length = length;
    array->items = items;

    for (size_t i = 0; i < length; ++i)
        BoolExpr_IncRef(array->items[i]);

    return array;
}


struct BoolExprArray *
BoolExprArray_New(size_t length, struct BoolExpr **items)
{
    struct BoolExpr **items_copy;

    items_copy = malloc(length * sizeof(struct BoolExpr *));
    if (items_copy == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0; i < length; ++i)
        items_copy[i] = items[i];

    return _bx_array_from(length, items_copy);
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

