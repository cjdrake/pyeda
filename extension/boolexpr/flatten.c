/*
** Filename: flatten.c
**
** Disjunctive/Conjunctive Normal Form
*/


#include "boolexpr.h"


/* boolexpr.c */
BoolExpr * _op_new(BoolExprType t, size_t n, BoolExpr **xs);

/* nnf.c */
BoolExpr * _to_nnf(BoolExpr *ex);

/* simple.c */
BoolExpr * _simplify(BoolExpr *ex);

/* util.c */
BoolExpr * _op_transform(BoolExpr *op, BoolExpr * (*fn)(BoolExpr *));
void _mark_flags(BoolExpr *ex, BoolExprFlags f);
bool _is_clause(BoolExpr *op);


/* Convert a two-level expression to set of sets form */
static BoolExprArray2 *
_nf2sets(BoolExpr *nf)
{
    size_t length = nf->data.xs->length;
    size_t lengths[length];
    BoolExpr **items[length];

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
static BoolExpr *
_distribute(BoolExprType t, BoolExpr *nf)
{
    BoolExprArray2 *sets;
    BoolExprArray *product;
    BoolExpr *temp;
    BoolExpr *dnf;

    sets = _nf2sets(nf);

    /* LCOV_EXCL_START */
    if (sets == NULL)
        return NULL;
    /* LCOV_EXCL_STOP */

    product = BoolExprArray2_Product(sets, t);

    /* LCOV_EXCL_START */
    if (product == NULL) {
        BoolExprArray2_Del(sets);
        return NULL;
    }
    /* LCOV_EXCL_STOP */

    temp = _op_new(DUAL(t), product->length, product->items);

    /* LCOV_EXCL_START */
    if (temp == NULL) {
        BoolExprArray_Del(product);
        BoolExprArray2_Del(sets);
    }
    /* LCOV_EXCL_STOP */

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
_set_cmp(BoolExprArray *xs, BoolExprArray *ys)
{
    size_t i = 0, j = 0;
    unsigned int ret = XS_LTE_YS | YS_LTE_XS;

    while (i < xs->length && j < ys->length) {
        BoolExpr *x = xs->items[i];
        BoolExpr *y = ys->items[j];

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


static BoolExpr *
_absorb(BoolExpr *dnf)
{
    BoolExprArray2 *sets;
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
        BoolExpr *xs[count];
        BoolExpr *temp;
        BoolExpr *dnf2;

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


static BoolExpr *
_to_dnf(BoolExpr *nnf)
{
    if (IS_ATOM(nnf)) {
        return BoolExpr_IncRef(nnf);
    }
    else {
        BoolExpr *temp;
        BoolExpr *nf1, *nf2;
        BoolExpr *dnf;

        /* Convert sub-expressions to DNF */
        CHECK_NULL(temp, _op_transform(nnf, _to_dnf));
        CHECK_NULL_1(nf1, _simplify(temp), temp);
        BoolExpr_DecRef(temp);

        /* a ; a | b | c ; a & b & c ; a & b | c & d */
        if (IS_ATOM(nf1) || _is_clause(nf1) || IS_OR(nf1))
            return nf1;

        /* (a | b) & (c | d) */
        CHECK_NULL_1(nf2, _absorb(nf1), nf1);
        BoolExpr_DecRef(nf1);

        if (IS_ATOM(nf2) || _is_clause(nf2) || IS_OR(nf2))
            return nf2;

        CHECK_NULL(temp, _distribute(OP_AND, nf2));
        BoolExpr_DecRef(nf2);
        CHECK_NULL_1(dnf, _absorb(temp), temp);
        BoolExpr_DecRef(temp);

        return dnf;
    }
}


static BoolExpr *
_to_cnf(BoolExpr *nnf)
{
    if (IS_ATOM(nnf)) {
        return BoolExpr_IncRef(nnf);
    }
    else {
        BoolExpr *temp;
        BoolExpr *nf1, *nf2;
        BoolExpr *cnf;

        /* Convert sub-expressions to CNF */
        CHECK_NULL(temp, _op_transform(nnf, _to_cnf));
        CHECK_NULL_1(nf1, _simplify(temp), temp);
        BoolExpr_DecRef(temp);

        /* a ; a | b | c ; a & b & c ; (a | b) & (c | d) */
        if (IS_ATOM(nf1) || _is_clause(nf1) || IS_AND(nf1))
            return nf1;

        /* a & b | c & d */
        CHECK_NULL_1(nf2, _absorb(nf1), nf1);
        BoolExpr_DecRef(nf1);

        if (IS_ATOM(nf2) || _is_clause(nf2) || IS_AND(nf2))
            return nf2;

        CHECK_NULL(temp, _distribute(OP_OR, nf2));
        BoolExpr_DecRef(nf2);
        CHECK_NULL_1(cnf, _absorb(temp), temp);
        BoolExpr_DecRef(temp);

        return cnf;
    }
}


BoolExpr *
BoolExpr_ToDNF(BoolExpr *ex)
{
    BoolExpr *nnf;
    BoolExpr *dnf;

    CHECK_NULL(nnf, _to_nnf(ex));
    CHECK_NULL_1(dnf, _to_dnf(nnf), nnf);
    BoolExpr_DecRef(nnf);

    _mark_flags(dnf, NNF | SIMPLE);

    return dnf;
}


BoolExpr *
BoolExpr_ToCNF(BoolExpr *ex)
{
    BoolExpr *nnf;
    BoolExpr *cnf;

    CHECK_NULL(nnf, _to_nnf(ex));
    CHECK_NULL_1(cnf, _to_cnf(nnf), nnf);
    BoolExpr_DecRef(nnf);

    _mark_flags(cnf, NNF | SIMPLE);

    return cnf;
}


// FIXME: Implement splitvar heuristic
static BoolExpr *
_choose_var(BoolExpr *dnf)
{
    BoolExpr *lit = IS_LIT(dnf->data.xs->items[0])
                  ? dnf->data.xs->items[0]
                  : dnf->data.xs->items[0]->data.xs->items[0];

    if (IS_COMP(lit))
        return Not(lit);
    else
        return BoolExpr_IncRef(lit);
}


static bool
_cofactors(BoolExpr **fv0, BoolExpr **fv1, BoolExpr *f, BoolExpr *v)
{
    BoolExprDict *v0, *v1;

    v0 = BoolExprVarMap_New();
    /* LCOV_EXCL_START */
    if (v0 == NULL)
        return false;
    /* LCOV_EXCL_STOP */

    /* LCOV_EXCL_START */
    if (!BoolExprDict_Insert(v0, v, &Zero)) {
        BoolExprDict_Del(v0);
        return false;
    }
    /* LCOV_EXCL_STOP */

    *fv0 = BoolExpr_Restrict(f, v0);

    /* LCOV_EXCL_START */
    if (fv0 == NULL) {
        BoolExprDict_Del(v0);
        return false;
    }
    /* LCOV_EXCL_STOP */

    BoolExprDict_Del(v0);

    v1 = BoolExprVarMap_New();

    /* LCOV_EXCL_START */
    if (v1 == NULL)
        return false;
    /* LCOV_EXCL_STOP */

    /* LCOV_EXCL_START */
    if (!BoolExprDict_Insert(v1, v, &One)) {
        BoolExprDict_Del(v1);
        return false;
    }
    /* LCOV_EXCL_STOP */

    *fv1 = BoolExpr_Restrict(f, v1);

    /* LCOV_EXCL_START */
    if (fv1 == NULL) {
        BoolExprDict_Del(v1);
        return false;
    }
    /* LCOV_EXCL_STOP */

    BoolExprDict_Del(v1);

    return true;
}


/* CS(f) = [x0 | CS(0, x1, ..., xn)] & [~x0 | CS(1, x1, ..., xn)] */
static BoolExpr *
_complete_sum(BoolExpr *dnf)
{
    if (BoolExpr_Depth(dnf) <= 1) {
        return BoolExpr_IncRef(dnf);
    }
    else {
        BoolExpr *v, *vn;
        BoolExpr *fv0, *fv1;
        BoolExpr *cs0, *cs1;
        BoolExpr *left, *right;
        BoolExpr *temp;
        BoolExpr *y;

        CHECK_NULL(v, _choose_var(dnf));

        /* LCOV_EXCL_START */
        if (!_cofactors(&fv0, &fv1, dnf, v)) {
            BoolExpr_DecRef(v);
            return NULL;
        }
        /* LCOV_EXCL_STOP */

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


BoolExpr *
BoolExpr_CompleteSum(BoolExpr *ex)
{
    BoolExpr *dnf;
    BoolExpr *sum;

    if (BoolExpr_IsDNF(ex))
        dnf = BoolExpr_IncRef(ex);
    else
        CHECK_NULL(dnf, BoolExpr_ToDNF(ex));

    CHECK_NULL_1(sum, _complete_sum(dnf), dnf);
    BoolExpr_DecRef(dnf);

    return sum;
}

