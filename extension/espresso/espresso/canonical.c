/* Module:canonical.c
 *	contains routines for finding the canonical cover of the 
 *	incompletely specified logic function.	
 * Routine:
 * pcover find_canonical_cover():
 *	Finds canonical cover of the incompletely specified logic function
 *	by iteratively calling ess_test_and_reduction for each cube in the
 *	ON-set.
 */

#include <stdio.h>
#include "espresso.h"
#include "signature.h"

/*
 * find_canonical_cover
 * Objective: find canonical cover of the essential signature cube
 * Input:
 *	F: ONSET cover;
 *	D: DC cover;
 *	R: OFFSET cover;
 * Output:
 *	Return canonical cover of the essential signature cube
 */
pcover
find_canonical_cover(F1,D,R)
pcover F1,D,R;
{
	pcover F;
	pcover E,ESC;
	pcover COVER;
	pcube last,p,s;
	pcube c;
	int count = 0;
	int last_fcount = F1->count;
	pcube d, *extended_dc;
	pcube sigma_c;

	F = sf_save(F1);
	E = new_cover(D->count);
	E->count = D->count;
	sf_copy(E,D);

	ESC = new_cover(F->count);
	
	while(F->count){
		c = GETSET(F,--F->count);
		RESET(c,NONESSEN);
		extended_dc = cube2list(E,F);
		d = reduce_cube(extended_dc,c);
		free_cubelist(extended_dc);
		if(setp_empty(d)){
			free_cube(d);
			continue;
		}
		c = get_sigma(R,d);
		S_EXECUTE(COVER = etr_order(F,E,R,c,d),ETR_TIME);
		free_cube(d);
		if(TESTP(c,NONESSEN)){
			sf_append(F,COVER);
		}
		else{
			free_cover(COVER);
			sf_addset(E,c);
			sf_addset(ESC,c);
		}
		free_cube(c);
	}
	free_cover(F);
	free_cover(E);

	return ESC;
}
