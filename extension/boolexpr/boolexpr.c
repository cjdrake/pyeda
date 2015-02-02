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

#include "boolexpr.h"


#define READ_ARGS \
do { \
    va_list vl; \
    va_start(vl, n); \
    for (int i = 0; i < n; ++i) \
        xs[i] = va_arg(vl, BoolExpr *); \
    va_end(vl); \
} while (0)


/* util.c */
size_t _uniqid2index(long uniqid);
bool _is_clause(BoolExpr *op);


BoolExprIter *
BoolExprIter_New(BoolExpr *ex)
{
    BoolExprIter *it;

    it = (BoolExprIter *) malloc(sizeof(BoolExprIter));

    /* LCOV_EXCL_START */
    if (it == NULL)
        return NULL;
    /* LCOV_EXCL_STOP */

    it->done = false;
    it->ex = ex;

    if (IS_OP(ex)) {
        it->index = 0;
        it->it = BoolExprIter_New(ex->data.xs->items[0]);

        /* LCOV_EXCL_START */
        if (it->it == NULL) {
            free(it);
            return NULL;
        }
        /* LCOV_EXCL_STOP */
    }

    return it;
}


void
BoolExprIter_Del(BoolExprIter *it)
{
    free(it);
}


BoolExpr *
BoolExprIter_Next(BoolExprIter *it)
{
    if (IS_ATOM(it->ex)) {
        it->done = true;
        return it->ex;
    }
    else {
        if (it->it->done) {
            BoolExprIter_Del(it->it);
            it->index += 1;
            if (it->index < it->ex->data.xs->length) {
                CHECK_NULL(it->it, BoolExprIter_New(it->ex->data.xs->items[it->index]));
                return BoolExprIter_Next(it->it);
            }
            else {
                it->done = true;
                return it->ex;
            }
        }
        else {
            return BoolExprIter_Next(it->it);
        }
    }
}


/* Initialize global constants */
BoolExpr Zero = {1, ZERO, {.pcval=1}, NNF | SIMPLE};
BoolExpr One  = {1, ONE,  {.pcval=2}, NNF | SIMPLE};

BoolExpr Logical   = {1, LOGICAL,   {.pcval=3}, NNF | SIMPLE};
BoolExpr Illogical = {1, ILLOGICAL, {.pcval=0}, NNF | SIMPLE};

BoolExpr * IDENTITY[16] = {
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    &Zero, &One, &Zero, &One,
    NULL, NULL, NULL, NULL,
};

BoolExpr * DOMINATOR[16] = {
    NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    &One, &Zero, NULL, NULL,
    NULL, NULL, NULL, NULL,
};


/* Returns a new reference */
BoolExpr *
_lit_new(BoolExprVector *lits, long uniqid)
{
    BoolExpr *lit;

    lit = (BoolExpr *) malloc(sizeof(BoolExpr));

    /* LCOV_EXCL_START */
    if (lit == NULL)
        return NULL;
    /* LCOV_EXCL_STOP */

    lit->refcount = 1;
    lit->type = uniqid < 0 ? COMP : VAR;
    lit->data.lit.uniqid = uniqid;
    lit->data.lit.lits = lits;
    lit->flags = NNF | SIMPLE;

    return lit;
}


static void
_lit_del(BoolExpr *lit)
{
    free(lit);
    lit = (BoolExpr *) NULL;
}


/* Returns a new reference */
BoolExpr *
_op_new(BoolExprType t, size_t n, BoolExpr **xs)
{
    BoolExpr *op;

    op = (BoolExpr *) malloc(sizeof(BoolExpr));

    /* LCOV_EXCL_START */
    if (op == NULL)
        return NULL;
    /* LCOV_EXCL_STOP */

    op->data.xs = BoolExprArray_New(n, xs);

    /* LCOV_EXCL_START */
    if (op->data.xs == NULL) {
        free(op);
        return NULL;
    }
    /* LCOV_EXCL_STOP */

    op->refcount = 1;
    op->type = t;
    op->flags = (BoolExprFlags) 0;

    return op;
}


BoolExpr *
_opn_new(BoolExprType t, size_t n, ...)
{
    BoolExpr *xs[n];
    READ_ARGS;
    return _op_new(t, n, xs);
}


static void
_op_del(BoolExpr *op)
{
    BoolExprArray_Del(op->data.xs);
    free(op);
}


