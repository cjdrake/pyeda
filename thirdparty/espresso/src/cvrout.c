// Filename: cvrout.c
//
// purpose: cube and cover output routines
//

#include <string.h>

#include "espresso.h"

void fprint_pla(FILE *fp, PLA_t *PLA, int output_type)
{
    int num;
    set *last, *p;

    if ((output_type & CONSTRAINTS_type) != 0) {
        output_symbolic_constraints(fp, PLA, 0);
        output_type &= ~ CONSTRAINTS_type;
        if (output_type == 0) {
            return;
        }
    }

    if ((output_type & SYMBOLIC_CONSTRAINTS_type) != 0) {
        output_symbolic_constraints(fp, PLA, 1);
        output_type &= ~ SYMBOLIC_CONSTRAINTS_type;
        if (output_type == 0) {
            return;
        }
    }

    if (output_type == PLEASURE_type) {
        pls_output(PLA);
    }
    else if (output_type == EQNTOTT_type) {
        eqn_output(PLA);
    }
    else if (output_type == KISS_type) {
        kiss_output(fp, PLA);
    }
    else {
        fpr_header(fp, PLA, output_type);

        num = 0;
        if (output_type & F_type)
            num += (PLA->F)->count;
        if (output_type & D_type)
            num += (PLA->D)->count;
        if (output_type & R_type)
            num += (PLA->R)->count;
        fprintf(fp, ".p %d\n", num);

        // quick patch 01/17/85 to support TPLA !
        if (output_type == F_type) {
            foreach_set(PLA->F, last, p) {
                print_cube(fp, p, "01");
            }
            fprintf(fp, ".e\n");
        }
        else {
            if (output_type & F_type) {
                foreach_set(PLA->F, last, p) {
                    print_cube(fp, p, "~1");
                }
            }
            if (output_type & D_type) {
                foreach_set(PLA->D, last, p) {
                    print_cube(fp, p, "~2");
                }
            }
            if (output_type & R_type) {
                foreach_set(PLA->R, last, p) {
                    print_cube(fp, p, "~0");
                }
            }
            fprintf(fp, ".end\n");
        }
    }
}

void
fpr_header(FILE *fp, PLA_t *PLA, int output_type)
{
    int i, var;
    int first, last;

    // .type keyword gives logical type
    if (output_type != F_type) {
        fprintf(fp, ".type ");
        if (output_type & F_type) putc('f', fp);
        if (output_type & D_type) putc('d', fp);
        if (output_type & R_type) putc('r', fp);
        putc('\n', fp);
    }

    // Check for binary or multiple-valued labels
    if (CUBE.num_mv_vars <= 1) {
        fprintf(fp, ".i %d\n", CUBE.num_binary_vars);
        if (CUBE.output != -1)
            fprintf(fp, ".o %d\n", CUBE.part_size[CUBE.output]);
    }
    else {
        fprintf(fp, ".mv %d %d", CUBE.num_vars, CUBE.num_binary_vars);
        for (var = CUBE.num_binary_vars; var < CUBE.num_vars; var++)
            fprintf(fp, " %d", CUBE.part_size[var]);
        fprintf(fp, "\n");
    }

    // binary valued labels
    if (PLA->label != NIL(char *) && PLA->label[1] != NIL(char) && CUBE.num_binary_vars > 0) {
        fprintf(fp, ".ilb");
        for (var = 0; var < CUBE.num_binary_vars; var++)
            fprintf(fp, " %s", INLABEL(var));
        putc('\n', fp);
    }

    // output-part (last multiple-valued variable) labels
    if (PLA->label != NIL(char *) && PLA->label[CUBE.first_part[CUBE.output]] != NIL(char) && CUBE.output != -1) {
        fprintf(fp, ".ob");
        for (i = 0; i < CUBE.part_size[CUBE.output]; i++)
            fprintf(fp, " %s", OUTLABEL(i));
        putc('\n', fp);
    }

    // multiple-valued labels
    for (var = CUBE.num_binary_vars; var < CUBE.num_vars-1; var++) {
        first = CUBE.first_part[var];
        last = CUBE.last_part[var];
        if (PLA->label != NULL && PLA->label[first] != NULL) {
            fprintf(fp, ".label var=%d", var);
            for (i = first; i <= last; i++) {
                fprintf(fp, " %s", PLA->label[i]);
            }
            putc('\n', fp);
        }
    }

    if (PLA->phase != (set *) NULL) {
        first = CUBE.first_part[CUBE.output];
        last = CUBE.last_part[CUBE.output];
        fprintf(fp, "#.phase ");
        for (i = first; i <= last; i++)
            putc(is_in_set(PLA->phase,i) ? '1' : '0', fp);
        fprintf(fp, "\n");
    }
}

