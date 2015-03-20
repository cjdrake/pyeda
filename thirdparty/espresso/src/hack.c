// Filename: hack.c

#include <string.h>

#include "espresso.h"

void map_dcset(PLA_t *PLA)
{
    int var, i;
    set_family_t *Tplus, *Tminus, *Tplusbar, *Tminusbar;
    set_family_t *newf, *term1, *term2, *dcset, *dcsetbar;
    set *cplus, *cminus, *last, *p;

    if (PLA->label == NIL(char *) || PLA->label[0] == NIL(char))
	return;

    /* try to find a binary variable named "DONT_CARE" */
    var = -1;
    for(i = 0; i < CUBE.num_binary_vars * 2; i++) {
	if (strncmp(PLA->label[i], "DONT_CARE", 9) == 0 ||
	  strncmp(PLA->label[i], "DONTCARE", 8) == 0 ||
	  strncmp(PLA->label[i], "dont_care", 9) == 0 ||
	  strncmp(PLA->label[i], "dontcare", 8) == 0) {
	    var = i/2;
	    break;
	}
    }
    if (var == -1) {
	return;
    }

    /* form the cofactor cubes for the don't-care variable */
    cplus = set_save(CUBE.fullset);
    cminus = set_save(CUBE.fullset);
    set_remove(cplus, var*2);
    set_remove(cminus, var*2 + 1);

    /* form the don't-care set */
    simp_comp(cofactor(cube1list(PLA->F), cplus), &Tplus, &Tplusbar);
    simp_comp(cofactor(cube1list(PLA->F), cminus), &Tminus, &Tminusbar);
    term1 = cv_intersect(Tplus, Tminusbar);
    term2 = cv_intersect(Tminus, Tplusbar);
    dcset = sf_union(term1, term2);
    simp_comp(cube1list(dcset), &PLA->D, &dcsetbar);
    newf = cv_intersect(PLA->F, dcsetbar);
    sf_free(PLA->F);
    PLA->F = newf;
    sf_free(Tplus);
    sf_free(Tminus);
    sf_free(Tplusbar);
    sf_free(Tminusbar);
    sf_free(dcsetbar);

    /* remove any cubes dependent on the DONT_CARE variable */
    sf_active(PLA->F);
    foreach_set(PLA->F, last, p) {
	if (! is_in_set(p, var*2) || ! is_in_set(p, var*2+1)) {
	    RESET(p, ACTIVE);
	}
    }
    PLA->F = sf_inactive(PLA->F);

    /* resize the cube and delete the don't-care variable */
    cube_setdown();
    for(i = 2*var+2; i < CUBE.size; i++) {
	PLA->label[i-2] = PLA->label[i];
    }
    for(i = var+1; i < CUBE.num_vars; i++) {
	CUBE.part_size[i-1] = CUBE.part_size[i];
    }
    CUBE.num_binary_vars--;
    CUBE.num_vars--;
    cube_setup();
    PLA->F = sf_delc(PLA->F, 2*var, 2*var+1);
    PLA->D = sf_delc(PLA->D, 2*var, 2*var+1);
}

