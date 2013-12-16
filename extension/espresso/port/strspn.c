/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * strspn - find length of initial segment of s consisting entirely
 * of characters from accept
 */

SIZET
strspn(s, accept)
CONST char *s;
CONST char *accept;
{
	register CONST char *sscan;
	register CONST char *ascan;
	register SIZET count;

	count = 0;
	for (sscan = s; *sscan != '\0'; sscan++) {
		for (ascan = accept; *ascan != '\0'; ascan++)
			if (*sscan == *ascan)
				break;
		if (*ascan == '\0')
			return count;
		count++;
	}
	return count;
}
#endif
