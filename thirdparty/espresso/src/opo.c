// Filename: opo.c

#include "espresso.h"

//
// Phase assignment technique (T. Sasao):
//
//     1. create a function with 2*m outputs which implements the
//        original function and its complement for each output
//
//     2. minimize this function
//
//     3. choose the minimum number of prime implicants from the
//        result of step 2 which are needed to realize either a function
//        or its complement for each output
//
// Step 3 is performed in a rather crude way -- by simply multiplying
// out a large expression of the form:
//
//     I = (ab + cdef)(acd + bgh) ...
//
// which is a product of m expressions where each expression has two
// product terms -- one representing which primes are needed for the
// function, and one representing which primes are needed for the
// complement.  The largest product term resulting shows which primes
// to keep to implement one function or the other for each output.
// For problems with many outputs, this may grind to a halt.
//
// Untried: form complement of I and use unate_complement ...
//
// I have unsuccessfully tried several modifications to the basic
// algorithm.  The first is quite simple: use Sasao's technique, but
// only commit to a single output at a time (rather than all
// outputs).  The goal would be that the later minimizations can "take
// into account" the partial assignment at each step.  This is
// expensive (m+1 minimizations rather than 2), and the results are
// discouraging.
//
// The second modification is rather complicated.  The result from the
// minimization in step 2 is guaranteed to be minimal.  Hence, for
// each output, the set of primes with a 1 in that output are both
// necessary and sufficient to implement the function.  Espresso
// achieves the minimality using the routine MAKE_SPARSE.  The
// modification is to prevent MAKE_SPARSE from running.  Hence, there
// are potentially many subsets of the set of primes with a 1 in a
// column which can be used to implement that output.  We use
// IRREDUNDANT to enumerate all possible subsets and then proceed as
// before.
//

static int opo_no_make_sparse;
static int opo_repeated;
static int opo_exact;
static void minimize(PLA_t *PLA);

void phase_assignment(PLA_t *PLA, int opo_strategy)
{
    opo_no_make_sparse = opo_strategy % 2;
    skip_make_sparse = opo_no_make_sparse;
    opo_repeated = (opo_strategy / 2) % 2;
    opo_exact = (opo_strategy / 4) % 2;

    // Determine a phase assignment
    if (PLA->phase != NULL) {
        FREE(PLA->phase);
    }

    if (opo_repeated) {
        PLA->phase = set_save(CUBE.fullset);
        repeated_phase_assignment(PLA);
    }
    else {
        PLA->phase = find_phase(PLA, 0, (set *) NULL);
    }

    // Now minimize with this assignment
    skip_make_sparse = FALSE;
    set_phase(PLA);
    minimize(PLA);
}

//
// repeated_phase_assignment -- an alternate strategy which commits
// to a single phase assignment a step at a time.  Performs m + 1
// minimizations !
//

void repeated_phase_assignment(PLA_t *PLA)
{
    int i;
    set *phase;

    for (i = 0; i < CUBE.part_size[CUBE.output]; i++) {

        // Find best assignment for all undecided outputs
        phase = find_phase(PLA, i, PLA->phase);

        // Commit for only a single output ...
        if (! is_in_set(phase, CUBE.first_part[CUBE.output] + i)) {
            set_remove(PLA->phase, CUBE.first_part[CUBE.output] + i);
        }

        set_free(phase);
    }
}

//
// find_phase -- find a phase assignment for the PLA for all outputs starting
// with output number first_output.
//

set *
find_phase(PLA_t *PLA, int first_output, set *phase1)
{
    set *phase;
    PLA_t *PLA1;

    phase = set_save(CUBE.fullset);

    // setup the double-phase characteristic function, resize the cube
    PLA1 = new_PLA();
    PLA1->F = sf_save(PLA->F);
    PLA1->R = sf_save(PLA->R);
    PLA1->D = sf_save(PLA->D);
    if (phase1 != NULL) {
        PLA1->phase = set_save(phase1);
        set_phase(PLA1);
    }
    output_phase_setup(PLA1, first_output);

    // minimize the double-phase function
    minimize(PLA1);

    // set the proper phases according to what gives a minimum solution
    PLA1->F = opo(phase, PLA1->F, PLA1->D, PLA1->R, first_output);
    free_PLA(PLA1);

    // set the cube structure to reflect the old size
    cube_setdown();
    CUBE.part_size[CUBE.output] -= (CUBE.part_size[CUBE.output] - first_output) / 2;
    cube_setup();

    return phase;
}

//
// opo -- multiply the expression out to determine a minimum subset of
// primes.
//

