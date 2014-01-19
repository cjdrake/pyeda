// Filename: cvrin.c
//
// purpose: cube and cover input routines
//

#include <ctype.h>
#include <string.h>

#include "espresso.h"

static bool line_length_error;
static int lineno;

void
skip_line(FILE *fpin, FILE *fpout, bool echo)
{
    int ch;
    while ((ch=getc(fpin)) != EOF && ch != '\n')
	if (echo)
	    putc(ch, fpout);
    if (echo)
	putc('\n', fpout);
    lineno++;
}

char *
get_word(FILE *fp, char *word)
{
    int ch, i = 0;
    while ((ch = getc(fp)) != EOF && isspace(ch))
	;
    word[i++] = ch;
    while ((ch = getc(fp)) != EOF && ! isspace(ch))
	word[i++] = ch;
    word[i++] = '\0';
    return word;
}

//
// Yes, I know this routine is a mess
//

void
read_cube(FILE *fp, PLA_t *PLA)
{
    int var, i;
    set *cf = CUBE.temp[0], *cr = CUBE.temp[1], *cd = CUBE.temp[2];
    bool savef = FALSE, saved = FALSE, saver = FALSE;
    char token[256];                // for kiss read hack
    int varx, first, last, offset;  // for kiss read hack

    set_clear(cf, CUBE.size);

    // Loop and read binary variables
    for (var = 0; var < CUBE.num_binary_vars; var++)
        switch(getc(fp)) {
        case EOF:
            goto bad_char;
        case '\n':
            if (! line_length_error)
                fprintf(stderr, "product term(s) %s\n",
                        "span more than one line (warning only)");
            line_length_error = TRUE;
            lineno++;
            var--;
            break;
        case ' ': case '|': case '\t':
            var--;
            break;
        case '2': case '-':
            set_insert(cf, var*2+1);
        case '0':
            set_insert(cf, var*2);
            break;
        case '1':
            set_insert(cf, var*2+1);
            break;
        case '?':
            break;
        default:
            goto bad_char;
        }

    /* Loop for the all but one of the multiple-valued variables */
    for(var = CUBE.num_binary_vars; var < CUBE.num_vars-1; var++)

	/* Read a symbolic multiple-valued variable */
	if (CUBE.part_size[var] < 0) {
	    fscanf(fp, "%s", token);
	    if (equal(token, "-") || equal(token, "ANY")) {
		if (kiss && var == CUBE.num_vars - 2) {
		    /* leave it empty */
		} else {
		    /* make it full */
		    set_or(cf, cf, CUBE.var_mask[var]);
		}
	    } else if (equal(token, "~")) {
		;
		/* leave it empty ... (?) */
	    } else {
		if (kiss && var == CUBE.num_vars - 2)
		    varx = var - 1, offset = ABS(CUBE.part_size[var-1]);
		else
		    varx = var, offset = 0;
		/* Find the symbolic label in the label table */
		first = CUBE.first_part[varx];
		last = CUBE.last_part[varx];
		for(i = first; i <= last; i++)
		    if (PLA->label[i] == (char *) NULL) {
			PLA->label[i] = strdup(token);	/* add new label */
			set_insert(cf, i+offset);
			break;
		    } else if (equal(PLA->label[i], token)) {
			set_insert(cf, i+offset);	/* use column i */
			break;
		    }
		if (i > last) {
		    fprintf(stderr,
"declared size of variable %d (counting from variable 0) is too small\n", var);
		    exit(-1);
		}
	    }

	} else for(i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++)
	    switch (getc(fp)) {
		case EOF:
		    goto bad_char;
		case '\n':
		    if (! line_length_error)
			fprintf(stderr, "product term(s) %s\n",
			    "span more than one line (warning only)");
		    line_length_error = TRUE;
		    lineno++;
		    i--;
		    break;
		case ' ': case '|': case '\t':
		    i--;
		    break;
		case '1':
		    set_insert(cf, i);
		case '0':
		    break;
		default:
		    goto bad_char;
	    }

    /* Loop for last multiple-valued variable */
    if (kiss) {
	saver = savef = TRUE;
	set_xor(cr, cf, CUBE.var_mask[CUBE.num_vars - 2]);
    } else
	set_copy(cr, cf);
    set_copy(cd, cf);
    for(i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++)
	switch (getc(fp)) {
	    case EOF:
		goto bad_char;
	    case '\n':
		if (! line_length_error)
		    fprintf(stderr, "product term(s) %s\n",
			"span more than one line (warning only)");
		line_length_error = TRUE;
		lineno++;
		i--;
		break;
	    case ' ': case '|': case '\t':
		i--;
		break;
	    case '4': case '1':
		if (PLA->pla_type & F_type)
		    set_insert(cf, i), savef = TRUE;
		break;
	    case '3': case '0':
		if (PLA->pla_type & R_type)
		    set_insert(cr, i), saver = TRUE;
		break;
	    case '2': case '-':
		if (PLA->pla_type & D_type)
		    set_insert(cd, i), saved = TRUE;
	    case '~':
		break;
	    default:
		goto bad_char;
	}
    if (savef) PLA->F = sf_addset(PLA->F, cf);
    if (saved) PLA->D = sf_addset(PLA->D, cd);
    if (saver) PLA->R = sf_addset(PLA->R, cr);
    return;

bad_char:
    fprintf(stderr, "(warning): input line #%d ignored\n", lineno);
    skip_line(fp, stdout, TRUE);
    return;
}

