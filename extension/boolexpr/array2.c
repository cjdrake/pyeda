/*
** Filename: array2.c
*/


#include "boolexpr.h"


/* boolexpr.c */
BoolExpr * _opn_new(BoolExprType t, size_t n, ...);


BoolExprArray2 *
BoolExprArray2_New(size_t length, size_t *lengths, BoolExpr ***items)
{
    BoolExprArray2 *array2;

    array2 = (BoolExprArray2 *) malloc(sizeof(BoolExprArray2));
    if (array2 == NULL)
        return NULL; // LCOV_EXCL_LINE

    array2->items = (BoolExprArray **) malloc(length * sizeof(BoolExprArray *));
    if (array2->items == NULL) {
        free(array2); // LCOV_EXCL_LINE
        return NULL;  // LCOV_EXCL_LINE
    }

    array2->length = length;

    for (size_t i = 0; i < length; ++i)
        array2->items[i] = BoolExprArray_New(lengths[i], items[i]);

    return array2;
}


void
BoolExprArray2_Del(BoolExprArray2 *array2)
{
    for (size_t i = 0; i < array2->length; ++i)
        BoolExprArray_Del(array2->items[i]);

    free(array2->items);
    free(array2);
}


bool
BoolExprArray2_Equal(BoolExprArray2 *self, BoolExprArray2 *other)
{
    if (self->length != other->length)
        return false;

    for (size_t i = 0; i < self->length; ++i)
        if (!BoolExprArray_Equal(self->items[i], other->items[i]))
            return false;

    return true;
}


static BoolExprArray *
_multiply(BoolExprArray *a, BoolExprArray *b, BoolExprType t)
{
    size_t length = a->length * b->length;
    BoolExpr **items;
    BoolExprArray *prod;

    items = (BoolExpr **) malloc(length * sizeof(BoolExpr *));
    if (items == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0, index = 0; i < a->length; ++i) {
        for (size_t j = 0; j < b->length; ++j, ++index) {
            items[index] = _opn_new(t, 2, a->items[i], b->items[j]);
            if (items[index] == NULL) {
                /* LCOV_EXCL_START */
                for (size_t k = 0; k < index; ++k)
                    BoolExpr_DecRef(items[k]);
                free(items);
                return NULL;
                /* LCOV_EXCL_STOP */
            }
        }
    }

    prod = BoolExprArray_New(length, items);

    for (size_t i = 0; i < length; ++i)
        BoolExpr_DecRef(items[i]);
    free(items);

    return prod;
}


static BoolExprArray *
_product(BoolExprArray2 *array2, BoolExprType t, size_t n)
{
    if (n == 0) {
        BoolExpr *items[] = {IDENTITY[t]};
        return BoolExprArray_New(1, items);
    }
    else {
        BoolExprArray *prev;
        BoolExprArray *prod;

        prev = _product(array2, t, n-1);
        if (prev == NULL)
            return NULL; // LCOV_EXCL_LINE

        prod = _multiply(array2->items[n-1], prev, t);

        BoolExprArray_Del(prev);

        return prod;
    }
}


BoolExprArray *
BoolExprArray2_Product(BoolExprArray2 *self, BoolExprType t)
{
    return _product(self, t, self->length);
}

