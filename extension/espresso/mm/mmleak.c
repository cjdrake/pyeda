#include "copyright.h"
/*
 * mmleak -- program to analyze traced malloc's/free's
 */

#include "port.h"
#include "utility.h"
#include <a.out.h>
#include <stab.h>

/* Version id for trace file */
#define MAGIC		0xA5A5A5A5
#define VER		1
#define VERSION		((MAGIC & ~0xFF) | (VER & 0xFF))

static int debug = 0;

usage(s)
char *s;
{
    (void) fprintf(stderr, "usage: %s [a.out] [malloc.out]\n", s);
}


main(argc, argv)
int argc;
char *argv[];
{
    FILE *nlistFile;
    FILE *traceFile;
    char *name = "a.out";
    char *tracename = "malloc.out";

    if (argc > 3) {
	usage(argv[0]);
	exit(2);
    }

    if (argc >= 2) {
	name = argv[1];
	if (argc == 3) {
	    tracename = argv[2];
	}
    }

    if ((nlistFile = fopen(name, "r")) == NULL) {
	perror(name);
	exit(1);
    }
    if ((traceFile = fopen(tracename, "r")) == NULL) {
	perror(tracename);
	exit(1);
    }

    if (! nlinit(nlistFile)) {
	exit(1);
    }

    if (getw(traceFile) != VERSION) {
	(void) fprintf(stderr, "%s: version mismatch on file %s\n", 
	    argv[0], tracename);
	exit(1);
    }

    while (process(traceFile))
	;
}

/*
 * process -- process the record of allocations
 */

process(fp)
FILE *fp;
{
    int times, size;
    unsigned pc;
    char *prefix;

    size = getw(fp);
    if (feof(fp)) return 0;
    times = getw(fp);

    (void) printf("\nmalloc of %d bytes", size);
    if (times != 1) {
	(void) printf(" (%d times with this same backtrace)", times);
    }
    putchar('\n');

    prefix = "at";
    while ((pc = getw(fp)) != 0) {
	(void) printf("\t%s ", prefix);
	praddr(pc);
	putchar('\n');
	prefix = "called from";

    }

    if (ferror(fp)) {
	(void) fprintf(stderr, "error reading trace file\n");
	exit(1);
    }

    return 1;
}

static struct nlist **nameList;
static int nsyms;

/*
 * nlinit() -- initialize namelist
 */

nlinit(fp)
FILE *fp;
{
    struct exec ahdr;
    struct nlist *sym;
    int i, strsiz, j, n;
    char *strp;
    char *x, *lastfunc;
    int compare();

    /* Read the a.out header */
    if (fread((char *) &ahdr, sizeof(ahdr), 1, fp) != 1) {
	(void) fprintf(stderr, "Error reading a.out header\n");
	return 0;
    }
    if (N_BADMAG(ahdr)) {
	(void) fprintf(stderr, "Bad format detected in object file\n");
	return 0;
    }


    /* Read the symbol table */
    if ((n = ahdr.a_syms / sizeof(struct nlist)) == 0) {
	(void) fprintf(stderr, "No symbol table found\n");
	return 0;
    }
    if (fseek(fp, (long) N_SYMOFF(ahdr), 0) < 0) {
	(void) fprintf(stderr, "Error reading symbol table (fseek)\n");
	return 0;
    }

    nameList = ALLOC(struct nlist *, n+1);
    nsyms = 0;
    for(i = 0; i < n; i++) {
	sym = ALLOC(struct nlist, 1);
	if (fread((char *) sym, sizeof(struct nlist), 1, fp) != 1) {
	    (void) fprintf(stderr, "Error reading symbol table (fread)\n");
	    return 0;
	}
	if ((sym->n_type & N_TYPE) == N_TEXT) {
	    nameList[nsyms++] = sym;
	}
    }


    /* Read the string table */
    if (fread((char *)&strsiz, sizeof(strsiz), 1, fp) != 1) {
	(void) fprintf(stderr, "Error reading string table (old format .o?)");
	return 0;
    }
    strp = ALLOC(char, strsiz);
    if (fread(strp + sizeof(strsiz), strsiz - sizeof(strsiz), 1, fp) != 1) {
	(void) fprintf(stderr, "Error reading string table (fread)\n");
	return 0;
    }


    /* Map each string index into a string pointer */
    lastfunc = "--noname--";
    for(j = 0; j < nsyms; j++) {
	if (nameList[j]->n_un.n_strx) {
	    nameList[j]->n_un.n_name = strp + nameList[j]->n_un.n_strx;
	} else {
	    nameList[j]->n_un.n_name = "";
	}

	/* Record the last function name information as the 
	 *  'name' for the source line number record
	 */
	if (nameList[j]->n_type == N_SLINE) {
	    nameList[j]->n_un.n_name = lastfunc;
	} else if (nameList[j]->n_type == N_FUN) {
	    lastfunc = nameList[j]->n_un.n_name;
	    /* strip trailing :xxx from the function name */
	    if ((x = strchr(lastfunc, ':')) != NULL) {
		*x = '\0';
	    }
	}
    }

    qsort((char *) nameList, nsyms, sizeof(struct nlist *), compare);

    if (debug) {
	for(i = 0; i < nsyms; i++) {
	    printf("\"%s\": n_type=%x n_desc=%d n_value=%x\n",
		nameList[i]->n_un.n_strx, nameList[i]->n_type,
		nameList[i]->n_desc, nameList[i]->n_value);
	}
    }

    return 1;
}


/*
 * compare() -- compare addresses
 */
compare(n1, n2)
struct nlist **n1, **n2;
{
    unsigned n1v = (*n1)->n_value;
    unsigned n2v = (*n2)->n_value;

    if (n1v > n2v) {
	return 1;
    } else if (n1v < n2v) {
	return -1;
    } else {
	return 0;
    }
}


/*
 * praddr(addr) -- print address in nice format
 */
praddr(addr)
unsigned addr;
{
    register int lo, hi, mid;
    register struct nlist *s;

    lo = 0;
    hi = nsyms - 1;
    while (lo < hi) {
	mid = (lo + hi) / 2;
	s = nameList[mid];
	if (addr == s->n_value) {
	    goto found;
	} else if (addr < s->n_value) {
	    hi = mid - 1;
	} else {
	    lo = mid + 1;
	}
    }

    /* Back up 1 if we are still past the target address */
    s = nameList[lo];
    if (addr < s->n_value) {
	if (lo != 0) {
	    s = nameList[lo-1];
	}
    }

found:
    if (s->n_type == N_SLINE) {
	(void) printf("%s at line %d", s->n_un.n_name, s->n_desc);
    } else {
	(void) printf("%s", s->n_un.n_name);
    }
}
