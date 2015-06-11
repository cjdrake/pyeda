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
#include "memcheck.h"


#define READ_ARGS(n, xs) \
do { \
    va_list vl; \
    va_start(vl, n); \
    for (size_t i = 0; i < n; ++i) \
        xs[i] = va_arg(vl, struct BoolExpr *); \
    va_end(vl); \
} while (0)


/* array.c */
struct BX_Array * _bx_array_from(size_t length, struct BoolExpr **items);

/* util.c */
size_t _uniqid2index(long uniqid);
bool _is_clause(struct BoolExpr *op);


struct BX_Iter *
BX_Iter_New(struct BoolExpr *ex)
{
    struct BX_Iter *it;

    it = malloc(sizeof(struct BX_Iter));
    if (it == NULL)
        return NULL; // LCOV_EXCL_LINE

    it->_ex = ex;
    it->done = false;

    if (BX_IS_ATOM(ex)) {
        it->item = ex;
        return it;
    }

    it->_index = 0;
    it->_it = BX_Iter_New(ex->data.xs->items[it->_index]);
    if (it->_it == NULL) {
        free(it);    // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }
    it->item = it->_it->item;

    return it;
}


void
BX_Iter_Del(struct BX_Iter *it)
{
    free(it);
}


bool
BX_Iter_Next(struct BX_Iter *it)
{
    if (it->done)
        return true;

    if (BX_IS_ATOM(it->_ex)) {
        it->done = true;
        return true;
    }

    if (it->_it) {
        if (!BX_Iter_Next(it->_it)) {
            free(it->_it); // LCOV_EXCL_LINE
            return false;  // LCOV_EXCL_LINE
        }

        if (!it->_it->done) {
            it->item = it->_it->item;
            return true;
        }

        free(it->_it);
        it->_index += 1;

        if (it->_index < it->_ex->data.xs->length) {
            it->_it = BX_Iter_New(it->_ex->data.xs->items[it->_index]);
            if (it->_it == NULL)
                return false; // LCOV_EXCL_LINE
            it->item = it->_it->item;
            return true;
        }

        it->_it = (struct BX_Iter *) NULL;
        it->item = it->_ex;
        return true;
    }

    it->item = (struct BoolExpr *) NULL;
    it->done = true;
    return true;
}


/* Initialize global constants */
struct BoolExpr BX_Zero = {1, ZERO, BX_NNF | BX_SIMPLE, {.pcval=1}};
struct BoolExpr BX_One  = {1, ONE,  BX_NNF | BX_SIMPLE, {.pcval=2}};

struct BoolExpr BX_Logical   = {1, LOGICAL,   BX_NNF | BX_SIMPLE, {.pcval=3}};
struct BoolExpr BX_Illogical = {1, ILLOGICAL, BX_NNF | BX_SIMPLE, {.pcval=0}};

struct BoolExpr * IDENTITY[16] = {
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    &BX_Zero, &BX_One, &BX_Zero, NULL,
    NULL, NULL, NULL, NULL,
};

struct BoolExpr * DOMINATOR[16] = {
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    &BX_One, &BX_Zero, NULL, NULL,
    NULL, NULL, NULL, NULL,
};


struct BoolExpr *
_lit_new(struct BX_Vector *lits, long uniqid)
{
    struct BoolExpr *lit;

    lit = malloc(sizeof(struct BoolExpr));
    if (lit == NULL)
        return NULL; // LCOV_EXCL_LINE

    lit->refcount = 1;
    lit->kind = uniqid < 0 ? COMP : VAR;
    lit->data.lit.uniqid = uniqid;
    lit->data.lit.lits = lits;
    lit->flags = BX_NNF | BX_SIMPLE;

    return lit;
}


static void
_lit_del(struct BoolExpr *lit)
{
    free(lit);
}


struct BoolExpr *
_bx_op_from(BX_Kind kind, size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *op;

    op = malloc(sizeof(struct BoolExpr));
    if (op == NULL)
        return NULL; // LCOV_EXCL_LINE

    op->refcount = 1;
    op->kind = kind;
    op->flags = (BX_Flags) 0;
    op->data.xs = _bx_array_from(n, xs);
    if (op->data.xs == NULL) {
        free(op);    // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    return op;
}


struct BoolExpr *
_op_new(BX_Kind kind, size_t n, struct BoolExpr **xs)
{
    struct BoolExpr **xs_copy;

    xs_copy = malloc(n * sizeof(struct BoolExpr *));
    if (xs_copy == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0; i < n; ++i)
        xs_copy[i] = xs[i];

    return _bx_op_from(kind, n, xs_copy);
}


struct BoolExpr *
_orandxor_new(BX_Kind kind, size_t n, struct BoolExpr **xs)
{
    if (n == 0)
        return BX_IncRef(IDENTITY[kind]);

    if (n == 1)
        return BX_IncRef(xs[0]);

    return _op_new(kind, n, xs);
}


struct BoolExpr *
_eq_new(size_t n, struct BoolExpr **xs)
{
    if (n <= 1)
        return BX_IncRef(&BX_One);

    return _op_new(OP_EQ, n, xs);
}


static void
_op_del(struct BoolExpr *op)
{
    BX_Array_Del(op->data.xs);
    free(op);
}


struct BoolExpr *
BX_Literal(struct BX_Vector *lits, long uniqid)
{
    size_t index = _uniqid2index(uniqid);
    struct BoolExpr *lit;

    lit = (index >= lits->length) ? (struct BoolExpr *) NULL : lits->items[index];
    if (lit == (struct BoolExpr *) NULL) {
        CHECK_NULL(lit, _lit_new(lits, uniqid));
        BX_Vector_Insert(lits, index, lit);
        return lit;
    }

    return BX_IncRef(lit);
}


struct BoolExpr *
BX_Or(size_t n, struct BoolExpr **xs)
{
    return _orandxor_new(OP_OR, n, xs);
}


struct BoolExpr *
BX_Nor(size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, BX_Or(n, xs));
    CHECK_NULL_1(y, BX_Not(temp), temp);
    BX_DecRef(temp);

    return y;
}


struct BoolExpr *
BX_And(size_t n, struct BoolExpr **xs)
{
    return _orandxor_new(OP_AND, n, xs);
}


struct BoolExpr *
BX_Nand(size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, BX_And(n, xs));
    CHECK_NULL_1(y, BX_Not(temp), temp);
    BX_DecRef(temp);

    return y;
}


