/*LINTLIBRARY*/
#include "port.h"
#ifdef LACK_SYS5
/*
 * strerror - map error number to descriptive string
 *
 * This version is obviously somewhat Unix-specific.
 */
char *
strerror(errnum)
int errnum;
{
	extern int errno, sys_nerr;
	extern char *sys_errlist[];

	if (errnum > 0 && errnum < sys_nerr)
		return sys_errlist[errnum];
	else
		return "unknown error";
}
#endif
