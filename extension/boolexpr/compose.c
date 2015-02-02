/*
** Filename: compose.c
**
** Function Composition
*/


#include "boolexpr.h"


/* boolexpr.c */
BoolExpr * _op_new(BoolExprType t, size_t n, BoolExpr **xs);


static BoolExpr *
_const_compose(BoolExpr *ex, BoolExprDict *var2ex)
{
    return BoolExpr_IncRef(ex);
}


static BoolExpr *
_var_compose(BoolExpr *x, BoolExprDict *var2ex)
{
    BoolExpr *ex = BoolExprDict_Search(var2ex, x);

    if (ex == (BoolExpr *) NULL)
        return BoolExpr_IncRef(x);
    else
        return BoolExpr_IncRef(ex);
}


static BoolExpr *
_comp_compose(BoolExpr *xn, BoolExprDict *var2ex)
{
    BoolExpr *lit = Literal(xn->data.lit.lits, -xn->data.lit.uniqid);
    BoolExpr *temp;
    BoolExpr *y;

    CHECK_NULL_1(temp, _var_compose(lit, var2ex), lit);
    BoolExpr_DecRef(lit);

    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


static BoolExpr *
_op_compose(BoolExpr *op, BoolExprDict *var2ex)
{
    size_t length = op->data.xs->length;
    BoolExpr *xs[length];
    unsigned int mod_count = 0;
    BoolExpr *y;

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


static BoolExpr * (*_compose[16])(BoolExpr *ex, BoolExprDict *var2ex) = {
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


BoolExpr *
BoolExpr_Compose(BoolExpr *ex, BoolExprDict *var2ex)
{
    return _compose[ex->type](ex, var2ex);
}


BoolExpr *
BoolExpr_Restrict(BoolExpr *ex, BoolExprDict *var2const)
{
    BoolExpr *temp;
    BoolExpr *y;

    CHECK_NULL(temp, BoolExpr_Compose(ex, var2const));
    CHECK_NULL_1(y, BoolExpr_Simplify(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}

