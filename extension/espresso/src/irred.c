// Filename: irred.c

#include <assert.h>

#include "espresso.h"

static void fcube_is_covered(set **T, set *c, sm_matrix *table);
static void ftautology(set **T, sm_matrix *table);
static bool ftaut_special_cases(set **T, sm_matrix *table);

static int Rp_current;

//
// irredundant -- Return a minimal subset of F
//

set_family_t *
irredundant(set_family_t *F, set_family_t *D)
{
    mark_irredundant(F, D);
    return sf_inactive(F);
}

//
// mark_irredundant -- find redundant cubes, and mark them "INACTIVE"
//

void
mark_irredundant(set_family_t *F, set_family_t *D)
{
    set_family_t *E, *Rt, *Rp;
    set *p, *p1, *last;
    sm_matrix *table;
    sm_row *cover;
    sm_element *pe;

    // extract a minimum cover
    irred_split_cover(F, D, &E, &Rt, &Rp);
    table = irred_derive_table(D, E, Rp);
    cover = sm_minimum_cover(table, NIL(int), /* heuristic */ 1, /* debug */ 0);

    // mark the cubes for the result
    foreach_set(F, last, p) {
        RESET(p, ACTIVE);
        RESET(p, RELESSEN);
    }
    foreach_set(E, last, p) {
        p1 = GETSET(F, SIZE(p));
        assert(setp_equal(p1, p));
        SET(p1, ACTIVE);
        SET(p1, RELESSEN);		/* for essen(), mark as rel. ess. */
    }
    sm_foreach_row_element(cover, pe) {
        p1 = GETSET(F, pe->col_num);
        SET(p1, ACTIVE);
    }

    if (debug & IRRED) {
        printf("# IRRED: F=%d E=%d R=%d Rt=%d Rp=%d Rc=%d Final=%d Bound=%d\n",
        F->count, E->count, Rt->count+Rp->count, Rt->count, Rp->count,
        cover->length, E->count + cover->length, 0);
    }

    sf_free(E);
    sf_free(Rt);
    sf_free(Rp);
    sm_free(table);
    sm_row_free(cover);
}

//
// irred_split_cover -- find E, Rt, and Rp from the cover F, D
//
// E  -- relatively essential cubes
// Rt -- totally redundant cubes
// Rp -- partially redundant cubes
//

void
irred_split_cover(set_family_t *F, set_family_t *D, set_family_t **E, set_family_t **Rt, set_family_t **Rp)
{
    set *p, *last;
    int index;
    set_family_t *R;
    set **FD, **ED;

    // number the cubes of F -- these numbers track into E, Rp, Rt, etc.
    index = 0;
    foreach_set(F, last, p) {
        PUTSIZE(p, index);
        index++;
    }

    *E = sf_new(10, CUBE.size);
    *Rt = sf_new(10, CUBE.size);
    *Rp = sf_new(10, CUBE.size);
    R = sf_new(10, CUBE.size);

    // Split F into E and R
    FD = cube2list(F, D);
    foreach_set(F, last, p) {
        if (cube_is_covered(FD, p)) {
            R = sf_addset(R, p);
        } else {
            *E = sf_addset(*E, p);
        }
        if (debug & IRRED1) {
            printf("IRRED1: zr=%d ze=%d to-go=%d\n", R->count, (*E)->count, F->count - (R->count + (*E)->count));
        }
    }
    free_cubelist(FD);

    // Split R into Rt and Rp
    ED = cube2list(*E, D);
    foreach_set(R, last, p) {
        if (cube_is_covered(ED, p)) {
            *Rt = sf_addset(*Rt, p);
        } else {
            *Rp = sf_addset(*Rp, p);
        }
        if (debug & IRRED1) {
            printf("IRRED1: zr=%d zrt=%d to-go=%d\n", (*Rp)->count, (*Rt)->count, R->count - ((*Rp)->count +(*Rt)->count));
        }
    }
    free_cubelist(ED);

    sf_free(R);
}

/*
 *  irred_derive_table -- given the covers D, E and the set of
 *  partially redundant primes Rp, build a covering table showing
 *  possible selections of primes to cover Rp.
 */

