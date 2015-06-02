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
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"

#define CMP(x, y) ((x) < (y) ? -1 : (x) > (y))


/* boolexpr.c */
struct BoolExpr * _op_new(BoolExprKind kind, size_t n, struct BoolExpr **xs);
struct BoolExpr * _orandxor_new(BoolExprKind kind, size_t n, struct BoolExpr **xs);

/* util.c */
struct BoolExpr * _op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *));
void _mark_flags(struct BoolExpr *ex, BoolExprFlags f);

/* simple.c */
static struct BoolExpr * _simple_op(BoolExprKind kind, size_t n, struct BoolExpr **xs);
static struct BoolExpr * _simple_opn(BoolExprKind kind, size_t n, ...);


/* NOTE: Equality testing can get expensive, so keep it simple */
static bool
_eq(struct BoolExpr *a, struct BoolExpr *b)
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
    const struct BoolExpr *a = *((struct BoolExpr **) p1);
    const struct BoolExpr *b = *((struct BoolExpr **) p2);

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
    else if (a->kind == b->kind) {
        return 0;
    }
    else {
        return CMP(a->kind, b->kind);
    }
}


static size_t
_count_assoc_args(struct BoolExpr *op)
{
    size_t count = 0;

    for (size_t i = 0; i < op->data.xs->length; ++i)
        if (op->data.xs->items[i]->kind == op->kind)
            count += op->data.xs->items[i]->data.xs->length;
        else
            count += 1;

    return count;
}


/* NOTE: assume operator arguments are already simple */
static struct BoolExpr *
_orand_simplify(struct BoolExpr *op)
{
    size_t n = _count_assoc_args(op);
    struct BoolExpr **flat;
    size_t flat_len = 0;
    struct BoolExpr **uniq;
    size_t uniq_len = 0;
    struct BoolExpr *y;

    flat = malloc(n * sizeof(struct BoolExpr *));

    /* 1. Flatten arguments, and eliminate {0, 1} */
    for (size_t i = 0; i < op->data.xs->length; ++i) {
        struct BoolExpr *item_i = op->data.xs->items[i];
        /* Or(1, x) <=> 1 */
        if (item_i == DOMINATOR[op->kind]) {
            free(flat);
            return BoolExpr_IncRef(DOMINATOR[op->kind]);
        }
        /* Or(Or(x0, x1), x2) <=> Or(x0, x1, x2) */
        else if (item_i->kind == op->kind) {
            for (size_t j = 0; j < item_i->data.xs->length; ++j) {
                struct BoolExpr *item_j = item_i->data.xs->items[j];
                /* Or(1, x) <=> 1 */
                if (item_j == DOMINATOR[op->kind]) {
                    free(flat);
                    return BoolExpr_IncRef(DOMINATOR[op->kind]);
                }
                /* Or(0, x) <=> x */
                else if (item_j != IDENTITY[op->kind]) {
                    flat[flat_len++] = item_j;
                }
            }
        }
        /* Or(0, x) <=> x */
        else if (item_i != IDENTITY[op->kind]) {
            flat[flat_len++] = item_i;
        }
    }

    /* 2. Sort arguments, so you get ~a, ~a, a, a, ~b, ... */
    qsort(flat, flat_len, sizeof(struct BoolExpr *), _cmp);

    uniq = malloc(flat_len * sizeof(struct BoolExpr *));

    /* 3. Apply: Or(~x, x) <=> 1, Or(x, x) <=> x */
    for (size_t i = 0; i < flat_len; ++i) {
        if (uniq_len == 0) {
            uniq[uniq_len++] = flat[i];
        }
        else {
            /* Or(~x, x) <=> 1 */
            if (COMPLEMENTARY(uniq[uniq_len-1], flat[i])) {
                free(flat);
                free(uniq);
                return BoolExpr_IncRef(DOMINATOR[op->kind]);
            }
            /* Or(x, x) <=> x */
            else if (!_eq(flat[i], uniq[uniq_len-1])) {
                uniq[uniq_len++] = flat[i];
            }
        }
    }

    free(flat);

    y = _orandxor_new(op->kind, uniq_len, uniq);

    free(uniq);

    return y;
}


