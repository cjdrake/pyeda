/*
** Filename: boolexpr.c
**
** NOTE: Many of these operations modify the inputs.
**       For example, creating an operator will update the reference count
**       of its children.
**       If we ever decide to allow parallel operations,
**       we will need a node mutex.
*/


#include <assert.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


#define READ_ARGS(n, xs) \
do { \
    va_list vl; \
    va_start(vl, n); \
    for (size_t i = 0; i < n; ++i) \
        xs[i] = va_arg(vl, struct BoolExpr *); \
    va_end(vl); \
} while (0)


/* util.c */
size_t _uniqid2index(long uniqid);
bool _is_clause(struct BoolExpr *op);


struct BoolExprIter *
BoolExprIter_New(struct BoolExpr *ex)
{
    struct BoolExprIter *it;

    it = malloc(sizeof(struct BoolExprIter));
    if (it == NULL)
        return NULL; // LCOV_EXCL_LINE

    it->done = false;
    it->ex = ex;

    if (IS_OP(ex)) {
        it->index = 0;
        it->it = BoolExprIter_New(ex->data.xs->items[0]);
        if (it->it == NULL) {
            free(it);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
    }

    return it;
}


void
BoolExprIter_Del(struct BoolExprIter *it)
{
    free(it);
}


struct BoolExpr *
BoolExprIter_Next(struct BoolExprIter *it)
{
    if (IS_ATOM(it->ex)) {
        it->done = true;
        return it->ex;
    }

    if (it->it->done) {
        BoolExprIter_Del(it->it);
        it->index += 1;
        if (it->index < it->ex->data.xs->length) {
            CHECK_NULL(it->it, BoolExprIter_New(it->ex->data.xs->items[it->index]));
            return BoolExprIter_Next(it->it);
        }

        it->done = true;
        return it->ex;
    }

    return BoolExprIter_Next(it->it);
}


/* Initialize global constants */
struct BoolExpr Zero = {1, ZERO, NNF | SIMPLE, {.pcval=1}};
struct BoolExpr One  = {1, ONE,  NNF | SIMPLE, {.pcval=2}};

struct BoolExpr Logical   = {1, LOGICAL,   NNF | SIMPLE, {.pcval=3}};
struct BoolExpr Illogical = {1, ILLOGICAL, NNF | SIMPLE, {.pcval=0}};

struct BoolExpr * IDENTITY[16] = {
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    &Zero, &One, &Zero, NULL,
    NULL, NULL, NULL, NULL,
};

struct BoolExpr * DOMINATOR[16] = {
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    &One, &Zero, NULL, NULL,
    NULL, NULL, NULL, NULL,
};


struct BoolExpr *
_lit_new(struct BoolExprVector *lits, long uniqid)
{
    struct BoolExpr *lit;

    lit = malloc(sizeof(struct BoolExpr));
    if (lit == NULL)
        return NULL; // LCOV_EXCL_LINE

    lit->refcount = 1;
    lit->kind = uniqid < 0 ? COMP : VAR;
    lit->data.lit.uniqid = uniqid;
    lit->data.lit.lits = lits;
    lit->flags = NNF | SIMPLE;

    return lit;
}


static void
_lit_del(struct BoolExpr *lit)
{
    free(lit);
}


struct BoolExpr *
_op_new(BoolExprKind kind, size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *op;

    op = malloc(sizeof(struct BoolExpr));
    if (op == NULL)
        return NULL; // LCOV_EXCL_LINE

    op->refcount = 1;
    op->kind = kind;
    op->flags = (BoolExprFlags) 0;
    op->data.xs = BoolExprArray_New(n, xs);
    if (op->data.xs == NULL) {
        free(op);    // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    return op;
}


struct BoolExpr *
_orandxor_new(BoolExprKind kind, size_t n, struct BoolExpr **xs)
{
    if (n == 0)
        return BoolExpr_IncRef(IDENTITY[kind]);

    if (n == 1)
        return BoolExpr_IncRef(xs[0]);

    return _op_new(kind, n, xs);
}


static void
_op_del(struct BoolExpr *op)
{
    BoolExprArray_Del(op->data.xs);
    free(op);
}


struct BoolExpr *
Literal(struct BoolExprVector *lits, long uniqid)
{
    size_t index = _uniqid2index(uniqid);
    struct BoolExpr *lit;

    lit = (index >= lits->length) ? (struct BoolExpr *) NULL : lits->items[index];
    if (lit == (struct BoolExpr *) NULL) {
        CHECK_NULL(lit, _lit_new(lits, uniqid));
        BoolExprVector_Insert(lits, index, lit);
        return lit;
    }

    return BoolExpr_IncRef(lit);
}


struct BoolExpr *
Or(size_t n, struct BoolExpr **xs)
{
    return _orandxor_new(OP_OR, n, xs);
}


struct BoolExpr *
Nor(size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, Or(n, xs));
    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


struct BoolExpr *
And(size_t n, struct BoolExpr **xs)
{
    return _orandxor_new(OP_AND, n, xs);
}


struct BoolExpr *
Nand(size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, And(n, xs));
    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


struct BoolExpr *
Xor(size_t n, struct BoolExpr **xs)
{
    return _orandxor_new(OP_XOR, n, xs);
}


struct BoolExpr *
Xnor(size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, Xor(n, xs));
    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


struct BoolExpr *
Equal(size_t n, struct BoolExpr **xs)
{
    /* Equal() <=> Equal(0) <=> Equal(1) <=> 1 */
    if (n <= 1)
        return BoolExpr_IncRef(&One);

    return _op_new(OP_EQ, n, xs);
}


struct BoolExpr *
Unequal(size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, Equal(n, xs));
    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


static struct BoolExpr * _zero_inv(struct BoolExpr *x)
{
    return BoolExpr_IncRef(&One);
}

static struct BoolExpr * _one_inv(struct BoolExpr *x)
{
    return BoolExpr_IncRef(&Zero);
}

static struct BoolExpr * _log_inv(struct BoolExpr *x)
{
    return BoolExpr_IncRef(&Logical);
}

static struct BoolExpr * _ill_inv(struct BoolExpr *x)
{
    return BoolExpr_IncRef(&Illogical);
}

static struct BoolExpr * _not_inv(struct BoolExpr *x)
{
    return BoolExpr_IncRef(x->data.xs->items[0]);
}

static struct BoolExpr * _lit_inv(struct BoolExpr *lit)
{
    return Literal(lit->data.lit.lits, -lit->data.lit.uniqid);
}

static struct BoolExpr * _op_inv(struct BoolExpr *op)
{
    struct BoolExpr *xs[1] = {op};

    return _op_new(OP_NOT, 1, xs);
}


static struct BoolExpr * (*_boolexpr_inv[16])(struct BoolExpr *ex) = {
    _zero_inv,
    _one_inv,
    _log_inv,
    _ill_inv,

    _lit_inv,
    _lit_inv,
    NULL,
    NULL,

    _op_inv,
    _op_inv,
    _op_inv,
    _op_inv,

    _not_inv,
    _op_inv,
    _op_inv,
    NULL,
};


struct BoolExpr *
Not(struct BoolExpr *x)
{
    return _boolexpr_inv[x->kind](x);
}


struct BoolExpr *
Implies(struct BoolExpr *p, struct BoolExpr *q)
{
    struct BoolExpr *xs[2] = {p, q};

    return _op_new(OP_IMPL, 2, xs);
}


struct BoolExpr *
ITE(struct BoolExpr *s, struct BoolExpr *d1, struct BoolExpr *d0)
{
    struct BoolExpr *xs[3] = {s, d1, d0};

    return _op_new(OP_ITE, 3, xs);
}


struct BoolExpr *
OrN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return Or(n, xs);
}


struct BoolExpr *
NorN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return Nor(n, xs);
}


