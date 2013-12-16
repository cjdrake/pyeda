/*
 *  Generic linked-list sorting package
 *  Richard Rudell, UC Berkeley, 4/1/87
 *
 *  Use:
 *	#define TYPE		the linked-list type (a struct or typedef)
 *	#define SORT		sorting routine (see below)
 *	#include "lsort.h"
 *
 *  Optional:
 *	#define NEXT		'next' field name in the linked-list structure
 *	#define DECL_SORT	'static' or undefined
 *	#define DECL_SORT1	'static' or undefined
 *	#define SORT1		optional sorting routine interface
 *	#define FIELD		select subfield of the structure for compare
 *	#define DIRECT_COMPARE	in-line expand the compare routine
 *
 *  This defines up to two routines:
 *	DECL_SORT TYPE *
 *	SORT1(list, compare)
 *	TYPE *list;
 *	int (*compare)(TYPE *x, TYPE *y);
 *	    sort the linked list 'list' according to the compare function
 *	    'compare'
 *
 *	DECL_SORT1 TYPE *
 *	SORT(list, compare, length)
 *	TYPE *list;
 *	int (*compare)(TYPE *x, TYPE *y);
 *	int length;
 *	    sort the linked list 'list' according to the compare function
 *	    'compare'.  length is the length of the linked list.
 *
 *  Both routines gracefully handle length == 0 (in which case, list == 0 
 *  is also allowed).
 *
 *  NEXT defines the name of the next field in the linked list.  If not
 *  given, 'next' is assumed.
 *
 *  By default, both routines are declared 'static'.  This can be changed
 *  using '#define DECL_SORT' or '#define DECL_SORT1'.
 *
 *  If FIELD is used, then a pointer to the particular field is passed
 *  to the comparison function (rather than a TYPE *).  In this case,
 *  the compare function is called with:
 *	
 *		if ((*compare)(x->FIELD, y->FIELD)) {
 *
 *  If DIRECT_COMPARE is used, then the 'FIELD' items are compared using
 *  a simple '>' (useful for scalars to save subroutine overhead)
 */

#ifndef NEXT
#define NEXT next
#endif

#ifndef DECL_SORT1
#define DECL_SORT1 static
#endif

#ifndef DECL_SORT
#define DECL_SORT static
#endif

DECL_SORT TYPE *SORT();


#ifdef SORT1

DECL_SORT1 TYPE *
SORT1(list_in, compare)
TYPE *list_in;
int (*compare)();
{
    register int cnt;
    register TYPE *p;

    /* Find the length of the list */
    for(p = list_in, cnt = 0; p != 0; p = p->NEXT, cnt++)
	;
    return SORT(list_in, compare, cnt);
}

#endif

DECL_SORT TYPE *
SORT(list_in, compare, cnt)
TYPE *list_in;
int (*compare)();
int cnt;
{
    register TYPE *p, **plast, *list1, *list2;
    register int i;

    if (cnt > 1) {
	/* break the list in half */
	for(p = list_in, i = cnt/2-1; i > 0; p = p->NEXT, i--)
	    ;
	list1 = list_in;
	list2 = p->NEXT;
	p->NEXT = 0;

	/* Recursively sort the sub-lists (unless only 1 element) */
	if ((i = cnt/2) > 1) {
	    list1 = SORT(list1, compare, i);
	}
	if ((i = cnt - i) > 1) {
	    list2 = SORT(list2, compare, i);
	}

	/* Merge the two sorted sub-lists */
	plast = &list_in;
	for(;;) {
#ifdef FIELD
#ifdef DIRECT_COMPARE
	    if (list1->FIELD < list2->FIELD) {
#else
	    if ((*compare)(list1->FIELD, list2->FIELD) <= 0) {
#endif
#else
	    if ((*compare)(list1, list2) <= 0) {
#endif
		*plast = list1;
		plast = &(list1->NEXT);
		if ((list1 = list1->NEXT) == 0) {
		    *plast = list2;
		    break;
		}
	    } else {
		*plast = list2;
		plast = &(list2->NEXT);
		if ((list2 = list2->NEXT) == 0) {
		    *plast = list1;
		    break;
		}
	    }
	}
    }

    return list_in;
}

#undef TYPE
#undef SORT
#undef SORT1
#undef DECL_SORT
#undef DECL_SORT1
#undef FIELD
#undef DIRECT_COMPARE
#undef NEXT
