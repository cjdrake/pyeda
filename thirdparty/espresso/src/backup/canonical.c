// Filename: canonical.c
//
// Routines for finding the canonical cover of the incompletely specified
// logic function.
//
// Routine:
//     set_family_t *find_canonical_cover():
//     Finds canonical cover of the incompletely specified logic function
//     by iteratively calling ess_test_and_reduction for each cube in the
//     ON-set.
//

#include "espresso.h"
#include "signature.h"

//
// find_canonical_cover
//
// Objective: find canonical cover of the essential signature cube
// Input:
//     F: ONSET cover;
//     D: DC cover;
//     R: OFFSET cover;
// Output:
//     Return canonical cover of the essential signature cube
//

set_family_t *
find_canonical_cover(set_family_t *F1, set_family_t *D, set_family_t *R)
{
    set_family_t *F;
    set_family_t *E, *ESC;
    set_family_t *COVER;
    set *last, *p, *s;
    set *c;
    int count = 0;
    int last_fcount = F1->count;
    set *d, **extended_dc;
    set *sigma_c;

    F = sf_save(F1);
    E = sf_new(D->count, cube.size);
    E->count = D->count;
    sf_copy(E, D);

    ESC = sf_new(F->count, cube.size);

    while (F->count) {
        c = GETSET(F, --F->count);
        RESET(c,NONESSEN);
        extended_dc = cube2list(E, F);
        d = reduce_cube(extended_dc, c);
        free_cubelist(extended_dc);
        if (setp_empty(d)) {
            set_free(d);
            continue;
        }
        c = get_sigma(R, d);
        COVER = etr_order(F, E, R, c, d);
        set_free(d);
        if (TESTP(c, NONESSEN)) {
            sf_append(F, COVER);
        } else {
            sf_free(COVER);
            sf_addset(E, c);
            sf_addset(ESC, c);
        }
        set_free(c);
    }
    sf_free(F);
    sf_free(E);

    return ESC;
}

