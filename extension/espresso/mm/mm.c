#include "copyright.h"
#include "port.h"
#include "errtrap.h"
#include "mm_int.h"
#include "mm.h"

/*
 *  Memory allocator with the following features:
 *
 *	1) Uses bins for objects up to a fixed size, and uses logarithmic 
 *         binning (with interpolation) for larger objects
 *
 *	2) Calls sbrk() to get large blocks (currently 64K bytes)
 *
 *      3) Checks for free object being freed, and corrupt objects;
 *	   Attempts to avoid core-dumping when passed a bad pointer
 *
 *	4) Attempts to compact free blocks when sbrk() fails
 *
 *	4) Option (MM_PARANOID) to perform bounds checking on each object
 *	   when that object is free'd.  Also trashes each block to catch
 *	   initialized assumptions, and attempts to use blcok after free.
 *
 *	5) Option (MM_TRACE) to record stack backtraces and dump to a file
 *	   information on each object still allocated at termination.
 *
 *  #Define options:
 *
 *  MM_PARANOID enables code to place extra word(s) at the start and
 *  end of each block to try to catch errors when the object is freed.
 *  MM_NPARANOID is the number of words to place at each end of the
 *  block.  
 *
 *  MM_TRACE enables code which keeps a stack trace with each
 *  allocation, and maintains a list of allocated objects (as well as
 *  the list of free objects) to allow detection of "leaks" when the
 *  program terminates.  This option implies MM_PARANOID, and also
 *  proceeds to check all objects which are still active when the
 *  program terminates.
 *
 *  MM_FILL fills each block with a fixed pattern when the block is
 *  allocated or free'd.  This attempts to find assumptions about
 *  initialization of malloc()'ed memory, and assumptions that an
 *  object can be de-referenced after being free'ed.
 *
 *  WARNING: Do not compile MM_TRACE with -pg; compile it with -g so that 
 *  prleak can print out the function name and source line number.
 *
 *  TODO:
 *	allow for arbitrary precision on interpolation of bins
 *	have first allocation round to 4k boundary ? Necessary ?
 *	salloc(obj, size) / sfree(obj, size) to avoid 4-word overhead
 *	    on very small objects
 */

/* LINTLIBRARY */

void
mm_set(a, b)
int a, b;
{
    return;
}

/* block_is_free -- see if a block is already on the free list */
static int
block_is_free(block)
memory_block *block;
{
    memory_block *p;
    int i;

    for(i = 0; i < BINS; i++) {
	for(p = free_list[i]; p != NIL(memory_block); p = p->nextblock) {
	    if (block == p) {
		return 1;
	    }
	}
    }
    return 0;
}


/* rebin -- place a block into the free list */
static void
rebin(block, size)
char *block;
long size;
{
    long bin, actual_bin_size;
    memory_block *p;

    if (size >= 4) {
	p = (memory_block *) block;
        /*
         * (bin, actual_bin_size) refers to the first bin with blocks
         * that are larger than (or equal to) 'size'.  If this is in fact
         * not the same size as 'size', then we must drop down a bin,
         * and then re-bin the remainder 
	 */
	GET_BIN(bin, size);
	GET_SIZE(bin, actual_bin_size);
	if (actual_bin_size != size) {
	    bin--;
	    GET_SIZE(bin, actual_bin_size);
	    rebin(block+actual_bin_size, size - actual_bin_size);
	}
	p->nextblock = free_list[bin];
	free_list[bin] = p;
    }
}


#ifdef DEBUG
static void
free_list_histogram()
{
    long i, size, cnt;
    memory_block *p;

    for(i = 0; i < BINS; i++) {
	if (free_list[i] != NIL(memory_block)) {
	    cnt = 0;
	    for(p = free_list[i]; p != NIL(memory_block); p = p->nextblock) {
		cnt++;
	    }
	    GET_SIZE(i, size);
	    (void) fprintf(stderr,
		"free_list bin %2d (size %5d) has %d objects\n", i, size, cnt);
	}
    }
}
#endif

/*
 *  malloc -- allocate a block of memory 
 */

