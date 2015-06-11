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
#include "memcheck.h"


#define DUAL(kind) (OP_OR + OP_AND - kind)


/* boolexpr.c */
struct BoolExpr * _orandxor_new(BX_Kind kind, size_t n, struct BoolExpr **xs);

/* nnf.c */
struct BoolExpr * _to_nnf(struct BoolExpr *ex);

/* simple.c */
struct BoolExpr * _simplify(struct BoolExpr *ex);

/* util.c */
struct BoolExpr * _op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *));
void _mark_flags(struct BoolExpr *ex, BX_Flags f);
bool _is_clause(struct BoolExpr *op);


static void
_free_arrays(size_t length, struct BX_Array **arrays)
{
    for (size_t i = 0; i < length; ++i)
        BX_Array_Del(arrays[i]);
    free(arrays);
}


/* Convert a normal-form expression to arrays of arrays form */
static struct BX_Array **
_nf2arrays(struct BoolExpr *nf)
{
    size_t length = nf->data.xs->length;
    struct BX_Array **arrays;

    arrays = malloc(length * sizeof(struct BX_Array *));

    for (size_t i = 0; i < length; ++i) {
        if (BX_IS_LIT(nf->data.xs->items[i]))
            arrays[i] = BX_Array_New(1, &nf->data.xs->items[i]);
        else
            arrays[i] = BX_Array_New(nf->data.xs->items[i]->data.xs->length,
                                     nf->data.xs->items[i]->data.xs->items);
        if (arrays[i] == NULL) {
            _free_arrays(i, arrays); // LCOV_EXCL_LINE
            return NULL;             // LCOV_EXCL_LINE
        }
    }

    return arrays;
}


