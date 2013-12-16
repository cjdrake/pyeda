/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * strrchr - find last occurrence of a character in a string
 */

char *				/* found char, or NULL if none */
strrchr(s, charwanted)
CONST char *s;
register char charwanted;
{
	register CONST char *scan;
	register CONST char *place;

	place = NULL;
	for (scan = s; *scan != '\0'; scan++)
		if (*scan == charwanted)
			place = scan;
	if (charwanted == '\0')
		return scan;
	return place;
}
#endif
