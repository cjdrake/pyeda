/* Module: sigma.c
 * Purpose:
 *     Contains routines for computing the signature cube of the given cube.
 * Routines:
 * set *get_sigma():
 *     Computes signature cube of the given cube d.
 * void set_not():
 */

#include <stdio.h>
#include "espresso.h"
#include "signature.h"

//
// get_sigma:
// Objective: computes signature cube corresponding to the cube c
// Input:
//     R: OFFSET cover;
//     c: ONSET cube;
// Output:
//     signature cube
//

set *
get_sigma(set_family_t *R, set *c)
{
    set_family_t *BB;
    set *out_part_r, *s;
    set *r, *b;
    int i;
    int w, last;
    unsigned int x;

    out_part_r = set_new(cube.size);
    s = set_new(cube.size);

    BB = sf_new(R->count, cube.size);
    BB->count = R->count;
    /* BB = get_blocking_matrix(R,c); */
    foreachi_set(R, i, r) {
        b = GETSET(BB, i);
        if ((last = cube.inword) != -1) {
            /* Check the partial word of binary variables */
            x = r[last] & c[last];
            x = ~(x | x >> 1) & cube.inmask;
            b[last] = r[last] & (x | x << 1);
            /* Check the full words of binary variables */
            for(w = 1; w < last; w++) {
                x = r[w] & c[w];
                x = ~(x | x >> 1) & DISJOINT;
                b[w] = r[w] & (x | x << 1);
            }
        }
        PUTLOOP(b,LOOP(r));
        set_and(b,b,cube.binary_mask);
        set_and(out_part_r,cube.mv_mask,r);
        if (!setp_implies(out_part_r,c)) {
            set_or(b,b,out_part_r);
        }
    }
    set_free(out_part_r);
    BB = unate_compl(BB);

    set_copy(s,cube.emptyset);
    foreachi_set(BB, i, b) {
        set_or(s,s,b);
    }
    sf_free(BB);
    set_not(s);
    return s;
}

// set_not: flip 0 to 1 and 1 to 0

void
set_not(set *c)
{
    set_diff(c,cube.fullset,c);
}

