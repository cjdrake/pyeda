/*
** Filename: vector.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* Minimum capacity */
#define MIN_CAP 64

/* Scale factor for resize */
#define SCALE_FACTOR 2.0


struct BX_Vector *
BX_Vector_New(void)
{
    struct BX_Vector *vec;

    vec = malloc(sizeof(struct BX_Vector));
    if (vec == NULL)
        return NULL; // LCOV_EXCL_LINE

    vec->length = 0;
    vec->capacity = MIN_CAP;
    vec->items = malloc(MIN_CAP * sizeof(struct BoolExpr *));
    if (vec->items == NULL) {
        free(vec);   // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    /* Initialize items to NULL */
    for (size_t i = 0; i < vec->capacity; ++i)
        vec->items[i] = (struct BoolExpr *) NULL;

    return vec;
}


void
BX_Vector_Del(struct BX_Vector *vec)
{
    for (size_t i = 0; i < vec->length; ++i) {
        if (vec->items[i] != (struct BoolExpr *) NULL)
            BX_DecRef(vec->items[i]);
    }
    free(vec->items);
    free(vec);
}


bool
BX_Vector_Insert(struct BX_Vector *vec, size_t index, struct BoolExpr *ex)
{
    /* Required length and capacity */
    size_t req_len = index + 1;
    size_t req_cap = vec->capacity;

    /* Scale up until we have enough capacity */
    while (req_cap < req_len)
        req_cap = (size_t) (SCALE_FACTOR * req_cap);

    if (req_cap > vec->capacity) {
        vec->items = realloc(vec->items, req_cap * sizeof(struct BoolExpr *));
        if (vec->items == NULL)
            return false; // LCOV_EXCL_LINE

        /* Initialize new items to NULL */
        for (size_t i = vec->capacity; i < req_cap; ++i)
            vec->items[i] = (struct BoolExpr *) NULL;

        vec->capacity = req_cap;
    }

    vec->items[index] = BX_IncRef(ex);
    if (req_len > vec->length)
        vec->length = req_len;

    return true;
}


bool
BX_Vector_Append(struct BX_Vector *vec, struct BoolExpr *ex)
{
    return BX_Vector_Insert(vec, vec->length, ex);
}

