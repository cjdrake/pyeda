/*
** Filename: nnf.c
**
** Negation Normal Form
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"
#include "memcheck.h"


/* nnf.c */
static struct BoolExpr * _xor_nnfify(struct BoolExpr *op);

/* simple.c */
struct BoolExpr * _simplify(struct BoolExpr *ex);

/* util.c */
struct BoolExpr * _op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *));
void _free_exs(int n, struct BoolExpr **exs);
void _mark_flags(struct BoolExpr *ex, BX_Flags f);


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_orandnot_nnfify(struct BoolExpr *op)
{
    return BX_IncRef(op);
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

        CHECK_NULL(xn0, BX_Not(op->data.xs->items[0]));
        CHECK_NULL_1(xn1, BX_Not(op->data.xs->items[1]), xn0);
        CHECK_NULL_2(or_xn0_xn1, BX_OrN(2, xn0, xn1), xn0, xn1);
        BX_DecRef(xn0);
        BX_DecRef(xn1);
        CHECK_NULL_1(or_x0_x1, BX_OrN(2, op->data.xs->items[0], op->data.xs->items[1]), or_xn0_xn1);
        y = BX_AndN(2, or_xn0_xn1, or_x0_x1);
        BX_DecRef(or_xn0_xn1);
        BX_DecRef(or_x0_x1);

        return y;
    }

    size_t mid = op->data.xs->length / 2;
    size_t n0 = mid;
    size_t n1 = op->data.xs->length - mid;
    struct BoolExpr **items0 = op->data.xs->items;
    struct BoolExpr **items1 = op->data.xs->items + mid;
    struct BoolExpr *xs[2];
    struct BoolExpr *temp;

    /* Xor(a, b, c, d) <=> Xor(Xor(a, b), Xor(c, d)) */
    if (n0 == 1) {
        xs[0] = BX_IncRef(items0[0]);
    }
    else {
        CHECK_NULL(temp, BX_Xor(n0, items0));
        CHECK_NULL_1(xs[0], _xor_nnfify(temp), temp);
        BX_DecRef(temp);
    }

    CHECK_NULL_1(temp, BX_Xor(n1, items1), xs[0]);
    CHECK_NULL_2(xs[1], _xor_nnfify(temp), xs[0], temp);
    BX_DecRef(temp);
    CHECK_NULL_2(temp, BX_Xor(2, xs), xs[0], xs[1]);
    BX_DecRef(xs[0]);
    BX_DecRef(xs[1]);
    y = _xor_nnfify(temp);
    BX_DecRef(temp);

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

        CHECK_NULL(xn0, BX_Not(op->data.xs->items[0]));
        CHECK_NULL_1(and_xn0_x1, BX_AndN(2, xn0, op->data.xs->items[1]), xn0);
        BX_DecRef(xn0);
        CHECK_NULL_1(xn1, BX_Not(op->data.xs->items[1]), and_xn0_x1);
        CHECK_NULL_2(and_x0_xn1, BX_AndN(2, op->data.xs->items[0], xn1), xn1, and_xn0_x1);
        BX_DecRef(xn1);
        y = BX_OrN(2, and_xn0_x1, and_x0_xn1);
        BX_DecRef(and_xn0_x1);
        BX_DecRef(and_x0_xn1);

        return y;
    }

    size_t mid = op->data.xs->length / 2;
    size_t n0 = mid;
    size_t n1 = op->data.xs->length - mid;
    struct BoolExpr **items0 = op->data.xs->items;
    struct BoolExpr **items1 = op->data.xs->items + mid;
    struct BoolExpr *xs[2];
    struct BoolExpr *temp;

    if (n0 == 1) {
        xs[0] = BX_IncRef(items0[0]);
    }
    else {
        CHECK_NULL(temp, BX_Xor(n0, items0));
        CHECK_NULL_1(xs[0], _xor_nnfify(temp), temp);
        BX_DecRef(temp);
    }

    CHECK_NULL_1(temp, BX_Xor(n1, items1), xs[0]);
    CHECK_NULL_2(xs[1], _xor_nnfify(temp), xs[0], temp);
    BX_DecRef(temp);
    CHECK_NULL_2(temp, BX_Xor(2, xs), xs[0], xs[1]);
    BX_DecRef(xs[0]);
    BX_DecRef(xs[1]);
    y = _xor_nnfify(temp);
    BX_DecRef(temp);

    return y;
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_xor_nnfify(struct BoolExpr *op)
{
    unsigned int num_ors = 0;
    unsigned int num_ands = 0;

    for (size_t i = 0; i < op->data.xs->length; ++i) {
        if (BX_IS_OR(op->data.xs->items[i]))
            num_ors += 1;
        else if (BX_IS_AND(op->data.xs->items[i]))
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
    struct BoolExpr **xns;
    struct BoolExpr *all0, *all1;
    struct BoolExpr *y;

    xns = malloc(length * sizeof(struct BoolExpr *));
    if (xns == NULL)
        return NULL; // LCOV_EXCL_LINE

    /* Equal(x0, x1, x2) <=> ~x0 & ~x1 & ~x2 | x0 & x1 & x2 */
    for (size_t i = 0; i < length; ++i)
        CHECK_NULL_N(xns[i], BX_Not(xs[i]), i, xns);

    CHECK_NULL_N(all0, BX_And(length, xns), length, xns);

    _free_exs(length, xns);

    CHECK_NULL_1(all1, BX_And(length, xs), all0);
    y = BX_OrN(2, all0, all1);
    BX_DecRef(all0);
    BX_DecRef(all1);

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
    CHECK_NULL(pn, BX_Not(p));
    y = BX_OrN(2, pn, q);
    BX_DecRef(pn);

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
    CHECK_NULL(sn, BX_Not(s));
    CHECK_NULL_1(or_sn_d1, BX_OrN(2, sn, d1), sn);
    BX_DecRef(sn);
    CHECK_NULL_1(or_s_d0, BX_OrN(2, s, d0), or_sn_d1);
    y = BX_AndN(2, or_sn_d1, or_s_d0);
    BX_DecRef(or_sn_d1);
    BX_DecRef(or_s_d0);

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
    CHECK_NULL(and_s_d1, BX_AndN(2, s, d1));
    CHECK_NULL(sn, BX_Not(s));
    CHECK_NULL_1(and_sn_d0, BX_AndN(2, sn, d0), sn);
    BX_DecRef(sn);
    y = BX_OrN(2, and_s_d1, and_sn_d0);
    BX_DecRef(and_s_d1);
    BX_DecRef(and_sn_d0);

    return y;
}


/* NOTE: assume operator arguments are already NNF */
static struct BoolExpr *
_ite_nnfify(struct BoolExpr *op)
{
    unsigned int num_ors = 0;
    unsigned int num_ands = 0;

    for (size_t i = 0; i < 3; ++i) {
        if (BX_IS_OR(op->data.xs->items[i]))
            num_ors += 1;
        else if (BX_IS_AND(op->data.xs->items[i]))
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
    if (BX_IS_NNF(ex))
        return BX_IncRef(ex);

    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, _op_transform(ex, _nnfify));
    y = _op_nnfify[temp->kind](temp);
    BX_DecRef(temp);

    return y;
}


struct BoolExpr *
_to_nnf(struct BoolExpr *ex)
{
    struct BoolExpr *t0, *t1;
    struct BoolExpr *nnf;

    CHECK_NULL(t0, _nnfify(ex));

    CHECK_NULL_1(t1, BX_PushDownNot(t0), t0);
    BX_DecRef(t0);

    CHECK_NULL_1(nnf, _simplify(t1), t1);
    BX_DecRef(t1);

    return nnf;
}


struct BoolExpr *
BX_ToNNF(struct BoolExpr *ex)
{
    struct BoolExpr *nnf;

    CHECK_NULL(nnf, _to_nnf(ex));

    _mark_flags(nnf, BX_NNF | BX_SIMPLE);

    return nnf;
}

