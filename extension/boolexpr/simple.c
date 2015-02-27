/*
** Filename: simple.c
**
** Simplification
**
** This is a recursive, two-step process.
**
** For constants, literals, operators that are already simple,
** just return the expression.
**
** Otherwise:
** 1. Simplify all operator arguments
** 2. Eliminate constants, and all sub-expressions that can be easily
**    converted to constants.
*/


#include <stdarg.h>

#include "boolexpr.h"

#define CMP(x, y) ((x) < (y) ? -1 : (x) > (y))


/* boolexpr.c */
BoolExpr * _op_new(BoolExprType t, size_t n, BoolExpr **xs);
BoolExpr * _orandxor_new(BoolExprType t, size_t n, BoolExpr **xs);

/* util.c */
BoolExpr * _op_transform(BoolExpr *op, BoolExpr * (*fn)(BoolExpr *));
void _mark_flags(BoolExpr *ex, BoolExprFlags f);

/* simple.c */
static BoolExpr * _simple_op(BoolExprType t, size_t n, BoolExpr **xs);
static BoolExpr * _simple_opn(BoolExprType t, size_t n, ...);


/* NOTE: Equality testing can get expensive, so keep it simple */
static bool
_eq(BoolExpr *a, BoolExpr *b)
{
    return (a == b);
}


/* Compare two nodes for qsort usage.
**
** Rules:
** 1. Literals are ordered ~a, ~a, a, a, ~b, ...
** 2. Nodes with same type are considered "equal".
** 3. Nodes with different types are ordered by type value.
**
** These rules make it easy to find (~x, x), and (x, x) arguments,
** which is useful for simplification.
*/
static int
_cmp(const void *p1, const void *p2)
{
    const BoolExpr *a = *((BoolExpr **) p1);
    const BoolExpr *b = *((BoolExpr **) p2);

    if (IS_LIT(a) && IS_LIT(b)) {
        long abs_a = labs(a->data.lit.uniqid);
        long abs_b = labs(b->data.lit.uniqid);

        if (abs_a < abs_b)
            return -1;
        else if (abs_a > abs_b)
            return 1;
        else
            return CMP(a->data.lit.uniqid, b->data.lit.uniqid);
    }
    else if (a->type == b->type) {
        return 0;
    }
    else {
        return CMP(a->type, b->type);
    }
}


static size_t
_count_assoc_args(BoolExpr *op)
{
    size_t count = 0;

    for (size_t i = 0; i < op->data.xs->length; ++i)
        if (op->data.xs->items[i]->type == op->type)
            count += op->data.xs->items[i]->data.xs->length;
        else
            count += 1;

    return count;
}


/* NOTE: assume operator arguments are already simple */
static BoolExpr *
_orand_simplify(BoolExpr *op)
{
    size_t count;
    size_t n = _count_assoc_args(op);
    BoolExpr *flat[n], *uniq[n];
    size_t flat_len, uniq_len;
    BoolExpr *y;

    /* 1. Flatten arguments, and eliminate {0, 1} */
    count = 0;
    for (size_t i = 0; i < op->data.xs->length; ++i) {
        BoolExpr *item_i = op->data.xs->items[i];
        /* Or(1, x) <=> 1 */
        if (item_i == DOMINATOR[op->type]) {
            y = BoolExpr_IncRef(DOMINATOR[op->type]);
            goto done;
        }
        /* Or(Or(x0, x1), x2) <=> Or(x0, x1, x2) */
        else if (item_i->type == op->type) {
            for (size_t j = 0; j < item_i->data.xs->length; ++j) {
                BoolExpr *item_j = item_i->data.xs->items[j];
                /* Or(1, x) <=> 1 */
                if (item_j == DOMINATOR[op->type]) {
                    y = BoolExpr_IncRef(DOMINATOR[op->type]);
                    goto done;
                }
                /* Or(0, x) <=> x */
                else if (item_j != IDENTITY[op->type]) {
                    flat[count++] = item_j;
                }
            }
        }
        /* Or(0, x) <=> x */
        else if (item_i != IDENTITY[op->type]) {
            flat[count++] = item_i;
        }
    }
    flat_len = count;

    /* 2. Sort arguments, so you get ~a, ~a, a, a, ~b, ... */
    qsort(flat, flat_len, sizeof(BoolExpr *), _cmp);

    /* 3. Apply: Or(~x, x) <=> 1, Or(x, x) <=> x */
    count = 0;
    for (size_t i = 0; i < flat_len; ++i) {
        if (count == 0) {
            uniq[count++] = flat[i];
        }
        else {
            /* Or(~x, x) <=> 1 */
            if (COMPLEMENTARY(uniq[count-1], flat[i])) {
                y = BoolExpr_IncRef(DOMINATOR[op->type]);
                goto done;
            }
            /* Or(x, x) <=> x */
            else if (!_eq(flat[i], uniq[count-1])) {
                uniq[count++] = flat[i];
            }
        }
    }
    uniq_len = count;

    CHECK_NULL(y, _orandxor_new(op->type, uniq_len, uniq));

done:

    return y;
}