void
parse_pla(FILE *fp, PLA_t *PLA)
{
    int i, var, ch, np, last;
    char word[256];

    lineno = 1;
    line_length_error = FALSE;

loop:
    switch(ch = getc(fp)) {
    case EOF:
        return;

    case '\n':
        lineno++;

    case ' ': case '\t': case '\f': case '\r':
        break;

    case '#':
        ungetc(ch, fp);
        skip_line(fp, stdout, echo_comments);
        break;

    case '.':
        /* .i gives the cube input size (binary-functions only) */
        if (equal(get_word(fp, word), "i")) {
            if (CUBE.fullset != NULL) {
                fprintf(stderr, "extra .i ignored\n");
                skip_line(fp, stdout, /* echo */ FALSE);
            }
            else {
                if (fscanf(fp, "%d", &CUBE.num_binary_vars) != 1)
                    fatal("error reading .i");
                CUBE.num_vars = CUBE.num_binary_vars + 1;
                CUBE.part_size = ALLOC(int, CUBE.num_vars);
            }

        /* .o gives the cube output size (binary-functions only) */
        }
        else if (equal(word, "o")) {
            if (CUBE.fullset != NULL) {
                fprintf(stderr, "extra .o ignored\n");
                skip_line(fp, stdout, /* echo */ FALSE);
            }
            else {
                if (CUBE.part_size == NULL)
                    fatal(".o cannot appear before .i");
                if (fscanf(fp, "%d", &(CUBE.part_size[CUBE.num_vars-1]))!=1)
                    fatal("error reading .o");
                cube_setup();
                PLA_labels(PLA);
            }

            /* .mv gives the cube size for a multiple-valued function */
        }
        else if (equal(word, "mv")) {
            if (CUBE.fullset != NULL) {
                fprintf(stderr, "extra .mv ignored\n");
                skip_line(fp, stdout, /* echo */ FALSE);
            }
            else {
                if (CUBE.part_size != NULL)
                    fatal("cannot mix .i and .mv");
                if (fscanf(fp,"%d %d", &CUBE.num_vars,&CUBE.num_binary_vars) != 2)
                    fatal("error reading .mv");
                if (CUBE.num_binary_vars < 0)
                    fatal("num_binary_vars (second field of .mv) cannot be negative");
                if (CUBE.num_vars < CUBE.num_binary_vars)
                    fatal("num_vars (1st field of .mv) must exceed num_binary_vars (2nd field of .mv)");
                CUBE.part_size = ALLOC(int, CUBE.num_vars);
                for (var=CUBE.num_binary_vars; var < CUBE.num_vars; var++)
                if (fscanf(fp, "%d", &(CUBE.part_size[var])) != 1)
                    fatal("error reading .mv");
                cube_setup();
                PLA_labels(PLA);
            }

	    /* .p gives the number of product terms -- we ignore it */
	    } else if (equal(word, "p"))
		fscanf(fp, "%d", &np);
	    /* .e and .end specify the end of the file */
	    else if (equal(word, "e") || equal(word,"end"))
		return;
	    /* .kiss turns on the kiss-hack option */
	    else if (equal(word, "kiss"))
		kiss = TRUE;

	    /* .type specifies a logical type for the PLA */
	    else if (equal(word, "type")) {
		get_word(fp, word);
		for(i = 0; pla_types[i].key != 0; i++)
		    if (equal(pla_types[i].key + 1, word)) {
			PLA->pla_type = pla_types[i].value;
			break;
		    }
		if (pla_types[i].key == 0)
		    fatal("unknown type in .type command");

	    /* parse the labels */
	    } else if (equal(word, "ilb")) {
		if (CUBE.fullset == NULL)
		    fatal("PLA size must be declared before .ilb or .ob");
		if (PLA->label == NULL)
		    PLA_labels(PLA);
		for(var = 0; var < CUBE.num_binary_vars; var++) {
		    get_word(fp, word);
		    i = CUBE.first_part[var];
		    PLA->label[i+1] = strdup(word);
		    PLA->label[i] = ALLOC(char, strlen(word) + 6);
		    sprintf(PLA->label[i], "%s.bar", word);
		}
	    } else if (equal(word, "ob")) {
		if (CUBE.fullset == NULL)
		    fatal("PLA size must be declared before .ilb or .ob");
		if (PLA->label == NULL)
		    PLA_labels(PLA);
		var = CUBE.num_vars - 1;
		for(i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
		    get_word(fp, word);
		    PLA->label[i] = strdup(word);
		}
	    /* .label assigns labels to multiple-valued variables */
	    } else if (equal(word, "label")) {
		if (CUBE.fullset == NULL)
		    fatal("PLA size must be declared before .label");
		if (PLA->label == NULL)
		    PLA_labels(PLA);
		if (fscanf(fp, "var=%d", &var) != 1)
		    fatal("Error reading labels");
		for(i = CUBE.first_part[var]; i <= CUBE.last_part[var]; i++) {
		    get_word(fp, word);
		    PLA->label[i] = strdup(word);
		}

	    } else if (equal(word, "symbolic")) {
		symbolic_t *newlist, *p1;
		if (read_symbolic(fp, PLA, word, &newlist)) {
		    if (PLA->symbolic == NIL(symbolic_t)) {
			PLA->symbolic = newlist;
		    } else {
			for(p1=PLA->symbolic;p1->next!=NIL(symbolic_t);
			    p1=p1->next){
			}
			p1->next = newlist;
		    }
		} else {
		    fatal("error reading .symbolic");
		}

	    } else if (equal(word, "symbolic-output")) {
		symbolic_t *newlist, *p1;
		if (read_symbolic(fp, PLA, word, &newlist)) {
		    if (PLA->symbolic_output == NIL(symbolic_t)) {
			PLA->symbolic_output = newlist;
		    } else {
			for(p1=PLA->symbolic_output;p1->next!=NIL(symbolic_t);
			    p1=p1->next){
			}
			p1->next = newlist;
		    }
		} else {
		    fatal("error reading .symbolic-output");
		}

	    /* .phase allows a choice of output phases */
	    } else if (equal(word, "phase")) {
		if (CUBE.fullset == NULL)
		    fatal("PLA size must be declared before .phase");
		if (PLA->phase != NULL) {
		    fprintf(stderr, "extra .phase ignored\n");
		    skip_line(fp, stdout, /* echo */ FALSE);
		} else {
		    do ch = getc(fp); while (ch == ' ' || ch == '\t');
		    ungetc(ch, fp);
		    PLA->phase = set_save(CUBE.fullset);
		    last = CUBE.last_part[CUBE.num_vars - 1];
		    for(i=CUBE.first_part[CUBE.num_vars - 1]; i <= last; i++)
			if ((ch = getc(fp)) == '0')
			    set_remove(PLA->phase, i);
			else if (ch != '1')
			    fatal("only 0 or 1 allowed in phase description");
		}

	    /* .pair allows for bit-pairing input variables */
	    } else if (equal(word, "pair")) {
		int j;
		if (PLA->pair != NULL) {
		    fprintf(stderr, "extra .pair ignored\n");
		} else {
		    pair_t *pair;
		    PLA->pair = pair = ALLOC(pair_t, 1);
		    if (fscanf(fp, "%d", &(pair->cnt)) != 1)
			fatal("syntax error in .pair");
		    pair->var1 = ALLOC(int, pair->cnt);
		    pair->var2 = ALLOC(int, pair->cnt);
		    for(i = 0; i < pair->cnt; i++) {
			get_word(fp, word);
			if (word[0] == '(') strcpy(word, word+1);
			if (label_index(PLA, word, &var, &j)) {
			    pair->var1[i] = var+1;
			} else {
			    fatal("syntax error in .pair");
			}

			get_word(fp, word);
			if (word[strlen(word)-1] == ')') {
			    word[strlen(word)-1]='\0';
			}
			if (label_index(PLA, word, &var, &j)) {
			    pair->var2[i] = var+1;
			} else {
			    fatal("syntax error in .pair");
			}
		    }
		}

	    } else {
		if (echo_unknown_commands)
		    printf("%c%s ", ch, word);
		skip_line(fp, stdout, echo_unknown_commands);
	    }
	    break;
	default:
	    ungetc(ch, fp);
	    if (CUBE.fullset == NULL) {
/*		fatal("unknown PLA size, need .i/.o or .mv");*/
		if (echo_comments)
		    putchar('#');
		skip_line(fp, stdout, echo_comments);
		break;
	    }
	    if (PLA->F == NULL) {
		PLA->F = sf_new(10, CUBE.size);
		PLA->D = sf_new(10, CUBE.size);
		PLA->R = sf_new(10, CUBE.size);
	    }
	    read_cube(fp, PLA);
    }
    goto loop;
}

