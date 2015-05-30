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
struct BoolExpr * _op_new(BoolExprKind kind, size_t n, struct BoolExpr **xs);

/* util.c */
void _free_xs(int n, struct BoolExpr **xs);


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
    struct BoolExpr **xs;
    unsigned int mod_count = 0;
    struct BoolExpr *y;

    xs = malloc(length * sizeof(struct BoolExpr *));
    if (xs == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0; i < length; ++i) {
        xs[i] = BoolExpr_Compose(op->data.xs->items[i], var2ex);
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
    return _compose[ex->kind](ex, var2ex);
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

