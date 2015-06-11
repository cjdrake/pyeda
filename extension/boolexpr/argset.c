/*
** Filename: argset.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"
#include "memcheck.h"


/* boolexpr.c */
struct BoolExpr * _bx_op_from(BX_Kind kind, size_t n, struct BoolExpr **xs);


static struct BoolExpr **
_set2array(struct BX_Set *set)
{
    struct BoolExpr **array;
    struct BX_SetIter it;

    array = malloc(set->length * sizeof(struct BoolExpr *));
    if (array == NULL)
        return NULL; // LCOV_EXCL_LINE

    size_t i = 0;
    for (BX_SetIter_Init(&it, set); !it.done; BX_SetIter_Next(&it))
        array[i++] = it.item->key;

    return array;
}


struct BX_OrAndArgSet *
BX_OrAndArgSet_New(BX_Kind kind)
{
    struct BX_OrAndArgSet *argset;

    argset = malloc(sizeof(struct BX_OrAndArgSet));
    if (argset == NULL)
        return NULL; // LCOV_EXCL_LINE

    argset->kind = kind;
    argset->min = true;
    argset->max = false;
    argset->xs = BX_Set_New();
    if (argset->xs == NULL) {
        free(argset); // LCOV_EXCL_LINE
        return NULL;  // LCOV_EXCL_LINE
    }

    return argset;
}


void
BX_OrAndArgSet_Del(struct BX_OrAndArgSet *argset)
{
    BX_Set_Del(argset->xs);
    free(argset);
}


bool
BX_OrAndArgSet_Insert(struct BX_OrAndArgSet *argset, struct BoolExpr *key)
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
    else if (BX_IS_LIT(key) || BX_IS_NOT(key)) {
        struct BoolExpr *temp = BX_Not(key);
        dominate = BX_Set_Contains(argset->xs, temp);
        BX_DecRef(temp);
    }
    if (dominate) {
        argset->min = false;
        argset->max = true;
        BX_Set_Clear(argset->xs);
        return true;
    }

    /* x | (y | z) = x | y | z ; x & (y & z) = x & y & z */
    if (key->kind == argset->kind) {
        for (size_t i = 0; i < key->data.xs->length; ++i) {
            if (!BX_OrAndArgSet_Insert(argset, key->data.xs->items[i]))
                return false; // LCOV_EXCL_LINE
        }
        return true;
    }

    /* x | x = x ; x & x = x */
    argset->min = false;
    return BX_Set_Insert(argset->xs, key);
}


struct BoolExpr *
BX_OrAndArgSet_Reduce(struct BX_OrAndArgSet *argset)
{
    struct BoolExpr **xs;
    size_t length = argset->xs->length;

    if (argset->min)
        return BX_IncRef(IDENTITY[argset->kind]);

    if (argset->max)
        return BX_IncRef(DOMINATOR[argset->kind]);

    CHECK_NULL(xs, _set2array(argset->xs));

    if (length == 1) {
        struct BoolExpr *y = BX_IncRef(xs[0]);
        free(xs);
        return y;
    }

    return _bx_op_from(argset->kind, length, xs);
}


struct BX_XorArgSet *
BX_XorArgSet_New(bool parity)
{
    struct BX_XorArgSet *argset;

    argset = malloc(sizeof(struct BX_XorArgSet));
    if (argset == NULL)
        return NULL; // LCOV_EXCL_LINE

    argset->parity = parity;
    argset->xs = BX_Set_New();
    if (argset->xs == NULL) {
        free(argset); // LCOV_EXCL_LINE
        return NULL;  // LCOV_EXCL_LINE
    }

    return argset;
}


void
BX_XorArgSet_Del(struct BX_XorArgSet *argset)
{
    BX_Set_Del(argset->xs);
    free(argset);
}


bool
BX_XorArgSet_Insert(struct BX_XorArgSet *argset, struct BoolExpr *key)
{
    if (BX_IS_CONST(key)) {
        argset->parity ^= (bool) key->kind;
        return true;
    }

    /* Xor(x, y, z, z) = Xor(x, y) */
    /* Xnor(x, y, z, z) = Xnor(x, y) */
    if (BX_Set_Contains(argset->xs, key)) {
        BX_Set_Remove(argset->xs, key);
        return true;
    }

    /* Xor(x, y, z, ~z) = Xnor(x, y) */
    /* Xnor(x, y, z, ~z) = Xor(x, y) */
    if (BX_IS_LIT(key) || BX_IS_NOT(key)) {
        struct BoolExpr *temp = BX_Not(key);
        bool flip = BX_Set_Contains(argset->xs, temp);
        BX_DecRef(temp);
        if (flip) {
            BX_Set_Remove(argset->xs, temp);
            argset->parity ^= true;
            return true;
        }
    }

    /* Xor (x, Xor(y, z)) = Xor (x, y, z) */
    /* Xnor(x, Xor(y, z)) = Xnor(x, y, z) */
    if (BX_IS_XOR(key)) {
        for (size_t i = 0; i < key->data.xs->length; ++i) {
            if (!BX_XorArgSet_Insert(argset, key->data.xs->items[i]))
                return false; // LCOV_EXCL_LINE
        }
        return true;
    }

    /* Xor (x, Xnor(y, z)) = Xnor(x, y, z) */
    /* Xnor(x, Xnor(y, z)) = Xor (x, y, z) */
    if (BX_IS_XNOR(key)) {
        for (size_t i = 0; i < key->data.xs->length; ++i) {
            if (!BX_XorArgSet_Insert(argset, key->data.xs->items[i]))
                return false; // LCOV_EXCL_LINE
        }
        argset->parity ^= true;
        return true;
    }

    return BX_Set_Insert(argset->xs, key);
}


