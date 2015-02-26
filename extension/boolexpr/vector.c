/*
** Filename: vector.c
*/


#include "boolexpr.h"


#define CAPACITY 64


BoolExprVector *
BoolExprVector_New()
{
    BoolExprVector *vec;

    vec = (BoolExprVector *) malloc(sizeof(BoolExprVector));
    if (vec == NULL)
        return NULL; // LCOV_EXCL_LINE

    vec->items = (BoolExpr **) malloc(CAPACITY * sizeof(BoolExpr *));
    if (vec->items == NULL) {
        free(vec);   // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    vec->length = 0;
    vec->capacity = CAPACITY;

    /* Initialize items to NULL expression */
    for (size_t i = 0; i < vec->capacity; ++i)
        vec->items[i] = (BoolExpr *) NULL;

    return vec;
}


void
BoolExprVector_Del(BoolExprVector *vec)
{
    for (size_t i = 0; i < vec->length; ++i) {
        if (vec->items[i] != (BoolExpr *) NULL)
            BoolExpr_DecRef(vec->items[i]);
    }

    free(vec->items);
    free(vec);
}


#define SCALE_FACTOR 2.0

bool
BoolExprVector_Insert(BoolExprVector *vec, size_t index, BoolExpr *ex)
{
    /* Required length and capacity */
    size_t req_len = index + 1;
    size_t req_cap = vec->capacity;

    /* Scale up until we have enough capacity */
    while (req_cap < req_len)
        req_cap = (size_t) (SCALE_FACTOR * req_cap);

    if (req_cap > vec->capacity) {
        vec->items = (BoolExpr **) realloc(vec->items, req_cap * sizeof(BoolExpr *));
        if (vec->items == NULL)
            return false; // LCOV_EXCL_LINE

        /* Initialize new items to NULL expression */
        for (size_t i = vec->capacity; i < req_cap; ++i)
            vec->items[i] = (BoolExpr *) NULL;

        vec->capacity = req_cap;
    }

    vec->items[index] = BoolExpr_IncRef(ex);
    if (req_len > vec->length)
        vec->length = req_len;

    return true;
}


bool
BoolExprVector_Append(BoolExprVector *vec, BoolExpr *ex)
{
    return BoolExprVector_Insert(vec, vec->length, ex);
}

