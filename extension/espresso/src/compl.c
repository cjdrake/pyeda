// Filename: compl.c
//
// purpose: compute the complement of a multiple-valued function
//
// The "unate recursive paradigm" is used.  After a set of special
// cases are examined, the function is split on the "most active
// variable".  These two halves are complemented recursively, and then
// the results are merged.
//
// Changes (from Version 2.1 to Version 2.2)
//     1. Minor bug in compl_lifting -- cubes in the left half were
//     not marked as active, so that when merging a leaf from the left
//     hand side, the active flags were essentially random.  This led
//     to minor impredictability problem, but never affected the
//     accuracy of the results.
//

#include "espresso.h"

#define USE_COMPL_LIFT                  0
#define USE_COMPL_LIFT_ONSET            1
#define USE_COMPL_LIFT_ONSET_COMPLEX    2
#define NO_LIFTING                      3

static bool compl_special_cases(set **T, set_family_t **Tbar);
static set_family_t *compl_merge(set **T1, set_family_t *L, set_family_t *R, set *cl, set *cr, int var, int lifting);
static void compl_d1merge(set **L1, set **R1);
static set_family_t *compl_cube(set *p);
static void compl_lift(set **A1, set **B1, set *bcube, int var);
static void compl_lift_onset(set **A1, set_family_t *T, set *bcube, int var);
static void compl_lift_onset_complex(set **A1, set_family_t *T, int var);
static bool simp_comp_special_cases(set **T, set_family_t **Tnew, set_family_t **Tbar);
static bool simplify_special_cases(set **T, set_family_t **Tnew);

// complement -- compute the complement of T
set_family_t *
complement(set **T)
{
    set *cl, *cr;
    int best;
    set_family_t *Tbar, *Tl, *Tr;
    int lifting;
    static int compl_level = 0;

    if (debug & COMPL)
        debug_print(T, "COMPLEMENT", compl_level++);

    if (compl_special_cases(T, &Tbar) == MAYBE) {
        // Allocate space for the partition cubes
        cl = set_new(CUBE.size);
        cr = set_new(CUBE.size);
        best = binate_split_select(T, cl, cr, COMPL);

        // Complement the left and right halves
        Tl = complement(scofactor(T, cl, best));
        Tr = complement(scofactor(T, cr, best));

        if (Tr->count*Tl->count > (Tr->count+Tl->count)*CUBELISTSIZE(T)) {
            lifting = USE_COMPL_LIFT_ONSET;
        } else {
            lifting = USE_COMPL_LIFT;
        }
        Tbar = compl_merge(T, Tl, Tr, cl, cr, best, lifting);

        set_free(cl);
        set_free(cr);
        free_cubelist(T);
    }

    if (debug & COMPL)
        debug1_print(Tbar, "exit COMPLEMENT", --compl_level);

    return Tbar;
}

