/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * memccpy - copy bytes up to a certain char
 */

VOIDSTAR
memccpy(dst, src, ucharstop, size)
VOIDSTAR dst;
CONST VOIDSTAR src;
SIZET size;
{
	register char *d;
	register CONST char *s;
	register SIZET n;
	register int uc;

	if (size <= 0)
		return NULL;

	s = src;
	d = dst;
	uc = UNSCHAR(ucharstop);
	for (n = size; n > 0; n--)
		if (UNSCHAR(*d++ = *s++) == uc)
			return d;

	return NULL;
}
#endif