struct BoolExpr *
AndN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return And(n, xs);
}


struct BoolExpr *
NandN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return Nand(n, xs);
}


struct BoolExpr *
XorN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return Xor(n, xs);
}


struct BoolExpr *
XnorN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return Xnor(n, xs);
}


struct BoolExpr *
EqualN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return Equal(n, xs);
}


struct BoolExpr *
UnequalN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return Unequal(n, xs);
}


struct BoolExpr *
BoolExpr_IncRef(struct BoolExpr *ex)
{
    /* Input must not be NULL */
    assert(ex != NULL);

    /* Input must have at least one reference already */
    assert(ex->refcount > 0);

    ex->refcount += 1;

    return ex;
}


static void (*_boolexpr_del[16])(struct BoolExpr * ex) = {
    NULL, NULL, NULL, NULL,

    _lit_del,
    _lit_del,
    NULL,
    NULL,

    _op_del,
    _op_del,
    _op_del,
    _op_del,

    _op_del,
    _op_del,
    _op_del,
    NULL,
};


void
BoolExpr_DecRef(struct BoolExpr * ex)
{
    /* Input must not be NULL */
    assert(ex != NULL);

    /* Input must have at least one reference left */
    assert(ex->refcount > 0);

    ex->refcount -= 1;

    if (ex->refcount == 0) {
        /* Constant refcount must never reach zero */
        assert(!IS_CONST(ex));
        _boolexpr_del[ex->kind](ex);
    }
}


