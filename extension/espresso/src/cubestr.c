//
// Module: cubestr.c -- routines for managing the global cube structure
//

#include "espresso.h"

//
// cube_setup -- assume that the fields "num_vars", "num_binary_vars", and
// part_size[num_binary_vars .. num_vars-1] are setup, and initialize the
// rest of CUBE and CDATA.
//
// If a part_size is < 0, then the field size is abs(part_size) and the
// field read from the input is symbolic.
//

void
cube_setup(void)
{
    int i, var;
    set *p;

    if (CUBE.num_binary_vars < 0 || CUBE.num_vars < CUBE.num_binary_vars)
        fatal("cube size is silly, error in .i/.o or .mv");

    CUBE.num_mv_vars = CUBE.num_vars - CUBE.num_binary_vars;
    CUBE.output = CUBE.num_mv_vars > 0 ? CUBE.num_vars - 1 : -1;
    CUBE.size = 0;
    CUBE.first_part = ALLOC(int, CUBE.num_vars);
    CUBE.last_part = ALLOC(int, CUBE.num_vars);
    CUBE.first_word = ALLOC(int, CUBE.num_vars);
    CUBE.last_word = ALLOC(int, CUBE.num_vars);

    for (var = 0; var < CUBE.num_vars; var++) {
        if (var < CUBE.num_binary_vars)
            CUBE.part_size[var] = 2;
        CUBE.first_part[var] = CUBE.size;
        CUBE.first_word[var] = WHICH_WORD(CUBE.size);
        CUBE.size += ABS(CUBE.part_size[var]);
        CUBE.last_part[var] = CUBE.size - 1;
        CUBE.last_word[var] = WHICH_WORD(CUBE.size - 1);
    }

    CUBE.var_mask = ALLOC(set *, CUBE.num_vars);
    CUBE.sparse = ALLOC(int, CUBE.num_vars);
    CUBE.binary_mask = set_new(CUBE.size);
    CUBE.mv_mask = set_new(CUBE.size);

    for (var = 0; var < CUBE.num_vars; var++) {
        p = CUBE.var_mask[var] = set_new(CUBE.size);
        for (i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++)
            set_insert(p, i);
        if (var < CUBE.num_binary_vars) {
            set_or(CUBE.binary_mask, CUBE.binary_mask, p);
            CUBE.sparse[var] = 0;
        }
        else {
            set_or(CUBE.mv_mask, CUBE.mv_mask, p);
            CUBE.sparse[var] = 1;
        }
    }
    if (CUBE.num_binary_vars == 0)
        CUBE.inword = -1;
    else {
        CUBE.inword = CUBE.last_word[CUBE.num_binary_vars - 1];
        CUBE.inmask = CUBE.binary_mask[CUBE.inword] & DISJOINT;
    }

    CUBE.temp = ALLOC(set *, CUBE_TEMP);
    for (i = 0; i < CUBE_TEMP; i++)
        CUBE.temp[i] = set_new(CUBE.size);

    CUBE.fullset = set_fill(set_new(CUBE.size), CUBE.size);
    CUBE.emptyset = set_new(CUBE.size);

    CDATA.part_zeros = ALLOC(int, CUBE.size);
    CDATA.var_zeros = ALLOC(int, CUBE.num_vars);
    CDATA.parts_active = ALLOC(int, CUBE.num_vars);
    CDATA.is_unate = ALLOC(int, CUBE.num_vars);
}

//
// cube_setdown -- free memory allocated for the CUBE/CDATA structs
// (free's all but the part_size array)
//

void
cube_setdown(void)
{
    int i, var;

    FREE(CUBE.first_part);
    FREE(CUBE.last_part);
    FREE(CUBE.first_word);
    FREE(CUBE.last_word);
    FREE(CUBE.sparse);

    set_free(CUBE.binary_mask);
    set_free(CUBE.mv_mask);
    set_free(CUBE.fullset);
    set_free(CUBE.emptyset);

    for (var = 0; var < CUBE.num_vars; var++)
        set_free(CUBE.var_mask[var]);
    FREE(CUBE.var_mask);

    for(i = 0; i < CUBE_TEMP; i++)
        set_free(CUBE.temp[i]);
    FREE(CUBE.temp);

    FREE(CDATA.part_zeros);
    FREE(CDATA.var_zeros);
    FREE(CDATA.parts_active);
    FREE(CDATA.is_unate);

    CUBE.first_part = CUBE.last_part = (int *) NULL;
    CUBE.first_word = CUBE.last_word = (int *) NULL;
    CUBE.sparse = (int *) NULL;
    CUBE.binary_mask = CUBE.mv_mask = (set *) NULL;
    CUBE.fullset = CUBE.emptyset = (set *) NULL;
    CUBE.var_mask = CUBE.temp = (set **) NULL;

    CDATA.part_zeros = CDATA.var_zeros = CDATA.parts_active = (int *) NULL;
    CDATA.is_unate = (bool *) NULL;
}

