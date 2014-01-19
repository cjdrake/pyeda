// Filename: primes.c

#include "espresso.h"

static bool primes_consensus_special_cases(set **T, set_family_t **Tnew);
static set_family_t *primes_consensus_merge(set_family_t *Tl, set_family_t *Tr, set *cl, set *cr);
static set_family_t *and_with_cofactor(set_family_t *A, set *cof);

// primes_consensus -- generate primes using consensus
set_family_t *
primes_consensus(set **T)
{
    set *cl, *cr;
    int best;
    set_family_t *Tnew, *Tl, *Tr;

    if (primes_consensus_special_cases(T, &Tnew) == MAYBE) {
        cl = set_new(CUBE.size);
        cr = set_new(CUBE.size);
        best = binate_split_select(T, cl, cr, COMPL);

        Tl = primes_consensus(scofactor(T, cl, best));
        Tr = primes_consensus(scofactor(T, cr, best));
        Tnew = primes_consensus_merge(Tl, Tr, cl, cr);

        set_free(cl);
        set_free(cr);
        free_cubelist(T);
    }

    return Tnew;
}

static bool
primes_consensus_special_cases(set **T, set_family_t **Tnew)
{
    set **T1, *p, *ceil, *cof=T[0];
    set *last;
    set_family_t *A;

    // Check for no cubes in the cover
    if (T[2] == NULL) {
        *Tnew = sf_new(0, CUBE.size);
        free_cubelist(T);
        return TRUE;
    }

    // Check for only a single cube in the cover
    if (T[3] == NULL) {
        *Tnew = sf_addset(sf_new(1, CUBE.size), set_or(cof, cof, T[2]));
        free_cubelist(T);
        return TRUE;
    }

    // Check for a row of all 1's (implies function is a tautology)
    for (T1 = T+2; (p = *T1++) != NULL; ) {
        if (full_row(p, cof)) {
            *Tnew = sf_addset(sf_new(1, CUBE.size), CUBE.fullset);
            free_cubelist(T);
            return TRUE;
        }
    }

    // Check for a column of all 0's which can be factored out
    ceil = set_save(cof);
    for (T1 = T+2; (p = *T1++) != NULL; ) {
        set_or(ceil, ceil, p);
    }
    if (! setp_equal(ceil, CUBE.fullset)) {
        p = set_new(CUBE.size);
        set_diff(p, CUBE.fullset, ceil);
        set_or(cof, cof, p);
        set_free(p);

        A = primes_consensus(T);
        foreach_set(A, last, p) {
            set_and(p, p, ceil);
        }
        *Tnew = A;
        set_free(ceil);
        return TRUE;
    }
    set_free(ceil);

    // Collect column counts, determine unate variables, etc.
    massive_count(T);

    // If single active variable not factored out above, then tautology!
    if (CDATA.vars_active == 1) {
        *Tnew = sf_addset(sf_new(1, CUBE.size), CUBE.fullset);
        free_cubelist(T);
        return TRUE;
    }
    // Check for unate cover
    else if (CDATA.vars_unate == CDATA.vars_active) {
        A = cubeunlist(T);
        *Tnew = sf_contain(A);
        free_cubelist(T);
        return TRUE;
    }
    // Not much we can do about it
    else {
        return MAYBE;
    }
}

static set_family_t *
primes_consensus_merge(set_family_t *Tl, set_family_t *Tr, set *cl, set *cr)
{
    set *pl, *pr, *lastl, *lastr, *pt;
    set_family_t *T, *Tsave;

    Tl = and_with_cofactor(Tl, cl);
    Tr = and_with_cofactor(Tr, cr);

    T = sf_new(500, Tl->sf_size);
    pt = T->data;
    Tsave = sf_contain(sf_join(Tl, Tr));

    foreach_set(Tl, lastl, pl) {
        foreach_set(Tr, lastr, pr) {
            if (cdist01(pl, pr) == 1) {
                consensus(pt, pl, pr);
                if (++T->count >= T->capacity) {
                    Tsave = sf_union(Tsave, sf_contain(T));
                    T = sf_new(500, Tl->sf_size);
                    pt = T->data;
                }
                else {
                    pt += T->wsize;
                }
            }
        }
    }
    sf_free(Tl);
    sf_free(Tr);

    Tsave = sf_union(Tsave, sf_contain(T));
    return Tsave;
}

static set_family_t *
and_with_cofactor(set_family_t *A, set *cof)
{
    set *last, *p;

    foreach_set(A, last, p) {
        set_and(p, p, cof);
        if (cdist(p, CUBE.fullset) > 0) {
            RESET(p, ACTIVE);
        }
        else {
            SET(p, ACTIVE);
        }
    }
    return sf_inactive(A);
}

