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

#define COMPLEMENTARY(x, y) \
    (IS_LIT(x) && IS_LIT(y) && \
     ((x)->data.lit.uniqid == -((y)->data.lit.uniqid)))


/* boolexpr.c */
struct BoolExpr * _op_new(BX_Kind kind, size_t n, struct BoolExpr **xs);
struct BoolExpr * _orandxor_new(BX_Kind kind, size_t n, struct BoolExpr **xs);

/* util.c */
struct BoolExpr * _op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *));
void _mark_flags(struct BoolExpr *ex, BX_Flags f);

/* simple.c */
static struct BoolExpr * _simple_op(BX_Kind kind, size_t n, struct BoolExpr **xs);
static struct BoolExpr * _simple_op2(BX_Kind kind, struct BoolExpr *x0, struct BoolExpr *x1);
static struct BoolExpr * _simple_nop(BX_Kind kind, size_t n, struct BoolExpr **xs);


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
_count_orand_args(struct BoolExpr *op)
{
    size_t count = 0;

    for (size_t i = 0; i < op->data.xs->length; ++i) {
        if (op->data.xs->items[i]->kind == op->kind)
            count += op->data.xs->items[i]->data.xs->length;
        else
            count += 1;
    }

    return count;
}


/* NOTE: assume operator arguments are already simple */
static struct BoolExpr *
_orand_simplify(struct BoolExpr *op)
{
    size_t n = _count_orand_args(op);
    struct BoolExpr **flat;
    size_t flat_len = 0;
    struct BoolExpr **uniq;
    size_t uniq_len = 0;
    struct BoolExpr *xi, *xj;
    struct BoolExpr *y;

    flat = malloc(n * sizeof(struct BoolExpr *));
    if (flat == NULL)
        return NULL; // LCOV_EXCL_LINE

    /* 1. Flatten arguments, and eliminate {0, 1} */
    for (size_t i = 0; i < op->data.xs->length; ++i) {
        xi = op->data.xs->items[i];
        /* Or(1, x) <=> 1 */
        if (xi == DOMINATOR[op->kind]) {
            free(flat);
            return BX_IncRef(DOMINATOR[op->kind]);
        }
        /* Or(Or(x0, x1), x2) <=> Or(x0, x1, x2) */
        else if (xi->kind == op->kind) {
            for (size_t j = 0; j < xi->data.xs->length; ++j) {
                xj = xi->data.xs->items[j];
                /* Or(1, x) <=> 1 */
                if (xj == DOMINATOR[op->kind]) {
                    free(flat);
                    return BX_IncRef(DOMINATOR[op->kind]);
                }
                /* Or(0, x) <=> x */
                else if (xj != IDENTITY[op->kind]) {
                    flat[flat_len++] = xj;
                }
            }
        }
        /* Or(0, x) <=> x */
        else if (xi != IDENTITY[op->kind]) {
            flat[flat_len++] = xi;
        }
    }

    /* 2. Sort arguments, so you get ~a, ~a, a, a, ~b, ... */
    qsort(flat, flat_len, sizeof(struct BoolExpr *), _cmp);

    uniq = malloc(flat_len * sizeof(struct BoolExpr *));
    if (uniq == NULL) {
        free(flat);  // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

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
                return BX_IncRef(DOMINATOR[op->kind]);
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


static size_t
_count_xor_args(struct BoolExpr *op)
{
    size_t count = 0;

    for (size_t i = 0; i < op->data.xs->length; ++i) {
        if (IS_XOR(op->data.xs->items[i]))
            count += op->data.xs->items[i]->data.xs->length;
        else if (IS_NOT(op->data.xs->items[i]) &&
                 IS_XOR(op->data.xs->items[i]->data.xs->items[0]))
            count += op->data.xs->items[i]->data.xs->items[0]->data.xs->length;
        else
            count += 1;
    }

    return count;
}


/* NOTE: assume operator arguments are already simple */
static struct BoolExpr *
_xor_simplify(struct BoolExpr *op)
{
    bool parity = true;

    size_t n = _count_xor_args(op);
    struct BoolExpr **flat;
    size_t flat_len = 0;
    struct BoolExpr **uniq;
    size_t uniq_len = 0;
    struct BoolExpr *xi, *xj;
    struct BoolExpr *y;

    flat = malloc(n * sizeof(struct BoolExpr *));
    if (flat == NULL)
        return NULL; // LCOV_EXCL_LINE

    /* 1. Flatten arguments, and eliminate {0, 1} */
    for (size_t i = 0; i < op->data.xs->length; ++i) {
        xi = op->data.xs->items[i];
        if (IS_CONST(xi)) {
            parity ^= (bool) xi->kind;
        }
        /* Xor(Xor(x0, x1), x2) <=> Xor(x0, x1, x2) */
        else if (IS_XOR(xi)) {
            for (size_t j = 0; j < xi->data.xs->length; ++j) {
                xj = xi->data.xs->items[j];
                if (IS_CONST(xj))
                    parity ^= (bool) xj->kind;
                else
                    flat[flat_len++] = xj;
            }
        }
        /* Xor(Xnor(x0, x1), x2) <=> Xnor(x0, x1, x2) */
        else if (IS_NOT(xi) && IS_XOR(xi->data.xs->items[0])) {
            parity ^= true;
            for (size_t j = 0; j < xi->data.xs->items[0]->data.xs->length; ++j) {
                xj = xi->data.xs->items[0]->data.xs->items[j];
                if (IS_CONST(xj))
                    parity ^= (bool) xj->kind;
                else
                    flat[flat_len++] = xj;
            }
        }
        else {
            flat[flat_len++] = xi;
        }
    }

    /* 2. Sort arguments, so you get ~a, ~a, a, a, ~b, ... */
    qsort(flat, flat_len, sizeof(struct BoolExpr *), _cmp);

    uniq = malloc(flat_len * sizeof(struct BoolExpr *));
    if (uniq == NULL) {
        free(flat);  // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

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

    y = parity ? BX_Xor(uniq_len, uniq) : BX_Xnor(uniq_len, uniq);

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
    struct BoolExpr *xi;
    struct BoolExpr *y;

    flat = malloc(length * sizeof(struct BoolExpr *));
    if (flat == NULL)
        return NULL; // LCOV_EXCL_LINE

    /* 1. Eliminate {0, 1} */
    for (size_t i = 0; i < length; ++i) {
        xi = op->data.xs->items[i];
        if (IS_ZERO(xi))
            found_zero = true;
        else if (IS_ONE(xi))
            found_one = true;
        else
            flat[flat_len++] = xi;
    }

    /* Equal(0, 1) <=> 0 */
    if (found_zero && found_one) {
        free(flat);
        return BX_IncRef(&BX_Zero);
    }

    /* 2. Sort arguments, so you get ~a, ~a, a, a, ~b, ... */
    qsort(flat, flat_len, sizeof(struct BoolExpr *), _cmp);

    uniq = malloc(flat_len * sizeof(struct BoolExpr *));
    if (uniq == NULL) {
        free(flat);  // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

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
                return BX_IncRef(&BX_Zero);
            }
            /* Equal(x0, x0, x1) <=> Equal(x0, x1) */
            else if (!_eq(flat[i], uniq[uniq_len-1]))
                uniq[uniq_len++] = flat[i];
        }
    }

    free(flat);

    if (found_zero) {
        /* Equal(0) <=> 1 */
        if (uniq_len == 0)
            y = BX_IncRef(&BX_One);
        /* Equal(0, x) <=> ~x */
        else if (uniq_len == 1)
            y = BX_Not(uniq[0]);
        /* Equal(0, x0, x1) <=> Nor(x0, x1) */
        else
            y = _simple_nop(OP_OR, uniq_len, uniq);
    }
    else if (found_one) {
        /* Equal(1) <=> 1 */
        if (uniq_len == 0)
            y = BX_IncRef(&BX_One);
        /* Equal(1, x) <=> x */
        else if (uniq_len == 1)
            y = BX_IncRef(uniq[0]);
        /* Equal(1, x0, ...) <=> And(x0, ...) */
        else
            y = _simple_op(OP_AND, uniq_len, uniq);
    }
    else {
        y = BX_Equal(uniq_len, uniq);
    }

    free(uniq);

    return y;
}


/* NOTE: assumes arguments are already simple */
static struct BoolExpr *
_not_simplify(struct BoolExpr *op)
{
    return BX_Not(op->data.xs->items[0]);
}


/* NOTE: assumes arguments are already simple */
static struct BoolExpr *
_impl_simplify(struct BoolExpr *op)
{
    struct BoolExpr *p = op->data.xs->items[0];
    struct BoolExpr *q = op->data.xs->items[1];

    /* Implies(0, q) <=> Implies(p, 1) <=> 1 */
    if (IS_ZERO(p) || IS_ONE(q))
        return BX_IncRef(&BX_One);

    /* Implies(1, q) <=> q */
    if (IS_ONE(p))
        return BX_IncRef(q);

    /* Implies(p, 0) <=> ~p */
    if (IS_ZERO(q))
        return BX_Not(p);

    /* Implies(p, p) <=> 1 */
    if (_eq(p, q))
        return BX_IncRef(&BX_One);

    /* Implies(~p, p) <=> p */
    if (COMPLEMENTARY(p, q))
        return BX_IncRef(q);

    return BX_Implies(p, q);
}


/* NOTE: assumes arguments are already simple */
static struct BoolExpr *
_ite_simplify(struct BoolExpr *op)
{
    struct BoolExpr *s = op->data.xs->items[0];
    struct BoolExpr *d1 = op->data.xs->items[1];
    struct BoolExpr *d0 = op->data.xs->items[2];

    struct BoolExpr *sn;
    struct BoolExpr *y;

    /* ITE(0, d1, d0) <=> d0 */
    if (IS_ZERO(s))
        return BX_IncRef(d0);

    /* ITE(1, d1, d0) <=> d1 */
    if (IS_ONE(s))
        return BX_IncRef(d1);

    if (IS_ZERO(d1)) {
        /* ITE(s, 0, 0) <=> 0 */
        if (IS_ZERO(d0))
            return BX_IncRef(&BX_Zero);

        /* ITE(s, 0, 1) <=> ~s */
        if (IS_ONE(d0))
            return BX_Not(s);

        /* ITE(s, 0, d0) <=> And(~s, d0) */
        CHECK_NULL(sn, BX_Not(s));
        y = _simple_op2(OP_AND, sn, d0);
        BX_DecRef(sn);
        return y;
    }

    if (IS_ONE(d1)) {
        /* ITE(s, 1, 0) <=> s */
        if (IS_ZERO(d0))
            return BX_IncRef(s);

        /* ITE(s, 1, 1) <=> 1 */
        if (IS_ONE(d0))
            return BX_IncRef(&BX_One);

        /* ITE(s, 1, d0) <=> Or(s, d0) */
        return _simple_op2(OP_OR, s, d0);
    }

    /* ITE(s, d1, 0) <=> And(s, d1) */
    if (IS_ZERO(d0))
        return _simple_op2(OP_AND, s, d1);

    /* ITE(s, d1, 1) <=> Or(~s, d1) */
    if (IS_ONE(d0)) {
        CHECK_NULL(sn, BX_Not(s));
        y = _simple_op2(OP_OR, sn, d1);
        BX_DecRef(sn);
        return y;
    }

    /* ITE(s, d1, d1) <=> d1 */
    if (_eq(d1, d0))
        return BX_IncRef(d1);

    /* ITE(s, s, d0) <=> Or(s, d0) */
    if (_eq(s, d1))
        return _simple_op2(OP_OR, s, d0);

    /* ITE(s, d1, s) <=> And(s, d1) */
    if (_eq(s, d0))
        return _simple_op2(OP_AND, s, d1);

    return BX_ITE(s, d1, d0);
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
_simple_op(BX_Kind kind, size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, _op_new(kind, n, xs));
    y = _op_simplify[kind](temp);
    BX_DecRef(temp);

    return y;
}


static struct BoolExpr *
_simple_op2(BX_Kind kind, struct BoolExpr *x0, struct BoolExpr *x1)
{
    struct BoolExpr *xs[2] = {x0, x1};

    return _simple_op(kind, 2, xs);
}


static struct BoolExpr *
_simple_nop(BX_Kind kind, size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    temp = _simple_op(kind, n, xs);
    y = BX_Not(temp);
    BX_DecRef(temp);

    return y;
}


struct BoolExpr *
_simplify(struct BoolExpr *ex)
{
    if (IS_SIMPLE(ex))
        return BX_IncRef(ex);

    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, _op_transform(ex, _simplify));
    y = _op_simplify[temp->kind](temp);
    BX_DecRef(temp);

    return y;
}


struct BoolExpr *
BX_Simplify(struct BoolExpr *ex)
{
    struct BoolExpr *y;

    CHECK_NULL(y, _simplify(ex));

    _mark_flags(y, SIMPLE);

    return y;
}

