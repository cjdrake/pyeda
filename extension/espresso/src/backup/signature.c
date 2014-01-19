/*
 * Module: signature.c
 * Purpose: The main signature algorithm
 * Routines;
 * set_family_t *signature():
 *	Entry point for the signature cubes algorithm.
 * set_family_t *generate_primes():
 *	Generates the set of primes corresponding to
 *	the Essential Signature Cubes
 */

#include <stdio.h>
#include <math.h>
#include <signal.h>
#include "espresso.h"
#include "signature.h"

set_family_t *
signature(F1, D1, R1)
set_family_t *F1, *D1, *R1;
{
	set_family_t *ESC, *ESSet, *ESSENTIAL;
	set_family_t *F, *D, *R;
	set *last, *p;

	/* make scratch copy */
	F = sf_save(F1);
	D = sf_save(D1);
	R = sf_save(R1);

	/* unwrap offset */
	R = unravel(R, cube.num_binary_vars);
	R = sf_contain(R);

	signal(SIGXCPU,cleanup);

	/* Initial expand and irredundant */
	foreach_set(F, last, p) {
		RESET(p, PRIME);
	}

	F = expand(F, R, FALSE);
	F = irredundant(F, D);
	ESSENTIAL = essential(&F,&D);

	ESC = find_canonical_cover(F,D,R);
	/**************************************************
	printf("ESCubes %d\n", ESC->count + ESSENTIAL->count);
	fflush(stdout);
	**************************************************/

	ESSet = generate_primes(ESC,R);
	/**************************************************
	printf("ESSet %d\n",ESSet->count + ESSENTIAL->count);
	fflush(stdout);
	**************************************************/

	F = signature_minimize_exact(ESC,ESSet);
	sf_append(F,ESSENTIAL);
	/**************************************************
	printf("Exact_Minimum %d\n",F->count);
	print_cover(F,"Exact Minimum");
	**************************************************/

	if (! skip_make_sparse && R != 0) {
		F = make_sparse(F, D1, R);
	}

	sf_free(D);
	sf_free(R);
	sf_free(ESC);
	sf_free(ESSet);
	return F;
}


set_family_t *
generate_primes(F,R)
set_family_t *F, *R;
{
	set *c, *r, *lastc, *b, *lastb;
	set_family_t *BB, *PRIMES;
	set *odd, *even, *out_part_r;
	int i;
    int w, last;
	unsigned int x;
	int count;

	out_part_r = set_new(cube.size);
	odd = set_new(cube.size);
	even = set_new(cube.size);

	count = 0;
	PRIMES = sf_new(F->count, cube.size);
	foreach_set(F,lastc,c){
		BB = sf_new(R->count, cube.size);
		BB->count = R->count;
		/* BB = get_blocking_matrix(R,c); */
		foreachi_set(R,i,r){
			b = GETSET(BB,i);
			if ((last = cube.inword) != -1) {
				/* Check the partial word of binary variables */
				x = r[last] & c[last];
				x = ~(x | x >> 1) & cube.inmask;
				b[last] = r[last] & (x | x << 1);
				/* Check the full words of binary variables */
				for(w = 1; w < last; w++) {
		    			x = r[w] & c[w];
		    			x = ~(x | x >> 1) & DISJOINT;
					b[w] = r[w] & (x | x << 1);
				}
	    		}
			PUTLOOP(b,LOOP(r));
			set_and(b,b,cube.binary_mask);
			set_and(out_part_r,cube.mv_mask,r);
			if(!setp_implies(out_part_r,c)){
				set_or(b,b,out_part_r);
			}
		}
		BB = unate_compl(BB);
		if(BB != NULL){
			foreach_set(BB,lastb,b){
				set_not(b);
			}
			sf_append(PRIMES,BB);
		}
		count++;
		if(count % 100 == 0){
			PRIMES = sf_contain(PRIMES);
		}
	}
	PRIMES = sf_contain(PRIMES);
	set_free(out_part_r);
	set_free(odd);
	set_free(even);
	return PRIMES;
}

void
cleanup()
{
    printf("CPU Limit Exceeded\n");
    exit(1);
}