unsigned long
BoolExpr_Depth(struct BoolExpr *ex)
{
    if (IS_ATOM(ex))
        return 0;

    unsigned long max_depth = 0;

    for (size_t i = 0; i < ex->data.xs->length; ++i) {
        unsigned long depth = BoolExpr_Depth(ex->data.xs->items[i]);
        if (depth > max_depth)
            max_depth = depth;
    }

    return max_depth + 1;
}


unsigned long
BoolExpr_Size(struct BoolExpr *ex)
{
    if (IS_ATOM(ex))
        return 1;

    unsigned long size = 1;

    for (size_t i = 0; i < ex->data.xs->length; ++i)
        size += BoolExpr_Size(ex->data.xs->items[i]);

    return size;
}


unsigned long
BoolExpr_AtomCount(struct BoolExpr *ex)
{
    if (IS_ATOM(ex))
        return 1;

    unsigned long atom_count = 0;

    for (size_t i = 0; i < ex->data.xs->length; ++i)
        atom_count += BoolExpr_AtomCount(ex->data.xs->items[i]);

    return atom_count;
}


unsigned long
BoolExpr_OpCount(struct BoolExpr *ex)
{
    if (IS_ATOM(ex))
        return 0;

    unsigned long op_count = 1;

    for (size_t i = 0; i < ex->data.xs->length; ++i)
        op_count += BoolExpr_OpCount(ex->data.xs->items[i]);

    return op_count;
}


bool
BoolExpr_IsDNF(struct BoolExpr *ex)
{
    if (IS_ZERO(ex) || IS_LIT(ex))
        return true;

    if (IS_OR(ex)) {
        for (size_t i = 0; i < ex->data.xs->length; ++i) {
            struct BoolExpr *x = ex->data.xs->items[i];
            if (!IS_LIT(x) && !(IS_AND(x) && _is_clause(x)))
                return false;
        }
        return true;
    }

    if (IS_AND(ex))
        return _is_clause(ex);

    return false;
}


bool
BoolExpr_IsCNF(struct BoolExpr *ex)
{
    if (IS_ONE(ex) || IS_LIT(ex))
        return true;

    if (IS_OR(ex))
        return _is_clause(ex);

    if (IS_AND(ex)) {
        for (size_t i = 0; i < ex->data.xs->length; ++i) {
            struct BoolExpr *x = ex->data.xs->items[i];
            if (!IS_LIT(x) && !(IS_OR(x) && _is_clause(x)))
                return false;
        }
        return true;
    }

    return false;
}

