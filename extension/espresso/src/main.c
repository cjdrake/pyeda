// Filename: main.c

#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "espresso.h"
#include "main.h"

static FILE *last_fp;
static int input_type = FD_type;

void
subcommands()
{
    int i, col;
    printf("                ");
    col = 16;
    for(i = 0; option_table[i].name != 0; i++) {
        if ((col + strlen(option_table[i].name) + 1) > 76) {
            printf(",\n                ");
            col = 16;
        } else if (i != 0) {
            printf(", ");
        }
        printf("%s", option_table[i].name);
        col += strlen(option_table[i].name) + 2;
    }
    printf("\n");
}

void
usage()
{
    printf("%s\n\n", VERSION);
    printf("SYNOPSIS: espresso [options] [file]\n\n");
    printf("  -d        Enable debugging\n");
    printf("  -e[opt]   Select espresso option:\n");
    printf("                fast, ness, nirr, nunwrap, onset, pos, strong,\n");
    printf("                eat, eatdots, kiss, random\n");
    printf("  -o[type]  Select output format:\n");
    printf("                f, fd, fr, fdr, pleasure, eqntott, kiss, cons\n");
    printf("  -rn-m     Select range for subcommands:\n");
    printf("                d1merge: first and last variables (0 ... m-1)\n");
    printf("                minterms: first and last variables (0 ... m-1)\n");
    printf("                opoall: first and last outputs (0 ... m-1)\n");
    printf("  -x        Suppress printing of solution\n");
    printf("  -v[type]  Verbose debugging detail (-v '' for all)\n");
    printf("  -D[cmd]   Execute subcommand 'cmd':\n");
    subcommands();
    printf("  -Sn       Select strategy for subcommands:\n");
    printf("                opo: bit2=exact bit1=repeated bit0=skip sparse\n");
    printf("                opoall: 0=minimize, 1=exact\n");
    printf("                pair: 0=algebraic, 1=strongd, 2=espresso, 3=exact\n");
    printf("                pairall: 0=minimize, 1=exact, 2=opo\n");
    printf("                so_espresso: 0=minimize, 1=exact\n");
    printf("                so_both: 0=minimize, 1=exact\n");
}

void
getPLA(int opt, int argc, char **argv, int option, PLA_t **PLA, int out_type)
{
    FILE *fp;
    int needs_dcset, needs_offset;
    char *fname;

    if (opt >= argc) {
        fp = stdin;
        fname = "(stdin)";
    } else {
        fname = argv[opt];
        if (strcmp(fname, "-") == 0) {
            fp = stdin;
        } else if ((fp = fopen(argv[opt], "r")) == NULL) {
            fprintf(stderr, "%s: Unable to open %s\n", argv[0], fname);
            exit(1);
        }
    }
    if (option_table[option].key == KEY_echo) {
        needs_dcset = (out_type & D_type) != 0;
        needs_offset = (out_type & R_type) != 0;
    } else {
        needs_dcset = option_table[option].needs_dcset;
        needs_offset = option_table[option].needs_offset;
    }

    if (read_pla(fp, needs_dcset, needs_offset, input_type, PLA) == EOF) {
        fprintf(stderr, "%s: Unable to find PLA on file %s\n", argv[0], fname);
        exit(1);
    }
    (*PLA)->filename = strdup(fname);
    filename = (*PLA)->filename;
    last_fp = fp;
}

// delete_arg -- delete an argument from the argument list
void
delete_arg(int *argc, char **argv, int num)
{
    int i;

    (*argc)--;
    for (i = num; i < *argc; i++)
        argv[i] = argv[i+1];
}

// check_arg -- scan argv for an argument, and return TRUE if found
bool
check_arg(int *argc, char **argv, char *s)
{
    int i;
    for (i = 1; i < *argc; i++) {
        if (strcmp(argv[i], s) == 0) {
            delete_arg(argc, argv, i);
            return TRUE;
        }
    }
    return FALSE;
}