sm_matrix *
irred_derive_table(set_family_t *D, set_family_t *E, set_family_t *Rp)
{
    set *last, *p, **list;
    sm_matrix *table;
    int size_last_dominance, i;

    // Mark each cube in DE as not part of the redundant set
    foreach_set(D, last, p) {
        RESET(p, REDUND);
    }
    foreach_set(E, last, p) {
        RESET(p, REDUND);
    }

    // Mark each cube in Rp as partially redundant
    foreach_set(Rp, last, p) {
        SET(p, REDUND);     // belongs to redundant set
    }

    // For each cube in Rp, find ways to cover its minterms
    list = cube3list(D, E, Rp);
    table = sm_alloc();
    size_last_dominance = 0;
    i = 0;
    foreach_set(Rp, last, p) {
        Rp_current = SIZE(p);
        fcube_is_covered(list, p, table);
        RESET(p, REDUND);   // can now consider this cube redundant
        if (debug & IRRED1) {
            printf("IRRED1: %d of %d to-go=%d, table=%dx%d\n", i, Rp->count, Rp->count - i, table->nrows, table->ncols);
        }
        // try to keep memory limits down by reducing table as we go along
        if (table->nrows - size_last_dominance > 1000) {
            sm_row_dominance(table);
            size_last_dominance = table->nrows;
            if (debug & IRRED1) {
                printf("IRRED1: delete redundant rows, now %dx%d\n",
                table->nrows, table->ncols);
            }
        }
        i++;
    }
    free_cubelist(list);

    return table;
}

// cube_is_covered -- determine if a cubelist "covers" a single cube

bool
cube_is_covered(set **T, set *c)
{
    return tautology(cofactor(T, c));
}

// tautology -- answer the tautology question for T

bool
tautology(set **T)
{
    set *cl, *cr;
    int best, result;
    static int taut_level = 0;

    if (debug & TAUT) {
        debug_print(T, "TAUTOLOGY", taut_level++);
    }

    if ((result = taut_special_cases(T)) == MAYBE) {
        cl = set_new(CUBE.size);
        cr = set_new(CUBE.size);
        best = binate_split_select(T, cl, cr, TAUT);
        result = tautology(scofactor(T, cl, best)) && tautology(scofactor(T, cr, best));
        free_cubelist(T);
        set_free(cl);
        set_free(cr);
    }

    if (debug & TAUT) {
        printf("exit TAUTOLOGY[%d]: %s\n", --taut_level, print_bool(result));
    }

    return result;
}

//
// taut_special_cases -- check special cases for tautology
//

bool
taut_special_cases(set **T)
{
    set **T1, **Tsave, *p, *ceil=CUBE.temp[0], *temp=CUBE.temp[1];
    set **A, **B;
    int var;

    // Check for a row of all 1's which implies tautology
    for (T1 = T+2; (p = *T1++) != NULL; ) {
        if (full_row(p, T[0])) {
            free_cubelist(T);
            return TRUE;
        }
    }

    // Check for a column of all 0's which implies no tautology
start:
    set_copy(ceil, T[0]);
    for (T1 = T+2; (p = *T1++) != NULL; ) {
        set_or(ceil, ceil, p);
    }
    if (! setp_equal(ceil, CUBE.fullset)) {
        free_cubelist(T);
        return FALSE;
    }

    // Collect column counts, determine unate variables, etc.
    massive_count(T);

    // If function is unate (and no row of all 1's), then no tautology
    if (CDATA.vars_unate == CDATA.vars_active) {
        free_cubelist(T);
        return FALSE;
    }
    // If active in a single variable (and no column of 0's) then tautology
    else if (CDATA.vars_active == 1) {
        free_cubelist(T);
        return TRUE;
    }
    // Check for unate variables, and reduce cover if there are any
    else if (CDATA.vars_unate != 0) {
        // Form a cube "ceil" with full variables in the unate variables
        set_copy(ceil, CUBE.emptyset);
        for (var = 0; var < CUBE.num_vars; var++) {
            if (CDATA.is_unate[var]) {
                set_or(ceil, ceil, CUBE.var_mask[var]);
            }
        }

        // Save only those cubes that are "full" in all unate variables
        for (Tsave = T1 = T+2; (p = *T1++) != 0; ) {
            if (setp_implies(ceil, set_or(temp, p, T[0]))) {
                *Tsave++ = p;
            }
        }
        *Tsave++ = NULL;
        T[1] = (set *) Tsave;

        if (debug & TAUT) {
            printf("UNATE_REDUCTION: %d unate variables, reduced to %ld\n",
            CDATA.vars_unate, CUBELISTSIZE(T));
        }
        goto start;

    }
    // Check for component reduction
    else if (CDATA.var_zeros[CDATA.best] < CUBELISTSIZE(T) / 2) {
        if (cubelist_partition(T, &A, &B, debug & TAUT) == 0) {
            return MAYBE;
        }
        else {
            free_cubelist(T);
            if (tautology(A)) {
                free_cubelist(B);
                return TRUE;
            } else {
                return tautology(B);
            }
        }
    }

    // We tried as hard as we could, but must recurse from here on
    return MAYBE;
}

