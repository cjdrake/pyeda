/*
** Filename: flatten.c
**
** Disjunctive/Conjunctive Normal Form
*/


#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* boolexpr.c */
struct BoolExpr * _op_new(BoolExprType t, size_t n, struct BoolExpr **xs);

/* nnf.c */
struct BoolExpr * _to_nnf(struct BoolExpr *ex);

/* simple.c */
struct BoolExpr * _simplify(struct BoolExpr *ex);

/* util.c */
struct BoolExpr * _op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *));
void _mark_flags(struct BoolExpr *ex, BoolExprFlags f);
bool _is_clause(struct BoolExpr *op);


/* Convert a two-level expression to set of sets form */
static struct BoolExprArray2 *
_nf2sets(struct BoolExpr *nf)
{
    size_t length = nf->data.xs->length;
    size_t lengths[length];
    struct BoolExpr **items[length];

    for (size_t i = 0; i < length; ++i) {
        if (IS_LIT(nf->data.xs->items[i])) {
            lengths[i] = 1;
            items[i] = &nf->data.xs->items[i];
        }
        else {
            lengths[i] = nf->data.xs->items[i]->data.xs->length;
            items[i] = nf->data.xs->items[i]->data.xs->items;
        }
    }

    return BoolExprArray2_New(length, lengths, items);
}


/* NOTE: Return size is exponential */
static struct BoolExpr *
_distribute(BoolExprType t, struct BoolExpr *nf)
{
    struct BoolExprArray2 *sets;
    struct BoolExprArray *product;
    struct BoolExpr *temp;
    struct BoolExpr *dnf;

    assert(nf->type == t);

    sets = _nf2sets(nf);
    if (sets == NULL)
        return NULL; // LCOV_EXCL_LINE

    product = BoolExprArray2_Product(sets, t);
    if (product == NULL) {
        BoolExprArray2_Del(sets); // LCOV_EXCL_LINE
        return NULL;              // LCOV_EXCL_LINE
    }

    temp = _op_new(DUAL(t), product->length, product->items);
    if (temp == NULL) {
        BoolExprArray_Del(product); // LCOV_EXCL_LINE
        BoolExprArray2_Del(sets);   // LCOV_EXCL_LINE
    }

    BoolExprArray_Del(product);
    BoolExprArray2_Del(sets);

    CHECK_NULL_1(dnf, _simplify(temp), temp);
    BoolExpr_DecRef(temp);

    return dnf;
}


/*
** Return an int that shows set membership.
**
** xs <= ys: 1
** xs >= ys: 2
** xs == ys: 3
**
** NOTE: This algorithm requires the literals to be sorted.
*/

#define XS_LTE_YS (1u << 0)
#define YS_LTE_XS (1u << 1)

static unsigned int
_set_cmp(struct BoolExprArray *xs, struct BoolExprArray *ys)
{
    size_t i = 0, j = 0;
    unsigned int ret = XS_LTE_YS | YS_LTE_XS;

    while (i < xs->length && j < ys->length) {
        struct BoolExpr *x = xs->items[i];
        struct BoolExpr *y = ys->items[j];

        assert(IS_LIT(x) && IS_LIT(y));

        if (x == y) {
            i += 1;
            j += 1;
        }
        else {
            long abs_x = labs(x->data.lit.uniqid);
            long abs_y = labs(y->data.lit.uniqid);

            if (abs_x < abs_y) {
                ret &= ~XS_LTE_YS;
                i += 1;
            }
            else if (abs_x > abs_y) {
                ret &= ~YS_LTE_XS;
                j += 1;
            }
            else {
                break;
            }
        }
    }

    if (i < xs->length)
        ret &= ~XS_LTE_YS;
    if (j < ys->length)
        ret &= ~YS_LTE_XS;

    return ret;
}