/*
    read_pla -- read a PLA from a file

    Input stops when ".e" is encountered in the input file, or upon reaching
    end of file.

    Returns the PLA in the variable PLA after massaging the "symbolic"
    representation into a positional cube notation of the ON-set, OFF-set,
    and the DC-set.

    needs_dcset and needs_offset control the computation of the OFF-set
    and DC-set (i.e., if either needs to be computed, then it will be
    computed via complement only if the corresponding option is TRUE.)
    pla_type specifies the interpretation to be used when reading the
    PLA.

    The phase of the output functions is adjusted according to the
    global option "pos" or according to an imbedded .phase option in
    the input file.  Note that either phase option implies that the
    OFF-set be computed regardless of whether the caller needs it
    explicitly or not.

    Bit pairing of the binary variables is performed according to an
    imbedded .pair option in the input file.

    The global cube structure also reflects the sizes of the PLA which
    was just read.  If these fields have already been set, then any
    subsequent PLA must conform to these sizes.

    The global flag trace controls the output produced during the read.

    Returns a status code as a result:
        EOF (-1) : End of file reached before any data was read
        > 0 : Operation successful
*/

int
read_pla(FILE *fp, bool needs_dcset, bool needs_offset, int pla_type, PLA_t **PLA_return)
{
    PLA_t *PLA;
    int i, second, third;
    cost_t cost;

    /* Allocate and initialize the PLA structure */
    PLA = *PLA_return = new_PLA();
    PLA->pla_type = pla_type;

    /* Read the pla */
    parse_pla(fp, PLA);

    /* Check for nothing on the file -- implies reached EOF */
    if (PLA->F == NULL) {
	return EOF;
    }

    /* This hack merges the next-state field with the outputs */
    for(i = 0; i < CUBE.num_vars; i++) {
	CUBE.part_size[i] = ABS(CUBE.part_size[i]);
    }
    if (kiss) {
	third = CUBE.num_vars - 3;
	second = CUBE.num_vars - 2;
	if (CUBE.part_size[third] != CUBE.part_size[second]) {
	    fprintf(stderr," with .kiss option, third to last and second\n");
	    fprintf(stderr, "to last variables must be the same size.\n");
	    return EOF;
	}
	for(i = 0; i < CUBE.part_size[second]; i++) {
	    PLA->label[i + CUBE.first_part[second]] =
		strdup(PLA->label[i + CUBE.first_part[third]]);
	}
	CUBE.part_size[second] += CUBE.part_size[CUBE.num_vars-1];
	CUBE.num_vars--;
	cube_setdown();
	cube_setup();
    }

    /* Decide how to break PLA into ON-set, OFF-set and DC-set */
    if (pos || PLA->phase != NULL || PLA->symbolic_output != NIL(symbolic_t)) {
        needs_offset = TRUE;
    }
    if (needs_offset && (PLA->pla_type==F_type || PLA->pla_type==FD_type)) {
        sf_free(PLA->R);
        PLA->R = complement(cube2list(PLA->F, PLA->D));
    } else if (needs_dcset && PLA->pla_type == FR_type) {
        set_family_t *X;
        sf_free(PLA->D);
        /* hack, why not? */
        X = d1merge(sf_join(PLA->F, PLA->R), CUBE.num_vars - 1);
        PLA->D = complement(cube1list(X));
        sf_free(X);
    } else if (PLA->pla_type == R_type || PLA->pla_type == DR_type) {
        sf_free(PLA->F);
        PLA->F = complement(cube2list(PLA->D, PLA->R));
    }

    /* Check for phase rearrangement of the functions */
    if (pos) {
	set_family_t *onset = PLA->F;
	PLA->F = PLA->R;
	PLA->R = onset;
	PLA->phase = set_new(CUBE.size);
	set_diff(PLA->phase, CUBE.fullset, CUBE.var_mask[CUBE.num_vars-1]);
    } else if (PLA->phase != NULL) {
	set_phase(PLA);
    }

    /* Setup minimization for two-bit decoders */
    if (PLA->pair != (pair_t *) NULL) {
	set_pair(PLA);
    }

    if (PLA->symbolic != NIL(symbolic_t)) {
	map_symbolic(PLA);
    }
    if (PLA->symbolic_output != NIL(symbolic_t)) {
	map_output_symbolic(PLA);
	if (needs_offset) {
	    sf_free(PLA->R);
    PLA->R = complement(cube2list(PLA->F, PLA->D));
    cover_cost(PLA->R, &cost);
	}
    }

    return 1;
}