char *
malloc(bytes)
unsigned bytes;
{
    char *block;
    register long bin, alloc_size, request;
    register memory_block *p;

    /* Decide how much we must really allocate */
    request = bytes + sizeof(memory_block) + TRAILER_SIZE;
    if (request < 8) request = 8;

    /* Determine which bin, and then how much we really need */
    GET_BIN(bin, request);
    GET_SIZE(bin, alloc_size);

    /* See if we have a block in the free list for this bin */
    if ((p = free_list[bin]) == NIL(memory_block)) {

        /* Must allocate a new block, check for space on the current page */
	if (sbrk_remaining < alloc_size) {

	    /* take remaining stuff on current page and place in free list */
	    rebin(sbrk_last, sbrk_remaining);

	    /* when PAGE_SIZE divides alloc_size this allocates an extra page
	     * worth; this is of no concern to us, we will use it eventually
	     */
	    sbrk_remaining = (alloc_size / PAGE_SIZE + 1) * PAGE_SIZE;
	    sbrk_last = sbrk((int) sbrk_remaining);

	    /* See if the sbrk() failed; if so, hunt around for more memory */
	    if ((int) sbrk_last == -1 || sbrk_last == NIL(char)) {
		find_more_memory(bin);
		if (sbrk_last == NIL(char)) {
		    errRaise(MM_PKG_NAME, 0, "out of memory");
		}
	    } else {
		/* keep track of lowest address and highest address seen */
		if (lo_water_mark == NIL(char) || sbrk_last < lo_water_mark) {
		    lo_water_mark = sbrk_last;
		}
		if (hi_water_mark == NIL(char) ||
		    sbrk_last + sbrk_remaining - 1 > hi_water_mark) {
			hi_water_mark = sbrk_last + sbrk_remaining - 1;
		}
		obj_allocated++;
		bytes_allocated += sbrk_remaining;
	    }
	}

	/* Peel off a piece from 'sbrk_last' for the next object */
	p = (memory_block *) sbrk_last;
	sbrk_last += alloc_size;
	sbrk_remaining -= alloc_size;

    } else {
        /* We can reuse the first entry on the garbage list for this size */
        free_list[bin] = p->nextblock;
    }

    /* Make sure the pointer looks good */
    if ((char *) p < lo_water_mark || (char *) p > hi_water_mark) {
	errRaise(MM_PKG_NAME, 0, "free list was corrupted somehow ...");
    }

    /* Save the bin-number and a MAGIC number */
    p->binnum = bin | (MAGIC & ~ 0xFFF);

    /* Keep some simple stats */
    obj_active++;
    bytes_active += alloc_size;
    if (bytes_active > max_bytes_active) max_bytes_active = bytes_active;

    /* Advance to the spot we'll hand back to the user */
    block = (char *) p + sizeof(memory_block) + TRAILER_SIZE/2;

#ifdef MM_PARANOID
    p->request = bytes;
    insert_trailer(p);
#ifdef MM_FILL
    memset(block, 0x40, bytes);		/* fill the block with garbage */
#endif
#endif

#ifdef MM_TRACE
    /* Link the block into the active list for this bin (double-link list) */
    p->nextblock = active_list[bin];
    p->prevblock = NIL(memory_block);
    if (p->nextblock != NIL(memory_block)) {
	p->nextblock->prevblock = p;
    }
    active_list[bin] = p;

    /* Get the call stack, and save it in the block */
    unwind_call_stack(p);
#endif

    return block;
}

/* 
 *  free -- free the memory allocated by malloc() 
 */

VOID_HACK
free(block)
char *block;
{
    register memory_block *p;
    register long bin, size;

    if (block == NIL(char)) return;

    /* Dereference the block */
    p = (memory_block *) (block - sizeof(memory_block) - TRAILER_SIZE/2);
    if ((char *) p < lo_water_mark || (char *) p > hi_water_mark) {
	errRaise(MM_PKG_NAME, 0, "attempt to free() bogus pointer");
    }
    bin = p->binnum;

    /* Check for binnum in bounds, and for magic number (high order) */
    if (((bin & ~0xFFF) != (MAGIC & ~0xFFF)) || ((bin & 0xFFF) >= BINS)) {
	if (block_is_free(p)) {
	    errRaise(MM_PKG_NAME, 0, "attempt to free() pointer which is already free");
	} else {
	    errRaise(MM_PKG_NAME, 0, "attempt to free() corrupt pointer");
	}
	return;
    }
    bin &= 0xFFF;

    obj_active--;
    GET_SIZE(bin, size);
    bytes_active -= size;

#ifdef MM_PARANOID
{   
    int status;
    check_trailer(p, &status);
    if (status != 0) {
	if (status == 1) {
	    errRaise(MM_PKG_NAME, 0, "corrupt pointer (write before beginning of object)");
	} else {
	    errRaise(MM_PKG_NAME, 0, "corrupt pointer (write past end of object)");
	}
    }
#ifdef MM_FILL
    memset(block, 0x40, p->request);	/* fill block with garbage */
#endif
}
#endif

#ifdef MM_TRACE
    /* unlink p from the active list for this block size */
    if (p->prevblock == NIL(memory_block)) {
	active_list[bin] = p->nextblock;
    } else {
	p->prevblock->nextblock = p->nextblock;
    }
    if (p->nextblock != NIL(memory_block)) {
	p->nextblock->prevblock = p->prevblock;
    }
    p->binnum = 0;		/* make the bin number corrupt */
#endif

    /* Link p into the free list for this block size */
    p->nextblock = free_list[bin];
    free_list[bin] = p;
}

