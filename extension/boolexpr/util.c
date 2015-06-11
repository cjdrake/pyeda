/*
** Filename: util.c
*/


#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"
#include "memcheck.h"
#include "share.h"


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


void
_bx_free_exs(int n, struct BoolExpr **exs)
{
    for (size_t i = 0; i < n; ++i)
        BX_DecRef(exs[i]);
    free(exs);
}


struct BoolExpr *
_bx_op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *))
{
    size_t length = op->data.xs->length;
    struct BoolExpr **xs;
    unsigned int mod_count = 0;
    struct BoolExpr *y;

    xs = malloc(length * sizeof(struct BoolExpr *));
    if (xs == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0; i < length; ++i) {
        CHECK_NULL_N(xs[i], fn(op->data.xs->items[i]), i, xs);
        mod_count += (xs[i] != op->data.xs->items[i]);
    }

    if (mod_count)
        y = _bx_op_new(op->kind, length, xs);
    else
        y = BX_IncRef(op);

    _bx_free_exs(length, xs);

    return y;
}


void
_bx_mark_flags(struct BoolExpr *ex, BX_Flags f)
{
    if ((ex->flags & f) != f) {
        for (size_t i = 0; i < ex->data.xs->length; ++i)
            _bx_mark_flags(ex->data.xs->items[i], f);
        ex->flags |= f;
    }
}


/* Return true if the operator is a clause, containing only literals */
bool
_bx_is_clause(struct BoolExpr *op)
{
    for (size_t i = 0; i < op->data.xs->length; ++i) {
        if (!BX_IS_LIT(op->data.xs->items[i]))
            return false;
    }

    return true;
}

