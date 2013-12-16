/* Version id for trace file */
#define VER		1
#define VERSION		((MAGIC & ~0xFF) | (VER & 0xFF))

#define MAX_STACK_TRACE	15		/* trace-back only 15 levels */

/*
 *  Active list is doubly linked using nextblock and prevblock, binnum
 *  tells to which bin it belongs, and stack_trace contains valid data
 *  giving the call stack when the object was allocated.  The free list
 *  is singly linked using nextblock; prevblock, binnum and stack_trace
 *  are unused.
 */
typedef struct memory_block_struct memory_block;
struct memory_block_struct {
    memory_block *nextblock;		/* pointer to next block */
    memory_block *prevblock;		/* pointer to previous block */
    long binnum;                        /* remember bin number */
    int stack_trace[MAX_STACK_TRACE];	/* stack backtrace for leaks */
#ifdef MM_PARANOID
    long request;			/* size user asked for */
#endif
};

static memory_block *free_list[BINS], *active_list[BINS];
static memory_block *list_sort();

extern int thispc(), whence(), nextfp();


static void
unwind_call_stack(p)
memory_block *p;
{
    register int i;
    int ret, pc;

    /* Trace of call addrs will be null-terminated */
    for (i = 0, ret = whence(); ret != 0; ret = nextfp(ret)) {
	pc = thispc(ret);
	p->stack_trace[i++] = pc;
	/* ending condition is not very machine independent ! */
        if (pc < 0x50 || i >= MAX_STACK_TRACE - 1) {
            break;
	}
    }
    p->stack_trace[i] = 0;
}


static int 
comp_memory_block(m1, m2)
memory_block *m1, *m2;
{
    register int *p1 = m1->stack_trace;
    register int *p2 = m2->stack_trace;

    if (m1->request != m2->request) {
	return m1->request - m2->request;
    } else {
	while (*p1 == *p2++) {
	    if (*p1++ == 0) {
		return 0;
	    }
	}
	return *p1 - *--p2;
    }
}


/* hack to avoid using stdio, because we've free'd it by malloc_write time */
#include <sys/file.h>
static char buffer[BUFSIZ];
static int buffern = 0;
static int fd;
#define wflush() {\
    (void) write(fd, buffer, buffern);\
    buffern = 0;\
}
#define wbyte(_c) {\
    buffer[buffern++] = _c;\
    if (buffern >= BUFSIZ) wflush();\
}
#define wshort(_i) {\
    int _j; short _val = _i;\
    char *_p = (char *) &_val;\
    for(_j = 0; _j < sizeof(short); _j++) wbyte(*_p++);\
}
#define wlong(_i) {\
    long _j, _val = _i;\
    char *_p = (char *) &_val;\
    for(_j = 0; _j < sizeof(long); _j++) wbyte(*_p++);\
}


static void
mallocTraceWrite(p, size, times)
memory_block *p;
long size, times;
{
    int i, pc;

    wlong(size);
    wlong(times);

    /* Trace of call addrs will be null-terminated */
    for(i = 0; i < MAX_STACK_TRACE; i++) {
	pc = p->stack_trace[i];
	wlong(pc);
        if (pc < 0x40) break;
    }
    if (pc != 0) wlong(0);
}


static void
write_malloc_out()
{
    long i, eql, cnt, size;
    register memory_block *p1, *p2;
    char msg[1024];

    if ((fd = open("malloc.out", O_CREAT | O_TRUNC | O_WRONLY, 0666)) < 0) {
	if ((fd = open("/dev/tty", O_WRONLY)) >= 0) {
	    (void) sprintf(msg, "Unable to open malloc.out\n");
	    (void) write(fd, msg, strlen(msg));
	    (void) close(fd);
	}
	return;
    }

    wlong(VERSION);

    cnt = 0;
    for(i = 0; i < BINS; i++) {
	if (active_list[i] != NIL(memory_block)) {

	    /* sort these objects by their back-trace */
	    active_list[i] = list_sort(active_list[i], comp_memory_block);

	    /* Count unique objects by backtrace, and output them */
	    eql = 0;
	    for(p1 = active_list[i]; p1 != 0; p1 = p1->nextblock) {
		eql++;
		p2 = p1->nextblock;
		if (p2 == NIL(memory_block) || comp_memory_block(p1, p2) != 0) {
		    size = p1->request;
		    mallocTraceWrite(p1, size, eql);
		    cnt++;
		    eql = 0;
		}
	    }
	}
    }

    wflush();
    (void) close(fd);

    if ((fd = open("/dev/tty", O_WRONLY)) >= 0) {
	(void) sprintf(msg,
	    "%ld object(s) still active at program termination\n%ld %s", 
	    obj_active, cnt,
	    "unique stack trace(s) dumped to file malloc.out\n"); 
	(void) write(fd, msg, strlen(msg));
	(void) close(fd);
    }
}


static void
dump_single_pointer(p)
memory_block *p;
{
    int i;
    for(i = 0; i < BINS; i++) {
	active_list[i] = 0;
    }
    active_list[0] = p;
    p->nextblock = 0;
    p->prevblock = 0;
    write_malloc_out();
}


static void 
check_pointer(p)
memory_block *p;
{
    long bin;

    if ((char *) p < lo_water_mark || (char *) p > hi_water_mark) {
	(void) fprintf(stderr, "check: bogus pointer on active list");
	dump_single_pointer(p);
	(void) _exit(1);
    }
    bin = p->binnum;

    /* Check for binnum in bounds, and for magic number (high order) */
    if (((bin & ~0xFFF) != (MAGIC & ~0xFFF)) || ((bin & 0xFFF) >= BINS)) {
	if (block_is_free(p)) {
	    (void) fprintf(stderr, "check: free pointer on active list");
	} else {
	    (void) fprintf(stderr, "check: corrupt pointer on active list");
	}
	dump_single_pointer(p);
	(void) _exit(1);
    }

#ifdef MM_PARANOID	/* always true ... */
{
    int status;
    check_trailer(p, &status);
    if (status != 0) {
	if (status == 1) {
	    (void) fprintf(stderr, 
		"check: corrupt pointer (write before beginning of block)\n");
	} else {
	    (void) fprintf(stderr, 
		"check: corrupt pointer (write past end of block)\n");
	}
	dump_single_pointer(p);
	(void) _exit(1);
    }
}
#endif
}


static void
check_all_pointers()
{
    memory_block *p;
    int i;

    for(i = 0; i < BINS; i++) {
	for(p = active_list[i]; p != 0; p = p->nextblock) {
	    check_pointer(p);
	}
    }
}


void exit(code)
int code;
{
    check_all_pointers();
    _cleanup();
    write_malloc_out();
    (void) _exit(code);
}
