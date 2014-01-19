//
// module: gasp.c
//
// The "last_gasp" heuristic computes the reduction of each cube in
// the cover (without replacement) and then performs an expansion of
// these cubes.  The cubes which expand to cover some other cube are
// added to the original cover and irredundant finds a minimal subset.
//
// If one of the reduced cubes expands to cover some other reduced
// cube, then the new prime thus generated is a candidate for reducing
// the size of the cover.
//
// super_gasp is a variation on this strategy which extracts a minimal
// subset from the set of all prime implicants which cover all
// maximally reduced cubes.
//

#include "espresso.h"

//
// reduce_gasp -- compute the maximal reduction of each cube of F
//
// If a cube does not reduce, it remains prime; otherwise, it is marked
// as nonprime.   If the cube is redundant (should NEVER happen here) we
// just crap out ...
//
// A cover with all of the cubes of F is returned.  Those that did
// reduce are marked "NONPRIME"; those that reduced are marked "PRIME".
// The cubes are in the same order as in F.
//

static set_family_t *
reduce_gasp(set_family_t *F, set_family_t *D)
{
    set *p, *last, *cunder, **FD;
    set_family_t *G;

    G = sf_new(F->count, CUBE.size);
    FD = cube2list(F, D);

    // Reduce cubes of F without replacement
    foreach_set(F, last, p) {
        cunder = reduce_cube(FD, p);
        if (setp_empty(cunder)) {
            fatal("empty reduction in reduce_gasp, shouldn't happen");
        }
        else if (setp_equal(cunder, p)) {
            SET(cunder, PRIME);			/* just to make sure */
            G = sf_addset(G, p);		/* it did not reduce ... */
        }
        else {
            RESET(cunder, PRIME);		/* it reduced ... */
            G = sf_addset(G, cunder);
        }
        if (debug & GASP) {
            printf("REDUCE_GASP: %s reduced to %s\n", pc1(p), pc2(cunder));
        }
        set_free(cunder);
    }

    free_cubelist(FD);
    return G;
}

//
// expand_gasp -- expand each nonprime cube of F into a prime implicant
//
// The gasp strategy differs in that only those cubes which expand to
// cover some other cube are saved; also, all cubes are expanded
// regardless of whether they become covered or not.
//

set_family_t *
expand_gasp(set_family_t *F, set_family_t *D, set_family_t *R, set_family_t *Foriginal)
{
    int c1index;
    set_family_t *G;

    // Try to expand each nonprime and noncovered cube
    G = sf_new(10, CUBE.size);
    for (c1index = 0; c1index < F->count; c1index++) {
        expand1_gasp(F, D, R, Foriginal, c1index, &G);
    }
    G = sf_dupl(G);
    G = expand(G, R, /*nonsparse*/ FALSE); /* Make them prime ! */

    return G;
}

//
// expand1 -- Expand a single cube against the OFF-set, using the gasp strategy
//

void
expand1_gasp(set_family_t *F, set_family_t *D, set_family_t *R, set_family_t *Foriginal, int c1index, set_family_t **G)
/* reduced cubes of ON-set */
/* DC-set */
/* OFF-set */
/* ON-set before reduction (same order as F) */
/* which index of F (or Freduced) to be checked */
{
    int c2index;
    set *p, *last, *c2under;
    set *RAISE, *FREESET, *temp, **FD, *c2essential;
    set_family_t *F1;

    if (debug & EXPAND1) {
        printf("\nEXPAND1_GASP:    \t%s\n", pc1(GETSET(F, c1index)));
    }

    RAISE = set_new(CUBE.size);
    FREESET = set_new(CUBE.size);
    temp = set_new(CUBE.size);

    // Initialize the OFF-set
    R->active_count = R->count;
    foreach_set(R, last, p) {
        SET(p, ACTIVE);
    }
    // Initialize the reduced ON-set, all nonprime cubes become active
    F->active_count = F->count;
    foreachi_set(F, c2index, c2under) {
        if (c1index == c2index || TESTP(c2under, PRIME)) {
            F->active_count--;
            RESET(c2under, ACTIVE);
        }
        else {
            SET(c2under, ACTIVE);
        }
    }

    // Initialize the raising and unassigned sets
    set_copy(RAISE, GETSET(F, c1index));
    set_diff(FREESET, CUBE.fullset, RAISE);

    // Determine parts which must be lowered
    essen_parts(R, F, RAISE, FREESET);

    // Determine parts which can always be raised
    essen_raising(R, RAISE, FREESET);

    // See which, if any, of the reduced cubes we can cover
    foreachi_set(F, c2index, c2under) {
        if (TESTP(c2under, ACTIVE)) {
            // See if this cube can be covered by an expansion
            if (setp_implies(c2under, RAISE) ||
                feasibly_covered(R, c2under, RAISE, temp)) {

                // See if c1under can expanded to cover c2 reduced against
                // (F - c1) u c1under; if so, c2 can definitely be removed !

                // Copy F and replace c1 with c1under
                F1 = sf_save(Foriginal);
                set_copy(GETSET(F1, c1index), GETSET(F, c1index));

                // Reduce c2 against ((F - c1) u c1under)
                FD = cube2list(F1, D);
                c2essential = reduce_cube(FD, GETSET(F1, c2index));
                free_cubelist(FD);
                sf_free(F1);

                // See if c2essential is covered by an expansion of c1under
                if (feasibly_covered(R, c2essential, RAISE, temp)) {
                    set_or(temp, RAISE, c2essential);
                    RESET(temp, PRIME);		/* cube not prime */
                    *G = sf_addset(*G, temp);
                }
                set_free(c2essential);
            }
        }
    }

    set_free(RAISE);
    set_free(FREESET);
    set_free(temp);
}

// irred_gasp -- Add new primes to F and find an irredundant subset

set_family_t *
irred_gasp(set_family_t *F, set_family_t *D, set_family_t *G)
{
    if (G->count != 0)
        F = irredundant(sf_append(F, G), D);
    else
        sf_free(G);

    return F;
}

// last_gasp

set_family_t *
last_gasp(set_family_t *F, set_family_t *D, set_family_t *R, cost_t *cost)
{
    set_family_t *G, *G1;

    G = reduce_gasp(F, D);
    cover_cost(G, cost);
    G1 = expand_gasp(G, D, R, F);
    cover_cost(G1, cost);
    sf_free(G);
    F = irred_gasp(F, D, G1);
    cover_cost(F, cost);

    return F;
}

// super_gasp
set_family_t *
super_gasp(set_family_t *F, set_family_t *D, set_family_t *R, cost_t *cost)
{
    set_family_t *G, *G1;

    G = reduce_gasp(F, D);
    cover_cost(G, cost);
    G1 = all_primes(G, R);
    cover_cost(G1, cost);
    sf_free(G);
    G = sf_dupl(sf_append(F, G1));
    F = irredundant(G, D);
    cover_cost(F, cost);

    return F;
}

