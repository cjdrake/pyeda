/*
** Filename: util.c
*/


#include <assert.h>

#include "boolexpr.h"


/* boolexpr.c */
BoolExpr * _op_new(BoolExprType t, size_t n, BoolExpr **xs);


/* Return the ceiling log base two of an integer. */
unsigned int
_clog2(unsigned int num)
{
    unsigned int accum = 0;
    unsigned int shifter = 1;

    assert(num >= 1);

    while (num > shifter) {
        shifter <<= 1;
        accum += 1;
    }

    return accum;
}


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


BoolExpr *
_op_transform(BoolExpr *op, BoolExpr * (*fn)(BoolExpr *))
{
    size_t length = op->data.xs->length;
    BoolExpr *xs[length];
    unsigned int mod_count = 0;
    BoolExpr *y;

    for (size_t i = 0; i < length; ++i) {
        CHECK_NULL_N(xs[i], fn(op->data.xs->items[i]), i, xs);
        if (xs[i] != op->data.xs->items[i])
            mod_count += 1;
    }

    if (mod_count)
        CHECK_NULL_N(y, _op_new(op->type, length, xs), length, xs);
    else
        y = BoolExpr_IncRef(op);

    for (size_t i = 0; i < length; ++i)
        BoolExpr_DecRef(xs[i]);

    return y;
}


void
_mark_flags(BoolExpr *ex, BoolExprFlags f)
{
    if ((ex->flags & f) != f) {
        for (size_t i = 0; i < ex->data.xs->length; ++i)
            _mark_flags(ex->data.xs->items[i], f);
        ex->flags |= f;
    }
}


/* Return true if the operator is a clause, containing only literals */
bool
_is_clause(BoolExpr *op)
{
    for (size_t i = 0; i < op->data.xs->length; ++i) {
        if (!IS_LIT(op->data.xs->items[i]))
            return false;
    }
    return true;
}

