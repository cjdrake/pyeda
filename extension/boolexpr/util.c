/*
** Filename: util.c
*/


#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* boolexpr.c */
struct BoolExpr * _op_new(BoolExprKind kind, size_t n, struct BoolExpr **xs);


/*
** Map negative lits onto evens, and positive lits onto odds.
** ~x : {-1, -2, -3, -4, ...} => {0, 2, 4, 6, ...}
**  x : { 1,  2,  3,  4, ...} => {1, 3, 5, 7, ...}
*/
size_t
_uniqid2index(long uniqid)
{
    assert(uniqid != 0);

    return (size_t) (uniqid < 0 ? -2 * uniqid - 2 : 2 * uniqid - 1);
}


/* LCOV_EXCL_START */
void
_free_xs(int n, struct BoolExpr **xs)
{
    for (size_t i = 0; i < n; ++i)
        BoolExpr_DecRef(xs[i]);
    free(xs);
}
/* LCOV_EXCL_STOP */


struct BoolExpr *
_op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *))
{
    size_t length = op->data.xs->length;
    struct BoolExpr **xs;
    unsigned int mod_count = 0;
    struct BoolExpr *y;

    xs = malloc(length * sizeof(struct BoolExpr *));
    if (xs == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0; i < length; ++i) {
        xs[i] = fn(op->data.xs->items[i]);
        if (xs[i] == NULL) {
            _free_xs(i, xs); // LCOV_EXCL_LINE
            return NULL;     // LCOV_EXCL_LINE
        }
        mod_count += (xs[i] != op->data.xs->items[i]);
    }

    if (mod_count)
        y = _op_new(op->kind, length, xs);
    else
        y = BoolExpr_IncRef(op);

    _free_xs(length, xs);

    return y;
}


void
_mark_flags(struct BoolExpr *ex, BoolExprFlags f)
{
    if ((ex->flags & f) != f) {
        for (size_t i = 0; i < ex->data.xs->length; ++i)
            _mark_flags(ex->data.xs->items[i], f);
        ex->flags |= f;
    }
}


/* Return true if the operator is a clause, containing only literals */
bool
_is_clause(struct BoolExpr *op)
{
    for (size_t i = 0; i < op->data.xs->length; ++i) {
        if (!IS_LIT(op->data.xs->items[i]))
            return false;
    }

    return true;
}