/* NOTE: Return size is exponential */
static struct BoolExpr *
_distribute(BX_Kind kind, struct BoolExpr *nf)
{
    size_t length = nf->data.xs->length;
    struct BX_Array **arrays;
    struct BX_Array *product;
    struct BoolExpr *temp;
    struct BoolExpr *y;

    assert(nf->kind == kind);

    arrays = _nf2arrays(nf);
    if (arrays == NULL)
        return NULL; // LCOV_EXCL_LINE

    product = BX_Product(kind, length, arrays);
    if (product == NULL) {
        _free_arrays(length, arrays); // LCOV_EXCL_LINE
        return NULL;                  // LCOV_EXCL_LINE
    }

    temp = _orandxor_new(DUAL(kind), product->length, product->items);
    if (temp == NULL) {
        BX_Array_Del(product);   // LCOV_EXCL_LINE
        _free_arrays(length, arrays); // LCOV_EXCL_LINE
    }

    BX_Array_Del(product);
    _free_arrays(length, arrays);

    CHECK_NULL_1(y, _simplify(temp), temp);
    BX_DecRef(temp);

    return y;
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
_lits_cmp(struct BX_Array *xs, struct BX_Array *ys)
{
    size_t i = 0, j = 0;
    unsigned int ret = XS_LTE_YS | YS_LTE_XS;

    while (i < xs->length && j < ys->length) {
        struct BoolExpr *x = xs->items[i];
        struct BoolExpr *y = ys->items[j];

        assert(BX_IS_LIT(x) && BX_IS_LIT(y));

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
_absorb(struct BoolExpr *nf)
{
    int length = nf->data.xs->length;
    bool *keep;
    struct BX_Array **arrays;
    unsigned int val;
    size_t count = 0;

    arrays = _nf2arrays(nf);
    if (arrays == NULL)
        return NULL; // LCOV_EXCL_LINE

    keep = malloc(length * sizeof(bool));
    if (keep == NULL) {
        _free_arrays(length, arrays); // LCOV_EXCL_LINE
        return NULL;                  // LCOV_EXCL_LINE
    }

    /* Keep all clauses by default */
    for (size_t i = 0; i < length; ++i)
        keep[i] = true;

    for (size_t i = 0; i < (length-1); ++i) {
        if (keep[i]) {
            for (size_t j = i+1; j < length; ++j) {
                val = _lits_cmp(arrays[i], arrays[j]);
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

    _free_arrays(length, arrays);

    for (size_t i = 0; i < length; ++i)
        count += (size_t) keep[i];

    if (count == length) {
        free(keep);
        return BX_IncRef(nf);
    }

    struct BoolExpr **xs;
    struct BoolExpr *temp;
    struct BoolExpr *y;

    xs = malloc(count * sizeof(struct BoolExpr *));
    if (xs == NULL) {
        free(keep);  // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    for (size_t i = 0, index = 0; i < length; ++i) {
        if (keep[i])
            xs[index++] = nf->data.xs->items[i];
    }

    free(keep);

    temp = _orandxor_new(nf->kind, count, xs);
    if (temp == NULL) {
        free(xs);    // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    y = _simplify(temp);
    BX_DecRef(temp);

    free(xs);

    return y;
}


static struct BoolExpr *
_to_dnf(struct BoolExpr *nnf)
{
    if (BX_IS_ATOM(nnf) || _is_clause(nnf))
        return BX_IncRef(nnf);

    struct BoolExpr *temp;
    struct BoolExpr *ex;

    /* Convert sub-expressions to DNF */
    CHECK_NULL(temp, _op_transform(nnf, _to_dnf));
    CHECK_NULL_1(ex, _simplify(temp), temp);
    BX_DecRef(temp);

    /* a ; a | b ; a & b */
    if (BX_IS_ATOM(ex) || _is_clause(ex))
        return ex;

    /* a | b & c */
    if (BX_IS_OR(ex)) {
        temp = ex;
        ex = _absorb(temp);
        BX_DecRef(temp);
        return ex;
    }

    /* (a | b) & (c | d) */
    temp = ex;
    CHECK_NULL_1(ex, _distribute(OP_AND, temp), temp);
    BX_DecRef(temp);

    /* a ; a | b ; a & b */
    if (BX_IS_ATOM(ex) || _is_clause(ex))
        return ex;

    temp = ex;
    ex = _absorb(temp);
    BX_DecRef(temp);
    return ex;
}


static struct BoolExpr *
_to_cnf(struct BoolExpr *nnf)
{
    if (BX_IS_ATOM(nnf) || _is_clause(nnf))
        return BX_IncRef(nnf);

    struct BoolExpr *temp;
    struct BoolExpr *ex;

    /* Convert sub-expressions to CNF */
    CHECK_NULL(temp, _op_transform(nnf, _to_cnf));
    CHECK_NULL_1(ex, _simplify(temp), temp);
    BX_DecRef(temp);

    /* a ; a | b ; a & b */
    if (BX_IS_ATOM(ex) || _is_clause(ex))
        return ex;

    /* a & (b | c) */
    if (BX_IS_AND(ex)) {
        temp = ex;
        ex = _absorb(temp);
        BX_DecRef(temp);
        return ex;
    }

    /* a & b | c & d */
    temp = ex;
    CHECK_NULL_1(ex, _distribute(OP_OR, temp), temp);
    BX_DecRef(temp);

    /* a ; a | b ; a & b */
    if (BX_IS_ATOM(ex) || _is_clause(ex))
        return ex;

    temp = ex;
    ex = _absorb(temp);
    BX_DecRef(temp);
    return ex;
}


struct BoolExpr *
BX_ToDNF(struct BoolExpr *ex)
{
    struct BoolExpr *nnf;
    struct BoolExpr *dnf;

    CHECK_NULL(nnf, _to_nnf(ex));
    CHECK_NULL_1(dnf, _to_dnf(nnf), nnf);
    BX_DecRef(nnf);

    _mark_flags(dnf, BX_NNF | BX_SIMPLE);

    return dnf;
}


struct BoolExpr *
BX_ToCNF(struct BoolExpr *ex)
{
    struct BoolExpr *nnf;
    struct BoolExpr *cnf;

    CHECK_NULL(nnf, _to_nnf(ex));
    CHECK_NULL_1(cnf, _to_cnf(nnf), nnf);
    BX_DecRef(nnf);

    _mark_flags(cnf, BX_NNF | BX_SIMPLE);

    return cnf;
}


// FIXME: Implement splitvar heuristic
static struct BoolExpr *
_choose_var(struct BoolExpr *dnf)
{
    struct BoolExpr *lit = BX_IS_LIT(dnf->data.xs->items[0])
                         ? dnf->data.xs->items[0]
                         : dnf->data.xs->items[0]->data.xs->items[0];

    if (BX_IS_COMP(lit))
        return BX_Not(lit);
    else
        return BX_IncRef(lit);
}


static bool
_cofactors(struct BoolExpr **fv0, struct BoolExpr **fv1, struct BoolExpr *f, struct BoolExpr *v)
{
    struct BX_Dict *v0, *v1;

    v0 = BX_Dict_New();
    if (v0 == NULL)
        return false; // LCOV_EXCL_LINE

    if (!BX_Dict_Insert(v0, v, &BX_Zero)) {
        BX_Dict_Del(v0); // LCOV_EXCL_LINE
        return false;         // LCOV_EXCL_LINE
    }

    *fv0 = BX_Restrict(f, v0);
    if (fv0 == NULL) {
        BX_Dict_Del(v0); // LCOV_EXCL_LINE
        return false;         // LCOV_EXCL_LINE
    }

    BX_Dict_Del(v0);

    v1 = BX_Dict_New();
    if (v1 == NULL)
        return false; // LCOV_EXCL_LINE

    if (!BX_Dict_Insert(v1, v, &BX_One)) {
        BX_Dict_Del(v1); // LCOV_EXCL_LINE
        return false;         // LCOV_EXCL_LINE
    }

    *fv1 = BX_Restrict(f, v1);
    if (fv1 == NULL) {
        BX_Dict_Del(v1); // LCOV_EXCL_LINE
        return false;         // LCOV_EXCL_LINE
    }

    BX_Dict_Del(v1);

    return true;
}


/* CS(f) = [x0 | CS(0, x1, ..., xn)] & [~x0 | CS(1, x1, ..., xn)] */
static struct BoolExpr *
_complete_sum(struct BoolExpr *dnf)
{
    if (BX_Depth(dnf) <= 1) {
        return BX_IncRef(dnf);
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
            BX_DecRef(v); // LCOV_EXCL_LINE
            return NULL;  // LCOV_EXCL_LINE
        }

        CHECK_NULL_3(cs0, _complete_sum(fv0), v, fv0, fv1);
        BX_DecRef(fv0);

        CHECK_NULL_3(left, BX_OrN(2, v, cs0), v, fv1, cs0);
        BX_DecRef(v);
        BX_DecRef(cs0);

        CHECK_NULL_2(cs1, _complete_sum(fv1), fv1, left);
        BX_DecRef(fv1);

        CHECK_NULL_2(vn, BX_Not(v), left, cs1);
        CHECK_NULL_3(right, BX_OrN(2, vn, cs1), left, cs1, vn);
        BX_DecRef(cs1);
        BX_DecRef(vn);

        CHECK_NULL_2(temp, BX_AndN(2, left, right), left, right);
        BX_DecRef(left);
        BX_DecRef(right);

        CHECK_NULL_1(y, BX_ToDNF(temp), temp);
        BX_DecRef(temp);

        return y;
    }
}


struct BoolExpr *
BX_CompleteSum(struct BoolExpr *ex)
{
    struct BoolExpr *dnf;
    struct BoolExpr *sum;

    if (BX_IsDNF(ex))
        dnf = BX_IncRef(ex);
    else
        CHECK_NULL(dnf, BX_ToDNF(ex));

    CHECK_NULL_1(sum, _complete_sum(dnf), dnf);
    BX_DecRef(dnf);

    return sum;
}

