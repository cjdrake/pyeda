/*
** Filename: array.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


struct BX_Array *
_bx_array_from(size_t length, struct BoolExpr **exprs)
{
    struct BX_Array *array;

    array = malloc(sizeof(struct BX_Array));
    if (array == NULL)
        return NULL; // LCOV_EXCL_LINE

    array->length = length;
    array->items = exprs;

    for (size_t i = 0; i < length; ++i)
        BX_IncRef(array->items[i]);

    return array;
}


struct BX_Array *
BX_Array_New(size_t length, struct BoolExpr **exprs)
{
    struct BoolExpr **exprs_copy;

    exprs_copy = malloc(length * sizeof(struct BoolExpr *));
    if (exprs_copy == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0; i < length; ++i)
        exprs_copy[i] = exprs[i];

    return _bx_array_from(length, exprs_copy);
}


void
BX_Array_Del(struct BX_Array *array)
{
    for (size_t i = 0; i < array->length; ++i)
        BX_DecRef(array->items[i]);
    free(array->items);
    free(array);
}


bool
BX_Array_Equal(struct BX_Array *self, struct BX_Array *other)
{
    if (self->length != other->length)
        return false;

    for (size_t i = 0; i < self->length; ++i) {
        if (self->items[i] != other->items[i])
            return false;
    }

    return true;
}

