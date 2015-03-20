// Filename: exact.c

#include <string.h>

#include "espresso.h"

static void dump_irredundant(set_family_t *E, set_family_t *Rt, set_family_t *Rp, sm_matrix *table);
static set_family_t *do_minimize(set_family_t *F, set_family_t *D, set_family_t *R, int exact_cover, int weighted);

//
// minimize_exact -- main entry point for exact minimization
//
// Global flags which affect this routine are:
//
//     debug
//     skip_make_sparse
//

set_family_t *
minimize_exact(set_family_t *F, set_family_t *D, set_family_t *R, int exact_cover)
{
    return do_minimize(F, D, R, exact_cover, /*weighted*/ 0);
}

set_family_t *
minimize_exact_literals(set_family_t *F, set_family_t *D, set_family_t *R, int exact_cover)
{
    return do_minimize(F, D, R, exact_cover, /*weighted*/ 1);
}

static set_family_t *
do_minimize(set_family_t *F, set_family_t *D, set_family_t *R, int exact_cover, int weighted)
{
    set_family_t *newF, *E, *Rt, *Rp;
    set *p, *last;
    int heur, level, *weights;
    sm_matrix *table;
    sm_row *cover;
    sm_element *pe;
    int debug_save = debug;

    if (debug & EXACT) {
        debug |= (IRRED | MINCOV);
    }
    level = (debug & MINCOV) ? 4 : 0;
    heur = ! exact_cover;

    // Generate all prime implicants
    F = primes_consensus(cube2list(F, D));

    // Setup the prime implicant table
    irred_split_cover(F, D, &E, &Rt, &Rp);
    table = irred_derive_table(D, E, Rp);

    // Solve either a weighted or nonweighted covering problem
    if (weighted) {
        // correct only for all 2-valued variables
        weights = ALLOC(int, F->count);
        foreach_set(Rp, last, p) {
            weights[SIZE(p)] = CUBE.size - set_ord(p);
        }
    }
    else {
        weights = NIL(int);
    }
    cover = sm_minimum_cover(table,weights,heur,level);
    if (weights != 0) {
        FREE(weights);
    }

    if (debug & EXACT) {
        dump_irredundant(E, Rt, Rp, table);
    }

    // Form the result cover
    newF = sf_new(100, CUBE.size);
    foreach_set(E, last, p) {
        newF = sf_addset(newF, p);
    }
    sm_foreach_row_element(cover, pe) {
        newF = sf_addset(newF, GETSET(F, pe->col_num));
    }

    sf_free(E);
    sf_free(Rt);
    sf_free(Rp);
    sm_free(table);
    sm_row_free(cover);
    sf_free(F);

    // Attempt to make the results more sparse
    debug &= ~ (IRRED | SHARP | MINCOV);
    if (! skip_make_sparse && R != 0) {
        newF = make_sparse(newF, D, R);
    }

    debug = debug_save;
    return newF;
}

static void
dump_irredundant(set_family_t *E, set_family_t *Rt, set_family_t *Rp, sm_matrix *table)
{
    FILE *fp_pi_table, *fp_primes;
    PLA_t *PLA;
    set *last, *p;
    char *file;

    if (filename == 0 || strcmp(filename, "(stdin)") == 0) {
        fp_pi_table = fp_primes = stdout;
    }
    else {
        file = ALLOC(char, strlen(filename)+20);
        sprintf(file, "%s.primes", filename);
        if ((fp_primes = fopen(file, "w")) == NULL) {
            fprintf(stderr, "espresso: Unable to open %s\n", file);
            fp_primes = stdout;
        }
        sprintf(file, "%s.pi", filename);
        if ((fp_pi_table = fopen(file, "w")) == NULL) {
            fprintf(stderr, "espresso: Unable to open %s\n", file);
            fp_pi_table = stdout;
        }
        FREE(file);
    }

    PLA = new_PLA();
    PLA_labels(PLA);

    fpr_header(fp_primes, PLA, F_type);
    free_PLA(PLA);

    fprintf(fp_primes, "# Essential primes are\n");
    foreach_set(E, last, p) {
        fprintf(fp_primes, "%s\n", pc1(p));
    }
    fprintf(fp_primes, "# Totally redundant primes are\n");
    foreach_set(Rt, last, p) {
        fprintf(fp_primes, "%s\n", pc1(p));
    }
    fprintf(fp_primes, "# Partially redundant primes are\n");
    foreach_set(Rp, last, p) {
        fprintf(fp_primes, "%s\n", pc1(p));
    }
    if (fp_primes != stdout) {
        fclose(fp_primes);
    }

    sm_write(fp_pi_table, table);
    if (fp_pi_table != stdout) {
        fclose(fp_pi_table);
    }
}

