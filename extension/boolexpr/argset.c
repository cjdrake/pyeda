/*
** Filename: argset.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* boolexpr.c */
struct BoolExpr * _bx_op_from(BoolExprKind kind, size_t n, struct BoolExpr **xs);


static struct BoolExpr **
_set2array(struct BoolExprSet *set)
{
    struct BoolExpr **array;
    struct BoolExprSetIter *it;

    array = malloc(set->length * sizeof(struct BoolExpr *));
    if (array == NULL)
        return NULL; // LCOV_EXCL_LINE

    it = BoolExprSetIter_New(set);
    if (it == NULL) {
        free(array); // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    for (size_t i = 0; !it->done; BoolExprSetIter_Next(it))
        array[i++] = BoolExprSetIter_Key(it);

    BoolExprSetIter_Del(it);

    return array;
}


struct BoolExprOrAndArgSet *
BoolExprOrAndArgSet_New(BoolExprKind kind)
{
    struct BoolExprOrAndArgSet *argset;

    argset = malloc(sizeof(struct BoolExprOrAndArgSet));
    if (argset == NULL)
        return NULL; // LCOV_EXCL_LINE

    argset->kind = kind;
    argset->min = true;
    argset->max = false;
    argset->xs = BoolExprSet_New();
    if (argset->xs == NULL) {
        free(argset); // LCOV_EXCL_LINE
        return NULL;  // LCOV_EXCL_LINE
    }

    return argset;
}


void
BoolExprOrAndArgSet_Del(struct BoolExprOrAndArgSet *argset)
{
    BoolExprSet_Del(argset->xs);
    free(argset);
}


bool
BoolExprOrAndArgSet_Insert(struct BoolExprOrAndArgSet *argset, struct BoolExpr *key)
{
    /* 1 | x = 1 ; 0 & x = 0 */
    /* x | 0 = x ; x & 1 = x */
    if (argset->max || key == IDENTITY[argset->kind])
        return true;

    bool dominate = false;
    /* x | 1 = 1 ; x & 0 = 0 */
    if (key == DOMINATOR[argset->kind]) {
        dominate = true;
    }
    /* x | ~x = 1 ; x & ~x = 0 */
    else if (IS_LIT(key) || IS_NOT(key)) {
        struct BoolExpr *temp = Not(key);
        dominate = BoolExprSet_Contains(argset->xs, temp);
        BoolExpr_DecRef(temp);
    }
    if (dominate) {
        argset->min = false;
        argset->max = true;
        BoolExprSet_Clear(argset->xs);
        return true;
    }

    /* x | (y | z) = x | y | z ; x & (y & z) = x & y & z */
    if (key->kind == argset->kind) {
        for (size_t i = 0; i < key->data.xs->length; ++i) {
            if (!BoolExprOrAndArgSet_Insert(argset, key->data.xs->items[i]))
                return false; // LCOV_EXCL_LINE
        }
        return true;
    }

    /* x | x = x ; x & x = x */
    argset->min = false;
    return BoolExprSet_Insert(argset->xs, key);
}


struct BoolExpr *
BoolExprOrAndArgSet_Reduce(struct BoolExprOrAndArgSet *argset)
{
    struct BoolExpr **xs;
    size_t length = argset->xs->length;

    if (argset->min)
        return BoolExpr_IncRef(IDENTITY[argset->kind]);

    if (argset->max)
        return BoolExpr_IncRef(DOMINATOR[argset->kind]);

    CHECK_NULL(xs, _set2array(argset->xs));

    if (length == 1) {
        struct BoolExpr *y = BoolExpr_IncRef(xs[0]);
        free(xs);
        return y;
    }

    return _bx_op_from(argset->kind, length, xs);
}


struct BoolExprXorArgSet *
BoolExprXorArgSet_New(bool parity)
{
    struct BoolExprXorArgSet *argset;

    argset = malloc(sizeof(struct BoolExprXorArgSet));
    if (argset == NULL)
        return NULL; // LCOV_EXCL_LINE

    argset->parity = parity;
    argset->xs = BoolExprSet_New();
    if (argset->xs == NULL) {
        free(argset); // LCOV_EXCL_LINE
        return NULL;  // LCOV_EXCL_LINE
    }

    return argset;
}


void
BoolExprXorArgSet_Del(struct BoolExprXorArgSet *argset)
{
    BoolExprSet_Del(argset->xs);
    free(argset);
}


bool
BoolExprXorArgSet_Insert(struct BoolExprXorArgSet *argset, struct BoolExpr *key)
{
    if (IS_CONST(key)) {
        argset->parity ^= (bool) key->kind;
        return true;
    }

    /* Xor(x, y, z, z) = Xor(x, y) */
    /* Xnor(x, y, z, z) = Xnor(x, y) */
    if (BoolExprSet_Contains(argset->xs, key)) {
        BoolExprSet_Remove(argset->xs, key);
        return true;
    }

    /* Xor(x, y, z, ~z) = Xnor(x, y) */
    /* Xnor(x, y, z, ~z) = Xor(x, y) */
    if (IS_LIT(key) || IS_NOT(key)) {
        struct BoolExpr *temp = Not(key);
        bool flip = BoolExprSet_Contains(argset->xs, temp);
        BoolExpr_DecRef(temp);
        if (flip) {
            BoolExprSet_Remove(argset->xs, temp);
            argset->parity ^= true;
            return true;
        }
    }

    /* Xor (x, Xor(y, z)) = Xor (x, y, z) */
    /* Xnor(x, Xor(y, z)) = Xnor(x, y, z) */
    if (IS_XOR(key)) {
        for (size_t i = 0; i < key->data.xs->length; ++i) {
            if (!BoolExprXorArgSet_Insert(argset, key->data.xs->items[i]))
                return false; // LCOV_EXCL_LINE
        }
        return true;
    }

    /* Xor (x, Xnor(y, z)) = Xnor(x, y, z) */
    /* Xnor(x, Xnor(y, z)) = Xor (x, y, z) */
    if (IS_NOT(key) && IS_XOR(key->data.xs->items[0])) {
        for (size_t i = 0; i < key->data.xs->length; ++i) {
            if (!BoolExprXorArgSet_Insert(argset, key->data.xs->items[i]))
                return false; // LCOV_EXCL_LINE
        }
        argset->parity ^= true;
        return true;
    }

    return BoolExprSet_Insert(argset->xs, key);
}


struct BoolExpr *
BoolExprXorArgSet_Reduce(struct BoolExprXorArgSet *argset)
{
    struct BoolExpr **xs;
    struct BoolExpr *temp;
    struct BoolExpr *y;
    size_t length = argset->xs->length;

    if (length == 0) {
        temp = BoolExpr_IncRef(IDENTITY[OP_XOR]);
        y = argset->parity ? BoolExpr_IncRef(temp) : Not(temp);
        BoolExpr_DecRef(temp);
        return y;
    }

    CHECK_NULL(xs, _set2array(argset->xs));

    if (length == 1) {
        temp = BoolExpr_IncRef(xs[0]);
        free(xs);
    }
    else {
        temp = _bx_op_from(OP_XOR, length, xs);
        if (temp == NULL) {
            free(xs);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
    }

    y = argset->parity ? BoolExpr_IncRef(temp) : Not(temp);
    BoolExpr_DecRef(temp);

    return y;
}


struct BoolExprEqArgSet *
BoolExprEqArgSet_New(void)
{
    struct BoolExprEqArgSet *argset;

    argset = malloc(sizeof(struct BoolExprEqArgSet));
    if (argset == NULL)
        return NULL; // LCOV_EXCL_LINE

    argset->zero = false;
    argset->one = false;
    argset->xs = BoolExprSet_New();
    if (argset->xs == NULL) {
        free(argset); // LCOV_EXCL_LINE
        return NULL;  // LCOV_EXCL_LINE
    }

    return argset;
}


void
BoolExprEqArgSet_Del(struct BoolExprEqArgSet *argset)
{
    BoolExprSet_Del(argset->xs);
    free(argset);
}


bool
BoolExprEqArgSet_Insert(struct BoolExprEqArgSet *argset, struct BoolExpr *key)
{
    if (argset->zero && argset->one)
        return true;

    if (key == &Zero) {
        argset->zero = true;
        if (argset->one)
            BoolExprSet_Clear(argset->xs);
        return true;
    }

    if (key == &One) {
        argset->one = true;
        if (argset->zero)
            BoolExprSet_Clear(argset->xs);
        return true;
    }

    /* Equal(~x, x) = 0 */
    if (IS_LIT(key) || IS_NOT(key)) {
        struct BoolExpr *temp = Not(key);
        bool contradict = BoolExprSet_Contains(argset->xs, temp);
        BoolExpr_DecRef(temp);
        if (contradict) {
            argset->zero = true;
            argset->one = true;
            BoolExprSet_Clear(argset->xs);
            return true;
        }
    }

    /* Equal(x, x, y) = Equal(x, y) */
    return BoolExprSet_Insert(argset->xs, key);
}


struct BoolExpr *
BoolExprEqArgSet_Reduce(struct BoolExprEqArgSet *argset)
{
    struct BoolExpr **xs;
    struct BoolExpr *y;
    size_t length = argset->xs->length;

    /* Equal(0, 1) = 0 */
    if (argset->zero && argset->one)
        return BoolExpr_IncRef(&Zero);

    /* Equal() = Equal(0) = Equal(1) = 1 */
    if (((size_t) argset->zero + (size_t) argset->one + length) <= 1)
        return BoolExpr_IncRef(&One);

    CHECK_NULL(xs, _set2array(argset->xs));

    /* Equal(0, x) = ~x */
    if (argset->zero && length == 1) {
        y = Not(xs[0]);
        free(xs);
        return y;
    }

    /* Equal(1, x) = x */
    if (argset->one && length == 1) {
        y = BoolExpr_IncRef(xs[0]);
        free(xs);
        return y;
    }

    /* Equal(0, x, y) = Nor(x, y) */
    if (argset->zero) {
        struct BoolExpr *temp = _bx_op_from(OP_OR, length, xs);
        if (temp == NULL) {
            free(xs);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
        y = Not(temp);
        BoolExpr_DecRef(temp);
        return y;
    }

    /* Equal(1, x, y) = Nand(x, y) */
    if (argset->one) {
        struct BoolExpr *temp = _bx_op_from(OP_AND, length, xs);
        if (temp == NULL) {
            free(xs);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
        y = Not(temp);
        BoolExpr_DecRef(temp);
        return y;
    }

    return _bx_op_from(OP_EQ, length, xs);
}

