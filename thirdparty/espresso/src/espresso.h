// Filename: espresso.h

#ifndef ESPRESSO_H
#define ESPRESSO_H

#include <stdio.h>

#include "utility.h"
#include "sparse.h"

/*-----THIS USED TO BE set.h----- */

//
// set.h -- definitions for packed arrays of bits
//
// This header file describes the data structures which comprise a
// facility for efficiently implementing packed arrays of bits
// (otherwise known as sets, cf. Pascal).
//
// A set is a vector of bits and is implemented here as an array of
// unsigned integers.  The low order bits of set[0] give the index of
// the last word of set data.  The higher order bits of set[0] are
// used to store data associated with the set.  The set data is
// contained in elements set[1] ... set[LOOP(set)] as a packed bit
// array.
//
// A family of sets is a two-dimensional matrix of bits and is
// implemented with the data type "set_family".
//

// bits per integer
#define BPI 32
#define LOGBPI 5

/* Define the set type */
typedef unsigned int set;

/* Define the set family type -- an array of sets */
typedef struct set_family {
    int wsize;                  /* Size of each set in 'ints' */
    int sf_size;                /* User declared set size */
    int capacity;               /* Number of sets allocated */
    int count;                  /* The number of sets in the family */
    int active_count;           /* Number of "active" sets */
    set *data;                  /* Pointer to the set data */
    struct set_family *next;    /* For garbage collection */
} set_family_t;

/* Macros to set and test single elements */
#define WHICH_WORD(element)     (((element) >> LOGBPI) + 1)
#define WHICH_BIT(element)      ((element) & (BPI-1))

/* # of ints needed to allocate a set with "size" elements */
#define SET_SIZE(size) ((size) <= BPI ? 2 : (WHICH_WORD((size)-1) + 1))

/*
 *  Three fields are maintained in the first word of the set
 *      LOOP is the index of the last word used for set data
 *      SIZE is available for general use (e.g., recording # elements in set)
 *      NELEM retrieves the number of elements in the set
 */
#define LOOP(set)               (set[0] & 0x03ff)
#define PUTLOOP(set, i)         (set[0] &= ~0x03ff, set[0] |= (i))
#define SIZE(set)               (set[0] >> 16)
#define PUTSIZE(set, size)      (set[0] &= 0xffff, set[0] |= ((size) << 16))

#define NELEM(set)              (BPI * LOOP(set))
#define LOOPINIT(size)          ((size <= BPI) ? 1 : WHICH_WORD((size)-1))

// FLAGS store general information about the set
#define SET(set, flag)      (set[0] |= (flag))
#define RESET(set, flag)    (set[0] &= ~ (flag))
#define TESTP(set, flag)    (set[0] & (flag))

// Flag definitions
#define PRIME       0x8000  // cube is prime
#define NONESSEN    0x4000  // cube cannot be essential prime
#define ACTIVE      0x2000  // cube is still active
#define REDUND      0x1000  // cube is redundant(at this point)
#define COVERED     0x0800  // cube has been covered
#define RELESSEN    0x0400  // cube is relatively essential

/* Most efficient way to look at all members of a set family */
#define foreach_set(R, last, p)                                                \
    for(p=R->data,last=p+R->count*R->wsize;p<last;p+=R->wsize)
#define foreach_remaining_set(R, last, pfirst, p)                              \
    for(p=pfirst+R->wsize,last=R->data+R->count*R->wsize;p<last;p+=R->wsize)
#define foreach_active_set(R, last, p)                                         \
    foreach_set(R,last,p) if (TESTP(p, ACTIVE))

/* Another way that also keeps the index of the current set member in i */
#define foreachi_set(R, i, p)                                                  \
    for(p=R->data,i=0;i<R->count;p+=R->wsize,i++)
#define foreachi_active_set(R, i, p)                                           \
    foreachi_set(R,i,p) if (TESTP(p, ACTIVE))

/* Looping over all elements in a set:
 *      foreach_set_element(set *p, int i, unsigned val, int base) {
 *          ...
 *      }
 */
#define foreach_set_element(p, i, val, base)                                   \
    for (i = LOOP(p); i > 0; )                                                 \
    for (val = p[i], base = --i << LOGBPI; val != 0; base++, val >>= 1)        \
        if (val & 1)

// Return a pointer to a given member of a set family
#define GETSET(family, index)   ((family)->data + (family)->wsize * (index))

