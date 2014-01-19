//
// sharp.c -- perform sharp, disjoint sharp, and intersection
//

#include "espresso.h"

// cv_sharp -- form the sharp product between two covers
//
//

set_family_t *
cv_sharp(set_family_t *A, set_family_t *B)
{
    set *last, *p;
    set_family_t *T;

    T = sf_new(0, CUBE.size);
    foreach_set(A, last, p)
        T = sf_union(T, cb_sharp(p, B));

    return T;
}

// cb_sharp -- form the sharp product between a cube and a cover
//
//

set_family_t *
cb_sharp(set *c, set_family_t *T)
{
    if (T->count == 0) {
        T = sf_addset(sf_new(1, CUBE.size), c);
    }
    else {
        T = cb_recur_sharp(c, T, 0, T->count-1, 0);
    }

    return T;
}

// recursive formulation to provide balanced merging
//
//

set_family_t *
cb_recur_sharp(set *c, set_family_t *T, int first, int last, int level)
{
    set_family_t *temp, *left, *right;
    int middle;

    if (first == last) {
        temp = sharp(c, GETSET(T, first));
    }
    else {
        middle = (first + last) / 2;
        left = cb_recur_sharp(c, T, first, middle, level+1);
        right = cb_recur_sharp(c, T, middle+1, last, level+1);
        temp = cv_intersect(left, right);
        if ((debug & SHARP) && level < 4) {
            printf("# SHARP[%d]: %4d = %4d x %4d\n", level, temp->count, left->count, right->count);
            fflush(stdout);
        }
        sf_free(left);
        sf_free(right);
    }

    return temp;
}

// sharp -- form the sharp product between two cubes
//
//

set_family_t *
sharp(set *a, set *b)
{
    int var;
    set *d = CUBE.temp[0], *temp = CUBE.temp[1], *temp1 = CUBE.temp[2];
    set_family_t *r = sf_new(CUBE.num_vars, CUBE.size);

    if (cdist0(a, b)) {
        set_diff(d, a, b);
        for (var = 0; var < CUBE.num_vars; var++) {
            if (! setp_empty(set_and(temp, d, CUBE.var_mask[var]))) {
                set_diff(temp1, a, CUBE.var_mask[var]);
                set_or(GETSET(r, r->count++), temp, temp1);
            }
        }
    }
    else {
        r = sf_addset(r, a);
    }

    return r;
}

set_family_t *
make_disjoint(set_family_t *A)
{
    set_family_t *R, *new;
    set *last, *p;

    R = sf_new(0, CUBE.size);
    foreach_set(A, last, p) {
        new = cb_dsharp(p, R);
        R = sf_append(R, new);
    }

    return R;
}

// cv_dsharp -- disjoint-sharp product between two covers
//
//

set_family_t *
cv_dsharp(set_family_t *A, set_family_t *B)
{
    set *last, *p;
    set_family_t *T;

    T = sf_new(0, CUBE.size);
    foreach_set(A, last, p) {
        T = sf_union(T, cb_dsharp(p, B));
    }

    return T;
}

// cb1_dsharp -- disjoint-sharp product between a cover and a cube
//
//

set_family_t *
cb1_dsharp(set_family_t *T, set *c)
{
    set *last, *p;
    set_family_t *R;

    R = sf_new(T->count, CUBE.size);
    foreach_set(T, last, p) {
        R = sf_union(R, dsharp(p, c));
    }

    return R;
}

// cb_dsharp -- disjoint-sharp product between a cube and a cover
//
//

set_family_t *
cb_dsharp(set *c, set_family_t *T)
{
    set *last, *p;
    set_family_t *Y, *Y1;

    if (T->count == 0) {
        Y = sf_addset(sf_new(1, CUBE.size), c);
    }
    else {
        Y = sf_new(T->count, CUBE.size);
        set_copy(GETSET(Y,Y->count++), c);
        foreach_set(T, last, p) {
            Y1 = cb1_dsharp(Y, p);
            sf_free(Y);
            Y = Y1;
        }
    }

    return Y;
}

// dsharp -- form the disjoint-sharp product between two cubes
//
//

set_family_t *
dsharp(set *a, set *b)
{
    set *mask, *diff, *and, *temp, *temp1 = CUBE.temp[0];
    int var;
    set_family_t *r;

    r = sf_new(CUBE.num_vars, CUBE.size);

    if (cdist0(a, b)) {
        diff = set_diff(set_new(CUBE.size), a, b);
        and = set_and(set_new(CUBE.size), a, b);
        mask = set_new(CUBE.size);
        for (var = 0; var < CUBE.num_vars; var++) {
            // check if position var of "a and not b" is not empty
            if (! setp_disjoint(diff, CUBE.var_mask[var])) {
                // coordinate var equals the difference between a and b
                temp = GETSET(r, r->count++);
                set_and(temp, diff, CUBE.var_mask[var]);

                // coordinates 0 ... var-1 equal the intersection
                set_and(temp1, and, mask);
                set_or(temp, temp, temp1);

                // coordinates var+1 .. CUBE.num_vars equal a
                set_or(mask, mask, CUBE.var_mask[var]);
                set_diff(temp1, a, mask);
                set_or(temp, temp, temp1);
            }
        }
        set_free(diff);
        set_free(and);
        set_free(mask);
    }
    else {
        r = sf_addset(r, a);
    }

    return r;
}

// cv_intersect -- form the intersection of two covers
//
//

#define MAGIC 500   // save 500 cubes before containment

set_family_t *
cv_intersect(set_family_t *A, set_family_t *B)
{
    set *pi, *pj, *lasti, *lastj, *pt;
    set_family_t *T, *Tsave = NULL;

    // How large should each temporary result cover be ?
    T = sf_new(MAGIC, CUBE.size);
    pt = T->data;

    // Form pairwise intersection of each cube of A with each cube of B
    foreach_set(A, lasti, pi) {
        foreach_set(B, lastj, pj) {
            if (cdist0(pi, pj)) {
                set_and(pt, pi, pj);
                if (++T->count >= T->capacity) {
                    if (Tsave == NULL)
                        Tsave = sf_contain(T);
                    else
                        Tsave = sf_union(Tsave, sf_contain(T));
                    T = sf_new(MAGIC, CUBE.size);
                    pt = T->data;
                }
                else
                    pt += T->wsize;
            }
        }
    }

    if (Tsave == NULL)
        Tsave = sf_contain(T);
    else
        Tsave = sf_union(Tsave, sf_contain(T));

    return Tsave;
}

