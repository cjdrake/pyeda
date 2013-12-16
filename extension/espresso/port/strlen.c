/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * strlen - length of string (not including NUL)
 */
SIZET
strlen(s)
CONST char *s;
{
	register CONST char *scan;
	register SIZET count;

	count = 0;
	scan = s;
	while (*scan++ != '\0')
		count++;
	return count;
}
#endif