// Allocate and deallocate sets
#define set_new(size)   set_clear(ALLOC(unsigned int, SET_SIZE(size)), size)
#define set_full(size)  set_fill(ALLOC(unsigned int, SET_SIZE(size)), size)
#define set_save(r)     set_copy(ALLOC(unsigned int, SET_SIZE(NELEM(r))), r)
#define set_free(r)     FREE(r)

// Check for set membership, remove set element and insert set element
#define is_in_set(set, e)   (set[WHICH_WORD(e)] &   (1 << WHICH_BIT(e)))
#define set_insert(set, e)  (set[WHICH_WORD(e)] |=  (1 << WHICH_BIT(e)))
#define set_remove(set, e)  (set[WHICH_WORD(e)] &= ~(1 << WHICH_BIT(e)))

#define count_ones(v)                                                          \
    ( bit_count[v & 255]                                                       \
    + bit_count[(v >>  8) & 255]                                               \
    + bit_count[(v >> 16) & 255]                                               \
    + bit_count[(v >> 24) & 255] )

// Table for efficient bit counting
extern int bit_count[256];

/*----- END OF set.h ----- */

// Define a boolean type
#define bool  int
#define FALSE 0
#define TRUE  1
#define MAYBE 2
#define print_bool(x) ((x) == 0 ? "FALSE" : ((x) == 1 ? "TRUE" : "MAYBE"))

// Map many cube/cover types/routines into equivalent set types/routines
#define free_cubelist(T) FREE(T[0]); FREE(T);

// cost_t describes the cost of a cover
typedef struct cost_struct {
    int cubes;      // number of cubes in the cover
    int in;         // transistor count, binary-valued variables
    int out;        // transistor count, output part
    int mv;         // transistor count, multiple-valued vars
    int total;      // total number of transistors
    int primes;     // number of prime cubes
} cost_t;

// pair_t describes bit-paired variables
typedef struct pair_struct {
    int cnt;
    int *var1;
    int *var2;
} pair_t;

// symbolic_list_t describes a single ".symbolic" line
typedef struct symbolic_list_struct {
    int variable;
    int pos;
    struct symbolic_list_struct *next;
} symbolic_list_t;

// symbolic_list_t describes a single ".symbolic" line
typedef struct symbolic_label_struct {
    char *label;
    struct symbolic_label_struct *next;
} symbolic_label_t;

// symbolic_t describes a linked list of ".symbolic" lines
typedef struct symbolic_struct {
    symbolic_list_t *symbolic_list;     // linked list of items
    int symbolic_list_length;           // length of symbolic_list list
    symbolic_label_t *symbolic_label;   // linked list of new names
    int symbolic_label_length;          // length of symbolic_label list
    struct symbolic_struct *next;
} symbolic_t;

// PLA_t stores the logical representation of a PLA
typedef struct {
    set_family_t *F, *D, *R;        // on-set, off-set and dc-set
    char *filename;                 // filename
    int pla_type;                   // logical PLA format
    set *phase;                     // phase to split into on-set and off-set
    pair_t *pair;                   // how to pair variables
    char **label;                   // labels for the columns
    symbolic_t *symbolic;           // allow binary->symbolic mapping
    symbolic_t *symbolic_output;    // allow symbolic output mapping
} PLA_t;

#define equal(a,b) (strcmp(a,b) == 0)

/* This is a hack which I wish I hadn't done, but too painful to change */
#define CUBELISTSIZE(T) (((set **) T[1] - T) - 3)

/* The pla_type field describes the input and output format of the PLA */
#define F_type          1
#define D_type          2
#define R_type          4
#define PLEASURE_type   8               /* output format */
#define EQNTOTT_type    16              /* output format algebraic eqns */
#define KISS_type       128             /* output format kiss */
#define CONSTRAINTS_type    256         /* output the constraints (numeric) */
#define SYMBOLIC_CONSTRAINTS_type   512 /* output the constraints (symbolic) */
#define FD_type (F_type | D_type)
#define FR_type (F_type | R_type)
#define DR_type (D_type | R_type)
#define FDR_type (F_type | D_type | R_type)

/* Definitions for the debug variable */
#define COMPL           0x0001
#define ESSEN           0x0002
#define EXPAND          0x0004
#define EXPAND1         0x0008
#define GASP            0x0010
#define IRRED           0x0020
#define REDUCE          0x0040
#define REDUCE1         0x0080
#define SPARSE          0x0100
#define TAUT            0x0200
#define EXACT           0x0400
#define MINCOV          0x0800
#define MINCOV1         0x1000
#define SHARP           0x2000
#define IRRED1          0x4000