struct BoolExpr *
BX_Xor(size_t n, struct BoolExpr **xs)
{
    return _orandxor_new(OP_XOR, n, xs);
}


struct BoolExpr *
BX_Xnor(size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, BX_Xor(n, xs));
    CHECK_NULL_1(y, BX_Not(temp), temp);
    BX_DecRef(temp);

    return y;
}


struct BoolExpr *
BX_Equal(size_t n, struct BoolExpr **xs)
{
    return _eq_new(n, xs);
}


struct BoolExpr *
BX_Unequal(size_t n, struct BoolExpr **xs)
{
    struct BoolExpr *temp;
    struct BoolExpr *y;

    CHECK_NULL(temp, BX_Equal(n, xs));
    CHECK_NULL_1(y, BX_Not(temp), temp);
    BX_DecRef(temp);

    return y;
}


static struct BoolExpr * _zero_inv(struct BoolExpr *x)
{
    return BX_IncRef(&BX_One);
}

static struct BoolExpr * _one_inv(struct BoolExpr *x)
{
    return BX_IncRef(&BX_Zero);
}

static struct BoolExpr * _log_inv(struct BoolExpr *x)
{
    return BX_IncRef(&BX_Logical);
}

static struct BoolExpr * _ill_inv(struct BoolExpr *x)
{
    return BX_IncRef(&BX_Illogical);
}

static struct BoolExpr * _not_inv(struct BoolExpr *x)
{
    return BX_IncRef(x->data.xs->items[0]);
}

