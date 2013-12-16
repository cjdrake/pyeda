#include "port.h"
#include "errtrap.h"

/*ARGSUSED*/
main(argc, argv)
int argc;
char *argv[];
{
    char *pkg, *msg;
    int code;
    void testFunc(), benignHandler();

    errProgramName(argv[0]);

    ERR_IGNORE(testFunc());
    if (errStatus(&pkg, &code, &msg)) {
	(void) fprintf(stderr, "Ignored error %d from `%s' package: %s\n",
		    code, pkg, msg);
    }

    errPushHandler(benignHandler);
    testFunc();
    exit(1);		/* shouldn't be reached */
}

void testFunc()
{
    errRaise("test", 0, "formatted message: (1)=%d; (hello)=%s", 1, "hello");
}

void benignHandler(pkgName, code, message)
char *pkgName;
int code;
char *message;
{
    (void) fprintf(stderr, "Error %d from `%s' package: %s\n",
		    code, pkgName, message);
    exit(0);
}