void
PLA_summary(PLA_t *PLA)
{
    int var, i;
    symbolic_list_t *p2;
    symbolic_t *p1;

    printf("# PLA is %s", PLA->filename);
    if (CUBE.num_binary_vars == CUBE.num_vars - 1)
	printf(" with %d inputs and %d outputs\n",
	    CUBE.num_binary_vars, CUBE.part_size[CUBE.num_vars - 1]);
    else {
	printf(" with %d variables (%d binary, mv sizes",
	    CUBE.num_vars, CUBE.num_binary_vars);
	for(var = CUBE.num_binary_vars; var < CUBE.num_vars; var++)
	    printf(" %d", CUBE.part_size[var]);
	printf(")\n");
    }
    printf("# ON-set cost is  %s\n", print_cost(PLA->F));
    printf("# OFF-set cost is %s\n", print_cost(PLA->R));
    printf("# DC-set cost is  %s\n", print_cost(PLA->D));
    if (PLA->phase != NULL)
	printf("# phase is %s\n", pc1(PLA->phase));
    if (PLA->pair != NULL) {
	printf("# two-bit decoders:");
	for(i = 0; i < PLA->pair->cnt; i++)
	    printf(" (%d %d)", PLA->pair->var1[i], PLA->pair->var2[i]);
	printf("\n");
    }
    if (PLA->symbolic != NIL(symbolic_t)) {
	for(p1 = PLA->symbolic; p1 != NIL(symbolic_t); p1 = p1->next) {
	    printf("# symbolic: ");
	    for(p2=p1->symbolic_list; p2!=NIL(symbolic_list_t); p2=p2->next) {
		printf(" %d", p2->variable);
	    }
	    printf("\n");
	}
    }
    if (PLA->symbolic_output != NIL(symbolic_t)) {
	for(p1 = PLA->symbolic_output; p1 != NIL(symbolic_t); p1 = p1->next) {
	    printf("# output symbolic: ");
	    for(p2=p1->symbolic_list; p2!=NIL(symbolic_list_t); p2=p2->next) {
		printf(" %d", p2->pos);
	    }
	    printf("\n");
	}
    }
    fflush(stdout);
}

