/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * memcmp - compare bytes
 */

int				/* <0, == 0, >0 */
memcmp(s1, s2, size)
CONST VOIDSTAR s1;
CONST VOIDSTAR s2;
SIZET size;
{
	register CONST char *scan1;
	register CONST char *scan2;
	register SIZET n;

	scan1 = s1;
	scan2 = s2;
	for (n = size; n > 0; n--)
		if (*scan1 == *scan2) {
			scan1++;
			scan2++;
		} else
			return *scan1 - *scan2;

	return 0;
}
#endif
