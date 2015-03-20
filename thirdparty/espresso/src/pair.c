// Filename: pair.c

#include <string.h>

#include "espresso.h"

void
set_pair(PLA_t *PLA)
{
    set_pair1(PLA, TRUE);
}

void
set_pair1(PLA_t *PLA, bool adjust_labels)
{
    int i, var, *paired, newvar;
    int old_num_vars, old_num_binary_vars, old_size, old_mv_start;
    int *new_part_size, new_num_vars, new_num_binary_vars, new_mv_start;
    pair_t *pair = PLA->pair;
    char scratch[1000], **oldlabel, *var1, *var1bar, *var2, *var2bar;

    if (adjust_labels)
        makeup_labels(PLA);

    // Check the pair structure for valid entries and see which binary
    // variables are left unpaired
    paired = ALLOC(bool, CUBE.num_binary_vars);
    for (var = 0; var < CUBE.num_binary_vars; var++)
        paired[var] = FALSE;
    for (i = 0; i < pair->cnt; i++)
        if ((pair->var1[i] > 0 && pair->var1[i] <= CUBE.num_binary_vars) &&
            (pair->var2[i] > 0 && pair->var2[i] <= CUBE.num_binary_vars)) {
            paired[pair->var1[i]-1] = TRUE;
            paired[pair->var2[i]-1] = TRUE;
        }
        else
            fatal("can only pair binary-valued variables");

    PLA->F = delvar(pairvar(PLA->F, pair), paired);
    PLA->R = delvar(pairvar(PLA->R, pair), paired);
    PLA->D = delvar(pairvar(PLA->D, pair), paired);

    // Now painfully adjust the cube size
    old_size = CUBE.size;
    old_num_vars = CUBE.num_vars;
    old_num_binary_vars = CUBE.num_binary_vars;
    old_mv_start = CUBE.first_part[CUBE.num_binary_vars];
    // Create the new CUBE.part_size vector and setup the cube structure
    new_num_binary_vars = 0;
    for (var = 0; var < old_num_binary_vars; var++)
        new_num_binary_vars += (paired[var] == FALSE);

    new_num_vars = new_num_binary_vars + pair->cnt;
    new_num_vars += old_num_vars - old_num_binary_vars;
    new_part_size = ALLOC(int, new_num_vars);

    for (var = 0; var < pair->cnt; var++)
        new_part_size[new_num_binary_vars + var] = 4;

    for (var = 0; var < old_num_vars - old_num_binary_vars; var++)
        new_part_size[new_num_binary_vars + pair->cnt + var] =
            CUBE.part_size[old_num_binary_vars + var];

    cube_setdown();
    FREE(CUBE.part_size);
    CUBE.num_vars = new_num_vars;
    CUBE.num_binary_vars = new_num_binary_vars;
    CUBE.part_size = new_part_size;
    cube_setup();

    // hack with the labels to get them correct
    if (adjust_labels) {
        oldlabel = PLA->label;
        PLA->label = ALLOC(char *, CUBE.size);
        for (var = 0; var < pair->cnt; var++) {
            newvar = CUBE.num_binary_vars*2 + var*4;
            var1 = oldlabel[ (pair->var1[var]-1) * 2 + 1];
            var2 = oldlabel[ (pair->var2[var]-1) * 2 + 1];
            var1bar = oldlabel[ (pair->var1[var]-1) * 2];
            var2bar = oldlabel[ (pair->var2[var]-1) * 2];
            sprintf(scratch, "%s+%s", var1bar, var2bar);
            PLA->label[newvar] = strdup(scratch);
            sprintf(scratch, "%s+%s", var1bar, var2);
            PLA->label[newvar+1] = strdup(scratch);
            sprintf(scratch, "%s+%s", var1, var2bar);
            PLA->label[newvar+2] = strdup(scratch);
            sprintf(scratch, "%s+%s", var1, var2);
            PLA->label[newvar+3] = strdup(scratch);
        }

        // Copy the old labels for the unpaired binary vars
        i = 0;
        for (var = 0; var < old_num_binary_vars; var++) {
            if (paired[var] == FALSE) {
                PLA->label[2*i] = oldlabel[2*var];
                PLA->label[2*i+1] = oldlabel[2*var+1];
                oldlabel[2*var] = oldlabel[2*var+1] = (char *) NULL;
                i++;
            }
        }

        // Copy the old labels for the remaining unpaired vars
        new_mv_start = CUBE.num_binary_vars*2 + pair->cnt*4;
        for (i = old_mv_start; i < old_size; i++) {
            PLA->label[new_mv_start + i - old_mv_start] = oldlabel[i];
            oldlabel[i] = (char *) NULL;
        }

        // free remaining entries in oldlabel
        for (i = 0; i < old_size; i++)
            if (oldlabel[i] != (char *) NULL)
                FREE(oldlabel[i]);
        FREE(oldlabel);
    }

    // the paired variables should not be sparse (cf. mv_reduce/raise_in)
    for (var = 0; var < pair->cnt; var++)
        CUBE.sparse[CUBE.num_binary_vars + var] = 0;

    FREE(paired);
}