#define VERSION "UC Berkeley, Espresso Version #2.3, Release date 01/31/88"

#define POSITIVE_PHASE(pos)\
    (is_in_set(PLA->phase, CUBE.first_part[CUBE.output]+pos) != 0)

#define INLABEL(var)    PLA->label[CUBE.first_part[var] + 1]
#define OUTLABEL(pos)   PLA->label[CUBE.first_part[CUBE.output] + pos]

#define GETINPUT(c, pos)                                                       \
    ((c[WHICH_WORD(2*pos)] >> WHICH_BIT(2*pos)) & 3)
#define GETOUTPUT(c, pos)                                                      \
    (is_in_set(c, CUBE.first_part[CUBE.output] + pos) != 0)

#define PUTINPUT(c, pos, value)\
    c[WHICH_WORD(2*pos)] = (c[WHICH_WORD(2*pos)] & ~(3 << WHICH_BIT(2*pos)))   \
                         | (value << WHICH_BIT(2*pos))
#define PUTOUTPUT(c, pos, value)\
    c[WHICH_WORD(pos)] = (c[WHICH_WORD(pos)] & (1 << WHICH_BIT(pos)))          \
                       | (value << WHICH_BIT(pos))

#define TWO  3
#define DASH 3
#define ONE  2
#define ZERO 1

//
// Global Variable Declarations
//

extern unsigned int debug;              /* debug parameter */
extern bool verbose_debug;              /* -v:  whether to print a lot */

extern bool echo_comments;              /* turned off by -eat option */
extern bool echo_unknown_commands;      /* always true ?? */
extern bool force_irredundant;          /* -nirr command line option */
extern bool skip_make_sparse;
extern bool kiss;                       /* -kiss command line option */
extern bool pos;                        /* -pos command line option */
extern bool print_solution;             /* -x command line option */
extern bool recompute_onset;            /* -onset command line option */
extern bool remove_essential;           /* -ness command line option */
extern bool single_expand;              /* -fast command line option */
extern bool unwrap_onset;               /* -nunwrap command line option */
extern bool use_random_order;           /* -random command line option */
extern bool use_super_gasp;             /* -strong command line option */
extern char *filename;                  /* filename PLA was read from */
extern bool debug_exact_minimization;   /* dumps info for -do exact */

/*
 *  pla_types are the input and output types for reading/writing a PLA
 */
struct pla_types_struct {
    char *key;
    int value;
};

/*
 *  The cube structure is a global structure which contains information
 *  on how a set maps into a cube -- i.e., number of parts per variable,
 *  number of variables, etc.  Also, many fields are pre-computed to
 *  speed up various primitive operations.
 */
#define CUBE_TEMP 10

struct cube_struct {
    int size;                   /* set size of a cube */
    int num_vars;               /* number of variables in a cube */
    int num_binary_vars;        /* number of binary variables */
    int *first_part;            /* first element of each variable */
    int *last_part;             /* first element of each variable */
    int *part_size;             /* number of elements in each variable */
    int *first_word;            /* first word for each variable */
    int *last_word;             /* last word for each variable */
    set *binary_mask;           /* Mask to extract binary variables */
    set *mv_mask;               /* mask to get mv parts */
    set **var_mask;             /* mask to extract a variable */
    set **temp;                 /* an array of temporary sets */
    set *fullset;               /* a full cube */
    set *emptyset;              /* an empty cube */
    unsigned int inmask;        /* mask to get odd word of binary part */
    int inword;                 /* which word number for above */
    int *sparse;                /* should this variable be sparse? */
    int num_mv_vars;            /* number of multiple-valued variables */
    int output;                 /* which variable is "output" (-1 if none) */
};

struct cdata_struct {
    int *part_zeros;            /* count of zeros for each element */
    int *var_zeros;             /* count of zeros for each variable */
    int *parts_active;          /* number of "active" parts for each var */
    bool *is_unate;             /* indicates given var is unate */
    int vars_active;            /* number of "active" variables */
    int vars_unate;             /* number of unate variables */
    int best;                   /* best "binate" variable */
};

extern struct pla_types_struct pla_types[];
extern struct cube_struct CUBE;
extern struct cdata_struct CDATA;

#define DISJOINT 0x55555555

// function declarations

