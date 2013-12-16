/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * strcspn - find length of initial segment of s consisting entirely
 * of characters not from reject
 */

SIZET
strcspn(s, reject)
CONST char *s;
CONST char *reject;
{
	register CONST char *scan;
	register CONST char *rscan;
	register SIZET count;

	count = 0;
	for (scan = s; *scan != '\0'; scan++) {
		for (rscan = reject; *rscan != '\0';)	/* ++ moved down. */
			if (*scan == *rscan++)
				return count;
		count++;
	}
	return count;
}
#endif