/* NOTE: assume operator arguments are already simple */
static struct BoolExpr *
_xor_simplify(struct BoolExpr *op)
{
    bool parity = true;

    size_t n = _count_assoc_args(op);
    struct BoolExpr **flat;
    size_t flat_len = 0;
    struct BoolExpr **uniq;
    size_t uniq_len = 0;
    struct BoolExpr *y;

    flat = malloc(n * sizeof(struct BoolExpr *));

    /* 1. Flatten arguments, and eliminate {0, 1} */
    for (size_t i = 0; i < op->data.xs->length; ++i) {
        struct BoolExpr *item_i = op->data.xs->items[i];
        if (IS_CONST(item_i)) {
            parity ^= (bool) item_i->kind;
        }
        /* Xor(Xor(x0, x1), x2) <=> Xor(x0, x1, x2) */
        else if (item_i->kind == op->kind) {
            for (size_t j = 0; j < item_i->data.xs->length; ++j) {
                struct BoolExpr *item_j = item_i->data.xs->items[j];
                if (IS_CONST(item_j))
                    parity ^= (bool) item_j->kind;
                else
                    flat[flat_len++] = item_j;
            }
        }
        else {
            flat[flat_len++] = item_i;
        }
    }

    /* 2. Sort arguments, so you get ~a, ~a, a, a, ~b, ... */
    qsort(flat, flat_len, sizeof(struct BoolExpr *), _cmp);

    uniq = malloc(flat_len * sizeof(struct BoolExpr *));

    /* 3. Apply: Xor(~x, x) <=> 1, Xor(x, x) <=> 0 */
    for (size_t i = 0; i < flat_len; ++i) {
        if (uniq_len == 0) {
            uniq[uniq_len++] = flat[i];
        }
        else {
            /* Xor(~x, x) <=> 1 */
            if (COMPLEMENTARY(uniq[uniq_len-1], flat[i])) {
                parity ^= true;
                uniq_len -= 1;
            }
            /* Xor(x, x) <=> 0 */
            else if (_eq(flat[i], uniq[uniq_len-1])) {
                uniq_len -= 1;
            }
            else {
                uniq[uniq_len++] = flat[i];
            }
        }
    }

    free(flat);

    y = parity ? Xor(uniq_len, uniq) : Xnor(uniq_len, uniq);

    free(uniq);

    return y;
}


/* NOTE: assumes arguments are already simple */
static struct BoolExpr *
_eq_simplify(struct BoolExpr *op)
{
    bool found_zero = false;
    bool found_one = false;

    size_t length = op->data.xs->length;
    struct BoolExpr **flat;
    size_t flat_len = 0;
    struct BoolExpr **uniq;
    size_t uniq_len = 0;
    struct BoolExpr *y;

    flat = malloc(length * sizeof(struct BoolExpr *));

    /* 1. Eliminate {0, 1} */
    for (size_t i = 0; i < length; ++i) {
        struct BoolExpr *item_i = op->data.xs->items[i];
        if (IS_ZERO(item_i))
            found_zero = true;
        else if (IS_ONE(item_i))
            found_one = true;
        else
            flat[flat_len++] = item_i;
    }

    /* Equal(0, 1) <=> 0 */
    if (found_zero && found_one) {
        free(flat);
        return BoolExpr_IncRef(&Zero);
    }

    /* 2. Sort arguments, so you get ~a, ~a, a, a, ~b, ... */
    qsort(flat, flat_len, sizeof(struct BoolExpr *), _cmp);

    uniq = malloc(flat_len * sizeof(struct BoolExpr *));

    /* 3. Apply: Equal(~x, x) <=> 0, Equal(x0, x0, x1) <=> Equal(x0, x1) */
    for (size_t i = 0; i < flat_len; ++i) {
        if (uniq_len == 0) {
            uniq[uniq_len++] = flat[i];
        }
        else {
            /* Equal(~x, x) <=> 0 */
            if (COMPLEMENTARY(uniq[uniq_len-1], flat[i])) {
                free(flat);
                free(uniq);
                return BoolExpr_IncRef(&Zero);
            }
            /* Equal(x0, x0, x1) <=> Equal(x0, x1) */
            else if (!_eq(flat[i], uniq[uniq_len-1]))
                uniq[uniq_len++] = flat[i];
        }
    }

    free(flat);

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
            struct BoolExpr *temp;
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
            struct BoolExpr *temp;
            CHECK_NULL(temp, _simple_op(OP_AND, uniq_len, uniq));
            CHECK_NULL_1(y, Not(temp), temp);
            BoolExpr_DecRef(temp);
        }
    }
    else {
        CHECK_NULL(y, Equal(uniq_len, uniq));
    }

    free(uniq);

    return y;
}


/* NOTE: assumes arguments are already simple */
static struct BoolExpr *
_not_simplify(struct BoolExpr *op)
{
    return Not(op->data.xs->items[0]);
}