// fcube_is_covered -- determine exactly how a cubelist "covers" a cube
static void
fcube_is_covered(set **T, set *c, sm_matrix *table)
{
    ftautology(cofactor(T,c), table);
}

// ftautology -- find ways to make a tautology
static void
ftautology(set **T, sm_matrix *table)
{
    set *cl, *cr;
    int best;
    static int ftaut_level = 0;

    if (debug & TAUT) {
        debug_print(T, "FIND_TAUTOLOGY", ftaut_level++);
    }

    if (ftaut_special_cases(T, table) == MAYBE) {
        cl = set_new(CUBE.size);
        cr = set_new(CUBE.size);
        best = binate_split_select(T, cl, cr, TAUT);

        ftautology(scofactor(T, cl, best), table);
        ftautology(scofactor(T, cr, best), table);

        free_cubelist(T);
        set_free(cl);
        set_free(cr);
    }

    if (debug & TAUT) {
        printf("exit FIND_TAUTOLOGY[%d]: table is %d by %d\n",
               --ftaut_level, table->nrows, table->ncols);
    }
}

static bool
ftaut_special_cases(set **T, sm_matrix *table)
{
    set **T1, **Tsave, *p, *temp = CUBE.temp[0], *ceil = CUBE.temp[1];
    int var, rownum;

    // Check for a row of all 1's in the essential cubes
    for (T1 = T+2; (p = *T1++) != 0; ) {
        if (! TESTP(p, REDUND)) {
            if (full_row(p, T[0])) {
                // subspace is covered by essentials -- no new rows for table
                free_cubelist(T);
                return TRUE;
            }
        }
    }

    // Collect column counts, determine unate variables, etc.
start:
    massive_count(T);

    // If function is unate, find the rows of all 1's
    if (CDATA.vars_unate == CDATA.vars_active) {
        // find which nonessentials cover this subspace
        rownum = table->last_row ? table->last_row->row_num+1 : 0;
        sm_insert(table, rownum, Rp_current);
        for (T1 = T+2; (p = *T1++) != 0; ) {
            if (TESTP(p, REDUND)) {
                // See if a redundant cube covers this leaf
                if (full_row(p, T[0])) {
                    sm_insert(table, rownum, (int) SIZE(p));
                }
            }
        }
        free_cubelist(T);
        return TRUE;

        // Perform unate reduction if there are any unate variables
    }
    else if (CDATA.vars_unate != 0) {
        // Form a cube "ceil" with full variables in the unate variables
        set_copy(ceil, CUBE.emptyset);
        for (var = 0; var < CUBE.num_vars; var++) {
            if (CDATA.is_unate[var]) {
                set_or(ceil, ceil, CUBE.var_mask[var]);
            }
        }

        // Save only those cubes that are "full" in all unate variables
        for (Tsave = T1 = T+2; (p = *T1++) != 0; ) {
            if (setp_implies(ceil, set_or(temp, p, T[0]))) {
                *Tsave++ = p;
            }
        }
        *Tsave++ = 0;
        T[1] = (set *) Tsave;

        if (debug & TAUT) {
            printf("UNATE_REDUCTION: %d unate variables, reduced to %ld\n",
            CDATA.vars_unate, CUBELISTSIZE(T));
        }
        goto start;
    }

    // Not much we can do about it
    return MAYBE;
}