void
pls_output(PLA_t *PLA)
{
    set *last, *p;

    printf(".option unmerged\n");
    makeup_labels(PLA);
    pls_label(PLA, stdout);
    pls_group(PLA, stdout);
    printf(".p %d\n", PLA->F->count);
    foreach_set(PLA->F, last, p) {
        print_expanded_cube(stdout, p, PLA->phase);
    }
    printf(".end\n");
}

void
pls_group(PLA_t *PLA, FILE *fp)
{
    int var, i, col, len;

    fprintf(fp, "\n.group");
    col = 6;
    for (var = 0; var < CUBE.num_vars-1; var++) {
        fprintf(fp, " ("), col += 2;
        for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
            len = strlen(PLA->label[i]);
            if (col + len > 75)
                fprintf(fp, " \\\n"), col = 0;
            else if (i != 0)
                putc(' ', fp), col += 1;
            fprintf(fp, "%s", PLA->label[i]), col += len;
        }
        fprintf(fp, ")"), col += 1;
    }
    fprintf(fp, "\n");
}

void
pls_label(PLA_t *PLA, FILE *fp)
{
    int var, i, col, len;

    fprintf(fp, ".label");
    col = 6;
    for (var = 0; var < CUBE.num_vars; var++)
        for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
            len = strlen(PLA->label[i]);
            if (col + len > 75)
                fprintf(fp, " \\\n"), col = 0;
            else
                putc(' ', fp), col += 1;
            fprintf(fp, "%s", PLA->label[i]), col += len;
        }
}

//
// eqntott output mode -- output algebraic equations
//

void
eqn_output(PLA_t *PLA)
{
    set *p, *last;
    int i, var, col, len;
    int x;
    bool firstand, firstor;

    if (CUBE.output == -1)
        fatal("Cannot have no-output function for EQNTOTT output mode");
    if (CUBE.num_mv_vars != 1)
        fatal("Must have binary-valued function for EQNTOTT output mode");
    makeup_labels(PLA);

    // Write a single equation for each output
    for (i = 0; i < CUBE.part_size[CUBE.output]; i++) {
        printf("%s = ", OUTLABEL(i));
        col = strlen(OUTLABEL(i)) + 3;
        firstor = TRUE;

        // Write product terms for each cube in this output
        foreach_set(PLA->F, last, p)
            if (is_in_set(p, i + CUBE.first_part[CUBE.output])) {
                if (firstor)
                    printf("("), col += 1;
                else
                    printf(" | ("), col += 4;
                firstor = FALSE;
                firstand = TRUE;

                // print out a product term
                for (var = 0; var < CUBE.num_binary_vars; var++)
                    if ((x=GETINPUT(p, var)) != DASH) {
                        len = strlen(INLABEL(var));
                        if (col+len > 72)
                            printf("\n    "), col = 4;
                        if (! firstand)
                            printf("&"), col += 1;
                        firstand = FALSE;
                        if (x == ZERO)
                            printf("!"), col += 1;
                        printf("%s", INLABEL(var)), col += len;
                    }

                printf(")"), col += 1;
            }

        printf(";\n\n");
    }
}

char *
fmt_cube(set *c, char *out_map, char *s)
{
    int i, var, last, len = 0;

    for (var = 0; var < CUBE.num_binary_vars; var++) {
        s[len++] = "?01-" [GETINPUT(c, var)];
    }
    for (var = CUBE.num_binary_vars; var < CUBE.num_vars - 1; var++) {
        s[len++] = ' ';
        for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
            s[len++] = "01" [is_in_set(c, i) != 0];
        }
    }
    if (CUBE.output != -1) {
        last = CUBE.last_part[CUBE.output];
        s[len++] = ' ';
        for (i = CUBE.first_part[CUBE.output]; i <= last; i++) {
            s[len++] = out_map [is_in_set(c, i) != 0];
        }
    }
    s[len] = '\0';
    return s;
}