/*  
 *  realloc -- re-allocate a block of memory  
 */

char *
realloc(block, new_size)
char *block;
unsigned new_size;
{
    register long bin, size;
    register memory_block *p;
    char *new_block;
    long data_size;

    if (block == NIL(char)) return malloc(new_size);

    /* Dereference the block */
    p = (memory_block *) (block - sizeof(memory_block) - TRAILER_SIZE/2);
    if ((char *) p < lo_water_mark || (char *) p > hi_water_mark) {
	errRaise(MM_PKG_NAME, 0, "attempt to realloc() bogus pointer");
    }
    bin = p->binnum;

    /* Check for binnum in bounds, and for magic number */
    if (((bin & ~0xFFF) != (MAGIC & ~0xFFF)) || ((bin & 0xFFF) >= BINS)) {
	if (block_is_free(p)) {
	    errRaise(MM_PKG_NAME, 0, "attempt to realloc() an already free pointer");
	} else {
	    errRaise(MM_PKG_NAME, 0, "attempt to realloc() corrupt pointer");
	}
	return NIL(char);
    }
    bin &= 0xFFF;
    GET_SIZE(bin, size);

#ifdef MM_PARANOID
{   
    int status;
    check_trailer(p, &status);
    if (status != 0) {
	if (status == 1) {
	    errRaise(MM_PKG_NAME, 0, "corrupt pointer (write before beginning of object)");
	} else {
	    errRaise(MM_PKG_NAME, 0, "corrupt pointer (write past end of object)");
	}
    }
}
#endif

    /* Check if there already is enough room */
    data_size = size - (sizeof(memory_block) + TRAILER_SIZE);
    if (data_size >= new_size) {
	new_block = block;
#ifdef MM_PARANOID
 	p->request = new_size;
	insert_trailer(p);
#endif
    } else {
	if ((new_block = malloc(new_size)) != NIL(char)) {
	    (void) memcpy(new_block, block, (int) data_size);
	    free(block);
	}
    }

    return new_block;
}

/*
 *  Bring in the generic linked-list sorting package
 */

#define SORT 		list_sort_length
#define SORT1 		list_sort
#define NEXT 		nextblock
#define TYPE 		memory_block
#include "lsort.h"


#define SIZE_FIELD(p)		(*(long *) (p + 1))

/* ARGSUSED */
static int 
four_byte_hack(p)
memory_block *p;
{
#ifdef REAL_SLOW
    memory_block **prevp1, *p1;

    /* walk down 4-byte list looking for 'p2' */
    prevp1 = &(free_list[1]);
    for(p1 = free_list[1]; p1 != NIL(memory_block); p1 = p1->nextblock) {
	if ((char *) p + SIZE_FIELD(p) == (char *) p1) {
	    /* unlink the block from the free list, and return */ 
	    *prevp1 = p1->nextblock;
	    return 1;
	} 
	prevp1 = &(p1->nextblock);
    }
    return 0;
#else
    /* 
     *  we just assume any missing four-byte chunk is on the free-list
     *  this is mostly safe because be never allocate less than 8 bytes
     *  for any object we give back to the user.
     *  It will fail, however, if someone attempts to sbrk(4) behind our
     *  back -- we may reclaim his memory !
     */
    free_list[1] = 0;
    return 1;
#endif
}


/* Sort the memory block by their address */
static int 
compact_compare(p1, p2)
memory_block *p1, *p2;
{
    return p1 - p2;
}