void map_output_symbolic(PLA_t *PLA)
{
    set_family_t *newF, *newD;
    set *compress;
    symbolic_t *p1;
    symbolic_list_t *p2;
    int i, bit, tot_size, base, old_size;

    /* Remove the DC-set from the ON-set (is this necessary ??) */
    if (PLA->D->count > 0) {
	sf_free(PLA->F);
	PLA->F = complement(cube2list(PLA->D, PLA->R));
    }

    /* tot_size = width added for all symbolic variables */
    tot_size = 0;
    for(p1=PLA->symbolic_output; p1!=NIL(symbolic_t); p1=p1->next) {
	for(p2=p1->symbolic_list; p2!=NIL(symbolic_list_t); p2=p2->next) {
	    if (p2->pos<0 || p2->pos>=CUBE.part_size[CUBE.output]) {
		fatal("symbolic-output index out of range");
/*	    } else if (p2->variable != CUBE.output) {
		fatal("symbolic-output label must be an output");*/
	    }
	}
	tot_size += 1 << p1->symbolic_list_length;
    }

    /* adjust the indices to skip over new outputs */
    for(p1=PLA->symbolic_output; p1!=NIL(symbolic_t); p1=p1->next) {
	for(p2=p1->symbolic_list; p2!=NIL(symbolic_list_t); p2=p2->next) {
	    p2->pos += tot_size;
	}
    }

    /* resize the cube structure -- add enough for the one-hot outputs */
    old_size = CUBE.size;
    CUBE.part_size[CUBE.output] += tot_size;
    cube_setdown();
    cube_setup();

    /* insert space in the output part for the one-hot output */
    base = CUBE.first_part[CUBE.output];
    PLA->F = sf_addcol(PLA->F, base, tot_size);
    PLA->D = sf_addcol(PLA->D, base, tot_size);
    PLA->R = sf_addcol(PLA->R, base, tot_size);

    /* do the real work */
    for(p1=PLA->symbolic_output; p1!=NIL(symbolic_t); p1=p1->next) {
	newF = sf_new(100, CUBE.size);
	newD = sf_new(100, CUBE.size);
	find_inputs(NIL(set_family_t), PLA, p1->symbolic_list, base, 0,
			    &newF, &newD);

	sf_free(PLA->F);
	PLA->F = newF;
/*
 *  retain OLD DC-set -- but we've lost the don't-care arc information
 *  (it defaults to branch to the zero state)
	sf_free(PLA->D);
	PLA->D = newD;
 */
	sf_free(newD);
	base += 1 << p1->symbolic_list_length;
    }

    /* delete the old outputs, and resize the cube */
    compress = set_full(newF->sf_size);
    for(p1=PLA->symbolic_output; p1!=NIL(symbolic_t); p1=p1->next) {
	for(p2=p1->symbolic_list; p2!=NIL(symbolic_list_t); p2=p2->next) {
	    bit = CUBE.first_part[CUBE.output] + p2->pos;
	    set_remove(compress, bit);
	}
    }
    CUBE.part_size[CUBE.output] -= newF->sf_size - set_ord(compress);
    cube_setdown();
    cube_setup();
    PLA->F = sf_compress(PLA->F, compress);
    PLA->D = sf_compress(PLA->D, compress);
    if (CUBE.size != PLA->F->sf_size) fatal("error");

    /* Quick minimization */
    PLA->F = sf_contain(PLA->F);
    PLA->D = sf_contain(PLA->D);
    for(i = 0; i < CUBE.num_vars; i++) {
	PLA->F = d1merge(PLA->F, i);
	PLA->D = d1merge(PLA->D, i);
    }
    PLA->F = sf_contain(PLA->F);
    PLA->D = sf_contain(PLA->D);

    sf_free(PLA->R);
    PLA->R = sf_new(0, CUBE.size);

    symbolic_hack_labels(PLA, PLA->symbolic_output,
			    compress, CUBE.size, old_size, tot_size);
    set_free(compress);
}

void find_inputs(set_family_t *A, PLA_t *PLA, symbolic_list_t *list, int base, int value, set_family_t **newF, set_family_t **newD)
{
    set_family_t *S, *S1;
    set *last, *p;

    /*
     *  A represents th 'input' values for which the outputs assume
     *  the integer value 'value
     */
    if (list == NIL(symbolic_list_t)) {
	/*
	 *  Simulate these inputs against the on-set; then, insert into the
	 *  new on-set a 1 in the proper position
	 */
	S = cv_intersect(A, PLA->F);
	foreach_set(S, last, p) {
	    set_insert(p, base + value);
	}
	*newF = sf_append(*newF, S);

	/*
	 *  'simulate' these inputs against the don't-care set
	S = cv_intersect(A, PLA->D);
	*newD = sf_append(*newD, S);
	 */

    } else {
	/* intersect and recur with the OFF-set */
	S = cof_output(PLA->R, CUBE.first_part[CUBE.output] + list->pos);
	if (A != NIL(set_family_t)) {
	    S1 = cv_intersect(A, S);
	    sf_free(S);
	    S = S1;
	}
	find_inputs(S, PLA, list->next, base, value*2, newF, newD);
	sf_free(S);

	/* intersect and recur with the ON-set */
	S = cof_output(PLA->F, CUBE.first_part[CUBE.output] + list->pos);
	if (A != NIL(set_family_t)) {
	    S1 = cv_intersect(A, S);
	    sf_free(S);
	    S = S1;
	}
	find_inputs(S, PLA, list->next, base, value*2 + 1, newF, newD);
	sf_free(S);
    }
}