static bool
compl_special_cases(set **T, set_family_t **Tbar)
{
    set **T1, *p, *ceil, *cof=T[0];
    set_family_t *A, *ceil_compl;

    // Check for no cubes in the cover
    if (T[2] == NULL) {
        *Tbar = sf_addset(sf_new(1, CUBE.size), CUBE.fullset);
        free_cubelist(T);
        return TRUE;
    }

    // Check for only a single cube in the cover
    if (T[3] == NULL) {
        *Tbar = compl_cube(set_or(cof, cof, T[2]));
        free_cubelist(T);
        return TRUE;
    }

    // Check for a row of all 1's (implies complement is null)
    for (T1 = T+2; (p = *T1++) != NULL; ) {
        if (full_row(p, cof)) {
            *Tbar = sf_new(0, CUBE.size);
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
        ceil_compl = compl_cube(ceil);
        set_or(cof, cof, set_diff(ceil, CUBE.fullset, ceil));
        set_free(ceil);
        *Tbar = sf_append(complement(T), ceil_compl);
        return TRUE;
    }
    set_free(ceil);

    // Collect column counts, determine unate variables, etc.
    massive_count(T);

    // If single active variable not factored out above, then tautology!
    if (CDATA.vars_active == 1) {
        *Tbar = sf_new(0, CUBE.size);
        free_cubelist(T);
        return TRUE;

    // Check for unate cover
    } else if (CDATA.vars_unate == CDATA.vars_active) {
        A = map_cover_to_unate(T);
        free_cubelist(T);
        A = unate_compl(A);
        *Tbar = map_unate_to_cover(A);
        sf_free(A);
        return TRUE;

    // Not much we can do about it
    } else {
        return MAYBE;
    }
}

//
// compl_merge -- merge the two cofactors around the splitting
// variable
//
// The merge operation involves intersecting each cube of the left
// cofactor with cl, and intersecting each cube of the right cofactor
// with cr.  The union of these two covers is the merged result.
//
// In order to reduce the number of cubes, a distance-1 merge is
// performed (note that two cubes can only combine distance-1 in the
// splitting variable).  Also, a simple expand is performed in the
// splitting variable (simple implies the covering check for the
// expansion is not full containment, but single-cube containment).
//

static set_family_t *compl_merge(set **T1, set_family_t *L, set_family_t *R, set *cl, set *cr, int var, int lifting)
/* Original ON-set */
/* Complement from each recursion branch */
/* cubes used for cofactoring */
/* splitting variable */
/* whether to perform lifting or not */
{
    set *p, *last, *pt;
    set_family_t *T, *Tbar;
    set **L1, **R1;

    if (debug & COMPL) {
        printf("compl_merge: left %d, right %d\n", L->count, R->count);
        printf("%s (cl)\n%s (cr)\nLeft is\n", pc1(cl), pc2(cr));
        cprint(L);
        printf("Right is\n");
        cprint(R);
    }

    // Intersect each cube with the cofactored cube
    foreach_set(L, last, p) {
        set_and(p, p, cl);
        SET(p, ACTIVE);
    }
    foreach_set(R, last, p) {
        set_and(p, p, cr);
        SET(p, ACTIVE);
    }

    /* Sort the arrays for a distance-1 merge */
    set_copy(CUBE.temp[0], CUBE.var_mask[var]);
    qsort((char *) (L1 = sf_list(L)), L->count, sizeof(set *), d1_order);
    qsort((char *) (R1 = sf_list(R)), R->count, sizeof(set *), d1_order);

    /* Perform distance-1 merge */
    compl_d1merge(L1, R1);

    /* Perform lifting */
    switch(lifting) {
    case USE_COMPL_LIFT_ONSET:
        T = cubeunlist(T1);
        compl_lift_onset(L1, T, cr, var);
        compl_lift_onset(R1, T, cl, var);
        sf_free(T);
        break;
    case USE_COMPL_LIFT_ONSET_COMPLEX:
        T = cubeunlist(T1);
        compl_lift_onset_complex(L1, T, var);
        compl_lift_onset_complex(R1, T, var);
        sf_free(T);
        break;
    case USE_COMPL_LIFT:
        compl_lift(L1, R1, cr, var);
        compl_lift(R1, L1, cl, var);
        break;
    case NO_LIFTING:
        break;
    }
    FREE(L1);
    FREE(R1);

    // Re-create the merged cover
    Tbar = sf_new(L->count + R->count, CUBE.size);
    pt = Tbar->data;
    foreach_set(L, last, p) {
        set_copy(pt, p);
        Tbar->count++;
        pt += Tbar->wsize;
    }
    foreach_active_set(R, last, p) {
        set_copy(pt, p);
        Tbar->count++;
        pt += Tbar->wsize;
    }

    if (debug & COMPL) {
        printf("Result %d\n", Tbar->count);
        if (verbose_debug)
            cprint(Tbar);
    }

    sf_free(L);
    sf_free(R);
    return Tbar;
}

//
// compl_lift_simple -- expand in the splitting variable using single
// cube containment against the other recursion branch to check
// validity of the expansion, and expanding all (or none) of the
// splitting variable.
//

static void
compl_lift(set **A1, set **B1, set *bcube, int var)
{
    set *a, *b, **B2, *lift=CUBE.temp[4], *liftor=CUBE.temp[5];
    set *mask = CUBE.var_mask[var];

    set_and(liftor, bcube, mask);

    // for each cube in the first array ...
    for (; (a = *A1++) != NULL; ) {
        if (TESTP(a, ACTIVE)) {

            /* create a lift of this cube in the merging coord */
            set_merge(lift, bcube, a, mask);

            /* for each cube in the second array */
            for (B2 = B1; (b = *B2++) != NULL; ) {
                if (! setp_implies(lift, b))
                    continue;
                /* when_true => fall through to next statement */

                /* cube of A1 was contained by some cube of B1, so raise */
                set_or(a, a, liftor);
                break;
            }
        }
    }
}

//
// compl_lift_onset -- expand in the splitting variable using a
// distance-1 check against the original on-set; expand all (or
// none) of the splitting variable.  Each cube of A1 is expanded
// against the original on-set T.
//

static void
compl_lift_onset(set **A1, set_family_t *T, set *bcube, int var)
{
    set *a, *last, *p, *lift=CUBE.temp[4], *mask=CUBE.var_mask[var];

    // for each active cube from one branch of the complement
    for(; (a = *A1++) != NULL; ) {
        if (TESTP(a, ACTIVE)) {

            // create a lift of this cube in the merging coord
            set_and(lift, bcube, mask); // isolate parts to raise
            set_or(lift, a, lift);      // raise these parts in a

            // for each cube in the ON-set, check for intersection
            foreach_set(T, last, p) {
                if (cdist0(p, lift)) {
                    goto nolift;
                }
            }
            set_copy(a, lift); // save the raising
            SET(a, ACTIVE);
nolift:
    ;
        }
    }
}

//
// compl_lift_complex -- expand in the splitting variable, but expand all
// parts which can possibly expand.
// T is the original ON-set
// A1 is either the left or right cofactor
//

static void
compl_lift_onset_complex(set **A1, set_family_t *T, int var)
{
    int dist;
    set *last, *p, *a, *xlower;

    // for each cube in the complement
    xlower = set_new(CUBE.size);
    for(; (a = *A1++) != NULL; ) {

        if (TESTP(a, ACTIVE)) {

            /* Find which parts of the splitting variable are forced low */
            set_clear(xlower, CUBE.size);
            foreach_set(T, last, p) {
                if ((dist = cdist01(p, a)) < 2) {
                    if (dist == 0) {
                        fatal("compl: ON-set and OFF-set are not orthogonal");
                    } else {
                        force_lower(xlower, p, a);
                    }
                }
            }

            set_diff(xlower, CUBE.var_mask[var], xlower);
            set_or(a, a, xlower);
            set_free(xlower);
        }
    }
}

//
// compl_d1merge -- distance-1 merge in the splitting variable
//

static void
compl_d1merge(set **L1, set **R1)
{
    set *pl, *pr;

    // Find equal cubes between the two cofactors
    for (pl = *L1, pr = *R1; (pl != NULL) && (pr != NULL); )
        switch (d1_order(L1, R1)) {
        case 1:
            pr = *(++R1); break; // advance right pointer
        case -1:
            pl = *(++L1); break; // advance left pointer
        case 0:
            RESET(pr, ACTIVE);
            set_or(pl, pl, pr);
            pr = *(++R1);
        }
}

// compl_cube -- return the complement of a single cube (De Morgan's law)
//
//

static set_family_t *
compl_cube(set *p)
{
    set *diff=CUBE.temp[7], *pdest, *mask, *full=CUBE.fullset;
    int var;
    set_family_t *R;

    // Allocate worst-case size cover (to avoid checking overflow)
    R = sf_new(CUBE.num_vars, CUBE.size);

    // Compute bit-wise complement of the cube
    set_diff(diff, full, p);

    for(var = 0; var < CUBE.num_vars; var++) {
        mask = CUBE.var_mask[var];
        // If the bit-wise complement is not empty in var ...
        if (! setp_disjoint(diff, mask)) {
            pdest = GETSET(R, R->count++);
            set_merge(pdest, diff, full, mask);
        }
    }
    return R;
}

// simp_comp -- quick simplification of T
void
simp_comp(set **T, set_family_t **Tnew, set_family_t **Tbar)
{
    set *cl, *cr;
    int best;
    set_family_t *Tl, *Tr, *Tlbar, *Trbar;
    int lifting;
    static int simplify_level = 0;

    if (debug & COMPL)
        debug_print(T, "SIMPCOMP", simplify_level++);

    if (simp_comp_special_cases(T, Tnew, Tbar) == MAYBE) {

        // Allocate space for the partition cubes
        cl = set_new(CUBE.size);
        cr = set_new(CUBE.size);
        best = binate_split_select(T, cl, cr, COMPL);

        // Complement the left and right halves
        simp_comp(scofactor(T, cl, best), &Tl, &Tlbar);
        simp_comp(scofactor(T, cr, best), &Tr, &Trbar);

        lifting = USE_COMPL_LIFT;
        *Tnew = compl_merge(T, Tl, Tr, cl, cr, best, lifting);

        lifting = USE_COMPL_LIFT;
        *Tbar = compl_merge(T, Tlbar, Trbar, cl, cr, best, lifting);

        // All of this work for nothing ? Let's hope not ...
        if ((*Tnew)->count > CUBELISTSIZE(T)) {
            sf_free(*Tnew);
            *Tnew = cubeunlist(T);
        }

        set_free(cl);
        set_free(cr);
        free_cubelist(T);
    }

    if (debug & COMPL) {
        debug1_print(*Tnew, "exit SIMPCOMP (new)", simplify_level);
        debug1_print(*Tbar, "exit SIMPCOMP (compl)", simplify_level);
        simplify_level--;
    }
}

static bool
simp_comp_special_cases(set **T, set_family_t **Tnew, set_family_t **Tbar)
{
    set **T1, *p, *ceil, *cof=T[0];
    set *last;
    set_family_t *A;

    // Check for no cubes in the cover (function is empty)
    if (T[2] == NULL) {
        *Tnew = sf_new(1, CUBE.size);
        *Tbar = sf_addset(sf_new(1, CUBE.size), CUBE.fullset);
        free_cubelist(T);
        return TRUE;
    }

    // Check for only a single cube in the cover
    if (T[3] == NULL) {
        set_or(cof, cof, T[2]);
        *Tnew = sf_addset(sf_new(1, CUBE.size), cof);
        *Tbar = compl_cube(cof);
        free_cubelist(T);
        return TRUE;
    }

    // Check for a row of all 1's (function is a tautology)
    for (T1 = T+2; (p = *T1++) != NULL; ) {
        if (full_row(p, cof)) {
            *Tnew = sf_addset(sf_new(1, CUBE.size), CUBE.fullset);
            *Tbar = sf_new(1, CUBE.size);
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
        simp_comp(T, Tnew, Tbar);

        // Adjust the ON-set
        A = *Tnew;
        foreach_set(A, last, p) {
            set_and(p, p, ceil);
        }

        // Compute the new complement
        *Tbar = sf_append(*Tbar, compl_cube(ceil));
        set_free(ceil);
        return TRUE;
    }
    set_free(ceil);

    // Collect column counts, determine unate variables, etc.
    massive_count(T);

    // If single active variable not factored out above, then tautology!
    if (CDATA.vars_active == 1) {
        *Tnew = sf_addset(sf_new(1, CUBE.size), CUBE.fullset);
        *Tbar = sf_new(1, CUBE.size);
        free_cubelist(T);
        return TRUE;

    // Check for unate cover
    } else if (CDATA.vars_unate == CDATA.vars_active) {
        // Make the cover minimum by single-cube containment
        A = cubeunlist(T);
        *Tnew = sf_contain(A);

        // Now form a minimum representation of the complement
        A = map_cover_to_unate(T);
        A = unate_compl(A);
        *Tbar = map_unate_to_cover(A);
        sf_free(A);
        free_cubelist(T);
        return TRUE;

    // Not much we can do about it
    } else {
        return MAYBE;
    }
}

// simplify -- quick simplification of T
set_family_t *
simplify(set **T)
{
    set *cl, *cr;
    int best;
    set_family_t *Tbar, *Tl, *Tr;
    int lifting;
    static int simplify_level = 0;

    if (debug & COMPL) {
        debug_print(T, "SIMPLIFY", simplify_level++);
    }

    if (simplify_special_cases(T, &Tbar) == MAYBE) {

        // Allocate space for the partition cubes
        cl = set_new(CUBE.size);
        cr = set_new(CUBE.size);

        best = binate_split_select(T, cl, cr, COMPL);

        // Complement the left and right halves
        Tl = simplify(scofactor(T, cl, best));
        Tr = simplify(scofactor(T, cr, best));

        lifting = USE_COMPL_LIFT;
        Tbar = compl_merge(T, Tl, Tr, cl, cr, best, lifting);

        // All of this work for nothing ? Let's hope not ...
        if (Tbar->count > CUBELISTSIZE(T)) {
            sf_free(Tbar);
            Tbar = cubeunlist(T);
        }

        set_free(cl);
        set_free(cr);
        free_cubelist(T);
    }

    if (debug & COMPL) {
        debug1_print(Tbar, "exit SIMPLIFY", --simplify_level);
    }

    return Tbar;
}

static bool
simplify_special_cases(set **T, set_family_t **Tnew)
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

        A = simplify(T);
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

    // Check for unate cover
    } else if (CDATA.vars_unate == CDATA.vars_active) {
        A = cubeunlist(T);
        *Tnew = sf_contain(A);
        free_cubelist(T);
        return TRUE;

    // Not much we can do about it
    } else {
        return MAYBE;
    }
}

