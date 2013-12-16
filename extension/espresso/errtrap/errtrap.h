#ifndef ERRTRAP_H
#define ERRTRAP_H

#include <setjmp.h>

#define ERR_PKG_NAME	"errtrap"

extern void errProgramName( /* char *progName */ );
extern void errCore( /* int flag */ );
extern void errPushHandler( /* void (*handler)() */ );
extern void errPopHandler();
extern void errRaise( /* char *pkgName, int code, char *format, ... */ );
extern void errPass( /* char *format, ... */ );

#define ERR_IGNORE(expr)	\
    {					\
	if ( ! setjmp(errJmpBuf)) {	\
	    errIgnPush();		\
	    expr;			\
	}				\
	errIgnPop();			\
    }
extern jmp_buf errJmpBuf;
extern void errIgnPush(), errIgnPop();
extern int errStatus();

#endif /* ERRTRAP_H */