static void 
compact_memory()
{
    long i, size, cnt, byte_cnt;
    memory_block *pnext, *last, *head, *p;

#ifdef DEBUG
    (void) fprintf(stderr, "MM: compacting memory\n");
    free_list_histogram();
    (void) fflush(stdout);
#endif

    /* 
     *  Place all blocks in a single linked-list; cheat and place the size
     *  in the first longword of each memory object;
     */
    head = NIL(memory_block);
    byte_cnt = cnt = 0;
    for(i = 2; i < BINS; i++) {
	if (free_list[i] != NIL(memory_block)) {
	    GET_SIZE(i, size);
	    for(p = free_list[i]; p != NIL(memory_block); p = p->nextblock) {
		SIZE_FIELD(p) = size;
		last = p;
		cnt++;
		byte_cnt += size;
	    }
	    last->nextblock = head;
	    head = free_list[i];
	    free_list[i] = NIL(memory_block);
	}
    }

#ifdef DEBUG
    (void) fprintf(stderr,
	"%ld free objects totaling %ld bytes\n", cnt, byte_cnt);
    (void) fflush(stdout);
#endif

    /* gratituous use of byte_cnt to shut up lint */
    if (byte_cnt == 0 || head == NIL(memory_block)) return;

    /* Sort this by address */
    head = list_sort_length(head, compact_compare, cnt);

    /* Coallesce adjacent blocks */
    for(p = head; p != NIL(memory_block); ) {

	/* See if the block fits perfectly */
	if ((char *) p + SIZE_FIELD(p) == (char *) p->nextblock) {
	    SIZE_FIELD(p) += SIZE_FIELD(p->nextblock);
	    p->nextblock = p->nextblock->nextblock;

	/* See if the block fits (except for a 4-byte missing chunk) */
	} else if ((char *) p + SIZE_FIELD(p) + 4 == (char *) p->nextblock) {
	    if (four_byte_hack(p)) {
		SIZE_FIELD(p) += SIZE_FIELD(p->nextblock) + 4;
		p->nextblock = p->nextblock->nextblock;
	    } else {
		p = p->nextblock;	/* no match */
	    }

	/* it just doesn't match */
	} else {
	    p = p->nextblock;
	}
    }

    /* Re-bin each of the blocks */
    cnt = 0;
    for(p = head; p != NIL(memory_block); p = pnext) {
	pnext = p->nextblock;
	cnt++;
	rebin((char *) p, SIZE_FIELD(p));
    }

#ifdef DEBUG
    (void) fprintf(stderr, "%ld free objects after compaction\n", cnt);
    free_list_histogram();
    (void) fflush(stdout);
#endif
}

static void 
find_more_memory(start_bin)
long start_bin;
{
    long bin, loop;

    for(loop = 0; loop < 2; loop++) {
	/* First look for a larger block to tear apart */
	for(bin = start_bin+1; bin < BINS; bin++) {
	    if (free_list[bin] != NIL(memory_block)) {
		sbrk_last = (char *) free_list[bin];
		GET_SIZE(bin, sbrk_remaining);
		free_list[bin] = free_list[bin]->nextblock;
		return;
	    }
	}

	/* okay, play hardball now -- compact the free memory list */
	if (loop == 0) compact_memory();
    }

    /* There's only so much we can do about it (buy more memory ?) */
    sbrk_last = NIL(char);
    sbrk_remaining = -1;
    return;
}


/* MMstats -- report memory usage statistics */
void
MMstats(active_objs, alloc_objs, active_bytes, alloc_bytes, max_bytes)
long *active_objs, *alloc_objs, *active_bytes, *alloc_bytes, *max_bytes;
{
    *active_objs = obj_active;
    *alloc_objs = obj_allocated;
    *active_bytes = bytes_active;
    *alloc_bytes = bytes_allocated;
    *max_bytes = max_bytes_active;
}


/* MMprintStats -- print memory usage statistics */
void
MMprintStats(fp)
FILE *fp;
{
    long active_objs, alloc_objs, active_bytes, alloc_bytes, max_bytes;

    MMstats(&active_objs, &alloc_objs, &active_bytes, &alloc_bytes, &max_bytes);
    (void) fprintf(fp, "# Memory use: %ldK bytes (%ld objects) active",
	(active_bytes + 512)/1024, active_objs);
    (void) fprintf(fp, " out of %ldK bytes allocated (%ldK)\n",
	(alloc_bytes + 512)/1024, (max_bytes + 512)/1024);
}

int MMcheckValidPointer(block)
char *block;
{
    long bin;
    memory_block *p;

    /* Dereference the block */
    p = (memory_block *) (block - sizeof(memory_block) - TRAILER_SIZE/2);
    if ((char *) p < lo_water_mark || (char *) p > hi_water_mark) {
	return 0;
    }
    bin = p->binnum;

    /* Check for binnum in bounds, and for magic number (high order) */
    if (((bin & ~0xFFF) != (MAGIC & ~0xFFF)) || ((bin & 0xFFF) >= BINS)) {
	return 0;
    }

#ifdef MM_PARANOID
{   
    int status;
    check_trailer(p, &status);
    if (status != 0) {
	return 0;
    }
}
#endif
    return 1;
}


#ifdef MM_TRACE
int MMcheckValid()
{
    int i;
    memory_block *p;
    char *block;

    for(i = 0; i < BINS; i++) {
	for(p = active_list[i]; p != NIL(memory_block); p = p->nextblock) {
	    block = (char *) p + sizeof(memory_block) + TRAILER_SIZE/2;
	    if (! MMcheckValidPointer(block)) {
		errRaise(MM_PKG_NAME, 0, "bad pointer on active list");
	    }
	}
    }
}
#endif