static struct BoolExpr *
_absorb(struct BoolExpr *dnf)
{
    struct BoolExprArray2 *sets;
    int length = dnf->data.xs->length;
    unsigned int val;
    bool keep[length];
    size_t count = 0;

    for (size_t i = 0; i < length; ++i)
        keep[i] = true;

    sets = _nf2sets(dnf);

    for (size_t i = 0; i < (length-1); ++i) {
        if (keep[i]) {
            for (size_t j = i+1; j < length; ++j) {
                val = _set_cmp(sets->items[i], sets->items[j]);
                /* xs <= ys */
                if (val & 1) {
                    keep[j] = false;
                }
                /* xs > ys */
                else if (val & 2) {
                    keep[i] = false;
                    break;
                }
            }
        }
    }

    BoolExprArray2_Del(sets);

    for (size_t i = 0; i < length; ++i)
        count += (size_t) keep[i];

    if (count == length) {
        return BoolExpr_IncRef(dnf);
    }
    else {
        struct BoolExpr *xs[count];
        struct BoolExpr *temp;
        struct BoolExpr *dnf2;

        for (size_t i = 0, index = 0; i < length; ++i) {
            if (keep[i])
                xs[index++] = dnf->data.xs->items[i];
        }

        CHECK_NULL(temp, _op_new(dnf->type, count, xs));
        CHECK_NULL_1(dnf2, _simplify(temp), temp);
        BoolExpr_DecRef(temp);

        return dnf2;
    }
}


static struct BoolExpr *
_to_dnf(struct BoolExpr *nnf)
{
    if (IS_ATOM(nnf)) {
        return BoolExpr_IncRef(nnf);
    }
    else {
        struct BoolExpr *temp;
        struct BoolExpr *nf;

        /* Convert sub-expressions to DNF */
        CHECK_NULL(temp, _op_transform(nnf, _to_dnf));
        CHECK_NULL_1(nf, _simplify(temp), temp);
        BoolExpr_DecRef(temp);

        if (IS_ATOM(nf) || _is_clause(nf)) {
            return nf;
        }
        else if (IS_OR(nf)) {
            temp = nf;
            CHECK_NULL_1(nf, _absorb(temp), temp);
            BoolExpr_DecRef(temp);
            return nf;
        }

        /* (a | b) & (c | d) */
        temp = nf;
        CHECK_NULL_1(nf, _distribute(OP_AND, temp), temp);
        BoolExpr_DecRef(temp);

        if (IS_ATOM(nf) || _is_clause(nf)) {
            return nf;
        }
        else {
            temp = nf;
            CHECK_NULL_1(nf, _absorb(temp), temp);
            BoolExpr_DecRef(temp);
            return nf;
        }
    }
}


static struct BoolExpr *
_to_cnf(struct BoolExpr *nnf)
{
    if (IS_ATOM(nnf)) {
        return BoolExpr_IncRef(nnf);
    }
    else {
        struct BoolExpr *temp;
        struct BoolExpr *nf;

        /* Convert sub-expressions to CNF */
        CHECK_NULL(temp, _op_transform(nnf, _to_cnf));
        CHECK_NULL_1(nf, _simplify(temp), temp);
        BoolExpr_DecRef(temp);

        if (IS_ATOM(nf) || _is_clause(nf)) {
            return nf;
        }
        else if (IS_AND(nf)) {
            temp = nf;
            CHECK_NULL_1(nf, _absorb(temp), temp);
            BoolExpr_DecRef(temp);
            return nf;
        }

        /* a & b | c & d */
        temp = nf;
        CHECK_NULL_1(nf, _distribute(OP_OR, temp), temp);
        BoolExpr_DecRef(temp);

        if (IS_ATOM(nf) || _is_clause(nf)) {
            return nf;
        }
        else {
            temp = nf;
            CHECK_NULL_1(nf, _absorb(temp), temp);
            BoolExpr_DecRef(temp);
            return nf;
        }
    }
}


struct BoolExpr *
BoolExpr_ToDNF(struct BoolExpr *ex)
{
    struct BoolExpr *nnf;
    struct BoolExpr *dnf;

    CHECK_NULL(nnf, _to_nnf(ex));
    CHECK_NULL_1(dnf, _to_dnf(nnf), nnf);
    BoolExpr_DecRef(nnf);

    _mark_flags(dnf, NNF | SIMPLE);

    return dnf;
}


struct BoolExpr *
BoolExpr_ToCNF(struct BoolExpr *ex)
{
    struct BoolExpr *nnf;
    struct BoolExpr *cnf;

    CHECK_NULL(nnf, _to_nnf(ex));
    CHECK_NULL_1(cnf, _to_cnf(nnf), nnf);
    BoolExpr_DecRef(nnf);

    _mark_flags(cnf, NNF | SIMPLE);

    return cnf;
}