/* NOTE: assume operator arguments are already simple */
static BoolExpr *
_xor_simplify(BoolExpr *op)
{
    size_t n = _count_assoc_args(op);
    size_t count;
    bool parity = true;
    BoolExpr *flat[n], *uniq[n];
    size_t flat_len, uniq_len;
    BoolExpr *y;

    /* 1. Flatten arguments, and eliminate {0, 1} */
    count = 0;
    for (size_t i = 0; i < op->data.xs->length; ++i) {
        BoolExpr *item_i = op->data.xs->items[i];
        if (IS_CONST(item_i)) {
            parity ^= (bool) item_i->type;
        }
        /* Xor(Xor(x0, x1), x2) <=> Xor(x0, x1, x2) */
        else if (item_i->type == op->type) {
            for (size_t j = 0; j < item_i->data.xs->length; ++j) {
                BoolExpr *item_j = item_i->data.xs->items[j];
                if (IS_CONST(item_j))
                    parity ^= (bool) item_j->type;
                else
                    flat[count++] = item_j;
            }
        }
        else {
            flat[count++] = item_i;
        }
    }
    flat_len = count;

    /* 2. Sort arguments, so you get ~a, ~a, a, a, ~b, ... */
    qsort(flat, flat_len, sizeof(BoolExpr *), _cmp);

    /* 3. Apply: Xor(~x, x) <=> 1, Xor(x, x) <=> 0 */
    count = 0;
    for (size_t i = 0; i < flat_len; ++i) {
        if (count == 0) {
            uniq[count++] = flat[i];
        }
        else {
            /* Xor(~x, x) <=> 1 */
            if (COMPLEMENTARY(uniq[count-1], flat[i])) {
                parity ^= true;
                count -= 1;
            }
            /* Xor(x, x) <=> 0 */
            else if (_eq(flat[i], uniq[count-1])) {
                count -= 1;
            }
            else {
                uniq[count++] = flat[i];
            }
        }
    }
    uniq_len = count;

    if (parity)
        CHECK_NULL(y, Xor(uniq_len, uniq));
    else
        CHECK_NULL(y, Xnor(uniq_len, uniq));

    return y;
}