void map_symbolic(PLA_t *PLA)
{
    symbolic_t *p1;
    symbolic_list_t *p2;
    int var, base, num_vars, num_binary_vars, *new_part_size;
    int new_size, size_added, num_deleted_vars, num_added_vars, newvar;
    set *compress;

    /* Verify legal values are in the symbolic lists */
    for(p1 = PLA->symbolic; p1 != NIL(symbolic_t); p1 = p1->next) {
	for(p2=p1->symbolic_list; p2!=NIL(symbolic_list_t); p2=p2->next) {
	    if (p2->variable  < 0 || p2->variable >= CUBE.num_binary_vars) {
		fatal(".symbolic requires binary variables");
	    }
	}
    }

    /*
     *  size_added = width added for all symbolic variables
     *  num_deleted_vars = # binary variables to be deleted
     *  num_added_vars = # new mv variables
     *  compress = a cube which will be used to compress the set families
     */
    size_added = 0;
    num_added_vars = 0;
    for(p1 = PLA->symbolic; p1 != NIL(symbolic_t); p1 = p1->next) {
	size_added += 1 << p1->symbolic_list_length;
	num_added_vars++;
    }
    compress = set_full(PLA->F->sf_size + size_added);
    for(p1 = PLA->symbolic; p1 != NIL(symbolic_t); p1 = p1->next) {
	for(p2=p1->symbolic_list; p2!=NIL(symbolic_list_t); p2=p2->next) {
	    set_remove(compress, p2->variable*2);
	    set_remove(compress, p2->variable*2+1);
	}
    }
    num_deleted_vars = ((PLA->F->sf_size + size_added) - set_ord(compress))/2;

    /* compute the new cube constants */
    num_vars = CUBE.num_vars - num_deleted_vars + num_added_vars;
    num_binary_vars = CUBE.num_binary_vars - num_deleted_vars;
    new_size = CUBE.size - num_deleted_vars*2 + size_added;
    new_part_size = ALLOC(int, num_vars);
    new_part_size[num_vars-1] = CUBE.part_size[CUBE.num_vars-1];
    for(var = CUBE.num_binary_vars; var < CUBE.num_vars-1; var++) {
	new_part_size[var-num_deleted_vars] = CUBE.part_size[var];
    }

    /* re-size the covers, opening room for the new mv variables */
    base = CUBE.first_part[CUBE.output];
    PLA->F = sf_addcol(PLA->F, base, size_added);
    PLA->D = sf_addcol(PLA->D, base, size_added);
    PLA->R = sf_addcol(PLA->R, base, size_added);

    /* compute the values for the new mv variables */
    newvar = (CUBE.num_vars - 1) - num_deleted_vars;
    for(p1 = PLA->symbolic; p1 != NIL(symbolic_t); p1 = p1->next) {
	PLA->F = map_symbolic_cover(PLA->F, p1->symbolic_list, base);
	PLA->D = map_symbolic_cover(PLA->D, p1->symbolic_list, base);
	PLA->R = map_symbolic_cover(PLA->R, p1->symbolic_list, base);
	base += 1 << p1->symbolic_list_length;
	new_part_size[newvar++] = 1 << p1->symbolic_list_length;
    }

    /* delete the binary variables which disappear */
    PLA->F = sf_compress(PLA->F, compress);
    PLA->D = sf_compress(PLA->D, compress);
    PLA->R = sf_compress(PLA->R, compress);

    symbolic_hack_labels(PLA, PLA->symbolic, compress,
		new_size, CUBE.size, size_added);
    cube_setdown();
    FREE(CUBE.part_size);
    CUBE.num_vars = num_vars;
    CUBE.num_binary_vars = num_binary_vars;
    CUBE.part_size = new_part_size;
    cube_setup();
    set_free(compress);
}

