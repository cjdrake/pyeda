/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * strncat - append at most n characters of string src to dst
 */
char *				/* dst */
strncat(dst, src, n)
char *dst;
CONST char *src;
SIZET n;
{
	register char *dscan;
	register CONST char *sscan;
	register SIZET count;

	for (dscan = dst; *dscan != '\0'; dscan++)
		continue;
	sscan = src;
	count = n;
	while (*sscan != '\0' && --count >= 0)
		*dscan++ = *sscan++;
	*dscan++ = '\0';
	return dst;
}
#endif