static struct BoolExpr * _lit_inv(struct BoolExpr *lit)
{
    return BX_Literal(lit->data.lit.lits, -lit->data.lit.uniqid);
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
BX_Not(struct BoolExpr *x)
{
    return _boolexpr_inv[x->kind](x);
}


struct BoolExpr *
BX_Implies(struct BoolExpr *p, struct BoolExpr *q)
{
    struct BoolExpr *xs[2] = {p, q};

    return _op_new(OP_IMPL, 2, xs);
}


struct BoolExpr *
BX_ITE(struct BoolExpr *s, struct BoolExpr *d1, struct BoolExpr *d0)
{
    struct BoolExpr *xs[3] = {s, d1, d0};

    return _op_new(OP_ITE, 3, xs);
}


struct BoolExpr *
BX_OrN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return BX_Or(n, xs);
}


struct BoolExpr *
BX_NorN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return BX_Nor(n, xs);
}


struct BoolExpr *
BX_AndN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return BX_And(n, xs);
}


struct BoolExpr *
BX_NandN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return BX_Nand(n, xs);
}


struct BoolExpr *
BX_XorN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return BX_Xor(n, xs);
}


struct BoolExpr *
BX_XnorN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return BX_Xnor(n, xs);
}


struct BoolExpr *
BX_EqualN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return BX_Equal(n, xs);
}


struct BoolExpr *
BX_UnequalN(size_t n, ...)
{
    struct BoolExpr *xs[n];
    READ_ARGS(n, xs);
    return BX_Unequal(n, xs);
}


struct BoolExpr *
BX_IncRef(struct BoolExpr *ex)
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
BX_DecRef(struct BoolExpr * ex)
{
    /* Input must not be NULL */
    assert(ex != NULL);

    /* Input must have at least one reference left */
    assert(ex->refcount > 0);

    ex->refcount -= 1;

    if (ex->refcount == 0) {
        /* Constant refcount must never reach zero */
        assert(!BX_IS_CONST(ex));
        _boolexpr_del[ex->kind](ex);
    }
}


unsigned long
BX_Depth(struct BoolExpr *ex)
{
    if (BX_IS_ATOM(ex))
        return 0;

    unsigned long max_depth = 0;

    for (size_t i = 0; i < ex->data.xs->length; ++i) {
        unsigned long depth = BX_Depth(ex->data.xs->items[i]);
        if (depth > max_depth)
            max_depth = depth;
    }

    return max_depth + 1;
}


unsigned long
BX_Size(struct BoolExpr *ex)
{
    if (BX_IS_ATOM(ex))
        return 1;

    unsigned long size = 1;

    for (size_t i = 0; i < ex->data.xs->length; ++i)
        size += BX_Size(ex->data.xs->items[i]);

    return size;
}


unsigned long
BX_AtomCount(struct BoolExpr *ex)
{
    if (BX_IS_ATOM(ex))
        return 1;

    unsigned long atom_count = 0;

    for (size_t i = 0; i < ex->data.xs->length; ++i)
        atom_count += BX_AtomCount(ex->data.xs->items[i]);

    return atom_count;
}


unsigned long
BX_OpCount(struct BoolExpr *ex)
{
    if (BX_IS_ATOM(ex))
        return 0;

    unsigned long op_count = 1;

    for (size_t i = 0; i < ex->data.xs->length; ++i)
        op_count += BX_OpCount(ex->data.xs->items[i]);

    return op_count;
}


bool
BX_IsDNF(struct BoolExpr *ex)
{
    if (BX_IS_ZERO(ex) || BX_IS_LIT(ex))
        return true;

    if (BX_IS_OR(ex)) {
        for (size_t i = 0; i < ex->data.xs->length; ++i) {
            struct BoolExpr *x = ex->data.xs->items[i];
            if (!BX_IS_LIT(x) && !(BX_IS_AND(x) && _is_clause(x)))
                return false;
        }
        return true;
    }

    if (BX_IS_AND(ex))
        return _is_clause(ex);

    return false;
}


bool
BX_IsCNF(struct BoolExpr *ex)
{
    if (BX_IS_ONE(ex) || BX_IS_LIT(ex))
        return true;

    if (BX_IS_OR(ex))
        return _is_clause(ex);

    if (BX_IS_AND(ex)) {
        for (size_t i = 0; i < ex->data.xs->length; ++i) {
            struct BoolExpr *x = ex->data.xs->items[i];
            if (!BX_IS_LIT(x) && !(BX_IS_OR(x) && _is_clause(x)))
                return false;
        }
        return true;
    }

    return false;
}

