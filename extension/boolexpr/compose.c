/*
** Filename: compose.c
**
** Function Composition
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* boolexpr.c */
struct BoolExpr * _op_new(BoolExprType t, size_t n, struct BoolExpr **xs);


static struct BoolExpr *
_const_compose(struct BoolExpr *ex, struct BoolExprDict *var2ex)
{
    return BoolExpr_IncRef(ex);
}


static struct BoolExpr *
_var_compose(struct BoolExpr *x, struct BoolExprDict *var2ex)
{
    struct BoolExpr *ex = BoolExprDict_Search(var2ex, x);

    if (ex == (struct BoolExpr *) NULL)
        return BoolExpr_IncRef(x);
    else
        return BoolExpr_IncRef(ex);
}


static struct BoolExpr *
_comp_compose(struct BoolExpr *xn, struct BoolExprDict *var2ex)
{
    struct BoolExpr *lit = Literal(xn->data.lit.lits, -xn->data.lit.uniqid);
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL_1(temp, _var_compose(lit, var2ex), lit);
    BoolExpr_DecRef(lit);

    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


static struct BoolExpr *
_op_compose(struct BoolExpr *op, struct BoolExprDict *var2ex)
{
    size_t length = op->data.xs->length;
    struct BoolExpr *xs[length];
    unsigned int mod_count = 0;
    struct BoolExpr *y;

    for (size_t i = 0; i < length; ++i) {
        CHECK_NULL_N(xs[i], BoolExpr_Compose(op->data.xs->items[i], var2ex), i, xs);
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


static struct BoolExpr * (*_compose[16])(struct BoolExpr *ex, struct BoolExprDict *var2ex) = {
    _const_compose,
    _const_compose,
    _const_compose,
    _const_compose,

    _comp_compose,
    _var_compose,
    NULL,
    NULL,

    _op_compose,
    _op_compose,
    _op_compose,
    _op_compose,

    _op_compose,
    _op_compose,
    _op_compose,
    NULL,
};


struct BoolExpr *
BoolExpr_Compose(struct BoolExpr *ex, struct BoolExprDict *var2ex)
{
    return _compose[ex->type](ex, var2ex);
}


struct BoolExpr *
BoolExpr_Restrict(struct BoolExpr *ex, struct BoolExprDict *var2const)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, BoolExpr_Compose(ex, var2const));
    CHECK_NULL_1(y, BoolExpr_Simplify(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}

