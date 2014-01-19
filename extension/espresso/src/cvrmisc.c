// Filename: cvrmisc.c

#include "espresso.h"

// cost -- compute the cost of a cover
void
cover_cost(set_family_t *F, cost_t *cost)
{
    set *p, *last;
    set **T;
    int var;

    // use the routine used by cofactor to decide splitting variables
    massive_count(T = cube1list(F));
    free_cubelist(T);

    cost->cubes = F->count;
    cost->total = cost->in = cost->out = cost->mv = cost->primes = 0;

    // Count transistors (zeros) for each binary variable (inputs)
    for (var = 0; var < CUBE.num_binary_vars; var++)
        cost->in += CDATA.var_zeros[var];

    // Count transistors for each mv variable based on sparse/dense
    for (var = CUBE.num_binary_vars; var < CUBE.num_vars - 1; var++)
        if (CUBE.sparse[var])
            cost->mv += F->count * CUBE.part_size[var] - CDATA.var_zeros[var];
        else
            cost->mv += CDATA.var_zeros[var];

    // Count the transistors (ones) for the output variable
    if (CUBE.num_binary_vars != CUBE.num_vars) {
        var = CUBE.num_vars - 1;
        cost->out = F->count * CUBE.part_size[var] - CDATA.var_zeros[var];
    }

    // Count the number of nonprime cubes
    foreach_set(F, last, p)
        cost->primes += TESTP(p, PRIME) != 0;

    // Count the total number of literals
    cost->total = cost->in + cost->out + cost->mv;
}

// fmt_cost -- return a string which reports the "cost" of a cover
char *
fmt_cost(cost_t *cost)
{
    static char s[200];

    if (CUBE.num_binary_vars == CUBE.num_vars - 1)
        sprintf(s, "c=%d(%d) in=%d out=%d tot=%d",
                cost->cubes, cost->cubes - cost->primes, cost->in,
                cost->out, cost->total);
    else
        sprintf(s, "c=%d(%d) in=%d mv=%d out=%d",
                cost->cubes, cost->cubes - cost->primes, cost->in,
                cost->mv, cost->out);
    return s;
}

char *
print_cost(set_family_t *F)
{
    cost_t cost;
    cover_cost(F, &cost);
    return fmt_cost(&cost);
}

// copy_cost -- copy a cost function from s to d
void
copy_cost(cost_t *s, cost_t *d)
{
    d->cubes = s->cubes;
    d->in = s->in;
    d->out = s->out;
    d->mv = s->mv;
    d->total = s->total;
    d->primes = s->primes;
}

// fatal -- report fatal error message and take a dive
void
fatal(char *s)
{
    fprintf(stderr, "espresso: %s\n", s);
    exit(1);
}