set_family_t *map_symbolic_cover(set_family_t *T, symbolic_list_t *list, int base)
{
    set *last, *p;
    foreach_set(T, last, p) {
        form_bitvector(p, base, 0, list);
    }
    return T;
}

void form_bitvector(
    set *p,     /* old cube, looking at binary variables */
    int base,   /* where in mv cube the new variable starts */
    int value,  /* current value for this recursion */
    symbolic_list_t *list   /* current place in the symbolic list */
)
{
    if (list == NIL(symbolic_list_t)) {
	set_insert(p, base + value);
    } else {
	switch(GETINPUT(p, list->variable)) {
	    case ZERO:
		form_bitvector(p, base, value*2, list->next);
		break;
	    case ONE:
		form_bitvector(p, base, value*2+1, list->next);
		break;
	    case TWO:
		form_bitvector(p, base, value*2, list->next);
		form_bitvector(p, base, value*2+1, list->next);
		break;
	    default:
		fatal("bad cube in form_bitvector");
	}
    }
}

void
symbolic_hack_labels(PLA_t *PLA, symbolic_t *list, set *compress, int new_size, int old_size, int size_added)
{
    int i, base;
    char **oldlabel;
    symbolic_t *p1;
    symbolic_label_t *p3;

    /* hack with the labels */
    if ((oldlabel = PLA->label) == NIL(char *))
	return;
    PLA->label = ALLOC(char *, new_size);
    for(i = 0; i < new_size; i++) {
	PLA->label[i] = NIL(char);
    }

    /* copy the binary variable labels and unchanged mv variable labels */
    base = 0;
    for(i = 0; i < CUBE.first_part[CUBE.output]; i++) {
	if (is_in_set(compress, i)) {
	    PLA->label[base++] = oldlabel[i];
	} else {
	    if (oldlabel[i] != NIL(char)) {
		FREE(oldlabel[i]);
	    }
	}
    }

    /* add the user-defined labels for the symbolic outputs */
    for(p1 = list; p1 != NIL(symbolic_t); p1 = p1->next) {
	p3 = p1->symbolic_label;
	for(i = 0; i < (1 << p1->symbolic_list_length); i++) {
	    if (p3 == NIL(symbolic_label_t)) {
		PLA->label[base+i] = ALLOC(char, 10);
		sprintf(PLA->label[base+i], "X%d", i);
	    } else {
		PLA->label[base+i] = p3->label;
		p3 = p3->next;
	    }
	}
	base += 1 << p1->symbolic_list_length;
    }

    /* copy the labels for the binary outputs which remain */
    for(i = CUBE.first_part[CUBE.output]; i < old_size; i++) {
	if (is_in_set(compress, i + size_added)) {
	    PLA->label[base++] = oldlabel[i];
	} else {
	    if (oldlabel[i] != NIL(char)) {
		FREE(oldlabel[i]);
	    }
	}
    }
    FREE(oldlabel);
}

static set_family_t *
fsm_simplify(set_family_t *F)
{
    set_family_t *D, *R;
    D = sf_new(0, CUBE.size);
    R = complement(cube1list(F));
    F = espresso(F, D, R);
    sf_free(D);
    sf_free(R);
    return F;
}

