//
// module: sparse.c
//
// make_sparse is a last-step cleanup to reduce the total number
// of literals in the cover.
//
// This is done by reducing the "sparse" variables (using a modified
// version of irredundant rather than reduce), followed by expanding
// the "dense" variables (using modified version of expand).
//

#include "espresso.h"

set_family_t *
make_sparse(set_family_t *F, set_family_t *D, set_family_t *R)
{
    cost_t cost, best_cost;

    cover_cost(F, &best_cost);

    do {
        F = mv_reduce(F, D);
        cover_cost(F, &cost);
        if (cost.total == best_cost.total)
            break;
        copy_cost(&cost, &best_cost);

        F = expand(F, R, TRUE);
        cover_cost(F, &cost);
        if (cost.total == best_cost.total)
            break;
        copy_cost(&cost, &best_cost);
    } while (force_irredundant);

    return F;
}

//
// mv_reduce -- perform an "optimal" reduction of the variables which
// we desire to be sparse
//
// This could be done using "reduce" and then saving just the desired
// part of the reduction.  Instead, this version uses IRRED to find
// which cubes of an output are redundant.  Note that this gets around
// the cube-ordering problem.
//
// In normal use, it is expected that the cover is irredundant and
// hence no cubes will be reduced to the empty cube (however, this is
// checked for and such cubes will be deleted)
//

set_family_t *
mv_reduce(set_family_t *F, set_family_t *D)
{
    int i, var;
    set *p, *p1, *last;
    int index;
    set_family_t *F1, *D1;
    set **F_cube_table;

    // loop for each multiple-valued variable
    for (var = 0; var < CUBE.num_vars; var++) {

        if (CUBE.sparse[var]) {

            // loop for each part of the variable
            for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {

                // remember mapping of F1 cubes back to F cubes
                F_cube_table = ALLOC(set *, F->count);

                // 'cofactor' against part #i of variable #var
                F1 = sf_new(F->count, CUBE.size);
                foreach_set(F, last, p) {
                    if (is_in_set(p, i)) {
                        F_cube_table[F1->count] = p;
                        p1 = GETSET(F1, F1->count++);
                        set_diff(p1, p, CUBE.var_mask[var]);
                        set_insert(p1, i);
                    }
                }

                // 'cofactor' against part #i of variable #var
                // not really necessary -- just more efficient ?
                D1 = sf_new(D->count, CUBE.size);
                foreach_set(D, last, p) {
                    if (is_in_set(p, i)) {
                        p1 = GETSET(D1, D1->count++);
                        set_diff(p1, p, CUBE.var_mask[var]);
                        set_insert(p1, i);
                    }
                }

                mark_irredundant(F1, D1);

                // now remove part i from cubes which are redundant
                index = 0;
                foreach_set(F1, last, p1) {
                    if (! TESTP(p1, ACTIVE)) {
                        p = F_cube_table[index];

                        // don't reduce a variable which is full
                        // (unless it is the output variable)
                        if (var == CUBE.num_vars-1 || ! setp_implies(CUBE.var_mask[var], p)) {
                            set_remove(p, i);
                        }
                        RESET(p, PRIME);
                    }
                    index++;
                }

                sf_free(F1);
                sf_free(D1);
                FREE(F_cube_table);
            }
        }
    }

    // Check if any cubes disappeared
    sf_active(F);
    for (var = 0; var < CUBE.num_vars; var++) {
        if (CUBE.sparse[var]) {
            foreach_active_set(F, last, p) {
                if (setp_disjoint(p, CUBE.var_mask[var])) {
                    RESET(p, ACTIVE);
                    F->active_count--;
                }
            }
        }
    }

    if (F->count != F->active_count) {
        F = sf_inactive(F);
    }

    return F;
}

