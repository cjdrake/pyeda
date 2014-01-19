#include "espresso.h"
#include "signature.h"


/*
 * signature_minimize_exact:
 * What does it do: forms and solves the covering table whose rows are
 *	essential signature cubes (ESCubes) and whose columns are
 *	union of essential signature sets (ESSet)
 * Input:
 *	ESCubes: essential signature cubes
 *	ESSet: union of essential signature sets
 * Output:
 *	COVER: exact cover
 */

set_family_t *
signature_minimize_exact(ESCubes,ESSet)
set_family_t *ESCubes, *ESSet;
{
	set *p;
	sm_matrix *table;
	sm_row *cover;
	sm_element *pe;
	set_family_t *COVER;
	int index;
	int *weights,heur,level;

	/* number ESCubes, ESSet */
	foreachi_set(ESCubes,index,p){
		PUTSIZE(p,index);
	}
	foreachi_set(ESSet,index,p){
		PUTSIZE(p,index);
	}

	/* form the covering table */
	table = signature_form_table(ESCubes, ESSet);

	/* solve the covering problem */
	weights = NIL(int); heur = FALSE; level = 0;
	cover = sm_minimum_cover(table,weights,heur,level);

	/* form the cover */
	COVER = sf_new(100, cube.size);
	sm_foreach_row_element(cover, pe) {
		COVER = sf_addset(COVER, GETSET(ESSet, pe->col_num));
	}

	sm_free(table);
	sm_row_free(cover);

	return COVER;
}

sm_matrix *
signature_form_table(ESCubes, ESSet)
set_family_t *ESCubes, *ESSet;
{
	sm_matrix *table;
	int row,column;
	set *c, *p;
	int col_deleted;

	table = sm_alloc();

	col_deleted = 0;
	foreachi_set(ESSet,column,p){
		if(column%1000 == 0){
			col_deleted += sm_col_dominance(table,NULL);
		}
		foreachi_set(ESCubes,row,c){
			if(setp_implies(c,p)){
				sm_insert(table,row,column);
			}
		}
	}
	col_deleted += sm_col_dominance(table,NULL);

	return table;
}
