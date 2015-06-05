/*
** Filename: product.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* array.c */
struct BoolExprArray * _bx_array_from(size_t length, struct BoolExpr **items);

/* boolexpr.c */
struct BoolExpr * _op_new(BoolExprKind kind, size_t n, struct BoolExpr **xs);

/* util.c */
void _free_xs(int length, struct BoolExpr **xs);


static struct BoolExprArray *
_multiply(BoolExprKind kind, struct BoolExprArray *a, struct BoolExprArray *b)
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
                _free_xs(index, items); // LCOV_EXCL_LINE
                return NULL;            // LCOV_EXCL_LINE
            }
        }
    }

    prod = _bx_array_from(length, items);

    for (size_t i = 0; i < length; ++i)
        BoolExpr_DecRef(items[i]);

    return prod;
}


static struct BoolExprArray *
_product(BoolExprKind kind, size_t n, struct BoolExprArray **arrays)
{
    if (n == 0) {
        struct BoolExpr *items[] = {IDENTITY[kind]};
        return BoolExprArray_New(1, items);
    }

    struct BoolExprArray *prev;
    struct BoolExprArray *prod;

    prev = _product(kind, n-1, arrays);
    if (prev == NULL)
        return NULL; // LCOV_EXCL_LINE

    prod = _multiply(kind, prev, arrays[n-1]);
    if (prod == NULL) {
        BoolExprArray_Del(prev); // LCOV_EXCL_LINE
        return NULL;             // LCOV_EXCL_LINE
    }

    BoolExprArray_Del(prev);

    return prod;
}


struct BoolExprArray *
BoolExpr_Product(BoolExprKind kind, size_t length, struct BoolExprArray **arrays)
{
    return _product(kind, length, arrays);
}

