/*
** Filename: bubble.c
**
** Bubbling the NOT operator
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"
#include "memcheck.h"
#include "share.h"


/* ~(a | b | ...) = ~a & ~b & ... */
static struct BoolExpr *
_inv_or(struct BoolExpr *op)
{
    size_t length = op->data.xs->length;
    struct BoolExpr **xs;
    struct BoolExpr *temp;
    struct BoolExpr *y;

    xs = malloc(length * sizeof(struct BoolExpr *));
    if (xs == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0; i < length; ++i) {
        temp = BX_Not(op->data.xs->items[i]);
        if (temp == NULL) {
            free(xs);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
        CHECK_NULL_N(xs[i], BX_PushDownNot(temp), i, xs);
        BX_DecRef(temp);
    }

    y = BX_And(length, xs);

    _bx_free_exs(length, xs);

    return y;
}


static struct BoolExpr *
_inv_and(struct BoolExpr *op)
{
    size_t length = op->data.xs->length;
    struct BoolExpr **xs;
    struct BoolExpr *temp;
    struct BoolExpr *y;

    xs = malloc(length * sizeof(struct BoolExpr *));
    if (xs == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0; i < length; ++i) {
        temp = BX_Not(op->data.xs->items[i]);
        if (temp == NULL) {
            free(xs);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
        CHECK_NULL_N(xs[i], BX_PushDownNot(temp), i, xs);
        BX_DecRef(temp);
    }

    y = BX_Or(length, xs);

    _bx_free_exs(length, xs);

    return y;
}


static struct BoolExpr *
_inv_ite(struct BoolExpr *op)
{
    struct BoolExpr *d1, *d0;
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, BX_Not(op->data.xs->items[1]));
    CHECK_NULL_1(d1, BX_PushDownNot(temp), temp);
    BX_DecRef(temp);

    CHECK_NULL_1(temp, BX_Not(op->data.xs->items[2]), d1);
    CHECK_NULL_2(d0, BX_PushDownNot(temp), d1, temp);
    BX_DecRef(temp);

    CHECK_NULL_2(y, BX_ITE(op->data.xs->items[0], d1, d0), d1, d0);
    BX_DecRef(d1);
    BX_DecRef(d0);

    return y;
}


struct BoolExpr *
BX_PushDownNot(struct BoolExpr *ex)
{
    if (BX_IS_ATOM(ex))
        return BX_IncRef(ex);

    if (BX_IS_NOR(ex))
        return _inv_or(ex->data.xs->items[0]);

    if (BX_IS_NAND(ex))
        return _inv_and(ex->data.xs->items[0]);

    if (BX_IS_NOT(ex) && BX_IS_ITE(ex->data.xs->items[0]))
        return _inv_ite(ex->data.xs->items[0]);

    return _bx_op_transform(ex, BX_PushDownNot);
}