set_family_t *
pairvar(set_family_t *A, pair_t *pair)
{
    set *last, *p;
    int val, p1, p2, b1, b0;
    int insert_col, pairnum;

    insert_col = CUBE.first_part[CUBE.num_vars - 1];

    // stretch the cover matrix to make room for the paired variables
    A = sf_delcol(A, insert_col, -4*pair->cnt);

    // compute the paired values
    foreach_set(A, last, p) {
        for (pairnum = 0; pairnum < pair->cnt; pairnum++) {
            p1 = CUBE.first_part[pair->var1[pairnum] - 1];
            p2 = CUBE.first_part[pair->var2[pairnum] - 1];
            b1 = is_in_set(p, p2+1);
            b0 = is_in_set(p, p2);
            val = insert_col + pairnum * 4;
            if (/* a0 */ is_in_set(p, p1)) {
                if (b0)
                    set_insert(p, val + 3);
                if (b1)
                    set_insert(p, val + 2);
            }
            if (/* a1 */ is_in_set(p, p1+1)) {
                if (b0)
                    set_insert(p, val + 1);
                if (b1)
                    set_insert(p, val);
            }
        }
    }

    return A;
}

// delvar -- delete variables from A, minimize the number of column shifts

set_family_t *
delvar(set_family_t *A, bool *paired)
{
    bool run;
    int first_run, run_length, var, offset = 0;

    run = FALSE; run_length = 0;

    for (var = 0; var < CUBE.num_binary_vars; var++)
        if (paired[var])
            if (run)
                run_length += CUBE.part_size[var];
            else {
                run = TRUE;
                first_run = CUBE.first_part[var];
                run_length = CUBE.part_size[var];
            }
        else
            if (run) {
                A = sf_delcol(A, first_run-offset, run_length);
                run = FALSE;
                offset += run_length;
            }

    if (run)
        A = sf_delcol(A, first_run-offset, run_length);

    return A;
}

//
// find_optimal_pairing -- find which binary variables should be paired
// to maximally reduce the number of terms
//
// This is essentially the technique outlined by T. Sasao in the
// Trans. on Comp., Oct 1984.  We estimate the cost of pairing each
// pair individually using 1 of 4 strategies: (1) algebraic division
// of F by the pair (exactly T. Sasao technique); (2) strong division
// of F by the paired variables (using REDUCE/EXPAND/ IRREDUNDANT from
// espresso); (3) full minimization using espresso; (4) exact
// minimization.  These are in order of both increasing accuracy and
// increasing difficulty (!)
//
// Once the n squared pairs have been evaluated, T. Sasao proposes a
// graph covering of nodes by disjoint edges.  For now, I solve this
// problem exhaustively (complexity = (n-1)*(n-3)*...*3*1 for n
// variables when n is even).  Note that solving this problem exactly
// is the same as evaluating the cost function for all possible
// pairings.
//
//        n       pairs
//
//     1, 2           1
//     3, 4           3
//     5, 6          15
//     7, 8         105
//     9,10         945
//    11,12      10,395
//    13,14     135,135
//    15,16   2,027,025
//    17,18  34,459,425
//    19,20 654,729,075
//

