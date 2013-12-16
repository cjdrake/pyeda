#include "copyright.h"
/*
** looptest.c -- intensive allocator tester 
**
** Usage:  looptest
**
** History:
**	4-Feb-1987 rtech!daveb 
*/

#include "port.h"
#include "utility.h"

extern int end;

#define PRINTF	(void) printf

#define MAXITER		25000		/* main loop iterations */
#define MAXOBJS		5000		/* objects in pool */

#define BIGOBJ		20000		/* max size of a big object */
#define TINYOBJ		256		/* max size of a small object */

#define BIGMOD		100		/* 1 in BIGMOD is a BIGOBJ */
#define REALLOCMOD	250		/* 1 in REALLOCMOD is a REALLOC */
#define STATMOD		5000		/* interation interval for status */

#define CHECK_OBJ

char *optProgName;

int
mm_random()
{
    static state = 0;
    state++;
    return state;
}

/*ARGSUSED*/
main(argc, argv)
int argc;
char **argv;
{
    char **objs;	/* array of objects */
    int size;		/* object size */
    int *sizes;		/* array of object sizes */

    register int n;	/* iteration counter */
    register int i;	/* object index */
#ifdef CHECK_OBJ
    register char *p;
    register int j, k;
#endif

    int objmax;		/* max size this iteration */
    int nm = 0;		/* number of mallocs */
    int nre = 0;	/* number of reallocs */

    optProgName = argv[0];

    printf("MAXITER %d MAXOBJS %d ", MAXITER, MAXOBJS );
    printf("BIGOBJ %d, TINYOBJ %d, nbig/ntiny 1/%d\n",
	BIGOBJ, TINYOBJ, BIGMOD );
    printf("Memory use at start: %d bytes\n", 
	(int) sbrk(0) - (int) &end);
    printf("Starting the test...\n");

    objs = ALLOC(char *, MAXOBJS);
    sizes = ALLOC(int, MAXOBJS);

    for( i = 0; i < MAXOBJS; i++ ) {
	objs[ i ] = NULL;
    }

    for(n = 0; n < MAXITER ; n++) {
	if(n % STATMOD == 0) {
	    printf("%d iterations\n", n);
	}

	/* determine object of interest and its size */
	objmax = (mm_random() % BIGMOD != 0) ? TINYOBJ : BIGOBJ;
	size = mm_random() % objmax;
	i = mm_random() % MAXOBJS;

	/* either replace the object or get a new one */
	if (objs[i] == NIL(char)) {
	    objs[i] = ALLOC(char, size);
	    nm++;
	} else {
#ifdef CHECK_OBJ
	    /* check the object before releasing it */
	    p = objs[i];
	    k = i % 127;
	    for(j = sizes[i]; j > 0; j--) {
		if (*p++ != k) {
		    printf("FAILED VERIFY\n");
		    exit(1);
		}
	    }
#endif

	    /* don't keep bigger objects around */
	    if (size > sizes[i] && (mm_random() % REALLOCMOD == 0)) {
		objs[i] = REALLOC(char, objs[i], size);
		nre++;
	    } else {
#ifdef MM_TRACE			/* leave some leaks around ... */
		if ((mm_random() % 100) != 0)
#endif
		    FREE(objs[i]);
		objs[i] = ALLOC(char, size);
		nm++;
	    }
	}
	sizes[i] = size;

#ifdef CHECK_OBJ
	/* Fill the block with data */
	p = objs[i];
	k = i % 127;
	for(j = size; j > 0; j--) *p++ = k;
#endif

    } /* for() */

    printf("Did %d iterations: %d mallocs, %d reallocs\n", 
	n, nm, nre);
    printf("Memory use at end: %d bytes\n", 
	(int) sbrk(0) - (int) &end);

    /* free all the objects */
    for(i = 0; i < MAXOBJS; i++) {
	if (objs[i] != NIL(char)) {
#ifdef CHECK_OBJ
	    p = objs[i];
	    k = i % 127;
	    for(j = sizes[i]; j > 0; j--) {
		if (*p++ != k) {
		    printf("FAILED VERIFY\n");
		    exit(1);
		}
	    }
#endif
	    FREE(objs[i]);
	}
    }

#ifndef MM_TRACE
    FREE(objs);
    FREE(sizes);
#else
    objs[-1] = 0;
#endif

    exit(0);
}