// Hack for backward compatibility (ACK! )
void
backward_compatibility_hack(int *argc, char **argv, int *option, int *out_type)
{
    int i, j;

    /* Scan the argument list for something to do (default is ESPRESSO) */
    *option = 0;
    for (i = 1; i < (*argc)-1; i++) {
        if (strcmp(argv[i], "-do") == 0) {
            for (j = 0; option_table[j].name != 0; j++)
                if (strcmp(argv[i+1], option_table[j].name) == 0) {
                    *option = j;
                    delete_arg(argc, argv, i+1);
                    delete_arg(argc, argv, i);
                    break;
                }
                if (option_table[j].name == 0) {
                    fprintf(stderr,
                            "espresso: bad keyword \"%s\" following -do\n",argv[i+1]);
                    exit(1);
                }
                break;
        }
    }

    for(i = 1; i < (*argc)-1; i++) {
        if (strcmp(argv[i], "-out") == 0) {
            for (j = 0; pla_types[j].key != 0; j++)
                if (strcmp(pla_types[j].key+1, argv[i+1]) == 0) {
                    *out_type = pla_types[j].value;
                    delete_arg(argc, argv, i+1);
                    delete_arg(argc, argv, i);
                    break;
                }
                if (pla_types[j].key == 0) {
                    fprintf(stderr,
                            "espresso: bad keyword \"%s\" following -out\n",argv[i+1]);
                    exit(1);
                }
                break;
        }
    }

    for(i = 1; i < (*argc); i++) {
        if (argv[i][0] == '-') {
            for (j = 0; esp_opt_table[j].name != 0; j++) {
                if (strcmp(argv[i]+1, esp_opt_table[j].name) == 0) {
                    delete_arg(argc, argv, i);
                    *(esp_opt_table[j].variable) = esp_opt_table[j].value;
                    break;
                }
            }
        }
    }

    if (check_arg(argc, argv, "-fdr")) input_type = FDR_type;
    if (check_arg(argc, argv, "-fr")) input_type = FR_type;
    if (check_arg(argc, argv, "-f")) input_type = F_type;
}