/* NOTE: assumes arguments are already simple */
static BoolExpr *
_eq_simplify(BoolExpr *op)
{
    size_t count;
    bool found_zero = false;
    bool found_one = false;
    size_t length = op->data.xs->length;
    BoolExpr *flat[length];
    BoolExpr *uniq[length];
    size_t flat_len, uniq_len;
    BoolExpr *y;

    /* 1. Eliminate {0, 1} */
    count = 0;
    for (size_t i = 0; i < length; ++i) {
        BoolExpr *item_i = op->data.xs->items[i];
        if (IS_ZERO(item_i))
            found_zero = true;
        else if (IS_ONE(item_i))
            found_one = true;
        else
            flat[count++] = item_i;
    }
    flat_len = count;

    /* Equal(0, 1) <=> 0 */
    if (found_zero && found_one) {
        y = BoolExpr_IncRef(&Zero);
        goto done;
    }

    /* 2. Sort arguments, so you get ~a, ~a, a, a, ~b, ... */
    qsort(flat, flat_len, sizeof(BoolExpr *), _cmp);

    /* 3. Apply: Equal(~x, x) <=> 0, Equal(x0, x0, x1) <=> Equal(x0, x1) */
    count = 0;
    for (size_t i = 0; i < flat_len; ++i) {
        if (count == 0) {
            uniq[count++] = flat[i];
        }
        else {
            /* Equal(~x, x) <=> 0 */
            if (COMPLEMENTARY(uniq[count-1], flat[i])) {
                y = BoolExpr_IncRef(&Zero);
                goto done;
            }
            /* Equal(x0, x0, x1) <=> Equal(x0, x1) */
            else if (!_eq(flat[i], uniq[count-1])) {
                uniq[count++] = flat[i];
            }
        }
    }
    uniq_len = count;

    if (found_zero) {
        /* Equal(0) <=> 1 */
        if (uniq_len == 0) {
            y = BoolExpr_IncRef(&One);
        }
        /* Equal(0, x) <=> ~x */
        else if (uniq_len == 1) {
            CHECK_NULL(y, Not(uniq[0]));
        }
        /* Equal(0, x0, x1) <=> Nor(x0, x1) */
        else {
            BoolExpr *temp;
            CHECK_NULL(temp, _simple_op(OP_OR, uniq_len, uniq));
            CHECK_NULL_1(y, Not(temp), temp);
            BoolExpr_DecRef(temp);
        }
    }
    else if (found_one) {
        /* Equal(1) <=> 1 */
        if (uniq_len == 0) {
            y = BoolExpr_IncRef(&One);
        }
        /* Equal(1, x) <=> x */
        else if (uniq_len == 1) {
            y = BoolExpr_IncRef(uniq[0]);
        }
        /* Equal(1, x0, ...) <=> Nand(x0, ...) */
        else {
            BoolExpr *temp;
            CHECK_NULL(temp, _simple_op(OP_AND, uniq_len, uniq));
            CHECK_NULL_1(y, Not(temp), temp);
            BoolExpr_DecRef(temp);
        }
    }
    else {
        CHECK_NULL(y, Equal(uniq_len, uniq));
    }

done:

    return y;
}


/* NOTE: assumes arguments are already simple */
static BoolExpr *
_not_simplify(BoolExpr *op)
{
    BoolExpr *x = op->data.xs->items[0];
    BoolExpr *y;

    CHECK_NULL(y, Not(x));

    return y;
}


/* NOTE: assumes arguments are already simple */
static BoolExpr *
_impl_simplify(BoolExpr *op)
{
    BoolExpr *p = op->data.xs->items[0];
    BoolExpr *q = op->data.xs->items[1];
    BoolExpr *y;

    /* Implies(0, q) <=> Implies(p, 1) <=> 1 */
    if (IS_ZERO(p) || IS_ONE(q))
        y = BoolExpr_IncRef(&One);
    /* Implies(1, q) <=> q */
    else if (IS_ONE(p))
        y = BoolExpr_IncRef(q);
    /* Implies(p, 0) <=> ~p */
    else if (IS_ZERO(q))
        CHECK_NULL(y, Not(p));
    /* Implies(p, p) <=> 1 */
    else if (_eq(p, q))
        y = BoolExpr_IncRef(&One);
    /* Implies(~p, p) <=> p */
    else if (COMPLEMENTARY(p, q))
        y = BoolExpr_IncRef(q);
    else
        CHECK_NULL(y, Implies(p, q));

    return y;
}


