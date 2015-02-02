/*
** Filename: bubble.c
**
** Bubbling the NOT operator
*/


#include "boolexpr.h"


/* util.c */
BoolExpr * _op_transform(BoolExpr *op, BoolExpr * (*fn)(BoolExpr *));


static BoolExpr *
_inv_or(BoolExpr *op)
{
    size_t length = op->data.xs->length;
    BoolExpr *xs[length];
    BoolExpr *temp;
    BoolExpr *y;

    for (size_t i = 0; i < length; ++i) {
        CHECK_NULL(temp, Not(op->data.xs->items[i]));
        CHECK_NULL_1(xs[i], BoolExpr_PushDownNot(temp), temp);
        BoolExpr_DecRef(temp);
    }

    CHECK_NULL_N(y, And(length, xs), length, xs);

    for (size_t i = 0; i < length; ++i)
        BoolExpr_DecRef(xs[i]);

    return y;
}


static BoolExpr *
_inv_and(BoolExpr *op)
{
    size_t length = op->data.xs->length;
    BoolExpr *xs[length];
    BoolExpr *temp;
    BoolExpr *y;

    for (size_t i = 0; i < length; ++i) {
        CHECK_NULL(temp, Not(op->data.xs->items[i]));
        CHECK_NULL_1(xs[i], BoolExpr_PushDownNot(temp), temp);
        BoolExpr_DecRef(temp);
    }

    CHECK_NULL_N(y, Or(length, xs), length, xs);

    for (size_t i = 0; i < length; ++i)
        BoolExpr_DecRef(xs[i]);

    return y;
}


//static BoolExpr *
//_inv_xor(BoolExpr *op)
//{
//    size_t length = op->data.xs->length;
//    BoolExpr *xs[length];
//    BoolExpr *temp;
//    BoolExpr *y;
//
//    CHECK_NULL(temp, Not(op->data.xs->items[0]));
//    CHECK_NULL_1(xs[0], BoolExpr_PushDownNot(temp), temp);
//    BoolExpr_DecRef(temp);
//
//    for (size_t i = 1; i < length; ++i)
//        CHECK_NULL(xs[i], BoolExpr_PushDownNot(op->data.xs->items[i]));
//
//    CHECK_NULL_N(y, Xor(length, xs), length, xs);
//
//    for (size_t i = 0; i < length; ++i) BoolExpr_DecRef(xs[i]);
//
//    return y;
//}


//static BoolExpr *
//_inv_eq2(BoolExpr *op)
//{
//    BoolExpr *x0, *x1;
//    BoolExpr *temp;
//    BoolExpr *y;
//
//    CHECK_NULL(temp, Not(op->data.xs->items[0]));
//    CHECK_NULL_1(x0, BoolExpr_PushDownNot(temp), temp);
//    BoolExpr_DecRef(temp);
//
//    CHECK_NULL(x1, BoolExpr_PushDownNot(op->data.xs->items[1]));
//
//    CHECK_NULL_2(y, EqualN(2, x0, x1), x0, x1);
//
//    BoolExpr_DecRef(x0);
//    BoolExpr_DecRef(x1);
//
//    return y;
//}


static BoolExpr *
_inv_ite(BoolExpr *op)
{
    BoolExpr *d1, *d0;
    BoolExpr *temp;
    BoolExpr *y;

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


BoolExpr *
BoolExpr_PushDownNot(BoolExpr *ex)
{
    if (IS_ATOM(ex)) {
        return BoolExpr_IncRef(ex);
    }
    else if (IS_NOT(ex) && IS_OR(ex->data.xs->items[0])) {
        return _inv_or(ex->data.xs->items[0]);
    }
    else if (IS_NOT(ex) && IS_AND(ex->data.xs->items[0])) {
        return _inv_and(ex->data.xs->items[0]);
    }
    //else if (IS_NOT(ex) && IS_XOR(ex->data.xs->items[0])) {
    //    return _inv_xor(ex->data.xs->items[0]);
    //}
    //else if (IS_NOT(ex) && IS_EQ(ex->data.xs->items[0]) &&
    //         ex->data.xs->items[0]->data.xs->length == 2) {
    //    return _inv_eq2(ex->data.xs->items[0]);
    //}
    else if (IS_NOT(ex) && IS_ITE(ex->data.xs->items[0])) {
        return _inv_ite(ex->data.xs->items[0]);
    }
    else {
        return _op_transform(ex, BoolExpr_PushDownNot);
    }
}