set_family_t *
opo(set *phase, set_family_t *T, set_family_t *D, set_family_t *R, int first_output)
{
    int offset, output, i, last_output, ind;
    set *pdest, *select, *p, *p1, *last, *last1, *not_covered, *tmp;
    set_family_t *temp, *T1, *T2;

    // must select all primes for outputs [0 .. first_output-1]
    select = set_full(T->count);
    for (output = 0; output < first_output; output++) {
        ind = CUBE.first_part[CUBE.output] + output;
        foreachi_set(T, i, p) {
            if (is_in_set(p, ind)) {
                set_remove(select, i);
            }
        }
    }

    // Recursively perform the intersections
    offset = (CUBE.part_size[CUBE.output] - first_output) / 2;
    last_output = first_output + offset - 1;
    temp = opo_recur(T, D, select, offset, first_output, last_output);

    // largest set is on top -- select primes which are inferred from it
    pdest = temp->data;
    T1 = sf_new(T->count, CUBE.size);
    foreachi_set(T, i, p) {
        if (! is_in_set(pdest, i)) {
            T1 = sf_addset(T1, p);
        }
    }

    set_free(select);
    sf_free(temp);

    // finding phases is difficult -- see which functions are not covered
    T2 = complement(cube1list(T1));
    not_covered = set_new(CUBE.size);
    tmp = set_new(CUBE.size);
    foreach_set(T, last, p) {
        foreach_set(T2, last1, p1) {
            if (cdist0(p, p1)) {
                set_or(not_covered, not_covered, set_and(tmp, p, p1));
            }
        }
    }
    sf_free(T);
    sf_free(T2);
    set_free(tmp);

    // Now reflect the phase choice in a single cube
    for (output = first_output; output <= last_output; output++) {
        ind = CUBE.first_part[CUBE.output] + output;
        if (is_in_set(not_covered, ind)) {
            if (is_in_set(not_covered, ind + offset)) {
                fatal("error in output phase assignment");
            }
            else {
                set_remove(phase, ind);
            }
        }
    }
    set_free(not_covered);

    return T1;
}

set_family_t *
opo_recur(set_family_t *T, set_family_t *D, set *select, int offset, int first, int last)
{
    static int level = 0;
    int middle;
    set_family_t *sl, *sr, *temp;

    level++;
    if (first == last) {
        temp = opo_leaf(T, select, first, first + offset);
    }
    else {
        middle = (first + last) / 2;
        sl = opo_recur(T, D, select, offset, first, middle);
        sr = opo_recur(T, D, select, offset, middle+1, last);
        temp = unate_intersect(sl, sr, level == 1);
        sf_free(sl);
        sf_free(sr);
    }
    level--;

    return temp;
}

set_family_t *
opo_leaf(set_family_t *T, set *select, int out1, int out2)
{
    set_family_t *temp;
    set *p, *pdest;
    int i;

    out1 += CUBE.first_part[CUBE.output];
    out2 += CUBE.first_part[CUBE.output];

    // Allocate space for the result
    temp = sf_new(2, T->count);

    // Find which primes are needed for the ON-set of this fct
    pdest = GETSET(temp, temp->count++);
    set_copy(pdest, select);
    foreachi_set(T, i, p) {
        if (is_in_set(p, out1)) {
            set_remove(pdest, i);
        }
    }

    // Find which primes are needed for the OFF-set of this fct
    pdest = GETSET(temp, temp->count++);
    set_copy(pdest, select);
    foreachi_set(T, i, p) {
        if (is_in_set(p, out2)) {
            set_remove(pdest, i);
        }
    }

    return temp;
}

//
// Take a PLA (ON-set, OFF-set and DC-set) and create the
// "double-phase characteristic function" which is merely a new
// function which has twice as many outputs and realizes both the
// function and the complement.
//
// The cube structure is assumed to represent the PLA upon entering.
// It will be modified to represent the double-phase function upon
// exit.
//
// Only the outputs numbered starting with "first_output" are
// duplicated in the output part
//

void
output_phase_setup(PLA_t *PLA, int first_output)
{
    set_family_t *F, *R, *D;
    set *mask, *mask1, *last;
    int first_part, offset;
    bool save;
    set *p, *pr, *pf;
    int i, last_part;

    if (CUBE.output == -1)
        fatal("output_phase_setup: must have an output");

    F = PLA->F;
    D = PLA->D;
    R = PLA->R;
    first_part = CUBE.first_part[CUBE.output] + first_output;
    last_part = CUBE.last_part[CUBE.output];
    offset = CUBE.part_size[CUBE.output] - first_output;

    // Change the output size, setup the cube structure
    cube_setdown();
    CUBE.part_size[CUBE.output] += offset;
    cube_setup();

    // Create a mask to select that part of the cube which isn't changing
    mask = set_save(CUBE.fullset);
    for (i = first_part; i < CUBE.size; i++)
        set_remove(mask, i);
    mask1 = set_save(mask);
    for (i = CUBE.first_part[CUBE.output]; i < first_part; i++) {
        set_remove(mask1, i);
    }

    PLA->F = sf_new(F->count + R->count, CUBE.size);
    PLA->R = sf_new(F->count + R->count, CUBE.size);
    PLA->D = sf_new(D->count, CUBE.size);

    foreach_set(F, last, p) {
        pf = GETSET(PLA->F, (PLA->F)->count++);
        pr = GETSET(PLA->R, (PLA->R)->count++);
        set_and(pf, mask, p);
        set_and(pr, mask1, p);
        for (i = first_part; i <= last_part; i++)
            if (is_in_set(p, i))
                set_insert(pf, i);
        save = FALSE;
        for (i = first_part; i <= last_part; i++)
            if (is_in_set(p, i))
                save = TRUE, set_insert(pr, i+offset);
        if (! save)
            PLA->R->count--;
    }

    foreach_set(R, last, p) {
        pf = GETSET(PLA->F, (PLA->F)->count++);
        pr = GETSET(PLA->R, (PLA->R)->count++);
        set_and(pf, mask1, p);
        set_and(pr, mask, p);
        save = FALSE;
        for (i = first_part; i <= last_part; i++)
            if (is_in_set(p, i))
                save = TRUE, set_insert(pf, i+offset);
        if (! save)
            PLA->F->count--;
        for (i = first_part; i <= last_part; i++)
            if (is_in_set(p, i))
                set_insert(pr, i);
    }

    foreach_set(D, last, p) {
        pf = GETSET(PLA->D, (PLA->D)->count++);
        set_and(pf, mask, p);
        for (i = first_part; i <= last_part; i++)
            if (is_in_set(p, i)) {
                set_insert(pf, i);
                set_insert(pf, i+offset);
            }
    }

    sf_free(F);
    sf_free(D);
    sf_free(R);
    set_free(mask);
    set_free(mask1);
}

