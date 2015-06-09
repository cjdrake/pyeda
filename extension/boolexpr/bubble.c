/*
** Filename: bubble.c
**
** Bubbling the NOT operator
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* util.c */
void _free_exs(int n, struct BoolExpr **exs);
struct BoolExpr * _op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *));


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
        temp = Not(op->data.xs->items[i]);
        if (temp == NULL) {
            free(xs);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
        CHECK_NULL_N(xs[i], BoolExpr_PushDownNot(temp), i, xs);
        BoolExpr_DecRef(temp);
    }

    y = And(length, xs);

    _free_exs(length, xs);

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
        temp = Not(op->data.xs->items[i]);
        if (temp == NULL) {
            free(xs);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
        CHECK_NULL_N(xs[i], BoolExpr_PushDownNot(temp), i, xs);
        BoolExpr_DecRef(temp);
    }

    y = Or(length, xs);

    _free_exs(length, xs);

    return y;
}


static struct BoolExpr *
_inv_ite(struct BoolExpr *op)
{
    struct BoolExpr *d1, *d0;
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, Not(op->data.xs->items[1]));
    CHECK_NULL_1(d1, BoolExpr_PushDownNot(temp), temp);
    BoolExpr_DecRef(temp);

    CHECK_NULL_1(temp, Not(op->data.xs->items[2]), d1);
    CHECK_NULL_2(d0, BoolExpr_PushDownNot(temp), d1, temp);
    BoolExpr_DecRef(temp);

    CHECK_NULL_2(y, ITE(op->data.xs->items[0], d1, d0), d1, d0);
    BoolExpr_DecRef(d1);
    BoolExpr_DecRef(d0);

    return y;
}


struct BoolExpr *
BoolExpr_PushDownNot(struct BoolExpr *ex)
{
    if (IS_ATOM(ex))
        return BoolExpr_IncRef(ex);

    if (IS_NOT(ex) && IS_OR(ex->data.xs->items[0]))
        return _inv_or(ex->data.xs->items[0]);

    if (IS_NOT(ex) && IS_AND(ex->data.xs->items[0]))
        return _inv_and(ex->data.xs->items[0]);

    if (IS_NOT(ex) && IS_ITE(ex->data.xs->items[0]))
        return _inv_ite(ex->data.xs->items[0]);

    return _op_transform(ex, BoolExpr_PushDownNot);
}

