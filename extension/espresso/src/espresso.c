/*
** Module: espresso.c
** Purpose: The main espresso algorithm
**
** Returns a minimized version of the ON-set of a function
**
** The following global variables affect the operation of Espresso:
**
** MISCELLANEOUS:
**     remove_essential
**         remove essential primes
**
**     single_expand
**         if true, stop after first expand/irredundant
**
** LAST_GASP or SUPER_GASP strategy:
**     use_super_gasp
**         uses the super_gasp strategy rather than last_gasp
**
** SETUP strategy:
**     recompute_onset
**         recompute onset using the complement before starting
**
**     unwrap_onset
**         unwrap the function output part before first expand
**
** MAKE_SPARSE strategy:
**     force_irredundant
**         iterates make_sparse to force a minimal solution (used
**         indirectly by make_sparse)
**
**     skip_make_sparse
**         skip the make_sparse step (used by opo only)
*/

#include "espresso.h"

set_family_t *
espresso(set_family_t *F, set_family_t *D, set_family_t *R)
{
    set_family_t *E, *Fsave, *Dsave;
    set *last, *p;
    cost_t cost, best_cost;

begin:
    Fsave = sf_save(F);
    Dsave = sf_save(D);

    /* Setup has always been a problem */
    if (recompute_onset) {
        E = simplify(cube1list(F));
        sf_free(F);
        F = E;
    }
    cover_cost(F, &cost);
    if (unwrap_onset && (CUBE.part_size[CUBE.num_vars - 1] > 1)
            && (cost.out != cost.cubes*CUBE.part_size[CUBE.num_vars-1])
            && (cost.out < 5000))
        F = sf_contain(unravel(F, CUBE.num_vars - 1));

    /* Initial expand and irredundant */
    foreach_set(F, last, p) {
        RESET(p, PRIME);
    }

    F = expand(F, R, FALSE);
    cover_cost(F, &cost);

    F = irredundant(F, Dsave);
    cover_cost(F, &cost);

    if (! single_expand) {
        if (remove_essential) {
            E = essential(&F, &Dsave);
            cover_cost(E, &cost);
        } else {
            E = sf_new(0, CUBE.size);
        }

        cover_cost(F, &cost);
        do {

            /* Repeat inner loop until solution becomes "stable" */
            do {
                copy_cost(&cost, &best_cost);
                F = reduce(F, Dsave);
                cover_cost(F, &cost);
                F = expand(F, R, FALSE);
                cover_cost(F, &cost);
                F = irredundant(F, Dsave);
                cover_cost(F, &cost);
            } while (cost.cubes < best_cost.cubes);

            /* Perturb solution to see if we can continue to iterate */
            copy_cost(&cost, &best_cost);
            if (use_super_gasp) {
                F = super_gasp(F, Dsave, R, &cost);
                if (cost.cubes >= best_cost.cubes)
                    break;
            } else {
                F = last_gasp(F, Dsave, R, &cost);
            }

        } while (cost.cubes < best_cost.cubes ||
                 (cost.cubes == best_cost.cubes && cost.total < best_cost.total));

        /* Append the essential cubes to F */
        F = sf_append(F, E);    /* disposes of E */
    }

    /* Free the Dsave which we used */
    sf_free(Dsave);

    /* Attempt to make the PLA matrix sparse */
    if (! skip_make_sparse) {
        F = make_sparse(F, D, R);
    }

    /*
    ** Check to make sure function is actually smaller.
    ** This can only happen because of the initial unravel.
    ** If we fail, then run the whole thing again without the unravel.
    */
    if (Fsave->count < F->count) {
        sf_free(F);
        F = Fsave;
        unwrap_onset = FALSE;
        goto begin;
    } else {
        sf_free(Fsave);
    }

    return F;
}