struct BoolExpr *
BX_XorArgSet_Reduce(struct BX_XorArgSet *argset)
{
    struct BoolExpr **xs;
    struct BoolExpr *temp;
    struct BoolExpr *y;
    size_t length = argset->xs->length;

    if (length == 0) {
        temp = BX_IncRef(IDENTITY[BX_OP_XOR]);
        y = argset->parity ? BX_IncRef(temp) : BX_Not(temp);
        BX_DecRef(temp);
        return y;
    }

    CHECK_NULL(xs, _set2array(argset->xs));

    if (length == 1) {
        temp = BX_IncRef(xs[0]);
        free(xs);
    }
    else {
        temp = _bx_op_from(BX_OP_XOR, length, xs);
        if (temp == NULL) {
            free(xs);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
    }

    y = argset->parity ? BX_IncRef(temp) : BX_Not(temp);
    BX_DecRef(temp);

    return y;
}


struct BX_EqArgSet *
BX_EqArgSet_New(void)
{
    struct BX_EqArgSet *argset;

    argset = malloc(sizeof(struct BX_EqArgSet));
    if (argset == NULL)
        return NULL; // LCOV_EXCL_LINE

    argset->zero = false;
    argset->one = false;
    argset->xs = BX_Set_New();
    if (argset->xs == NULL) {
        free(argset); // LCOV_EXCL_LINE
        return NULL;  // LCOV_EXCL_LINE
    }

    return argset;
}


void
BX_EqArgSet_Del(struct BX_EqArgSet *argset)
{
    BX_Set_Del(argset->xs);
    free(argset);
}


bool
BX_EqArgSet_Insert(struct BX_EqArgSet *argset, struct BoolExpr *key)
{
    if (argset->zero && argset->one)
        return true;

    if (key == &BX_Zero) {
        argset->zero = true;
        if (argset->one)
            BX_Set_Clear(argset->xs);
        return true;
    }

    if (key == &BX_One) {
        argset->one = true;
        if (argset->zero)
            BX_Set_Clear(argset->xs);
        return true;
    }

    /* Equal(~x, x) = 0 */
    if (BX_IS_LIT(key) || BX_IS_NOT(key)) {
        struct BoolExpr *temp = BX_Not(key);
        bool contradict = BX_Set_Contains(argset->xs, temp);
        BX_DecRef(temp);
        if (contradict) {
            argset->zero = true;
            argset->one = true;
            BX_Set_Clear(argset->xs);
            return true;
        }
    }

    /* Equal(x, x, y) = Equal(x, y) */
    return BX_Set_Insert(argset->xs, key);
}


struct BoolExpr *
BX_EqArgSet_Reduce(struct BX_EqArgSet *argset)
{
    struct BoolExpr **xs;
    struct BoolExpr *y;
    size_t length = argset->xs->length;

    /* Equal(0, 1) = 0 */
    if (argset->zero && argset->one)
        return BX_IncRef(&BX_Zero);

    /* Equal() = Equal(0) = Equal(1) = 1 */
    if (((size_t) argset->zero + (size_t) argset->one + length) <= 1)
        return BX_IncRef(&BX_One);

    CHECK_NULL(xs, _set2array(argset->xs));

    /* Equal(0, x) = ~x */
    if (argset->zero && length == 1) {
        y = BX_Not(xs[0]);
        free(xs);
        return y;
    }

    /* Equal(1, x) = x */
    if (argset->one && length == 1) {
        y = BX_IncRef(xs[0]);
        free(xs);
        return y;
    }

    /* Equal(0, x, y) = Nor(x, y) */
    if (argset->zero) {
        struct BoolExpr *temp = _bx_op_from(BX_OP_OR, length, xs);
        if (temp == NULL) {
            free(xs);    // LCOV_EXCL_LINE
            return NULL; // LCOV_EXCL_LINE
        }
        y = BX_Not(temp);
        BX_DecRef(temp);
        return y;
    }

    /* Equal(1, x, y) = And(x, y) */
    if (argset->one)
        return _bx_op_from(BX_OP_AND, length, xs);

    return _bx_op_from(BX_OP_EQ, length, xs);
}