PLA_t *
new_PLA(void)
{
    PLA_t *PLA;

    PLA = ALLOC(PLA_t, 1);
    PLA->F = PLA->D = PLA->R = (set_family_t *) NULL;
    PLA->phase = (set *) NULL;
    PLA->pair = (pair_t *) NULL;
    PLA->label = (char **) NULL;
    PLA->filename = (char *) NULL;
    PLA->pla_type = 0;
    PLA->symbolic = NIL(symbolic_t);
    PLA->symbolic_output = NIL(symbolic_t);

    return PLA;
}

void PLA_labels(PLA_t *PLA)
{
    int i;

    PLA->label = ALLOC(char *, CUBE.size);
    for(i = 0; i < CUBE.size; i++)
	PLA->label[i] = (char *) NULL;
}

void
free_PLA(PLA_t *PLA)
{
    symbolic_list_t *p2, *p2next;
    symbolic_t *p1, *p1next;
    int i;

    if (PLA->F != (set_family_t *) NULL)
	sf_free(PLA->F);
    if (PLA->R != (set_family_t *) NULL)
	sf_free(PLA->R);
    if (PLA->D != (set_family_t *) NULL)
	sf_free(PLA->D);
    if (PLA->phase != (set *) NULL)
	set_free(PLA->phase);
    if (PLA->pair != (pair_t *) NULL) {
	FREE(PLA->pair->var1);
	FREE(PLA->pair->var2);
	FREE(PLA->pair);
    }
    if (PLA->label != NULL) {
	for(i = 0; i < CUBE.size; i++)
	    if (PLA->label[i] != NULL)
		FREE(PLA->label[i]);
	FREE(PLA->label);
    }
    if (PLA->filename != NULL) {
	FREE(PLA->filename);
    }
    for(p1 = PLA->symbolic; p1 != NIL(symbolic_t); p1 = p1next) {
	for(p2 = p1->symbolic_list; p2 != NIL(symbolic_list_t); p2 = p2next) {
	    p2next = p2->next;
	    FREE(p2);
	}
	p1next = p1->next;
	FREE(p1);
    }
    PLA->symbolic = NIL(symbolic_t);
    for(p1 = PLA->symbolic_output; p1 != NIL(symbolic_t); p1 = p1next) {
	for(p2 = p1->symbolic_list; p2 != NIL(symbolic_list_t); p2 = p2next) {
	    p2next = p2->next;
	    FREE(p2);
	}
	p1next = p1->next;
	FREE(p1);
    }
    PLA->symbolic_output = NIL(symbolic_t);
    FREE(PLA);
}

