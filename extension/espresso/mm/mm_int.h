#ifndef MM_INT_H
#define MM_INT_H

#ifdef MM_TRACE
#define MM_PARANOID
#endif

#define MM_PKG_NAME "mm"

#ifndef NIL
#define NIL(type)		((type *) 0)
#endif

extern char *sbrk();
static char *sbrk_last = NIL(char);	/* pointer to free page */
static long sbrk_remaining = -1;	/* number of bytes remaining on page */
static char *lo_water_mark = NIL(char);	/* lo-water mark on sbrk() */
static char *hi_water_mark = NIL(char);	/* hi-water mark on sbrk() */

#define ALIGNMENT	sizeof(double)
#define SMALL_SIZE	256
#define LOG_SMALL_SIZE	8
#define BINS 		(SMALL_SIZE/ALIGNMENT + 32 * 2 + 1)

#define MAGIC		0xA5A5A5A5	/* magic value at header/trailer */
#ifndef PAGE_SIZE
#define PAGE_SIZE	65536		/* page size for sbrk() */
#endif

static long obj_allocated = 0, obj_active = 0;
static long bytes_allocated = 0, bytes_active = 0;
static long max_bytes_active = 0;

void MMprintStats();
static void find_more_memory();


#ifdef MM_PARANOID

#ifndef MM_NPARANOID
#define MM_NPARANOID			1
#endif

#define TRAILER_SIZE			(2*MM_NPARANOID*sizeof(long))

/* These are macro's so MM_PARANOID can give reasonable performance */ 
#define insert_trailer(p) {\
    register long *l, i;\
    l = (long *) ((char *) p + sizeof(memory_block));\
    for(i = 0; i < MM_NPARANOID; i++) l[i] = MAGIC;\
    l = (long *) ((char *) p + sizeof(memory_block) +\
	MM_NPARANOID*sizeof(long) + p->request);\
    for(i = 0; i < MM_NPARANOID; i++) l[i] = MAGIC;\
}

#define check_trailer(p, x) {\
    register long *l, i;\
    *(x) = 0;\
    l = (long *) ((char *) p + sizeof(memory_block));\
    for(i = 0; i < MM_NPARANOID; i++) if (l[i] != MAGIC) *(x)=1;\
    l = (long *) ((char *) p + sizeof(memory_block) +\
	MM_NPARANOID*sizeof(long) + p->request);\
    for(i = 0; i < MM_NPARANOID; i++) if (l[i] != MAGIC) *(x)=2;\
}

#else		/* not MM_PARANOID */
#define TRAILER_SIZE			(0)
#endif


#ifdef MM_TRACE
#include "trace.c"

#else		/* not MM_TRACE */

/*
 *  Normal operation, no active list is maintained.  The free list is
 *  singly linked using nextblock.  For an allocated block, binnum has
 *  the bin number which is used when the block is freed.  An extra
 *  long is placed at the beginning and end of the block to detect write 
 *  past end of block (when MM_PARANOID is enabled).
 */
typedef struct memory_block_struct memory_block;
struct memory_block_struct {
    union memory_block_union {
	memory_block *u_nextblock;	/* pointer to next block */
	long u_binnum;			/* remember bin number */
    } mem_union;
#ifdef MM_PARANOID
    long request;			/* size user asked for */
#endif
};

#define nextblock	mem_union.u_nextblock
#define binnum		mem_union.u_binnum
static memory_block *free_list[BINS];

#endif		/* #ifdef MM_TRACE */

/* GET_BIN -- determine the bin number based on the size; this is magic */
#define GET_BIN(bin, size){\
    register unsigned long n, log;\
    if ((size) <= 0) (bin) = 0;\
    else if ((size) <= SMALL_SIZE) (bin) = ((size) - 1) / ALIGNMENT + 1;\
    else {\
	for(log = LOG_SMALL_SIZE, n = ((size)-1) >> log; n > 0; log++, n>>=1);\
	(bin) = log*2 + SMALL_SIZE/ALIGNMENT - 2*LOG_SMALL_SIZE \
	    - ((size) <= (3 << (log-2)));\
    }\
}


/* GET_SIZE -- get the block size from the bin number; this is magic */
#define GET_SIZE(bin, size) {\
    register unsigned long tmp;\
    if ((bin) <= SMALL_SIZE/ALIGNMENT) (size) = (bin) * ALIGNMENT;\
    else {\
	tmp = (bin) - SMALL_SIZE/ALIGNMENT + 2*LOG_SMALL_SIZE - 3;\
	(size) = ((tmp & 1) == 0 ? 3 : 4) << (tmp >> 1);\
    }\
}

#endif /* MM_INT_H */