int
main(int argc, char **argv)
{
    int i, j, first, last, strategy, out_type, option;
    PLA_t *PLA, *PLA1;
    set_family_t *F, *Fold, *Dold;
    set *last1, *p;
    cost_t cost;
    bool error, exact_cover;
    extern char *optarg;
    extern int optind;

    error = FALSE;
#ifdef RANDOM
    srandom(314973);
#endif

    option = 0;			/* default -D: ESPRESSO */
    out_type = F_type;		/* default -o: default is ON-set only */
    debug = 0;			/* default -d: no debugging info */
    verbose_debug = FALSE;	/* default -v: not verbose */
    print_solution = TRUE;	/* default -x: print the solution (!) */
    strategy = 0;		/* default -S: strategy number */
    first = -1;			/* default -R: select range */
    last = -1;
    remove_essential = TRUE;	/* default -e: */
    force_irredundant = TRUE;
    unwrap_onset = TRUE;
    single_expand = FALSE;
    pos = FALSE;
    recompute_onset = FALSE;
    use_super_gasp = FALSE;
    use_random_order = FALSE;
    kiss = FALSE;
    echo_comments = TRUE;
    echo_unknown_commands = TRUE;
    exact_cover = FALSE;	/* for -qm option, the default */

    backward_compatibility_hack(&argc, argv, &option, &out_type);

    /* parse command line options*/
    while ((i = getopt(argc, argv, "D:S:de:o:r:stv:x")) != EOF) {
	switch(i) {
	    case 'D':		/* -Dcommand invokes a subcommand */
		for(j = 0; option_table[j].name != 0; j++) {
		    if (strcmp(optarg, option_table[j].name) == 0) {
			option = j;
			break;
		    }
		}
		if (option_table[j].name == 0) {
		    fprintf(stderr, "%s: bad subcommand \"%s\"\n",
			argv[0], optarg);
		    exit(1);
		}
		break;

	    case 'o':		/* -ooutput selects and output option */
		for(j = 0; pla_types[j].key != 0; j++) {
		    if (strcmp(optarg, pla_types[j].key+1) == 0) {
			out_type = pla_types[j].value;
			break;
		    }
		}
		if (pla_types[j].key == 0) {
		    fprintf(stderr, "%s: bad output type \"%s\"\n",
			argv[0], optarg);
		    exit(1);
		}
		break;

	    case 'e':		/* -eespresso selects an option for espresso */
		for(j = 0; esp_opt_table[j].name != 0; j++) {
		    if (strcmp(optarg, esp_opt_table[j].name) == 0) {
			*(esp_opt_table[j].variable) = esp_opt_table[j].value;
			break;
		    }
		}
		if (esp_opt_table[j].name == 0) {
		    fprintf(stderr, "%s: bad espresso option \"%s\"\n",
			argv[0], optarg);
		    exit(1);
		}
		break;

	    case 'd':		/* -d turns on (softly) all debug switches */
		debug = debug_table[0].value;
		break;

	    case 'v':		/* -vdebug invokes a debug option */
		verbose_debug = TRUE;
		for(j = 0; debug_table[j].name != 0; j++) {
		    if (strcmp(optarg, debug_table[j].name) == 0) {
			debug |= debug_table[j].value;
			break;
		    }
		}
		if (debug_table[j].name == 0) {
		    fprintf(stderr, "%s: bad debug type \"%s\"\n",
			argv[0], optarg);
		    exit(1);
		}
		break;

	    case 'x':		/* -x suppress printing of results */
		print_solution = FALSE;
		break;

	    case 'S':		/* -S sets a strategy for several cmds */
		strategy = atoi(optarg);
		break;

	    case 'r':		/* -r selects range (outputs or vars) */
		if (sscanf(optarg, "%d-%d", &first, &last) < 2) {
		    fprintf(stderr, "%s: bad output range \"%s\"\n",
			argv[0], optarg);
		    exit(1);
		}
		break;

	    default:
		usage();
		exit(1);
	}
    }

    /* the remaining arguments are argv[optind ... argc-1] */
    PLA = PLA1 = NIL(PLA_t);
    switch(option_table[option].num_plas) {
	case 2:
	    if (optind+2 < argc) fatal("trailing arguments on command line");
	    getPLA(optind++, argc, argv, option, &PLA, out_type);
	    getPLA(optind++, argc, argv, option, &PLA1, out_type);
	    break;
	case 1:
	    if (optind+1 < argc) fatal("trailing arguments on command line");
	    getPLA(optind++, argc, argv, option, &PLA, out_type);
	    break;
    }
    if (optind < argc) fatal("trailing arguments on command line");

    // Decide what to do
    switch(option_table[option].key) {

    case KEY_ESPRESSO:
        Fold = sf_save(PLA->F);
        PLA->F = espresso(PLA->F, PLA->D, PLA->R);
        error = verify(PLA->F, Fold, PLA->D);
        cover_cost(PLA->F, &cost);
        if (error) {
            print_solution = FALSE;
            PLA->F = Fold;
            check_consistency(PLA);
        } else {
            sf_free(Fold);
        }
        break;

    //case KEY_MANY_ESPRESSO: {
    //    int pla_type;
    //    do {
    //        PLA->F = espresso(PLA->F,PLA->D,PLA->R);
    //        if (print_solution) {
    //            fprint_pla(stdout, PLA, out_type);
    //            fflush(stdout);
    //        }
    //        pla_type = PLA->pla_type;
    //        free_PLA(PLA);
    //        cube_setdown();
    //        FREE(CUBE.part_size);
    //    } while (read_pla(last_fp, TRUE, TRUE, pla_type, &PLA) != EOF);
    //    exit(0);
    //}

    //case KEY_simplify:
    //    PLA->F = simplify(cube1list(PLA->F));
    //    break;

    //case KEY_so: // minimize all functions as single-output
    //    if (strategy < 0 || strategy > 1) {
    //        strategy = 0;
    //    }
    //    so_espresso(PLA, strategy);
    //    break;

    //case KEY_so_both: // minimize all functions as single-output
    //    if (strategy < 0 || strategy > 1) {
    //        strategy = 0;
    //    }
    //    so_both_espresso(PLA, strategy);
    //    break;

    //case KEY_expand: // execute expand
    //    PLA->F = expand(PLA->F,PLA->R,FALSE);
    //    cover_cost(PLA->F, &cost);
    //    break;

    //case KEY_irred: // extract minimal irredundant subset
    //    PLA->F = irredundant(PLA->F, PLA->D);
    //    cover_cost(PLA->F, &cost);
    //    break;

    //case KEY_reduce: // perform reduction
    //    PLA->F = reduce(PLA->F, PLA->D);
    //    cover_cost(PLA->F, &cost);
    //    break;

    //case KEY_essen: // check for essential primes
    //    foreach_set(PLA->F, last1, p) {
    //        SET(p, RELESSEN);
    //        RESET(p, NONESSEN);
    //    }
    //    F = essential(&(PLA->F), &(PLA->D));
    //    cover_cost(PLA->F, &cost);
    //    sf_free(F);
    //    break;

    //case KEY_super_gasp:
    //    PLA->F = super_gasp(PLA->F, PLA->D, PLA->R, &cost);
    //    break;

    //case KEY_gasp:
    //    PLA->F = last_gasp(PLA->F, PLA->D, PLA->R, &cost);
    //    break;

    //case KEY_make_sparse: // make_sparse step of Espresso
    //    PLA->F = make_sparse(PLA->F, PLA->D, PLA->R);
    //    break;

    //case KEY_exact:
    //    exact_cover = TRUE;

    case KEY_qm:
        Fold = sf_save(PLA->F);
        PLA->F = minimize_exact(PLA->F, PLA->D, PLA->R, exact_cover);
        error = verify(PLA->F, Fold, PLA->D);
        cover_cost(PLA->F, &cost);
        if (error) {
            print_solution = FALSE;
            PLA->F = Fold;
            check_consistency(PLA);
        }
        sf_free(Fold);
        break;

    //case KEY_primes: // generate all prime implicants
    //    PLA->F = primes_consensus(cube2list(PLA->F, PLA->D));
    //    break;

    //case KEY_map: // print out a Karnaugh map of function
    //    map(PLA->F);
    //    print_solution = FALSE;
    //    break;

    //case KEY_signature:
    //    Fold = sf_save(PLA->F);
    //    PLA->F = signature(PLA->F, PLA->D, PLA->R);
    //    error = verify(PLA->F, Fold, PLA->D);
    //    cover_cost(PLA->F, &cost);
    //    if (error) {
    //        print_solution = FALSE;
    //        PLA->F = Fold;
    //        check_consistency(PLA);
    //    } else {
    //        sf_free(Fold);
    //    }
    //    break;

    //case KEY_opo: // sasao output phase assignment
    //    phase_assignment(PLA, strategy);
    //    break;

    //case KEY_opoall: // try all phase assignments (!)
    //    if (first < 0 || first >= CUBE.part_size[CUBE.output]) {
    //        first = 0;
    //    }
    //    if (last < 0 || last >= CUBE.part_size[CUBE.output]) {
    //        last = CUBE.part_size[CUBE.output] - 1;
    //    }
    //    opoall(PLA, first, last, strategy);
    //    break;

    //case KEY_pair: // find an optimal pairing
    //    find_optimal_pairing(PLA, strategy);
    //    break;

    //case KEY_pairall: // try all pairings !!
    //    pair_all(PLA, strategy);
    //    break;

    //case KEY_echo: // echo the PLA
    //    break;

    //case KEY_taut: // tautology check
    //    printf("ON-set is%sa tautology\n", tautology(cube1list(PLA->F)) ? " " : " not ");
    //    print_solution = FALSE;
    //    break;

    //case KEY_contain: // single cube containment
    //    PLA->F = sf_contain(PLA->F);
    //    break;

    //case KEY_intersect: // cover intersection
    //    PLA->F = cv_intersect(PLA->F, PLA1->F);
    //    break;

    //case KEY_union: // cover union
    //    PLA->F = sf_union(PLA->F, PLA1->F);
    //    break;

    //case KEY_disjoint: // make cover disjoint
    //    PLA->F = make_disjoint(PLA->F);
    //    break;

    //case KEY_dsharp: // cover disjoint-sharp
    //    PLA->F = cv_dsharp(PLA->F, PLA1->F);
    //    break;

    //case KEY_sharp: // cover sharp
    //    PLA->F = cv_sharp(PLA->F, PLA1->F);
    //    break;

    //case KEY_lexsort: // lexical sort order
    //    PLA->F = lex_sort(PLA->F);
    //    break;

    //case KEY_stats: // print info on size
    //    if (! summary) PLA_summary(PLA);
    //    print_solution = FALSE;
    //    break;

    //case KEY_minterms: // explode into minterms
    //    if (first < 0 || first >= CUBE.num_vars) {
    //        first = 0;
    //    }
    //    if (last < 0 || last >= CUBE.num_vars) {
    //        last = CUBE.num_vars - 1;
    //    }
    //    PLA->F = sf_dupl(unravel_range(PLA->F, first, last));
    //    break;

    //case KEY_d1merge: // distance-1 merge
    //    if (first < 0 || first >= CUBE.num_vars) {
    //        first = 0;
    //    }
    //    if (last < 0 || last >= CUBE.num_vars) {
    //        last = CUBE.num_vars - 1;
    //    }
    //    for(i = first; i <= last; i++) {
    //        PLA->F = d1merge(PLA->F, i);
    //    }
    //    break;

    //case KEY_d1merge_in: // distance-1 merge inputs only
    //    for(i = 0; i < CUBE.num_binary_vars; i++) {
    //        PLA->F = d1merge(PLA->F, i);
    //    }
    //    break;

    //case KEY_PLA_verify: // check two PLAs for equivalence
    //    error = PLA_verify(PLA, PLA1);
    //    cover_cost(PLA->F, &cost);
    //    if (error) {
    //        printf("PLA comparison failed; the PLA's are not equivalent\n");
    //        exit(1);
    //    } else {
    //        printf("PLA's compared equal\n");
    //        exit(0);
    //    }
    //    break;

    //case KEY_verify: // check two covers for equivalence
    //    Fold = PLA->F;
    //    Dold = PLA->D;
    //    F = PLA1->F;
    //    error = verify(F, Fold, Dold);
    //    cover_cost(PLA->F, &cost);
    //    if (error) {
    //        printf("PLA comparison failed; the PLA's are not equivalent\n");
    //        exit(1);
    //    } else {
    //        printf("PLA's compared equal\n");
    //        exit(0);
    //    }
    //    break;

    //case KEY_check: // check consistency
    //    check_consistency(PLA);
    //    print_solution = FALSE;
    //    break;

    //case KEY_mapdc: // compute don't care set
    //    map_dcset(PLA);
    //    out_type = FD_type;
    //    break;

    //case KEY_equiv:
    //    find_equiv_outputs(PLA);
    //    print_solution = FALSE;
    //    break;

    //case KEY_separate: // remove PLA->D from PLA->F
    //    PLA->F = complement(cube2list(PLA->D, PLA->R));
    //    break;

    //case KEY_xor: {
    //    set_family_t *T1 = cv_intersect(PLA->F, PLA1->R);
    //    set_family_t *T2 = cv_intersect(PLA1->F, PLA->R);
    //    sf_free(PLA->F);
    //    PLA->F = sf_contain(sf_join(T1, T2));
    //    sf_free(T1);
    //    sf_free(T2);
    //    break;
    //}

    //case KEY_fsm: {
    //    disassemble_fsm(PLA);
    //    print_solution = FALSE;
    //    break;
    //}

    //case KEY_test: {
    //    set_family_t *T, *E;
    //    T = sf_join(PLA->D, PLA->R);
    //    E = sf_new(10, CUBE.size);
    //    sf_free(PLA->F);
    //    PLA->F = complement(cube1list(T));
    //    cover_cost(PLA->F, &cost);
    //    PLA->F = expand(PLA->F, T, FALSE);
    //    cover_cost(PLA->F, &cost);
    //    PLA->F = irredundant(PLA->F, E);
    //    cover_cost(PLA->F, &cost);
    //    sf_free(T);
    //    T = sf_join(PLA->F, PLA->R);
    //    PLA->D = expand(PLA->D, T, FALSE);
    //    cover_cost(PLA->D, &cost);
    //    PLA->D = irredundant(PLA->D, E);
    //    cover_cost(PLA->D, &cost);
    //    sf_free(T);
    //    sf_free(E);
    //    break;
    //}

    } // end switch

    /* Output the solution */
    if (print_solution) {
        fprint_pla(stdout, PLA, out_type);
        cover_cost(PLA->F, &cost);
    }

    /* Crash and burn if there was a verify error */
    if (error) {
        fatal("cover verification failed");
    }

    /* cleanup all used memory */
    free_PLA(PLA);
    FREE(CUBE.part_size);
    cube_setdown();             /* free the CUBE/CDATA structure data */
    sf_cleanup();               /* free unused set structures */
    sm_cleanup();               /* sparse matrix cleanup */

    return 0;
}

