/*
** Filename: array2.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* array.c */
struct BoolExprArray * _bx_array_from(size_t length, struct BoolExpr **items);

/* boolexpr.c */
struct BoolExpr * _op_new(BoolExprKind kind, size_t n, struct BoolExpr **xs);


struct BoolExprArray2 *
BoolExprArray2_New(size_t length, size_t *lengths, struct BoolExpr ***items)
{
    struct BoolExprArray2 *array2;

    array2 = malloc(sizeof(struct BoolExprArray2));
    if (array2 == NULL)
        return NULL; // LCOV_EXCL_LINE

    array2->length = length;
    array2->items = malloc(length * sizeof(struct BoolExprArray *));
    if (array2->items == NULL) {
        free(array2); // LCOV_EXCL_LINE
        return NULL;  // LCOV_EXCL_LINE
    }

    for (size_t i = 0; i < length; ++i) {
        array2->items[i] = BoolExprArray_New(lengths[i], items[i]);
        /* LCOV_EXCL_START */
        if (array2->items[i] == NULL) {
            for (size_t j = 0; j < i; ++j)
                BoolExprArray_Del(array2->items[j]);
            free(array2->items);
            free(array2);
            return NULL;
        }
        /* LCOV_EXCL_STOP */
    }

    return array2;
}


void
BoolExprArray2_Del(struct BoolExprArray2 *array2)
{
    for (size_t i = 0; i < array2->length; ++i)
        BoolExprArray_Del(array2->items[i]);
    free(array2->items);
    free(array2);
}


bool
BoolExprArray2_Equal(struct BoolExprArray2 *self, struct BoolExprArray2 *other)
{
    if (self->length != other->length)
        return false;

    for (size_t i = 0; i < self->length; ++i) {
        if (!BoolExprArray_Equal(self->items[i], other->items[i]))
            return false;
    }

    return true;
}


static struct BoolExprArray *
_multiply(struct BoolExprArray *a, struct BoolExprArray *b, BoolExprKind kind)
{
    size_t length = a->length * b->length;
    struct BoolExpr **items;
    struct BoolExprArray *prod;

    items = malloc(length * sizeof(struct BoolExpr *));
    if (items == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0, index = 0; i < a->length; ++i) {
        for (size_t j = 0; j < b->length; ++j, ++index) {
            struct BoolExpr *xs[2] = {a->items[i], b->items[j]};
            items[index] = _op_new(kind, 2, xs);
            if (items[index] == NULL) {
                /* LCOV_EXCL_START */
                for (size_t k = 0; k < j; ++k)
                    BoolExpr_DecRef(items[k]);
                free(items);
                return NULL;
                /* LCOV_EXCL_STOP */
            }
        }
    }

    prod = _bx_array_from(length, items);

    for (size_t i = 0; i < length; ++i)
        BoolExpr_DecRef(items[i]);

    return prod;
}


static struct BoolExprArray *
_product(struct BoolExprArray2 *array2, BoolExprKind kind, size_t n)
{
    if (n == 0) {
        struct BoolExpr *items[] = {IDENTITY[kind]};
        return BoolExprArray_New(1, items);
    }

    struct BoolExprArray *prev;
    struct BoolExprArray *prod;

    prev = _product(array2, kind, n-1);
    if (prev == NULL)
        return NULL; // LCOV_EXCL_LINE

    prod = _multiply(array2->items[n-1], prev, kind);
    if (prod == NULL) {
        BoolExprArray_Del(prev); // LCOV_EXCL_LINE
        return NULL;             // LCOV_EXCL_LINE
    }

    BoolExprArray_Del(prev);

    return prod;
}


struct BoolExprArray *
BoolExprArray2_Product(struct BoolExprArray2 *self, BoolExprKind kind)
{
    return _product(self, kind, self->length);
}