// cofactor.c
int binate_split_select(set **T, set *cleft, set *cright, int debug_flag);
set_family_t *cubeunlist(set **A1);
set **cofactor(set **T, set *c);
set **cube1list(set_family_t *A);
set **cube2list(set_family_t *A, set_family_t *B);
set **cube3list(set_family_t *A, set_family_t *B, set_family_t *C);
set **scofactor(set **T, set *c, int var);
void massive_count(set **T);

// compl.c
set_family_t *complement(set **T);
set_family_t *simplify(set **T);
void simp_comp(set **T, set_family_t **Tnew, set_family_t **Tbar);

// contain.c
int d1_rm_equal(set **A1, int (*compare)(set **, set**));
int rm2_contain(set **A1, set **B1);
int rm2_equal(set **A1, set **B1, set **E1, int (*compare)(set **, set**));
int rm_contain(set **A1);
int rm_equal(set **A1, int (*compare)(set **, set**));
int rm_rev_contain(set **A1);
set **sf_list(set_family_t *A);
set **sf_sort(set_family_t *A, int (*compare)(set **, set **));
set_family_t *d1merge(set_family_t *A, int var);
set_family_t *dist_merge(set_family_t *A, set *mask);
set_family_t *sf_contain(set_family_t *A);
set_family_t *sf_dupl(set_family_t *A);
set_family_t *sf_ind_contain(set_family_t *A, int *row_indices);
set_family_t *sf_ind_unlist(set **A1, int totcnt, int size, int *row_indices, set *pfirst);
set_family_t *sf_merge(set **A1, set **B1, set **E1, int totcnt, int size);
set_family_t *sf_rev_contain(set_family_t *A);
set_family_t *sf_union(set_family_t *A, set_family_t *B);
set_family_t *sf_unlist(set **A1, int totcnt, int size);

// cubestr.c
void cube_setup(void);
void cube_setdown(void);

// cvrin.c
void PLA_labels(PLA_t *PLA);
char *get_word(FILE *fp, char *word);
int label_index(PLA_t *PLA, char *word, int *varp, int *ip);
int read_pla(FILE *fp, bool needs_dcset, bool needs_offset, int pla_type, PLA_t **PLA_return);
int read_symbolic(FILE *fp, PLA_t *PLA, char *word, symbolic_t **retval);
PLA_t *new_PLA(void);
void PLA_summary(PLA_t *PLA);
void free_PLA(PLA_t *PLA);
void parse_pla(FILE *fp, PLA_t *PLA);
void read_cube(FILE *fp, PLA_t *PLA);
void skip_line(FILE *fpin, FILE *fpout, bool echo);

// cvrm.c
void foreach_output_function(PLA_t *PLA, int (*func)(PLA_t *, int), int (*func1)(PLA_t *, int));
int cubelist_partition(set **T, set ***A, set ***B, unsigned int comp_debug);
int so_both_do_espresso(PLA_t *PLA, int i);
int so_both_do_exact(PLA_t *PLA, int i);
int so_both_save(PLA_t *PLA, int i);
int so_do_espresso(PLA_t *PLA, int i);
int so_do_exact(PLA_t *PLA, int i);
int so_save(PLA_t *PLA, int i);
set_family_t *cof_output(set_family_t *T, int i);
set_family_t *lex_sort(set_family_t *T);
set_family_t *mini_sort(set_family_t *F, int (*compare)(set **, set**));
set_family_t *random_order(set_family_t *F);
set_family_t *size_sort(set_family_t *T);
set_family_t *sort_reduce(set_family_t *T);
set_family_t *uncof_output(set_family_t *T, int i);
set_family_t *unravel(set_family_t *B, int start);
set_family_t *unravel_range(set_family_t *B, int start, int end);
void so_both_espresso(PLA_t *PLA, int strategy);
void so_espresso(PLA_t *PLA, int strategy);

// cvrmisc.c
char *fmt_cost(cost_t *cost);
char *print_cost(set_family_t *F);
void copy_cost(cost_t *s, cost_t *d);
void cover_cost(set_family_t *F, cost_t *cost);
void fatal(char *s);