void find_optimal_pairing(PLA_t *PLA, int strategy)
{
    int i, **cost_array;

    cost_array = find_pairing_cost(PLA, strategy);

    if (CUBE.num_binary_vars <= 14) {
        PLA->pair = pair_best_cost(cost_array);
    }
    else {
        greedy_best_cost(cost_array, &(PLA->pair));
    }
    printf("# ");
    print_pair(PLA->pair);

    for(i = 0; i < CUBE.num_binary_vars; i++)
        FREE(cost_array[i]);
    FREE(cost_array);

    set_pair(PLA);
    PLA->F = espresso(PLA->F, PLA->D, PLA->R);
}

int **
find_pairing_cost(PLA_t *PLA, int strategy)
{
    int var1, var2, **cost_array;
    int i, j, xnum_binary_vars, xnum_vars, *xpart_size, cost;
    set_family_t *T, *Fsave, *Dsave, *Rsave;
    set *mask;

    // data is returned in the cost array
    cost_array = ALLOC(int *, CUBE.num_binary_vars);
    for (i = 0; i < CUBE.num_binary_vars; i++)
        cost_array[i] = ALLOC(int, CUBE.num_binary_vars);
    for (i = 0; i < CUBE.num_binary_vars; i++)
        for (j = 0; j < CUBE.num_binary_vars; j++)
            cost_array[i][j] = 0;

    // Setup the pair structure for pairing variables together
    PLA->pair = pair_new(1);
    PLA->pair->cnt = 1;

    for (var1 = 0; var1 < CUBE.num_binary_vars-1; var1++) {
        for (var2 = var1+1; var2 < CUBE.num_binary_vars; var2++) {
            // if anything but simple strategy, perform setup
            if (strategy > 0) {
                // save the original covers
                Fsave = sf_save(PLA->F);
                Dsave = sf_save(PLA->D);
                Rsave = sf_save(PLA->R);

                // save the original cube structure
                xnum_binary_vars = CUBE.num_binary_vars;
                xnum_vars = CUBE.num_vars;
                xpart_size = ALLOC(int, CUBE.num_vars);
                for (i = 0; i < CUBE.num_vars; i++)
                    xpart_size[i] = CUBE.part_size[i];

                // pair two variables together
                PLA->pair->var1[0] = var1 + 1;
                PLA->pair->var2[0] = var2 + 1;
                set_pair1(PLA, /* adjust_labels */ FALSE);
            }

            // decide how to best estimate worth of this pairing
            switch(strategy) {
            case 3:
                // exact minimization
                PLA->F = minimize_exact(PLA->F, PLA->D, PLA->R, 1);
                cost = Fsave->count - PLA->F->count;
                break;
            case 2:
                // full minimization
                PLA->F = espresso(PLA->F, PLA->D, PLA->R);
                cost = Fsave->count - PLA->F->count;
                break;
            case 1:
                // strong division
                PLA->F = reduce(PLA->F, PLA->D);
                PLA->F = expand(PLA->F, PLA->R, FALSE);
                PLA->F = irredundant(PLA->F, PLA->D);
                cost = Fsave->count - PLA->F->count;
                break;
            case 0:
                // weak division
                mask = set_new(CUBE.size);
                set_or(mask, CUBE.var_mask[var1], CUBE.var_mask[var2]);
                T = dist_merge(sf_save(PLA->F), mask);
                cost = PLA->F->count - T->count;
                sf_free(T);
                set_free(mask);
            }

            cost_array[var1][var2] = cost;

            if (strategy > 0) {
                // restore the original cube structure -- free the new ones
                cube_setdown();
                FREE(CUBE.part_size);
                CUBE.num_binary_vars = xnum_binary_vars;
                CUBE.num_vars = xnum_vars;
                CUBE.part_size = xpart_size;
                cube_setup();

                // restore the original cover(s) -- free the new ones
                sf_free(PLA->F);
                sf_free(PLA->D);
                sf_free(PLA->R);
                PLA->F = Fsave;
                PLA->D = Dsave;
                PLA->R = Rsave;
            }
        }
    }

    pair_free(PLA->pair);
    PLA->pair = NULL;

    return cost_array;
}

static int best_cost;
static int **cost_array;
static pair_t *best_pair;
static set *best_phase;
static PLA_t *global_PLA;
static set_family_t *best_F, *best_D, *best_R;
static int pair_minim_strategy;