/* NOTE: assumes arguments are already simple */
static struct BoolExpr *
_impl_simplify(struct BoolExpr *op)
{
    struct BoolExpr *p = op->data.xs->items[0];
    struct BoolExpr *q = op->data.xs->items[1];

    /* Implies(0, q) <=> Implies(p, 1) <=> 1 */
    if (IS_ZERO(p) || IS_ONE(q))
        return BoolExpr_IncRef(&One);

    /* Implies(1, q) <=> q */
    if (IS_ONE(p))
        return BoolExpr_IncRef(q);

    /* Implies(p, 0) <=> ~p */
    if (IS_ZERO(q))
        return Not(p);

    /* Implies(p, p) <=> 1 */
    if (_eq(p, q))
        return BoolExpr_IncRef(&One);

    /* Implies(~p, p) <=> p */
    if (COMPLEMENTARY(p, q))
        return BoolExpr_IncRef(q);

    return Implies(p, q);
}


/* NOTE: assumes arguments are already simple */
static struct BoolExpr *
_ite_simplify(struct BoolExpr *op)
{
    struct BoolExpr *s = op->data.xs->items[0];
    struct BoolExpr *d1 = op->data.xs->items[1];
    struct BoolExpr *d0 = op->data.xs->items[2];

    struct BoolExpr *y;

    /* ITE(0, d1, d0) <=> d0 */
    if (IS_ZERO(s))
        return BoolExpr_IncRef(d0);

    /* ITE(1, d1, d0) <=> d1 */
    if (IS_ONE(s))
        return BoolExpr_IncRef(d1);

    if (IS_ZERO(d1)) {
        /* ITE(s, 0, 0) <=> 0 */
        if (IS_ZERO(d0))
            return BoolExpr_IncRef(&Zero);

        /* ITE(s, 0, 1) <=> ~s */
        if (IS_ONE(d0))
            return Not(s);

        /* ITE(s, 0, d0) <=> And(~s, d0) */
        struct BoolExpr *sn;
        CHECK_NULL(sn, Not(s));
        CHECK_NULL_1(y, _simple_opn(OP_AND, 2, sn, d0), sn);
        BoolExpr_DecRef(sn);
        return y;
    }

    if (IS_ONE(d1)) {
        /* ITE(s, 1, 0) <=> s */
        if (IS_ZERO(d0))
            return BoolExpr_IncRef(s);

        /* ITE(s, 1, 1) <=> 1 */
        if (IS_ONE(d0))
            return BoolExpr_IncRef(&One);
        /* ITE(s, 1, d0) <=> Or(s, d0) */
        return _simple_opn(OP_OR, 2, s, d0);
    }

    /* ITE(s, d1, 0) <=> And(s, d1) */
    if (IS_ZERO(d0))
        return _simple_opn(OP_AND, 2, s, d1);

    /* ITE(s, d1, 1) <=> Or(~s, d1) */
    if (IS_ONE(d0)) {
        struct BoolExpr *sn;
        CHECK_NULL(sn, Not(s));
        CHECK_NULL_1(y, _simple_opn(OP_OR, 2, sn, d1), sn);
        BoolExpr_DecRef(sn);
        return y;
    }

    /* ITE(s, d1, d1) <=> d1 */
    if (_eq(d1, d0))
        return BoolExpr_IncRef(d1);

    /* ITE(s, s, d0) <=> Or(s, d0) */
    if (_eq(s, d1))
        return _simple_opn(OP_OR, 2, s, d0);

    /* ITE(s, d1, s) <=> And(s, d1) */
    if (_eq(s, d0))
        return _simple_opn(OP_AND, 2, s, d1);

    return ITE(s, d1, d0);
}


static struct BoolExpr * (*_op_simplify[16])(struct BoolExpr *op) = {
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


static struct BoolExpr *
_simple_op(BoolExprKind kind, size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, _op_new(kind, n, xs));
    CHECK_NULL_1(y, _op_simplify[kind](temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


static struct BoolExpr *
_simple_opn(BoolExprKind kind, size_t n, ...)
{
    struct BoolExpr *xs[n];
    va_list vl;

    va_start(vl, n);
    for (int i = 0; i < n; ++i)
        xs[i] = va_arg(vl, struct BoolExpr *);
    va_end(vl);

    return _simple_op(kind, n, xs);
}


struct BoolExpr *
_simplify(struct BoolExpr *ex)
{
    struct BoolExpr *y;

    if (IS_SIMPLE(ex)) {
        y = BoolExpr_IncRef(ex);
    }
    else {
        struct BoolExpr *temp;
        CHECK_NULL(temp, _op_transform(ex, _simplify));
        CHECK_NULL_1(y, _op_simplify[temp->kind](temp), temp);
        BoolExpr_DecRef(temp);
    }

    return y;
}


struct BoolExpr *
BoolExpr_Simplify(struct BoolExpr *ex)
{
    struct BoolExpr *y;

    CHECK_NULL(y, _simplify(ex));

    _mark_flags(y, SIMPLE);

    return y;
}