//
// set_phase -- given a "cube" which describes which phases of the output
// are to be implemented, compute the appropriate on-set and off-set
//

PLA_t *
set_phase(PLA_t *PLA)
{
    set_family_t *F1, *R1;
    set *last, *p, *outmask;
    set *temp=CUBE.temp[0], *phase=PLA->phase, *phase1=CUBE.temp[1];

    outmask = CUBE.var_mask[CUBE.num_vars - 1];
    set_diff(phase1, outmask, phase);
    set_or(phase1, set_diff(temp, CUBE.fullset, outmask), phase1);
    F1 = sf_new((PLA->F)->count + (PLA->R)->count, CUBE.size);
    R1 = sf_new((PLA->F)->count + (PLA->R)->count, CUBE.size);

    foreach_set(PLA->F, last, p) {
        if (! setp_disjoint(set_and(temp, p, phase), outmask))
            set_copy(GETSET(F1, F1->count++), temp);
        if (! setp_disjoint(set_and(temp, p, phase1), outmask))
            set_copy(GETSET(R1, R1->count++), temp);
    }
    foreach_set(PLA->R, last, p) {
        if (! setp_disjoint(set_and(temp, p, phase), outmask))
            set_copy(GETSET(R1, R1->count++), temp);
        if (! setp_disjoint(set_and(temp, p, phase1), outmask))
            set_copy(GETSET(F1, F1->count++), temp);
    }
    sf_free(PLA->F);
    sf_free(PLA->R);
    PLA->F = F1;
    PLA->R = R1;

    return PLA;
}

#define POW2(x) (1 << (x))

void
opoall(PLA_t *PLA, int first_output, int last_output, int opo_strategy)
{
    set_family_t *F, *D, *R, *best_F, *best_D, *best_R;
    int i, j, ind, num;
    set *bestphase;

    opo_exact = opo_strategy;

    if (PLA->phase != NULL) {
        set_free(PLA->phase);
    }

    bestphase = set_save(CUBE.fullset);
    best_F = sf_save(PLA->F);
    best_D = sf_save(PLA->D);
    best_R = sf_save(PLA->R);

    for (i = 0; i < POW2(last_output - first_output + 1); i++) {

        // save the initial PLA covers
        F = sf_save(PLA->F);
        D = sf_save(PLA->D);
        R = sf_save(PLA->R);

        /* compute the phase cube for this iteration */
        PLA->phase = set_save(CUBE.fullset);
        num = i;
        for (j = last_output; j >= first_output; j--) {
            if (num % 2 == 0) {
                ind = CUBE.first_part[CUBE.output] + j;
                set_remove(PLA->phase, ind);
            }
            num /= 2;
        }

        // set the phase and minimize
        set_phase(PLA);
        printf("# phase is %s\n", pc1(PLA->phase));
        minimize(PLA);

        // see if this is the best so far
        if (PLA->F->count < best_F->count) {
            // save new best solution
            set_copy(bestphase, PLA->phase);
            sf_free(best_F);
            sf_free(best_D);
            sf_free(best_R);
            best_F = PLA->F;
            best_D = PLA->D;
            best_R = PLA->R;
        }
        else {
            // throw away the solution
            sf_free(PLA->F);
            sf_free(PLA->D);
            sf_free(PLA->R);
        }
        set_free(PLA->phase);

        // restore the initial PLA covers
        PLA->F = F;
        PLA->D = D;
        PLA->R = R;
    }

    // one more minimization to restore the best answer
    PLA->phase = bestphase;
    sf_free(PLA->F);
    sf_free(PLA->D);
    sf_free(PLA->R);
    PLA->F = best_F;
    PLA->D = best_D;
    PLA->R = best_R;
}

static void minimize(PLA_t *PLA)
{
    if (opo_exact) {
        PLA->F = minimize_exact(PLA->F, PLA->D, PLA->R, 1);
    }
    else {
        PLA->F = espresso(PLA->F, PLA->D, PLA->R);
    }
}

