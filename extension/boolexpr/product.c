/*
** Filename: product.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"
#include "memcheck.h"
#include "share.h"


static struct BX_Array *
_multiply(BX_Kind kind, struct BX_Array *a, struct BX_Array *b)
{
    size_t length = a->length * b->length;
    struct BoolExpr **items;
    struct BX_Array *prod;

    items = malloc(length * sizeof(struct BoolExpr *));
    if (items == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0, index = 0; i < a->length; ++i) {
        for (size_t j = 0; j < b->length; ++j, ++index) {
            struct BoolExpr *xs[2] = {a->items[i], b->items[j]};
            CHECK_NULL_N(items[index], _op_new(kind, 2, xs), index, items);
        }
    }

    prod = _bx_array_from(length, items);

    for (size_t i = 0; i < length; ++i)
        BX_DecRef(items[i]);

    return prod;
}


static struct BX_Array *
_product(BX_Kind kind, size_t n, struct BX_Array **arrays)
{
    if (n == 0) {
        struct BoolExpr *items[] = {IDENTITY[kind]};
        return BX_Array_New(1, items);
    }

    struct BX_Array *prev;
    struct BX_Array *prod;

    prev = _product(kind, n-1, arrays);
    if (prev == NULL)
        return NULL; // LCOV_EXCL_LINE

    prod = _multiply(kind, arrays[n-1], prev);
    if (prod == NULL) {
        BX_Array_Del(prev); // LCOV_EXCL_LINE
        return NULL;             // LCOV_EXCL_LINE
    }

    BX_Array_Del(prev);

    return prod;
}


struct BX_Array *
BX_Product(BX_Kind kind, size_t length, struct BX_Array **arrays)
{
    return _product(kind, length, arrays);
}