/* NOTE: assumes arguments are already simple */
static BoolExpr *
_ite_simplify(BoolExpr *op)
{
    BoolExpr *s = op->data.xs->items[0];
    BoolExpr *d1 = op->data.xs->items[1];
    BoolExpr *d0 = op->data.xs->items[2];
    BoolExpr *y;

    /* ITE(0, d1, d0) <=> d0 */
    if (IS_ZERO(s)) {
        y = BoolExpr_IncRef(d0);
    }
    /* ITE(1, d1, d0) <=> d1 */
    else if (IS_ONE(s)) {
        y = BoolExpr_IncRef(d1);
    }
    else if (IS_ZERO(d1)) {
        /* ITE(s, 0, 0) <=> 0 */
        if (IS_ZERO(d0)) {
            y = BoolExpr_IncRef(&Zero);
        }
        /* ITE(s, 0, 1) <=> ~s */
        else if (IS_ONE(d0)) {
            CHECK_NULL(y, Not(s));
        }
        /* ITE(s, 0, d0) <=> And(~s, d0) */
        else {
            BoolExpr *sn;
            CHECK_NULL(sn, Not(s));
            CHECK_NULL_1(y, _simple_opn(OP_AND, 2, sn, d0), sn);
            BoolExpr_DecRef(sn);
        }
    }
    else if (IS_ONE(d1)) {
        /* ITE(s, 1, 0) <=> s */
        if (IS_ZERO(d0))
            y = BoolExpr_IncRef(s);
        /* ITE(s, 1, 1) <=> 1 */
        else if (IS_ONE(d0))
            y = BoolExpr_IncRef(&One);
        /* ITE(s, 1, d0) <=> Or(s, d0) */
        else
            CHECK_NULL(y, _simple_opn(OP_OR, 2, s, d0));
    }
    /* ITE(s, d1, 0) <=> And(s, d1) */
    else if (IS_ZERO(d0)) {
        CHECK_NULL(y, _simple_opn(OP_AND, 2, s, d1));
    }
    /* ITE(s, d1, 1) <=> Or(~s, d1) */
    else if (IS_ONE(d0)) {
        BoolExpr *sn;
        CHECK_NULL(sn, Not(s));
        CHECK_NULL_1(y, _simple_opn(OP_OR, 2, sn, d1), sn);
        BoolExpr_DecRef(sn);
    }
    /* ITE(s, d1, d1) <=> d1 */
    else if (_eq(d1, d0)) {
        y = BoolExpr_IncRef(d1);
    }
    /* ITE(s, s, d0) <=> Or(s, d0) */
    else if (_eq(s, d1)) {
        CHECK_NULL(y, _simple_opn(OP_OR, 2, s, d0));
    }
    /* ITE(s, d1, s) <=> And(s, d1) */
    else if (_eq(s, d0)) {
        CHECK_NULL(y, _simple_opn(OP_AND, 2, s, d1));
    }
    else {
        CHECK_NULL(y, ITE(s, d1, d0));
    }

    return y;
}


static BoolExpr * (*_op_simplify[16])(BoolExpr *op) = {
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,

    _orand_simplify,
    _orand_simplify,
    _xor_simplify,
    _eq_simplify,

    _not_simplify,
    _impl_simplify,
    _ite_simplify,
    NULL,
};


static BoolExpr *
_simple_op(BoolExprType t, size_t n, BoolExpr **xs)
{
    BoolExpr *temp;
    BoolExpr *y;

    CHECK_NULL(temp, _op_new(t, n, xs));
    CHECK_NULL_1(y, _op_simplify[t](temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


static BoolExpr *
_simple_opn(BoolExprType t, size_t n, ...)
{
    BoolExpr *xs[n];
    va_list vl;

    va_start(vl, n);
    for (int i = 0; i < n; ++i)
        xs[i] = va_arg(vl, BoolExpr *);
    va_end(vl);

    return _simple_op(t, n, xs);
}


BoolExpr *
_simplify(BoolExpr *ex)
{
    BoolExpr *y;

    if (IS_SIMPLE(ex)) {
        y = BoolExpr_IncRef(ex);
    }
    else {
        BoolExpr *temp;

        CHECK_NULL(temp, _op_transform(ex, _simplify));
        CHECK_NULL_1(y, _op_simplify[temp->type](temp), temp);
        BoolExpr_DecRef(temp);
    }

    return y;
}


BoolExpr *
BoolExpr_Simplify(BoolExpr *ex)
{
    BoolExpr *y;

    CHECK_NULL(y, _simplify(ex));

    _mark_flags(y, SIMPLE);

    return y;
}

