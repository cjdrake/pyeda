/*
** Filename: nnf.c
**
** Negation Normal Form
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* nnf.c */
static struct BoolExpr * _xor_nnfify(struct BoolExpr *op);

/* simple.c */
struct BoolExpr * _simplify(struct BoolExpr *ex);

/* util.c */
struct BoolExpr * _op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *));
void _mark_flags(struct BoolExpr *ex, BoolExprFlags f);


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_orandnot_nnfify(struct BoolExpr *op)
{
    return BoolExpr_IncRef(op);
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_xor_nnfify_conj(struct BoolExpr *op)
{
    struct BoolExpr *y;

    /* x0 ^ x1 <=> (x0 | x1) & (~x0 | ~x1) */
    if (op->data.xs->length == 2) {
        struct BoolExpr *xn0, *xn1;
        struct BoolExpr *or_xn0_xn1, *or_x0_x1;

        CHECK_NULL(xn0, Not(op->data.xs->items[0]));
        CHECK_NULL_1(xn1, Not(op->data.xs->items[1]), xn0);
        CHECK_NULL_2(or_xn0_xn1, OrN(2, xn0, xn1), xn0, xn1);
        BoolExpr_DecRef(xn0);
        BoolExpr_DecRef(xn1);

        CHECK_NULL_1(or_x0_x1, OrN(2, op->data.xs->items[0], op->data.xs->items[1]), or_xn0_xn1);
        CHECK_NULL_2(y, AndN(2, or_xn0_xn1, or_x0_x1), or_xn0_xn1, or_x0_x1);
        BoolExpr_DecRef(or_xn0_xn1);
        BoolExpr_DecRef(or_x0_x1);
    }
    else {
        size_t mid = op->data.xs->length / 2;
        size_t n0 = mid;
        size_t n1 = op->data.xs->length - mid;
        struct BoolExpr **items0 = op->data.xs->items;
        struct BoolExpr **items1 = op->data.xs->items + mid;
        struct BoolExpr *xs[2];
        struct BoolExpr *temp;

        /* Xor(a, b, c, d) <=> Xor(Xor(a, b), Xor(c, d)) */
        if (n0 == 1) {
            xs[0] = BoolExpr_IncRef(items0[0]);
        }
        else {
            CHECK_NULL(temp, Xor(n0, items0));
            CHECK_NULL_1(xs[0], _xor_nnfify(temp), temp);
            BoolExpr_DecRef(temp);
        }

        CHECK_NULL_1(temp, Xor(n1, items1), xs[0]);
        CHECK_NULL_2(xs[1], _xor_nnfify(temp), xs[0], temp);
        BoolExpr_DecRef(temp);

        CHECK_NULL_2(temp, Xor(2, xs), xs[0], xs[1]);
        BoolExpr_DecRef(xs[0]);
        BoolExpr_DecRef(xs[1]);

        CHECK_NULL_1(y, _xor_nnfify(temp), temp);
        BoolExpr_DecRef(temp);
    }

    return y;
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_xor_nnfify_disj(struct BoolExpr *op)
{
    struct BoolExpr *y;

    /* x0 ^ x1 <=> ~x0 & x1 | x0 & ~x1 */
    if (op->data.xs->length == 2) {
        struct BoolExpr *xn0, *xn1;
        struct BoolExpr *and_xn0_x1, *and_x0_xn1;

        CHECK_NULL(xn0, Not(op->data.xs->items[0]));
        CHECK_NULL_1(and_xn0_x1, AndN(2, xn0, op->data.xs->items[1]), xn0);
        BoolExpr_DecRef(xn0);

        CHECK_NULL_1(xn1, Not(op->data.xs->items[1]), and_xn0_x1);
        CHECK_NULL_2(and_x0_xn1, AndN(2, op->data.xs->items[0], xn1), xn1, and_xn0_x1);
        BoolExpr_DecRef(xn1);

        CHECK_NULL_2(y, OrN(2, and_xn0_x1, and_x0_xn1), and_xn0_x1, and_x0_xn1);
        BoolExpr_DecRef(and_xn0_x1);
        BoolExpr_DecRef(and_x0_xn1);
    }
    else {
        size_t mid = op->data.xs->length / 2;
        size_t n0 = mid;
        size_t n1 = op->data.xs->length - mid;
        struct BoolExpr **items0 = op->data.xs->items;
        struct BoolExpr **items1 = op->data.xs->items + mid;
        struct BoolExpr *xs[2];
        struct BoolExpr *temp;

        if (n0 == 1) {
            xs[0] = BoolExpr_IncRef(items0[0]);
        }
        else {
            CHECK_NULL(temp, Xor(n0, items0));
            CHECK_NULL_1(xs[0], _xor_nnfify(temp), temp);
            BoolExpr_DecRef(temp);
        }

        CHECK_NULL_1(temp, Xor(n1, items1), xs[0]);
        CHECK_NULL_2(xs[1], _xor_nnfify(temp), xs[0], temp);
        BoolExpr_DecRef(temp);

        CHECK_NULL_2(temp, Xor(2, xs), xs[0], xs[1]);
        BoolExpr_DecRef(xs[0]);
        BoolExpr_DecRef(xs[1]);

        CHECK_NULL_1(y, _xor_nnfify(temp), temp);
        BoolExpr_DecRef(temp);
    }

    return y;
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_xor_nnfify(struct BoolExpr *op)
{
    unsigned int num_ors = 0;
    unsigned int num_ands = 0;

    for (size_t i = 0; i < op->data.xs->length; ++i) {
        if (IS_OR(op->data.xs->items[i]))
            num_ors += 1;
        else if (IS_AND(op->data.xs->items[i]))
            num_ands += 1;
    }

    if (num_ors > num_ands)
        return _xor_nnfify_conj(op);
    else
        return _xor_nnfify_disj(op);
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_eq_nnfify(struct BoolExpr *op)
{
    int length = op->data.xs->length;
    struct BoolExpr **xs = op->data.xs->items;
    struct BoolExpr *xns[length];
    struct BoolExpr *all0, *all1;
    struct BoolExpr *y;

    /* Equal(x0, x1, x2) <=> ~x0 & ~x1 & ~x2 | x0 & x1 & x2 */
    for (size_t i = 0; i < length; ++i)
        CHECK_NULL_N(xns[i], Not(xs[i]), i, xns);
    CHECK_NULL_N(all0, And(length, xns), length, xns);
    for (size_t i = 0; i < length; ++i)
        BoolExpr_DecRef(xns[i]);

    CHECK_NULL_1(all1, And(length, xs), all0);

    CHECK_NULL_2(y, OrN(2, all0, all1), all0, all1);
    BoolExpr_DecRef(all0);
    BoolExpr_DecRef(all1);

    return y;
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_impl_nnfify(struct BoolExpr *op)
{
    struct BoolExpr *p, *q;
    struct BoolExpr *pn;
    struct BoolExpr *y;

    p = op->data.xs->items[0];
    q = op->data.xs->items[1];

    /* p => q <=> ~p | q */
    CHECK_NULL(pn, Not(p));
    CHECK_NULL_1(y, OrN(2, pn, q), pn);
    BoolExpr_DecRef(pn);

    return y;
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_ite_nnfify_conj(struct BoolExpr *op)
{
    struct BoolExpr *s, *d1, *d0;
    struct BoolExpr *sn;
    struct BoolExpr *or_sn_d1, *or_s_d0;
    struct BoolExpr *y;

    s = op->data.xs->items[0];
    d1 = op->data.xs->items[1];
    d0 = op->data.xs->items[2];

    /* s ? d1 : d0 <=> (~s | d1) & (s | d0) */
    CHECK_NULL(sn, Not(s));
    CHECK_NULL_1(or_sn_d1, OrN(2, sn, d1), sn);
    BoolExpr_DecRef(sn);

    CHECK_NULL_1(or_s_d0, OrN(2, s, d0), or_sn_d1);

    CHECK_NULL_2(y, AndN(2, or_sn_d1, or_s_d0), or_sn_d1, or_s_d0);
    BoolExpr_DecRef(or_sn_d1);
    BoolExpr_DecRef(or_s_d0);

    return y;
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_ite_nnfify_disj(struct BoolExpr *op)
{
    struct BoolExpr *s, *d1, *d0;
    struct BoolExpr *sn;
    struct BoolExpr *and_s_d1, *and_sn_d0;
    struct BoolExpr *y;

    s = op->data.xs->items[0];
    d1 = op->data.xs->items[1];
    d0 = op->data.xs->items[2];

    /* s ? d1 : d0 <=> s & d1 | ~s & d0 */
    CHECK_NULL(and_s_d1, AndN(2, s, d1));

    CHECK_NULL(sn, Not(s));
    CHECK_NULL_1(and_sn_d0, AndN(2, sn, d0), sn);
    BoolExpr_DecRef(sn);

    CHECK_NULL_2(y, OrN(2, and_s_d1, and_sn_d0), and_s_d1, and_sn_d0);
    BoolExpr_DecRef(and_s_d1);
    BoolExpr_DecRef(and_sn_d0);

    return y;
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_ite_nnfify(struct BoolExpr *op)
{
    unsigned int num_ors = 0;
    unsigned int num_ands = 0;

    for (size_t i = 0; i < 3; ++i) {
        if (IS_OR(op->data.xs->items[i]))
            num_ors += 1;
        else if (IS_AND(op->data.xs->items[i]))
            num_ands += 1;
    }

    if (num_ors > num_ands)
        return _ite_nnfify_conj(op);
    else
        return _ite_nnfify_disj(op);
}


static struct BoolExpr * (*_op_nnfify[16])(struct BoolExpr *op) = {
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,

    _orandnot_nnfify,
    _orandnot_nnfify,
    _xor_nnfify,
    _eq_nnfify,

    _orandnot_nnfify,
    _impl_nnfify,
    _ite_nnfify,
    NULL,
};


struct BoolExpr *
_nnfify(struct BoolExpr *ex)
{
    struct BoolExpr *y;

    if (IS_NNF(ex)) {
        y = BoolExpr_IncRef(ex);
    }
    else {
        struct BoolExpr *temp;

        CHECK_NULL(temp, _op_transform(ex, _nnfify));
        CHECK_NULL_1(y, _op_nnfify[temp->type](temp), temp);
        BoolExpr_DecRef(temp);
    }

    return y;
}


struct BoolExpr *
_to_nnf(struct BoolExpr *ex)
{
    struct BoolExpr *t0, *t1;
    struct BoolExpr *nnf;

    CHECK_NULL(t0, _nnfify(ex));

    CHECK_NULL_1(t1, BoolExpr_PushDownNot(t0), t0);
    BoolExpr_DecRef(t0);

    CHECK_NULL_1(nnf, _simplify(t1), t1);
    BoolExpr_DecRef(t1);

    return nnf;
}


struct BoolExpr *
BoolExpr_ToNNF(struct BoolExpr *ex)
{
    struct BoolExpr *nnf;

    CHECK_NULL(nnf, _to_nnf(ex));

    _mark_flags(nnf, NNF | SIMPLE);

    return nnf;
}

