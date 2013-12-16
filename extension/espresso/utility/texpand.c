/* LINTLIBRARY */
#include "copyright.h"
#include "port.h"
#include "st.h"
#include "utility.h"

#define PATHLEN 1024

#include <pwd.h>

char *
util_tilde_expand(fname)
char *fname;
{
    char username[PATHLEN];
    static char result[8][PATHLEN];
    static int count = 0;
    static st_table *table = NIL(st_table);
    struct passwd *userRecord;
    extern struct passwd *getpwuid(), *getpwnam();
    char *dir;
    register int i, j;

    if (++count > 7) {
	count = 0;
    }

    /* Clear the return string */
    i = 0;
    result[count][0] = '\0';

    /* Tilde? */
    if (fname[0] == '~') {
	j = 0;
	i = 1;
	while ((fname[i] != '\0') && (fname[i] != '/')) {
	    username[j++] = fname[i++];
	}
	username[j] = '\0';

	if (table == NIL(st_table)) {
	    table = st_init_table(strcmp, st_strhash);
	     /* Get CADROOT directory from environment */
	    dir = getenv("OCTTOOLS");
	    if (dir) {
		(void) st_add_direct(table, "octtools", dir);
	    }
	}

	if (!st_lookup(table, username, &dir)) {
	    /* ~/ resolves to the home directory of the current user */
	    if (username[0] == '\0') {
		if ((userRecord = getpwuid(getuid())) != 0) {
		    (void) strcpy(result[count], userRecord->pw_dir);
		    (void) st_add_direct(table, "", util_strsav(userRecord->pw_dir));
		} else {
		    i = 0;
		}
	    } else if ((userRecord = getpwnam(username)) != 0) {
		/* ~user/ resolves to home directory of 'user' */
		(void) strcpy(result[count], userRecord->pw_dir);
		(void) st_add_direct(table, util_strsav(username),
				     util_strsav(userRecord->pw_dir));
	    } else {
		i = 0;
	    }
	} else {
	    (void) strcat(result[count], dir);
	}
    }

    /* Concantenate remaining portion of file name */
    (void) strcat(result[count], fname + i);
    return result[count];
}
