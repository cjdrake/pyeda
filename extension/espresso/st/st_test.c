/*
 * Hash table tester
 * Peter Moore
 */

#include "copyright.h"
#include "port.h"
#include "st.h"

#define strsave(string) strcpy(malloc((unsigned) strlen(string)+1), string)

char *optProgName;		/* For errTrap package */

char *usage = "? - help\ni name number - insert number under name\nl name - lookup name\nd name - delete name\np name - print table\nc - clear the table\n^D - exit\n";

enum st_retval print_entry(), free_entry();

main(argc, argv)
int argc;
char **argv;
{
    int c, val;
    char name[20], *ptr, *value;
    int number;
    st_table *table;

    optProgName = argv[0];
    if (argc > 1) {
        table = st_init_table_with_params(strcmp, st_strhash,
					  ST_DEFAULT_INIT_TABLE_SIZE,
					  ST_DEFAULT_MAX_DENSITY,
					  ST_DEFAULT_GROW_FACTOR, 1);
    } else {
	table = st_init_table(strcmp, st_strhash);
    }

    (void) printf(usage);

    val = 0;
    for(;;) {

	(void) printf("%d> ", val++);
	c = fetch();

	switch(c) {
	    
	    case '?' :
		(void) printf(usage);
		break;

	    case 'i' :
		(void) scanf("%s", name);
		(void) scanf("%d", &number);
		(void) printf("Inserting %d for %s\n", number, name);
		if (st_lookup(table, name, (char **) 0)) {
			/* don't bother to save the name */
		    (void) st_insert(table, name, (char *)number);
		} else {
		    (void) st_insert(table, strsave(name), (char *)number);
		}
		break;

	    case 'l' :
		(void) scanf("%s", name);
		if (st_lookup(table, name, &value)) {
		    (void) printf("Found %d for %s\n", (int) value, name);
		} else {
		    (void) printf("Nothing found under %s\n", name);
		}
		break;

	    case 'd' :
		(void) scanf("%s", name);
		ptr = name;
		if (st_delete(table, &ptr, &value)) {
		    (void) printf("Deleted %d for %s\n", (int) value, name);
		    if (ptr != 0) {
			free(ptr);
		    }
		} else {
		    (void) printf("Nothing found under %s\n", name);
		}
		break;
	    
	    case 'p' :
		(void) printf("Dumping the table :\n");
		(void) st_foreach(table, print_entry, (char *) 34);
		break;
	    
	    case 'c' :
		(void) printf("Clearing all entries");
		(void) st_foreach(table, free_entry, (char *) 34);
		break;

	    case EOF :
		(void) st_foreach(table, free_entry, (char *) 34);
		st_free_table(table);
		(void) printf("Exiting\n");
		exit(0);
		break;
	}
    }
}

enum st_retval
print_entry(name, record, junk)
char *name;
char *record;
int junk;
{
    (void) printf("%s is %d (%d)\n", name, record, junk);
    return ST_CONTINUE;
}

/*ARGSUSED*/
enum st_retval
free_entry(name, record, junk)
char *name;
char *record;
int junk;
{
    (void) printf("Freeing %s (%d)\n", name, record);
    free(name);
    return ST_DELETE;
}

int fetch()
/* Gets a non-space character */
{
    int c;

    while (isspace((c = getchar()))) {
	/* EMPTY */
    }
    return c;
}