// cvrout.c
char *fmt_cube(set *c, char *out_map, char *s);
char *pc1(set *c);
char *pc2(set *c);
void makeup_labels(PLA_t *PLA);
void kiss_output(FILE *fp, PLA_t *PLA);
void kiss_print_cube(FILE *fp, PLA_t *PLA, set *p, char *out_string);
void output_symbolic_constraints(FILE *fp, PLA_t *PLA, int output_symbolic);
void cprint(set_family_t *T);
void debug1_print(set_family_t *T, char *name, int num);
void debug_print(set **T, char *name, int level);
void eqn_output(PLA_t *PLA);
void fpr_header(FILE *fp, PLA_t *PLA, int output_type);
void fprint_pla(FILE *fp, PLA_t *PLA, int output_type);
void pls_group(PLA_t *PLA, FILE *fp);
void pls_label(PLA_t *PLA, FILE *fp);
void pls_output(PLA_t *PLA);
void print_cube(FILE *fp, set *c, char *out_map);
void print_expanded_cube(FILE *fp, set *c, set *phase);

// espresso.c
set_family_t *espresso(set_family_t *F, set_family_t *D1, set_family_t *R);

// essen.c
bool essen_cube(set_family_t *F, set_family_t *D, set *c);
set_family_t *cb_consensus(set_family_t *T, set *c);
set_family_t *cb_consensus_dist0(set_family_t *R, set *p, set *c);
set_family_t *essential(set_family_t **Fp, set_family_t **Dp);

// exact.c
set_family_t *minimize_exact(set_family_t *F, set_family_t *D, set_family_t *R, int exact_cover);
set_family_t *minimize_exact_literals(set_family_t *F, set_family_t *D, set_family_t *R, int exact_cover);

// expand.c
bool feasibly_covered(set_family_t *BB, set *c, set *RAISE, set *new_lower);
int most_frequent(set_family_t *CC, set *FREESET);
set_family_t *all_primes(set_family_t *F, set_family_t *R);
set_family_t *expand(set_family_t *F, set_family_t *R, bool nonsparse);
set_family_t *find_all_primes(set_family_t *BB, set *RAISE, set *FREESET);
void elim_lowering(set_family_t *BB, set_family_t *CC, set *RAISE, set *FREESET);
void essen_parts(set_family_t *BB, set_family_t *CC, set *RAISE, set *FREESET);
void essen_raising(set_family_t *BB, set *RAISE, set *FREESET);
void expand1(set_family_t *BB, set_family_t *CC, set *RAISE, set *FREESET,
             set *OVEREXPANDED_CUBE, set *SUPER_CUBE, set *INIT_LOWER,
             int *num_covered, set *c);
void mincov(set_family_t *BB, set *RAISE, set *FREESET);
void select_feasible(set_family_t *BB, set_family_t *CC, set *RAISE, set *FREESET, set *SUPER_CUBE, int *num_covered);
void setup_BB_CC(set_family_t *BB, set_family_t *CC);

// gasp.c
set_family_t *expand_gasp(set_family_t *F, set_family_t *D, set_family_t *R, set_family_t *Foriginal);
set_family_t *irred_gasp(set_family_t *F, set_family_t *D, set_family_t *G);
set_family_t *last_gasp(set_family_t *F, set_family_t *D, set_family_t *R, cost_t *cost);
set_family_t *super_gasp(set_family_t *F, set_family_t *D, set_family_t *R, cost_t *cost);
void expand1_gasp(set_family_t *F, set_family_t *D, set_family_t *R, set_family_t *Foriginal, int c1index, set_family_t **G);

// hack.c
void find_inputs(set_family_t *A, PLA_t *PLA, symbolic_list_t *list, int base, int value, set_family_t **newF, set_family_t **newD);
void form_bitvector(set *p, int base, int value, symbolic_list_t *list);
void map_dcset(PLA_t *PLA);
void map_output_symbolic(PLA_t *PLA);
void map_symbolic(PLA_t *PLA);
set_family_t *map_symbolic_cover(set_family_t *T, symbolic_list_t *list, int base);
void symbolic_hack_labels(PLA_t *PLA, symbolic_t *list, set *compress, int new_size, int old_size, int size_added);

// irred.c
bool cube_is_covered(set **T, set *c);
bool taut_special_cases(set **T);
bool tautology(set **T);
set_family_t *irredundant(set_family_t *F, set_family_t *D);
void mark_irredundant(set_family_t *F, set_family_t *D);
void irred_split_cover(set_family_t *F, set_family_t *D, set_family_t **E, set_family_t **Rt, set_family_t **Rp);
sm_matrix *irred_derive_table(set_family_t *D, set_family_t *E, set_family_t *Rp);