void
print_pair(pair_t *pair)
{
    int i;

    printf("pair is");
    for (i = 0; i < pair->cnt; i++)
        printf (" (%d %d)", pair->var1[i], pair->var2[i]);
    printf("\n");
}

int
greedy_best_cost(int **cost_array_local, pair_t **pair_p)
{
    int i, j, besti, bestj, maxcost, total_cost;
    set *cand;
    pair_t *pair;

    pair = pair_new(CUBE.num_binary_vars);
    cand = set_full(CUBE.num_binary_vars);
    total_cost = 0;

    while (set_ord(cand) >= 2) {
        maxcost = -1;
        for (i = 0; i < CUBE.num_binary_vars; i++) {
            if (is_in_set(cand, i)) {
                for (j = i+1; j < CUBE.num_binary_vars; j++) {
                    if (is_in_set(cand, j)) {
                        if (cost_array_local[i][j] > maxcost) {
                            maxcost = cost_array_local[i][j];
                            besti = i;
                            bestj = j;
                        }
                    }
                }
            }
        }
        pair->var1[pair->cnt] = besti + 1;
        pair->var2[pair->cnt] = bestj + 1;
        pair->cnt++;
        set_remove(cand, besti);
        set_remove(cand, bestj);
        total_cost += maxcost;
    }
    set_free(cand);
    *pair_p = pair;

    return total_cost;
}

pair_t *
pair_best_cost(int **cost_array_local)
{
    pair_t *pair;
    set *candidate;

    best_cost = -1;
    best_pair = NULL;
    cost_array = cost_array_local;

    pair = pair_new(CUBE.num_binary_vars);
    candidate = set_full(CUBE.num_binary_vars);
    generate_all_pairs(pair, CUBE.num_binary_vars, candidate, find_best_cost);
    pair_free(pair);
    set_free(candidate);
    return best_pair;
}

void
find_best_cost(pair_t *pair)
{
    int i, cost;

    cost = 0;
    for (i = 0; i < pair->cnt; i++)
        cost += cost_array[pair->var1[i]-1][pair->var2[i]-1];
    if (cost > best_cost) {
        best_cost = cost;
        best_pair = pair_save(pair, pair->cnt);
    }
    if (debug & MINCOV) {
        printf("cost is %d ", cost);
        print_pair(pair);
    }
}

//
// pair_all: brute-force approach to try all possible pairings
//
// pair_strategy is:
// 2) for espresso
// 3) for minimize_exact
// 4) for phase assignment
//

void
pair_all(PLA_t *PLA, int pair_strategy)
{
    pair_t *pair;
    set *candidate;

    global_PLA = PLA;
    pair_minim_strategy = pair_strategy;
    best_cost = PLA->F->count + 1;
    best_pair = NULL;
    best_phase = NULL;
    best_F = best_D = best_R = NULL;
    pair = pair_new(CUBE.num_binary_vars);
    candidate = set_fill(set_new(CUBE.num_binary_vars), CUBE.num_binary_vars);

    generate_all_pairs(pair, CUBE.num_binary_vars, candidate, minimize_pair);

    pair_free(pair);
    set_free(candidate);

    PLA->pair = best_pair;
    PLA->phase = best_phase;

    set_pair(PLA);
    printf("# ");
    print_pair(PLA->pair);

    sf_free(PLA->F);
    sf_free(PLA->D);
    sf_free(PLA->R);
    PLA->F = best_F;
    PLA->D = best_D;
    PLA->R = best_R;
}

//
// minimize_pair -- called as each pair is generated
//