int
read_symbolic(FILE *fp, PLA_t *PLA, char *word, symbolic_t **retval)
{
    symbolic_list_t *listp, *prev_listp;
    symbolic_label_t *labelp, *prev_labelp;
    symbolic_t *newlist;
    int i, var;

    newlist = ALLOC(symbolic_t, 1);
    newlist->next = NIL(symbolic_t);
    newlist->symbolic_list = NIL(symbolic_list_t);
    newlist->symbolic_list_length = 0;
    newlist->symbolic_label = NIL(symbolic_label_t);
    newlist->symbolic_label_length = 0;
    prev_listp = NIL(symbolic_list_t);
    prev_labelp = NIL(symbolic_label_t);

    for(;;) {
	get_word(fp, word);
	if (equal(word, ";"))
	    break;
	if (label_index(PLA, word, &var, &i)) {
	    listp = ALLOC(symbolic_list_t, 1);
	    listp->variable = var;
	    listp->pos = i;
	    listp->next = NIL(symbolic_list_t);
	    if (prev_listp == NIL(symbolic_list_t)) {
		newlist->symbolic_list = listp;
	    } else {
		prev_listp->next = listp;
	    }
	    prev_listp = listp;
	    newlist->symbolic_list_length++;
	} else {
	    return FALSE;
	}
    }

    for(;;) {
        get_word(fp, word);
        if (equal(word, ";"))
            break;
        labelp = ALLOC(symbolic_label_t, 1);
        labelp->label = strdup(word);
        labelp->next = NIL(symbolic_label_t);
        if (prev_labelp == NIL(symbolic_label_t)) {
            newlist->symbolic_label = labelp;
        }
        else {
            prev_labelp->next = labelp;
        }
        prev_labelp = labelp;
        newlist->symbolic_label_length++;
    }

    *retval = newlist;
    return TRUE;
}

int
label_index(PLA_t *PLA, char *word, int *varp, int *ip)
{
    int var, i;

    if (PLA->label == NIL(char *) || PLA->label[0] == NIL(char)) {
	if (sscanf(word, "%d", varp) == 1) {
	    *ip = *varp;
	    return TRUE;
	}
    } else {
	for(var = 0; var < CUBE.num_vars; var++) {
	    for(i = 0; i < CUBE.part_size[var]; i++) {
		if (equal(PLA->label[CUBE.first_part[var]+i], word)) {
		    *varp = var;
		    *ip = i;
		    return TRUE;
		}
	    }
	}
    }
    return FALSE;
}

