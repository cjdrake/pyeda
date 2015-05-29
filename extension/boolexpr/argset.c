/*
** Filename: argset.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


struct BoolExprOrAndArgSet *
BoolExprOrAndArgSet_New(BoolExprKind kind)
{
    struct BoolExprOrAndArgSet *argset;

    argset = (struct BoolExprOrAndArgSet *) malloc(sizeof(struct BoolExprOrAndArgSet));
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
    // x | ~x = 1 ; x & ~x = 0
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

    // x | (y | z) = x | y | z ; x & (y & z) = x & y & z
    if (key->kind == argset->kind) {
        for (size_t i = 0; i < key->data.xs->length; ++i) {
            if (!BoolExprOrAndArgSet_Insert(argset, key->data.xs->items[i]))
                return false; // LCOV_EXCL_LINE
        }
        return true;
    }

    // x | x = x ; x & x = x
    argset->min = false;
    return BoolExprSet_Insert(argset->xs, key);
}


struct BoolExprXorArgSet *
BoolExprXorArgSet_New(bool parity)
{
    struct BoolExprXorArgSet *argset;

    argset = (struct BoolExprXorArgSet *) malloc(sizeof(struct BoolExprXorArgSet));
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
        bool inset = BoolExprSet_Contains(argset->xs, temp);
        BoolExpr_DecRef(temp);
        if (inset) {
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


struct BoolExprEqArgSet *
BoolExprEqArgSet_New(void)
{
    struct BoolExprEqArgSet *argset;

    argset = (struct BoolExprEqArgSet *) malloc(sizeof(struct BoolExprEqArgSet));
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
        bool inset = BoolExprSet_Contains(argset->xs, temp);
        BoolExpr_DecRef(temp);
        if (inset) {
            argset->zero = true;
            argset->one = true;
            BoolExprSet_Clear(argset->xs);
            return true;
        }
    }

    /* Equal(x, x, y) = Equal(x, y) */
    return BoolExprSet_Insert(argset->xs, key);
}

