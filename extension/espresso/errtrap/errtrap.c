#include "copyright.h"
#include "port.h"
#include <varargs.h>
#include "uprintf.h"
#include "errtrap.h"

/*LINTLIBRARY*/

#define ERR_BUF_SIZE	4096

#define STACK_SIZE	100

/* error handler stack */
static void (*handlerList[STACK_SIZE])();
static int numHandlers = 0;
static int curHandlerIdx = -1;

/* information given to errRaise */
static char *errPkg = (char *) 0;
static int errCode = 0;
static char errMessage[ERR_BUF_SIZE];
static char *errProgName = "\t\t*** ATTENTION ***\n\
    The writer of this program failed to register the name of the program\n\
    by calling `errProgramName'.  Consequently, the name of program that\n\
    failed cannot be determined by the error handling package.\n\n<unknown>";
static int errCoreFlag = 0;

void errProgramName(name)
char *name;
{
    errProgName = name;
}

void errCore(flag)
int flag;
{
    errCoreFlag = flag;
}

void errPushHandler(func)
void (*func)();
{
    if (numHandlers >= STACK_SIZE) {
	errRaise(ERR_PKG_NAME, 0,
		"errPushHandler:  can't push error handler -- stack is full");
    }
    handlerList[numHandlers++] = func;
}

void errPopHandler()
{
    if (numHandlers < 1) {
	errRaise(ERR_PKG_NAME, 0,
		"errPopHandler:  can't pop error handler -- stack is empty");
    }
    numHandlers--;
}

#ifdef lint
/*ARGSUSED*/
/*VARARGS3*/

void errRaise(pkg, code, fmt, va_alist)
char *pkg;
int code;
char *fmt;
va_dcl

#else	/*LINT*/
void errRaise(va_alist)
va_dcl
#endif	/*LINT*/

{
    va_list ap;
    char *format;
    static void defaultHandler();

    va_start(ap);
    errPkg = va_arg(ap, char *);
    errCode = va_arg(ap, int);
    format = va_arg(ap, char *);
    if (format != errMessage) {
	(void) uprintf(errMessage, format, &ap);
    }
    va_end(ap);

    curHandlerIdx = numHandlers;
    while (curHandlerIdx > 0) {
	(*handlerList[--curHandlerIdx])(errPkg, errCode, errMessage);
    }
    defaultHandler(errPkg, errCode, errMessage);
}

static void defaultHandler(pkgName, code, mesg)
char *pkgName;
int code;
char *mesg;
{
    (void) fprintf(stderr,
		"%s: unexpected fatal error detected by %s (code %d):\n\t%s\n",
		errProgName, pkgName, code, mesg);
    if (errCoreFlag) {
	abort();
    } else {
	exit(1);
    }
}

#ifdef lint
/*ARGSUSED*/
/*VARARGS1*/

void errPass(fmt, va_alist)
char *fmt;
va_dcl

#else	/*LINT*/
void errPass(va_alist)
va_dcl
#endif	/*LINT*/

{
    va_list ap;
    char *format;
    static char tmpBuffer[ERR_BUF_SIZE];
    static void defaultHandler();

    va_start(ap);
    format = va_arg(ap, char *);
    (void) uprintf(tmpBuffer, format, &ap);
    (void) strcpy(errMessage, tmpBuffer);
    va_end(ap);

    /* this should have been set by errRaise, but make sure it's possible */
    if (curHandlerIdx > numHandlers) curHandlerIdx = numHandlers;

    while (curHandlerIdx > 0) {
	(*handlerList[--curHandlerIdx])(errPkg, errCode, errMessage);
    }

    defaultHandler(errPkg, errCode, errMessage);
}

jmp_buf errJmpBuf;

static jmp_buf jmpBufList[STACK_SIZE];
static numJmpBufs = 0;

void errIgnPush()
{
    static void ignoreHandler();

    /* don't need to check for overflow, since errPushHandler will */
    errPushHandler(ignoreHandler);
    (void) memcpy((char *) jmpBufList[numJmpBufs++], (char *) errJmpBuf,
			    sizeof(jmp_buf));

    /* so errStatus can tell if something trapped */
    errPkg = (char *) 0;
}

void errIgnPop()
{
    if (numJmpBufs <= 0) {
	errRaise(ERR_PKG_NAME, 0, "errIgnPop called before errIgnPush");
    }
    errPopHandler();
    numJmpBufs--;
}

/*ARGSUSED*/
static void ignoreHandler(pkgName, code, message)
char *pkgName;
int code;
char *message;
{
    if (numJmpBufs <= 0) {
	errRaise(ERR_PKG_NAME, 0,
	"errtrap internal error:  ERR_IGNORE handler called with no jmp_buf");
    }
    longjmp(jmpBufList[numJmpBufs - 1], 1);
}

int errStatus(pkgNamePtr, codePtr, messagePtr)
char **pkgNamePtr;
int *codePtr;
char **messagePtr;
{
    if (errPkg) {
	*pkgNamePtr = errPkg;
	*codePtr = errCode;
	*messagePtr = errMessage;
	return(1);
    }
    return(0);
}
