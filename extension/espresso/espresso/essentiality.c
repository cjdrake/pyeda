/*
/* Module:essentiality.c
 *	contains routines for performing essentiality test and reduction
 * Routines:
 * pcover ess_test_and_reduction():
 *	determines essentiality of the given signature cube and returns
 * 	cover of the signature cube (Hammered signature cube) if found
 *	inessential.	
 * pcover aux_ess_test_and_reduction():
 *	core compuation routine which determines the essentiality of
 *	the signature cube and performs reduction of inessential signature
 *	cubes by recursively descending down the cube-tree.
 */



#include <stdio.h>
#include "espresso.h"
#include "signature.h"

/* Yuk, Yuk, Yuk!! More Globals. It seems recursive routines have unholy
   alliance with globals */

static int *c_free_list; /* List of raised variables  in cube c */
static int c_free_count; /* active size of the above list */

static int *r_free_list; /* List of subset of raised variables in cube c
			which are raised in each cube of offset R */
static int r_free_count; /* active size of the above list */
static int r_head; /* current position in  the list above */

static int *reduced_c_free_list; /* c_free_list - r_free_list */
static int reduced_c_free_count; /* active size of the above list */

typedef struct {
	int variable;
	int free_count;
	} VAR;

static VAR *unate_list; /* List of unate variables in the reduced_c_free_list */
static int unate_count; /* active size of the above list */

static VAR *binate_list; /* List of binate variables in the 
			 reduced_c_free_list */
static int binate_count; /* active size of the above list */

static int *variable_order; /* permutation of reduced c_free_count determining 
			    static ordering of variables */
static int variable_count; /* active size of the above list */
static int variable_head; /* current position in  the list above */

/* The passive size allocated on the first call to etr_order is equal
   to the number of binary variables */
/* Clearly not the most optimized usage of memory. Not worth saving
   few pennies when the total memory budget is quite large */

pcover COVER; /* A global bag to collect the signature cubes in the cover 
		 of inessential signature cube */

/* etr_order:
 * What does it do:
 *	Performs performs ordering of variables before calling
 *	essentiality test and reduction routine 
 * Inputs:
 *	R: Cover of the Off-set.
 *	c: cube to be reduced
 * Output:
 *	COVER: signature cube cover of given inessential signature cube
 * Strategy: As many cubes in the cover as possible.
 * 	-> As deep a search tree recursion as possible
 *	-> variable ordering
 *	-> static ordering to minimize computation
 *		1. Free
 *		2. Freer Unate
 *		3. Freer Binate
 */
pcover
etr_order(F,E,R,c,d)
pcover F,E,R;
pcube c,d;
{
	static int num_binary_vars;
	int v,e0,e1;
	int i,free_var;
	pcube lastr,r;
	int even_count,odd_count,free_count;
	int odd,even;
	VAR *p;

	num_binary_vars = cube.num_binary_vars;
	c_free_list = (int *)calloc(num_binary_vars,sizeof(int));
	r_free_list = (int *)calloc(num_binary_vars,sizeof(int));
	reduced_c_free_list = (int *)calloc(num_binary_vars,sizeof(int));
	unate_list = (VAR *)calloc(num_binary_vars,sizeof(VAR));
	binate_list = (VAR *)calloc(num_binary_vars,sizeof(VAR));

	variable_order = (int *)calloc(num_binary_vars,sizeof(int));

	if(!c_free_list || !r_free_list || !reduced_c_free_list ||
		!unate_list || !binate_list || !variable_order){
		perror("etr_order:alloc");
		exit(1);
	}

	/* 1.Identify free variables of cube c */	
	c_free_count = 0;
	for(v = 0; v < num_binary_vars; v++){
		e0 = v<<1;
		e1 = e0 + 1;
		if(is_in_set(d,e0) && is_in_set(d,e1)){
			c_free_list[c_free_count++] = v;
		}
	}

	/* 2.Identify corresponding free variables of R */
	r_head = 0;
	r_free_count = 0;
	reduced_c_free_count = 0;
	for(i = 0; i < c_free_count; i++){
		v = c_free_list[i];
		e0 = v<<1;
		e1 = e0 + 1;
		free_var = TRUE;
		foreach_set(R,lastr,r){
			if(!is_in_set(r,e0) || !is_in_set(r,e1)){
				free_var = FALSE;
				break;
			}
		}
		if(free_var){
			r_free_list[r_free_count++] = v;
		}
		else{
			reduced_c_free_list[reduced_c_free_count++] = v;
		}
	}

	/* 3.Identify unate and binate variables and sort them in the 
	     decreasing free_count */
	unate_count = 0;
	binate_count = 0;
	for(i = 0; i < reduced_c_free_count; i++){
		v = reduced_c_free_list[i];
		e0 = v<<1;
		e1 = e0 + 1;
		even_count = 0;
		odd_count = 0;
		free_count = 0;
		foreach_set(R,lastr,r){
			odd = is_in_set(r,e0);
			even = is_in_set(r,e1);
			if(odd && even){
				free_count++;
			}
			else if(odd){
				odd_count++;
			}
			else{
				even_count++;
			}
		}
		if(odd_count == 0 || even_count == 0){
			p = &unate_list[unate_count++];
			p->variable = v;
			p->free_count = free_count;
		}
		else{
			p = &binate_list[binate_count++];
			p->variable = v;
			p->free_count = free_count;
		}
	}

	qsort(unate_list,unate_count,sizeof(VAR),ascending);
	qsort(binate_list,binate_count,sizeof(VAR),ascending);

	variable_head = 0;
	variable_count = 0;
	for(i = 0; i < binate_count; i++){
		variable_order[variable_count++] = binate_list[i].variable;
	}
	for(i = 0; i < unate_count; i++){
		variable_order[variable_count++] = unate_list[i].variable;
	}
	
	/* 4.Recursively go down the tree defined by r_free_list,
	     invoking "etr" at the leaves */

	COVER = new_cover(10);
	setup_bw(R,c);
	SET(c,NONESSEN);

	aux_etr_order(F,E,R,c,d);

	free_bw();
	free(c_free_list);
	free(r_free_list);
	free(reduced_c_free_list);
	free(unate_list);
	free(binate_list);
	free(variable_order);

	return COVER;
}