BoolExpr *
Literal(BoolExprVector *lits, long uniqid)
{
    size_t index;
    BoolExpr *lit;

    index = _uniqid2index(uniqid);

    lit = index >= lits->length ? (BoolExpr *) NULL : lits->items[index];
    if (lit == (BoolExpr *) NULL) {
        CHECK_NULL(lit, _lit_new(lits, uniqid));
        BoolExprVector_Insert(lits, index, lit);
        return lit;
    }
    else {
        return BoolExpr_IncRef(lit);
    }
}


BoolExpr *
Or(size_t n, BoolExpr **xs)
{
    BoolExpr *y;

    /* Or() <=> 0 */
    if (n == 0) {
        y = BoolExpr_IncRef(IDENTITY[OP_OR]);
    }
    /* Or(x) <=> x */
    else if (n == 1) {
        y = BoolExpr_IncRef(xs[0]);
    }
    else {
        CHECK_NULL(y, _op_new(OP_OR, n, xs));
    }

    return y;
}


BoolExpr *
Nor(size_t n, BoolExpr **xs)
{
    BoolExpr *temp;
    BoolExpr *y;

    CHECK_NULL(temp, Or(n, xs));
    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


BoolExpr *
And(size_t n, BoolExpr **xs)
{
    BoolExpr *y;

    /* And() <=> 1 */
    if (n == 0) {
        y = BoolExpr_IncRef(IDENTITY[OP_AND]);
    }
    /* And(x) <=> x */
    else if (n == 1) {
        y = BoolExpr_IncRef(xs[0]);
    }
    else {
        CHECK_NULL(y, _op_new(OP_AND, n, xs));
    }

    return y;
}


BoolExpr *
Nand(size_t n, BoolExpr **xs)
{
    BoolExpr *temp;
    BoolExpr *y;

    CHECK_NULL(temp, And(n, xs));
    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


BoolExpr *
Xor(size_t n, BoolExpr **xs)
{
    BoolExpr *y;

    /* Xor() <=> 0 */
    if (n == 0) {
        y = BoolExpr_IncRef(IDENTITY[OP_XOR]);
    }
    /* Xor(x) <=> x */
    else if (n == 1) {
        y = BoolExpr_IncRef(xs[0]);
    }
    else {
        CHECK_NULL(y, _op_new(OP_XOR, n, xs));
    }

    return y;
}


BoolExpr *
Xnor(size_t n, BoolExpr **xs)
{
    BoolExpr *temp;
    BoolExpr *y;

    CHECK_NULL(temp, Xor(n, xs));
    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


BoolExpr *
Equal(size_t n, BoolExpr **xs)
{
    BoolExpr *y;

    /* Equal() <=> Equal(0) <=> Equal(1) <=> 1 */
    if (n <= 1) {
        y = BoolExpr_IncRef(IDENTITY[OP_EQ]);
    }
    else {
        CHECK_NULL(y, _op_new(OP_EQ, n, xs));
    }

    return y;
}


BoolExpr *
Unequal(size_t n, BoolExpr **xs)
{
    BoolExpr *temp;
    BoolExpr *y;

    CHECK_NULL(temp, Equal(n, xs));
    CHECK_NULL_1(y, Not(temp), temp);
    BoolExpr_DecRef(temp);

    return y;
}


static BoolExpr * _zero_inv(BoolExpr *x)  { return BoolExpr_IncRef(&One); }
static BoolExpr * _one_inv(BoolExpr *x)   { return BoolExpr_IncRef(&Zero); }
static BoolExpr * _log_inv(BoolExpr *x)   { return BoolExpr_IncRef(&Logical); }
static BoolExpr * _ill_inv(BoolExpr *x)   { return BoolExpr_IncRef(&Illogical); }
static BoolExpr * _not_inv(BoolExpr *x)   { return BoolExpr_IncRef(x->data.xs->items[0]); }
static BoolExpr * _lit_inv(BoolExpr *lit) { return Literal(lit->data.lit.lits, -lit->data.lit.uniqid); }
static BoolExpr * _op_inv(BoolExpr *op)   { return _opn_new(OP_NOT, 1, op); }


static BoolExpr * (*_boolexpr_inv[16])(BoolExpr *ex) = {
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


BoolExpr *
Not(BoolExpr *x)
{
    return _boolexpr_inv[x->type](x);
}


BoolExpr *
Implies(BoolExpr *p, BoolExpr *q)
{
    return _opn_new(OP_IMPL, 2, p, q);
}


BoolExpr *
ITE(BoolExpr *s, BoolExpr *d1, BoolExpr *d0)
{
    return _opn_new(OP_ITE, 3, s, d1, d0);
}


BoolExpr *
OrN(size_t n, ...)
{
    BoolExpr *xs[n];
    READ_ARGS;
    return Or(n, xs);
}


BoolExpr *
NorN(size_t n, ...)
{
    BoolExpr *xs[n];
    READ_ARGS;
    return Nor(n, xs);
}


BoolExpr *
AndN(size_t n, ...)
{
    BoolExpr *xs[n];
    READ_ARGS;
    return And(n, xs);
}


BoolExpr *
NandN(size_t n, ...)
{
    BoolExpr *xs[n];
    READ_ARGS;
    return Nand(n, xs);
}


BoolExpr *
XorN(size_t n, ...)
{
    BoolExpr *xs[n];
    READ_ARGS;
    return Xor(n, xs);
}


BoolExpr *
XnorN(size_t n, ...)
{
    BoolExpr *xs[n];
    READ_ARGS;
    return Xnor(n, xs);
}


BoolExpr *
EqualN(size_t n, ...)
{
    BoolExpr *xs[n];
    READ_ARGS;
    return Equal(n, xs);
}


BoolExpr *
UnequalN(size_t n, ...)
{
    BoolExpr *xs[n];
    READ_ARGS;
    return Unequal(n, xs);
}


BoolExpr *
BoolExpr_IncRef(BoolExpr *ex)
{
    /* Input must not be NULL */
    assert(ex != NULL);

    /* Input must have at least one reference already */
    assert(ex->refcount > 0);

    ex->refcount += 1;

    return ex;
}


static void (*_boolexpr_del[16])(BoolExpr * ex) = {
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
BoolExpr_DecRef(BoolExpr * ex)
{
    /* Input must not be NULL */
    assert(ex != NULL);

    /* Input must have at least one reference left */
    assert(ex->refcount > 0);

    ex->refcount -= 1;
    if (ex->refcount == 0) {
        /* Constant refcount must never reach zero */
        assert(!IS_CONST(ex));
        _boolexpr_del[ex->type](ex);
    }
}


unsigned long
BoolExpr_Depth(BoolExpr *ex)
{
    if (IS_ATOM(ex)) {
        return 0;
    }
    else {
        unsigned long max_depth = 0;

        for (size_t i = 0; i < ex->data.xs->length; ++i) {
            unsigned long depth = BoolExpr_Depth(ex->data.xs->items[i]);
            if (depth > max_depth)
                max_depth = depth;
        }

        return max_depth + 1;
    }
}


unsigned long
BoolExpr_Size(BoolExpr *ex)
{
    if (IS_ATOM(ex)) {
        return 1;
    }
    else {
        unsigned long size = 1;

        for (size_t i = 0; i < ex->data.xs->length; ++i)
            size += BoolExpr_Size(ex->data.xs->items[i]);

        return size;
    }
}


unsigned long
BoolExpr_AtomCount(BoolExpr *ex)
{
    if (IS_ATOM(ex)) {
        return 1;
    }
    else {
        unsigned long atom_count = 0;

        for (size_t i = 0; i < ex->data.xs->length; ++i)
            atom_count += BoolExpr_AtomCount(ex->data.xs->items[i]);

        return atom_count;
    }
}


unsigned long
BoolExpr_OpCount(BoolExpr *ex)
{
    if (IS_ATOM(ex)) {
        return 0;
    }
    else {
        unsigned long op_count = 1;

        for (size_t i = 0; i < ex->data.xs->length; ++i)
            op_count += BoolExpr_OpCount(ex->data.xs->items[i]);

        return op_count;
    }
}


bool
BoolExpr_IsDNF(BoolExpr *ex)
{
    if (!IS_SIMPLE(ex))
        return false;

    if (IS_ZERO(ex) || IS_LIT(ex)) {
        return true;
    }
    else if (IS_OR(ex)) {
        for (size_t i = 0; i < ex->data.xs->length; ++i) {
            BoolExpr *x = ex->data.xs->items[i];
            if (!IS_LIT(x) && !(IS_AND(x) && _is_clause(x)))
                return false;
        }
        return true;
    }
    else if (IS_AND(ex)) {
        return _is_clause(ex);
    }
    else {
        return false;
    }
}


bool
BoolExpr_IsCNF(BoolExpr *ex)
{
    if (!IS_SIMPLE(ex))
        return false;

    if (IS_ONE(ex) || IS_LIT(ex)) {
        return true;
    }
    else if (IS_OR(ex)) {
        return _is_clause(ex);
    }
    else if (IS_AND(ex)) {
        for (size_t i = 0; i < ex->data.xs->length; ++i) {
            BoolExpr *x = ex->data.xs->items[i];
            if (!IS_LIT(x) && !(IS_OR(x) && _is_clause(x))) {
                return false;
            }
        }
        return true;
    }
    else {
        return false;
    }
}