void
print_cube(FILE *fp, set *c, char *out_map)
{
    int i, var, ch;
    int last;

    for (var = 0; var < CUBE.num_binary_vars; var++) {
        ch = "?01-" [GETINPUT(c, var)];
        putc(ch, fp);
    }
    for (var = CUBE.num_binary_vars; var < CUBE.num_vars - 1; var++) {
        putc(' ', fp);
        for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
            ch = "01" [is_in_set(c, i) != 0];
            putc(ch, fp);
        }
    }
    if (CUBE.output != -1) {
        last = CUBE.last_part[CUBE.output];
        putc(' ', fp);
        for (i = CUBE.first_part[CUBE.output]; i <= last; i++) {
            ch = out_map [is_in_set(c, i) != 0];
            putc(ch, fp);
        }
    }
    putc('\n', fp);
}

void
print_expanded_cube(FILE *fp, set *c, set *phase)
{
    int i, var, ch;
    char *out_map;

    for (var = 0; var < CUBE.num_binary_vars; var++) {
        for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
            ch = "~1" [is_in_set(c, i) != 0];
            putc(ch, fp);
        }
    }
    for (var = CUBE.num_binary_vars; var < CUBE.num_vars - 1; var++) {
        for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
            ch = "1~" [is_in_set(c, i) != 0];
            putc(ch, fp);
        }
    }
    if (CUBE.output != -1) {
        var = CUBE.num_vars - 1;
        putc(' ', fp);
        for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
            if (phase == (set *) NULL || is_in_set(phase, i)) {
                out_map = "~1";
            }
            else {
                out_map = "~0";
            }
            ch = out_map[is_in_set(c, i) != 0];
            putc(ch, fp);
        }
    }
    putc('\n', fp);
}

char *
pc1(set *c)
{
    static char s1[256];
    return fmt_cube(c, "01", s1);
}

char *
pc2(set *c)
{
    static char s2[256];
    return fmt_cube(c, "01", s2);
}

void
debug_print(set **T, char *name, int level)
{
    set **T1, *p, *temp;
    int cnt;

    cnt = CUBELISTSIZE(T);
    temp = set_new(CUBE.size);
    if (verbose_debug && level == 0)
        printf("\n");
    printf("%s[%d]: ord(T)=%d\n", name, level, cnt);
    if (verbose_debug) {
        printf("cofactor=%s\n", pc1(T[0]));
        for (T1 = T+2, cnt = 1; (p = *T1++) != (set *) NULL; cnt++)
            printf("%4d. %s\n", cnt, pc1(set_or(temp, p, T[0])));
    }
    set_free(temp);
}

void
debug1_print(set_family_t *T, char *name, int num)
{
    int cnt = 1;
    set *p, *last;

    if (verbose_debug && num == 0)
        printf("\n");
    printf("%s[%d]: ord(T)=%d\n", name, num, T->count);
    if (verbose_debug)
        foreach_set(T, last, p)
            printf("%4d. %s\n", cnt++, pc1(p));
}

void
cprint(set_family_t *T)
{
    set *p, *last;

    foreach_set(T, last, p)
        printf("%s\n", pc1(p));
}

void
makeup_labels(PLA_t *PLA)
{
    int var, i, ind;

    if (PLA->label == (char **) NULL)
        PLA_labels(PLA);

    for (var = 0; var < CUBE.num_vars; var++)
        for (i = 0; i < CUBE.part_size[var]; i++) {
            ind = CUBE.first_part[var] + i;
            if (PLA->label[ind] == (char *) NULL) {
                PLA->label[ind] = ALLOC(char, 15);
                if (var < CUBE.num_binary_vars)
                    if ((i % 2) == 0)
                        sprintf(PLA->label[ind], "v%d.bar", var);
                    else
                        sprintf(PLA->label[ind], "v%d", var);
                else
                    sprintf(PLA->label[ind], "v%d.%d", var, i);
            }
        }
}