void
minimize_pair(pair_t *pair)
{
    set_family_t *Fsave, *Dsave, *Rsave;
    int i, xnum_binary_vars, xnum_vars, *xpart_size;

    // save the original covers
    Fsave = sf_save(global_PLA->F);
    Dsave = sf_save(global_PLA->D);
    Rsave = sf_save(global_PLA->R);

    // save the original cube structure
    xnum_binary_vars = CUBE.num_binary_vars;
    xnum_vars = CUBE.num_vars;
    xpart_size = ALLOC(int, CUBE.num_vars);
    for (i = 0; i < CUBE.num_vars; i++)
        xpart_size[i] = CUBE.part_size[i];

    // setup the paired variables
    global_PLA->pair = pair;
    set_pair1(global_PLA, /* adjust_labels */ FALSE);

    // call the minimizer
    switch(pair_minim_strategy) {
    case 2:
        phase_assignment(global_PLA,0);
        break;
    case 1:
        global_PLA->F = minimize_exact(global_PLA->F, global_PLA->D, global_PLA->R, 1);
        break;
    case 0:
        global_PLA->F = espresso(global_PLA->F, global_PLA->D, global_PLA->R);
        break;
    default:
        break;
    }

    // see if we have a new best solution
    if (global_PLA->F->count < best_cost) {
        best_cost = global_PLA->F->count;
        best_pair = pair_save(pair, pair->cnt);
        best_phase = global_PLA->phase!=NULL?set_save(global_PLA->phase):NULL;
        if (best_F != NULL) sf_free(best_F);
        if (best_D != NULL) sf_free(best_D);
        if (best_R != NULL) sf_free(best_R);
        best_F = sf_save(global_PLA->F);
        best_D = sf_save(global_PLA->D);
        best_R = sf_save(global_PLA->R);
    }

    // restore the original cube structure -- free the new ones
    cube_setdown();
    FREE(CUBE.part_size);
    CUBE.num_binary_vars = xnum_binary_vars;
    CUBE.num_vars = xnum_vars;
    CUBE.part_size = xpart_size;
    cube_setup();

    // restore the original cover(s) -- free the new ones
    sf_free(global_PLA->F);
    sf_free(global_PLA->D);
    sf_free(global_PLA->R);
    global_PLA->F = Fsave;
    global_PLA->D = Dsave;
    global_PLA->R = Rsave;
    global_PLA->pair = NULL;
    global_PLA->phase = NULL;
}

void
generate_all_pairs(pair_t *pair, int n, set *candidate, void (*action)(pair_t *))
{
    int i, j;
    set *recur_candidate;
    pair_t *recur_pair;

    if (set_ord(candidate) < 2) {
        (*action)(pair);
        return;
    }

    recur_pair = pair_save(pair, n);
    recur_candidate = set_save(candidate);

    // Find first variable still in the candidate set
    for (i = 0; i < n; i++)
        if (is_in_set(candidate, i))
            break;

    // Try all pairs of i with other variables
    for (j = i+1; j < n; j++)
        if (is_in_set(candidate, j)) {
            // pair (i j) -- remove from candidate set for future pairings
            set_remove(recur_candidate, i);
            set_remove(recur_candidate, j);

            // add to the pair array
            recur_pair->var1[recur_pair->cnt] = i+1;
            recur_pair->var2[recur_pair->cnt] = j+1;
            recur_pair->cnt++;

            // recur looking for the end ...
            generate_all_pairs(recur_pair, n, recur_candidate, action);

            // now break this pair, and restore candidate set
            recur_pair->cnt--;
            set_insert(recur_candidate, i);
            set_insert(recur_candidate, j);
        }

    // if odd, generate all pairs which do NOT include i
    if ((set_ord(candidate) % 2) == 1) {
        set_remove(recur_candidate, i);
        generate_all_pairs(recur_pair, n, recur_candidate, action);
    }

    pair_free(recur_pair);
    set_free(recur_candidate);
}

pair_t *
pair_new(int n)
{
    pair_t *pair1;

    pair1 = ALLOC(pair_t, 1);
    pair1->cnt = 0;
    pair1->var1 = ALLOC(int, n);
    pair1->var2 = ALLOC(int, n);
    return pair1;
}

pair_t *
pair_save(pair_t *pair, int n)
{
    int k;
    pair_t *pair1;

    pair1 = pair_new(n);
    pair1->cnt = pair->cnt;
    for (k = 0; k < pair->cnt; k++) {
        pair1->var1[k] = pair->var1[k];
        pair1->var2[k] = pair->var2[k];
    }
    return pair1;
}

void
pair_free(pair_t *pair)
{
    FREE(pair->var1);
    FREE(pair->var2);
    FREE(pair);
}