void
disassemble_fsm(PLA_t *PLA)
{
    int nin, nstates, nout;
    int before, after, present_state, next_state, i, j;
    set *next_state_mask, *present_state_mask, *state_mask, *p, *p1, *last;
    set_family_t *go_nowhere, *F, *tF;

    /* We make the DISGUSTING assumption that the first 'n' outputs have
     *  been created by .symbolic-output, and represent a one-hot encoding
     * of the next state.  'n' is the size of the second-to-last multiple-
     * valued variable (i.e., before the outputs
     */

    if (CUBE.num_vars - CUBE.num_binary_vars != 2) {
	fprintf(stderr,
	"use .symbolic and .symbolic-output to specify\n");
	fprintf(stderr,
	"the present state and next state field information\n");
	fatal("disassemble_pla: need two multiple-valued variables\n");
    }

    nin = CUBE.num_binary_vars;
    nstates = CUBE.part_size[CUBE.num_binary_vars];
    nout = CUBE.part_size[CUBE.num_vars - 1];
    if (nout < nstates) {
	fprintf(stderr,
	    "use .symbolic and .symbolic-output to specify\n");
	fprintf(stderr,
	    "the present state and next state field information\n");
	fatal("disassemble_pla: # outputs < # states\n");
    }


    present_state = CUBE.first_part[CUBE.num_binary_vars];
    present_state_mask = set_new(CUBE.size);
    for(i = 0; i < nstates; i++) {
	set_insert(present_state_mask, i + present_state);
    }

    next_state = CUBE.first_part[CUBE.num_binary_vars+1];
    next_state_mask = set_new(CUBE.size);
    for(i = 0; i < nstates; i++) {
	set_insert(next_state_mask, i + next_state);
    }

    state_mask = set_or(set_new(CUBE.size), next_state_mask, present_state_mask);

    F = sf_new(10, CUBE.size);


    /*
     *  check for arcs which go from ANY state to state #i
     */
    for(i = 0; i < nstates; i++) {
	tF = sf_new(10, CUBE.size);
	foreach_set(PLA->F, last, p) {
	    if (setp_implies(present_state_mask, p)) { /* from any state ! */
		if (is_in_set(p, next_state + i)) {
		    tF = sf_addset(tF, p);
		}
	    }
	}
	before = tF->count;
	if (before > 0) {
	    tF = fsm_simplify(tF);
	    /* don't allow the next state to disappear ... */
	    foreach_set(tF, last, p) {
		set_insert(p, next_state + i);
	    }
	    after = tF->count;
	    F = sf_append(F, tF);
	}
    }


    /*
     *  some 'arcs' may NOT have a next state -- handle these
     *  we must unravel the present state part
     */
    go_nowhere = sf_new(10, CUBE.size);
    foreach_set(PLA->F, last, p) {
	if (setp_disjoint(p, next_state_mask)) { /* no next state !! */
	    go_nowhere = sf_addset(go_nowhere, p);
	}
    }
    before = go_nowhere->count;
    go_nowhere = unravel_range(go_nowhere,
				CUBE.num_binary_vars, CUBE.num_binary_vars);
    after = go_nowhere->count;
    F = sf_append(F, go_nowhere);

    /*
     *  minimize cover for all arcs from state #i to state #j
     */
    for(i = 0; i < nstates; i++) {
	for(j = 0; j < nstates; j++) {
	    tF = sf_new(10, CUBE.size);
	    foreach_set(PLA->F, last, p) {
		/* not EVERY state */
		if (! setp_implies(present_state_mask, p)) {
		    if (is_in_set(p, present_state + i)) {
			if (is_in_set(p, next_state + j)) {
			    p1 = set_save(p);
			    set_diff(p1, p1, state_mask);
			    set_insert(p1, present_state + i);
			    set_insert(p1, next_state + j);
			    tF = sf_addset(tF, p1);
			    set_free(p1);
			}
		    }
		}
	    }
	    before = tF->count;
	    if (before > 0) {
		tF = fsm_simplify(tF);
		/* don't allow the next state to disappear ... */
		foreach_set(tF, last, p) {
		    set_insert(p, next_state + j);
		}
		after = tF->count;
		F = sf_append(F, tF);
	    }
	}
    }


    set_free(state_mask);
    set_free(present_state_mask);
    set_free(next_state_mask);

    sf_free(PLA->F);
    PLA->F = F;
    sf_free(PLA->D);
    PLA->D = sf_new(0, CUBE.size);

    cube_setdown();
    FREE(CUBE.part_size);
    CUBE.num_binary_vars = nin;
    CUBE.num_vars = nin + 3;
    CUBE.part_size = ALLOC(int, CUBE.num_vars);
    CUBE.part_size[CUBE.num_binary_vars] = nstates;
    CUBE.part_size[CUBE.num_binary_vars+1] = nstates;
    CUBE.part_size[CUBE.num_binary_vars+2] = nout - nstates;
    cube_setup();

    foreach_set(PLA->F, last, p) {
	kiss_print_cube(stdout, PLA, p, "~1");
    }
}