void kiss_output(FILE *fp, PLA_t *PLA)
{
    set *last, *p;

    foreach_set(PLA->F, last, p) {
        kiss_print_cube(fp, PLA, p, "~1");
    }
    foreach_set(PLA->D, last, p) {
        kiss_print_cube(fp, PLA, p, "~2");
    }
}

void
kiss_print_cube(FILE *fp, PLA_t *PLA, set *p, char *out_string)
{
    int i, var;
    int part, x;

    for (var = 0; var < CUBE.num_binary_vars; var++) {
        x = "?01-" [GETINPUT(p, var)];
        putc(x, fp);
    }

    for (var = CUBE.num_binary_vars; var < CUBE.num_vars - 1; var++) {
        putc(' ', fp);
        if (setp_implies(CUBE.var_mask[var], p)) {
            putc('-', fp);
        }
        else {
            part = -1;
            for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
                if (is_in_set(p, i)) {
                    if (part != -1) {
                        fatal("more than 1 part in a symbolic variable\n");
                    }
                    part = i;
                }
            }
            if (part == -1) {
                putc('~', fp);	/* no parts, hope its an output ... */
            }
            else {
                fputs(PLA->label[part], fp);
            }
        }
    }

    if ((var = CUBE.output) != -1) {
        putc(' ', fp);
        for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
            x = out_string [is_in_set(p, i) != 0];
            putc(x, fp);
        }
    }

    putc('\n', fp);
}

void
output_symbolic_constraints(FILE *fp, PLA_t *PLA, int output_symbolic)
{
    set_family_t *A;
    int i, j;
    int size, var, npermute, *permute, *weight, noweight;

    if ((CUBE.num_vars - CUBE.num_binary_vars) <= 1) {
        return;
    }
    makeup_labels(PLA);

    for (var=CUBE.num_binary_vars; var < CUBE.num_vars-1; var++) {

        // pull out the columns for variable "var"
        npermute = CUBE.part_size[var];
        permute = ALLOC(int, npermute);
        for (i=0; i < npermute; i++) {
            permute[i] = CUBE.first_part[var] + i;
        }
        A = sf_permute(sf_save(PLA->F), permute, npermute);
        FREE(permute);

        // Delete the singletons and the full sets
        noweight = 0;
        for (i = 0; i < A->count; i++) {
            size = set_ord(GETSET(A,i));
            if (size == 1 || size == A->sf_size) {
                sf_delset(A, i--);
                noweight++;
            }
        }

        // Count how many times each is duplicated
        weight = ALLOC(int, A->count);
        for (i = 0; i < A->count; i++) {
            RESET(GETSET(A, i), COVERED);
        }
        for (i = 0; i < A->count; i++) {
            weight[i] = 0;
            if (! TESTP(GETSET(A,i), COVERED)) {
                weight[i] = 1;
                for (j = i+1; j < A->count; j++) {
                    if (setp_equal(GETSET(A,i), GETSET(A,j))) {
                        weight[i]++;
                        SET(GETSET(A,j), COVERED);
                    }
                }
            }
        }

        // Print out the contraints
        if (! output_symbolic) {
            fprintf(fp, "# Symbolic constraints for variable %d (Numeric form)\n", var);
            fprintf(fp, "# unconstrained weight = %d\n", noweight);
            fprintf(fp, "num_codes=%d\n", CUBE.part_size[var]);
            for (i = 0; i < A->count; i++) {
                if (weight[i] > 0) {
                    fprintf(fp, "weight=%d: ", weight[i]);
                    for (j = 0; j < A->sf_size; j++) {
                        if (is_in_set(GETSET(A,i), j)) {
                            fprintf(fp, " %d", j);
                        }
                    }
                    fprintf(fp, "\n");
                }
            }
        }
        else {
            fprintf(fp, "# Symbolic constraints for variable %d (Symbolic form)\n", var);
            for (i = 0; i < A->count; i++) {
                if (weight[i] > 0) {
                    fprintf(fp, "#   w=%d: (", weight[i]);
                    for (j = 0; j < A->sf_size; j++) {
                        if (is_in_set(GETSET(A,i), j)) {
                            fprintf(fp, " %s",
                            PLA->label[CUBE.first_part[var]+j]);
                        }
                    }
                    fprintf(fp, " )\n");
                }
            }
            FREE(weight);
        }
    }
}