// mincov.c
sm_row *sm_minimum_cover(sm_matrix *A, int *weight, int heuristic, int debug_level);

// opo.c
void output_phase_setup(PLA_t *PLA, int first_output);
PLA_t *set_phase(PLA_t *PLA);
set_family_t *opo(set *phase, set_family_t *T, set_family_t *D, set_family_t *R, int first_output);
set *find_phase(PLA_t *PLA, int first_output, set *phase1);
set_family_t *opo_leaf(set_family_t *T, set *select, int out1, int out2);
set_family_t *opo_recur(set_family_t *T, set_family_t *D, set *select, int offset, int first, int last);
void opoall(PLA_t *PLA, int first_output, int last_output, int opo_strategy);
void phase_assignment(PLA_t *PLA, int opo_strategy);
void repeated_phase_assignment(PLA_t *PLA);

// pair.c
void generate_all_pairs(pair_t *pair, int n, set *candidate, void (*action)(pair_t *));
int **find_pairing_cost(PLA_t *PLA, int strategy);
void find_best_cost(pair_t *pair);
int greedy_best_cost(int **cost_array_local, pair_t **pair_p);
void minimize_pair(pair_t *pair);
void pair_free(pair_t *pair);
void pair_all(PLA_t *PLA, int pair_strategy);
set_family_t *delvar(set_family_t *A, bool *paired);
set_family_t *pairvar(set_family_t *A, pair_t *pair);
pair_t *pair_best_cost(int **cost_array_local);
pair_t *pair_new(int n);
pair_t *pair_save(pair_t *pair, int n);
void print_pair(pair_t *pair);
void find_optimal_pairing(PLA_t *PLA, int strategy);
void set_pair(PLA_t *PLA);
void set_pair1(PLA_t *PLA, bool adjust_labels);

// primes.c
set_family_t *primes_consensus(set **T);

// reduce.c
bool sccc_special_cases(set **T, set **result);
set_family_t *reduce(set_family_t *F, set_family_t *D);
set *reduce_cube(set **FD, set *p);
set *sccc(set **T);
set *sccc_cube(set *result, set *p);
set *sccc_merge(set *left, set *right, set *cl, set *cr);

#include "set.h"

// setc.c
bool ccommon(set *a, set *b, set *cof);
bool cdist0(set *a, set *b);
bool full_row(set *p, set *cof);
int ascend(set **a, set **b);
int cactive(set *a);
int cdist(set *a, set *b);
int cdist01(set *a, set *b);
int d1_order(set **a, set **b);
int desc1(set *a, set *b);
int descend(set **a, set **b);
int lex_order(set **a, set **b);
set *force_lower(set *xlower, set *a, set *b);
void consensus(set *r, set *a, set *b);

// sharp.c
set_family_t *cb1_dsharp(set_family_t *T, set *c);
set_family_t *cb_dsharp(set *c, set_family_t *T);
set_family_t *cb_recur_sharp(set *c, set_family_t *T, int first, int last, int level);
set_family_t *cb_sharp(set *c, set_family_t *T);
set_family_t *cv_dsharp(set_family_t *A, set_family_t *B);
set_family_t *cv_intersect(set_family_t *A, set_family_t *B);
set_family_t *cv_sharp(set_family_t *A, set_family_t *B);
set_family_t *dsharp(set *a, set *b);
set_family_t *make_disjoint(set_family_t *A);
set_family_t *sharp(set *a, set *b);

// sminterf.c
set *do_sm_minimum_cover(set_family_t *A);

// sparse.c
set_family_t *make_sparse(set_family_t *F, set_family_t *D, set_family_t *R);
set_family_t *mv_reduce(set_family_t *F, set_family_t *D);

// unate.c
set_family_t *map_cover_to_unate(set **T);
set_family_t *map_unate_to_cover(set_family_t *A);
set_family_t *exact_minimum_cover(set_family_t *T);
set_family_t *unate_compl(set_family_t *A);
set_family_t *unate_complement(set_family_t *A);
set_family_t *unate_intersect(set_family_t *A, set_family_t *B, bool largest_only);

// verify.c
void PLA_permute(PLA_t *PLA1, PLA_t *PLA2);
bool PLA_verify(PLA_t *PLA1, PLA_t *PLA2);
bool check_consistency(PLA_t *PLA);
bool verify(set_family_t *F, set_family_t *Fold, set_family_t *Dold);

#endif // ESPRESSO_H