// FIXME: Implement splitvar heuristic
static struct BoolExpr *
_choose_var(struct BoolExpr *dnf)
{
    struct BoolExpr *lit = IS_LIT(dnf->data.xs->items[0])
                         ? dnf->data.xs->items[0]
                         : dnf->data.xs->items[0]->data.xs->items[0];

    if (IS_COMP(lit))
        return Not(lit);
    else
        return BoolExpr_IncRef(lit);
}


static bool
_cofactors(struct BoolExpr **fv0, struct BoolExpr **fv1, struct BoolExpr *f, struct BoolExpr *v)
{
    struct BoolExprDict *v0, *v1;

    v0 = BoolExprVarMap_New();
    if (v0 == NULL)
        return false; // LCOV_EXCL_LINE

    if (!BoolExprDict_Insert(v0, v, &Zero)) {
        BoolExprDict_Del(v0); // LCOV_EXCL_LINE
        return false;         // LCOV_EXCL_LINE
    }

    *fv0 = BoolExpr_Restrict(f, v0);
    if (fv0 == NULL) {
        BoolExprDict_Del(v0); // LCOV_EXCL_LINE
        return false;         // LCOV_EXCL_LINE
    }

    BoolExprDict_Del(v0);

    v1 = BoolExprVarMap_New();
    if (v1 == NULL)
        return false; // LCOV_EXCL_LINE

    if (!BoolExprDict_Insert(v1, v, &One)) {
        BoolExprDict_Del(v1); // LCOV_EXCL_LINE
        return false;         // LCOV_EXCL_LINE
    }

    *fv1 = BoolExpr_Restrict(f, v1);
    if (fv1 == NULL) {
        BoolExprDict_Del(v1); // LCOV_EXCL_LINE
        return false;         // LCOV_EXCL_LINE
    }

    BoolExprDict_Del(v1);

    return true;
}


/* CS(f) = [x0 | CS(0, x1, ..., xn)] & [~x0 | CS(1, x1, ..., xn)] */
static struct BoolExpr *
_complete_sum(struct BoolExpr *dnf)
{
    if (BoolExpr_Depth(dnf) <= 1) {
        return BoolExpr_IncRef(dnf);
    }
    else {
        struct BoolExpr *v, *vn;
        struct BoolExpr *fv0, *fv1;
        struct BoolExpr *cs0, *cs1;
        struct BoolExpr *left, *right;
        struct BoolExpr *temp;
        struct BoolExpr *y;

        CHECK_NULL(v, _choose_var(dnf));

        if (!_cofactors(&fv0, &fv1, dnf, v)) {
            BoolExpr_DecRef(v); // LCOV_EXCL_LINE
            return NULL;        // LCOV_EXCL_LINE
        }

        CHECK_NULL_3(cs0, _complete_sum(fv0), v, fv0, fv1);
        BoolExpr_DecRef(fv0);

        CHECK_NULL_3(left, OrN(2, v, cs0), v, fv1, cs0);
        BoolExpr_DecRef(v);
        BoolExpr_DecRef(cs0);

        CHECK_NULL_2(cs1, _complete_sum(fv1), fv1, left);
        BoolExpr_DecRef(fv1);

        CHECK_NULL_2(vn, Not(v), left, cs1);
        CHECK_NULL_3(right, OrN(2, vn, cs1), left, cs1, vn);
        BoolExpr_DecRef(cs1);
        BoolExpr_DecRef(vn);

        CHECK_NULL_2(temp, AndN(2, left, right), left, right);
        BoolExpr_DecRef(left);
        BoolExpr_DecRef(right);

        CHECK_NULL_1(y, BoolExpr_ToDNF(temp), temp);
        BoolExpr_DecRef(temp);

        return y;
    }
}


struct BoolExpr *
BoolExpr_CompleteSum(struct BoolExpr *ex)
{
    struct BoolExpr *dnf;
    struct BoolExpr *sum;

    if (BoolExpr_IsDNF(ex))
        dnf = BoolExpr_IncRef(ex);
    else
        CHECK_NULL(dnf, BoolExpr_ToDNF(ex));

    CHECK_NULL_1(sum, _complete_sum(dnf), dnf);
    BoolExpr_DecRef(dnf);

    return sum;
}

