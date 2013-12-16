/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * memset - set bytes
 */

VOIDSTAR
memset(s, ucharfill, size)
CONST VOIDSTAR s;
register int ucharfill;
SIZET size;
{
	register CONST char *scan;
	register SIZET n;
	register int uc;

	scan = s;
	uc = UNSCHAR(ucharfill);
	for (n = size; n > 0; n--)
		*scan++ = uc;

	return s;
}
#endif
