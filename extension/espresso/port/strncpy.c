/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * strncpy - copy at most n characters of string src to dst
 */
char *				/* dst */
strncpy(dst, src, n)
char *dst;
CONST char *src;
SIZET n;
{
	register char *dscan;
	register CONST char *sscan;
	register SIZET count;

	dscan = dst;
	sscan = src;
	count = n;
	while (--count >= 0 && (*dscan++ = *sscan++) != '\0')
		continue;
	while (--count >= 0)
		*dscan++ = '\0';
	return dst;
}
#endif
