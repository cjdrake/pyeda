#include "copyright.h"
#include "port.h"

#ifdef __STDC__
#include "stdarg.h"
#else
#include <varargs.h>
#endif

#include "uprintf.h"

#define Fprintf		(void) fprintf
#define Printf		(void) printf

#ifdef __STDC__

/* ANSI version */
void error(char *func_name, char *file_name, int line_num, char *format, ...)
/*
 * error(func, file, line, format, ... )
 */
{
    va_list ap;
    char buf[1024];

    va_start(ap, format);

    Fprintf(stderr, "Error: function %s, file %s, line %d:\n  %s\n",
	    func_name, file_name, line_num,
	    uprintf(buf, format, &ap));

    va_end(ap);
}

#else

/* Normal version */
/*VARARGS1*/
void error(va_alist)
va_dcl
/*
 * error(func, file, line, format, ... )
 */
{
    char *func_name, *file_name, *format;
    va_list ap;
    char buf[1024];
    int line_num;

    va_start(ap);

    func_name = va_arg(ap, char *);
    file_name = va_arg(ap, char *);
    line_num = va_arg(ap, int);
    format = va_arg(ap, char *);

    Fprintf(stderr, "Error: function %s, file %s, line %d:\n  %s\n",
	    func_name, file_name, line_num,
	    uprintf(buf, format, &ap));

    va_end(ap);
}

#endif

#define PI 3.14159

main()
/* Tests error routine */
{
    Printf("Begin processing\n");
    error("main", __FILE__, __LINE__, "value of pi is %f\n", PI);
}