int
ascending(p1,p2)
VAR *p1,*p2;
{
	int f1 = p1->free_count;
	int f2 = p2->free_count;

	if(f1 > f2){
		return 1;
	}
	else if(f1 < f2){
		return -1;
	}
	else{
		return 0;
	}	
}

/*
 * aux_etr_order
 * Objective:main recursive routine for reducing the inessential signature cube.
 *	Very similar to aux_ess_test_and_reduction;
 * Input:
 *	c: signature cube;
 *	d: cube contained in the signature cube;
 *	E: Extended don't care set. DC + identified ESC;
 *	R: OFFSET cover;
 */
int
aux_etr_order(F,E,R,c,d)
pcover F,E,R;
pcube c,d;
{
	pcover  minterms;
	pcube d_minterm;
	pcube sigma_d;
	int v_index,e0,e1;
	int i;
	pcube *local_dc;

	/* Special Cases */
	local_dc = cube3list(F,E,COVER);
	if(cube_is_covered(local_dc,d)){
		free_cubelist(local_dc);
		return;
	}
	if(black_white() == FALSE){
		free_cubelist(local_dc);
		sigma_d = get_sigma(R,d);
		sf_addset(COVER,sigma_d);
		free_cube(sigma_d);
		return;
	}
	if(variable_head == variable_count){
		minterms = get_mins(d);
		foreachi_set(minterms,i,d_minterm){
			if(cube_is_covered(local_dc,d_minterm))continue;
			sigma_d = get_sigma(R,d_minterm);
			if(setp_equal(sigma_d,c)){
				RESET(c,NONESSEN);
				free_cube(sigma_d);
				break;
			}
			sf_addset(COVER,sigma_d);
			free_cube(sigma_d);
		}
		sf_free(minterms);
		free_cubelist(local_dc);
		return;
	}
	else{
		v_index = variable_order[variable_head];
	}
	free_cubelist(local_dc);
		
	e0 = (v_index<<1);
	e1 = e0 + 1;

	variable_head++;

	set_remove(d,e1);
	reset_black_list();
	split_list(R,e0);
	push_black_list();
	S_EXECUTE(aux_etr_order(F,E,R,c,d),ETRAUX_TIME);
	if(TESTP(c,NONESSEN) == FALSE)return;
	pop_black_list();
	merge_list();
	set_insert(d,e1);

	set_remove(d,e0);
	reset_black_list();
	split_list(R,e1);
	push_black_list();
	S_EXECUTE(aux_etr_order(F,E,R,c,d),ETRAUX_TIME);
	if(TESTP(c,NONESSEN) == FALSE)return;
	pop_black_list();
	merge_list();
	set_insert(d,e0);

	variable_head--;

	return;
}

pcover
get_mins(c)
pcube c;
{
	pcover minterms;
	pcube d_minterm;
	int i,j;

	minterms = new_cover(1);
	d_minterm = new_cube();
	set_copy(d_minterm,c);
	set_and(d_minterm,d_minterm,cube.binary_mask);
	for(i = cube.num_binary_vars;
	    i < cube.num_vars;i++){
		for(j = cube.first_part[i]; j <= cube.last_part[i];j++){
			if(is_in_set(c,j)){
				set_insert(d_minterm,j);
				sf_addset(minterms,d_minterm);
				set_remove(d_minterm,j);
			}
		}
	}
	free_cube(d_minterm);
	return minterms;
}

print_list(n,x,name)
int n;
int *x;
char *name;
{
	int i;
	printf("%s:\n",name);
	for(i = 0; i < n; i++){
		printf("%d%c",x[i],(i+1)%10?'\t':'\n');
	}
	printf("\n");
}
