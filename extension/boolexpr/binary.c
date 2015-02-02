/*
** Filename: binary.c
**
** Convert all N-ary operators to binary operators
*/


#include "boolexpr.h"


/* boolexpr.c */
BoolExpr * _op_new(BoolExprType t, size_t n, BoolExpr **xs);

/* util.c */
BoolExpr * _op_transform(BoolExpr *op, BoolExpr * (*fn)(BoolExpr *));


static BoolExpr *
_commutative_binify(BoolExpr *op)
{
    if (op->data.xs->length == 2) {
        return BoolExpr_IncRef(op);
    }
    else {
        size_t mid = op->data.xs->length / 2;
        size_t n0 = mid;
        size_t n1 = op->data.xs->length - mid;
        BoolExpr **items0 = op->data.xs->items;
        BoolExpr **items1 = op->data.xs->items + mid;
        BoolExpr *xs[2];
        BoolExpr *temp;
        BoolExpr *y;

        if (n0 == 1) {
            xs[0] = BoolExpr_IncRef(items0[0]);
        }
        else {
            CHECK_NULL(temp, _op_new(op->type, n0, items0));
            CHECK_NULL_1(xs[0], _commutative_binify(temp), temp);
            BoolExpr_DecRef(temp);
        }

        CHECK_NULL_1(temp, _op_new(op->type, n1, items1), xs[0]);
        CHECK_NULL_2(xs[1], _commutative_binify(temp), xs[0], temp);
        BoolExpr_DecRef(temp);

        CHECK_NULL_2(y, _op_new(op->type, 2, xs), xs[0], xs[1]);
        BoolExpr_DecRef(xs[0]);
        BoolExpr_DecRef(xs[1]);

        return y;
    }
}


static BoolExpr *
_eq_binify(BoolExpr *op)
{
    if (op->data.xs->length == 2) {
        return BoolExpr_IncRef(op);
    }
    else {
        size_t length;
        BoolExpr **xs;
        BoolExpr *temp;
        BoolExpr *y;

        length = (op->data.xs->length * (op->data.xs->length - 1)) >> 1;
        xs = (BoolExpr **) malloc(length * sizeof(BoolExpr *));

        for (size_t i = 0, index = 0; i < (op->data.xs->length - 1); ++i) {
            for (size_t j = i+1; j < op->data.xs->length; ++j, ++index) {

                xs[index] = EqualN(2, op->data.xs->items[i],
                                      op->data.xs->items[j]);

                /* LCOV_EXCL_START */
                if (xs[index] == NULL) {
                    for (size_t k = 0; k < index; ++k)
                        BoolExpr_DecRef(xs[k]);
                    free(xs);
                    return NULL;
                }
                /* LCOV_EXCL_STOP */
            }
        }

        temp = And(length, xs);

        /* LCOV_EXCL_START */
        if (temp == NULL) {
            for (size_t i = 0; i < length; ++i)
                BoolExpr_DecRef(xs[i]);
            free(xs);
        }
        /* LCOV_EXCL_STOP */

        for (size_t i = 0; i < length; ++i)
            BoolExpr_DecRef(xs[i]);
        free(xs);

        CHECK_NULL_1(y, _commutative_binify(temp), temp);
        BoolExpr_DecRef(temp);

        return y;
    }
}


static BoolExpr *
_fixed_binify(BoolExpr *op)
{
    return BoolExpr_IncRef(op);
}


static BoolExpr * (*_op_binify[16])(BoolExpr *ex) = {
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,

    _commutative_binify,
    _commutative_binify,
    _commutative_binify,
    _eq_binify,

    _fixed_binify,
    _fixed_binify,
    _fixed_binify,
    NULL,
};


BoolExpr *
BoolExpr_ToBinary(BoolExpr *ex)
{
    if (IS_ATOM(ex)) {
        return BoolExpr_IncRef(ex);
    }
    else {
        BoolExpr *temp;
        BoolExpr *y;

        CHECK_NULL(temp, _op_transform(ex, BoolExpr_ToBinary));
        CHECK_NULL_1(y, _op_binify[temp->type](temp), temp);
        BoolExpr_DecRef(temp);

        return y;
    }
}

