/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * memchr - search for a byte
 */

VOIDSTAR
memchr(s, ucharwanted, size)
CONST VOIDSTAR s;
int ucharwanted;
SIZET size;
{
	register CONST char *scan;
	register SIZET n;
	register int uc;

	scan = s;
	uc = UNSCHAR(ucharwanted);
	for (n = size; n > 0; n--)
		if (UNSCHAR(*scan) == uc)
			return scan;
		else
			scan++;

	return NULL;
}
#endif
