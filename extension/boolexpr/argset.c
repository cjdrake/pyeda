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
    // 1 + x = 1 ; 0 & x = 0
    // x + 0 = x ; x & 1 = x
    if (argset->max || key == IDENTITY[argset->kind])
        return true;

    bool dominate = false;
    // x + 1 = 1 ; x & 0 = 0
    if (key == DOMINATOR[argset->kind]) {
        dominate = true;
    }
    // x + ~x = 1 ; x & ~x = 0
    else if (IS_LIT(key) || IS_NOT(key)) {
        struct BoolExpr *ex = Not(key);
        dominate = BoolExprSet_Contains(argset->xs, ex);
        BoolExpr_DecRef(ex);
    }
    if (dominate) {
        argset->min = false;
        argset->max = true;
        BoolExprSet_Clear(argset->xs);
        return true;
    }

    // x + (y + z) = x + y + z ; x & (y & z) = x & y & z
    if (key->kind == argset->kind) {
        for (size_t i = 0; i < key->data.xs->length; ++i) {
            if (!BoolExprOrAndArgSet_Insert(argset, key->data.xs->items[i]))
                return false; // LCOV_EXCL_LINE
        }
        return true;
    }

    // x + x = x
    if (!BoolExprSet_Insert(argset->xs, key))
        return false; // LCOV_EXCL_LINE
    argset->min = false;

    return true;
}

