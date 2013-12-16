/*LINTLIBRARY*/
/*
 * Uprintf - user controllable printf
 *
 * David Harrison
 * University of California, Berkeley
 * 1988
 *
 * This file contains an implementation of a portable mechanism for
 * user-definable printf() like functions.  The usage is as follows:
 *
 * #include <varargs.h>
 *
 * user_function(va_alist)
 * va_dcl
 * {
 *    va_list ap;
 *    char *fmt;
 *    char buf[1024];
 *
 *    va_start(ap);
 *    /* Process any interesting prefix parameters */
/*    fmt = va_arg(ap, char *);
 *    uprintf(buf, fmt, &ap);
 *    /* Do something with `buf' */
/*    /* Process any remaining parameters */
/*    va_end(ap);
 * }
 */

#include "copyright.h"
#include "port.h"

#ifdef __STDC__
#include <stdarg.h>
#else
#include <varargs.h>
#endif

#define MAXSPEC	2048

char *uprintf_pkg_name = "uprintf";

/* Types */
#define UPF_INT		0
#define UPF_LONG	1
#define UPF_UINT	2
#define UPF_ULONG	3
#define UPF_FLOAT	4
#define UPF_DOUBLE	5
#define UPF_CHAR	6
#define UPF_CHARPTR	7

/* Flag word values */
#define UPF_EXTEND	0x01
#define UPF_DOT		0x02
#define UPF_BLANK	0x04
#define UPF_MINUS	0x08
#define UPF_PLUS	0x10
#define UPF_ALT		0x20

static char *upf_parse(fmt, dest, spec, type, fnums)
char *fmt;			/* Format string      */
char *dest;			/* Destination string */
char spec[MAXSPEC];		/* Returned spec      */
int *type;			/* Returned type      */
int *fnums;			/* Number of stars    */
/*
 * This routine examines `fmt' for printf style output directives.
 * Characters not involved in such a directive are copied to `dest'.
 * The specification is written in `spec'.  The type of the
 * spec is written in `type'.  If it is a star form, the number
 * of star specifications is written in `fnums'.
 */
{
    char *rtn_spec;
    int flag_word;

    dest = &(dest[strlen(dest)]);
    /* Scan to a % sign copying into dest */
    while (*fmt && *fmt != '%') *(dest++) = *(fmt++);
    *dest = '\0';
    if (!*fmt) return (char *) 0;

    /* Directive scanning */
    flag_word = 0;
    *fnums = 0;
    rtn_spec = spec;
    *(rtn_spec++) = *(fmt++);
    while (*fmt) {
	switch (*fmt) {
	case '%':
	    *(dest++) = *(fmt++);
	    *dest = '\0';
	    return upf_parse(fmt, dest, spec, type, fnums);
	case 'l':
	    *(rtn_spec++) = *(fmt++);
	    if (flag_word & UPF_EXTEND) {
		*rtn_spec = '\0';
		(void) strcat(dest, spec);
		return upf_parse(fmt, dest, spec, type, fnums);
	    } else {
		flag_word |= UPF_EXTEND;
	    }
	    break;
	case 'd':
	case 'o':
	case 'x':
	case 'X':
	    *(rtn_spec++) = *(fmt++); *rtn_spec = '\0';
	    if (flag_word & UPF_EXTEND) *type = UPF_LONG;
	    else *type = UPF_INT;
	    return fmt;
	case 'u':
	    *(rtn_spec++) = *(fmt++); *rtn_spec = '\0';
	    if (flag_word & UPF_EXTEND) *type = UPF_ULONG;
	    else *type = UPF_UINT;
	    return fmt;
	case 'f':
	case 'e':
	case 'E':
	case 'g':
	case 'G':
	    *(rtn_spec++) = *(fmt++); *rtn_spec = '\0';
	    if (flag_word & UPF_EXTEND) *type = UPF_DOUBLE;
	    else *type = UPF_FLOAT;
	    return fmt;
	case 'c':
	    *(rtn_spec++) = *(fmt++); *rtn_spec = '\0';
	    *type = UPF_CHAR;
	    return fmt;
	    break;
	case 's':
	    *(rtn_spec++) = *(fmt++); *rtn_spec = '\0';
	    *type = UPF_CHARPTR;
	    return fmt;
	case '#':
	    *(rtn_spec++) = *(fmt++);
	    if (flag_word & UPF_ALT) {
		*rtn_spec = '\0';
		(void) strcat(dest, spec);
		return upf_parse(fmt, dest, spec, type, fnums);
	    } else {
		flag_word |= UPF_ALT;
	    }
	    break;
	case '*':
	    *(rtn_spec++) = *(fmt++);
	    *fnums += 1;
	    break;
	case '0':
	case '1':
	case '2':
	case '3':
	case '4':
	case '5':
	case '6':
	case '7':
	case '8':
	case '9':
	    *(rtn_spec++) = *(fmt++);
	    break;
	case '-':
	    *(rtn_spec++) = *(fmt++);
	    if (flag_word & UPF_MINUS) {
		*rtn_spec = '\0';
		(void) strcat(dest, spec);
		return upf_parse(fmt, dest, spec, type, fnums);
	    } else {
		flag_word |= UPF_MINUS;
	    }
	    break;
	case '+':
	    *(rtn_spec++) = *(fmt++);
	    if (flag_word & UPF_PLUS) {
		*rtn_spec = '\0';
		(void) strcat(dest, spec);
		return upf_parse(fmt, dest, spec, type, fnums);
	    } else {
		flag_word |= UPF_PLUS;
	    }
	    break;
	case ' ':
	    *(rtn_spec++) = *(fmt++);
	    if (flag_word & UPF_BLANK) {
		*rtn_spec = '\0';
		(void) strcat(dest, spec);
		return upf_parse(fmt, dest, spec, type, fnums);
	    } else {
		flag_word |= UPF_BLANK;
	    }
	    break;
	case '.':
	    *(rtn_spec++) = *(fmt++);
	    if (flag_word & UPF_DOT) {
		*rtn_spec = '\0';
		(void) strcat(dest, spec);
		return upf_parse(fmt, dest, spec, type, fnums);
	    } else {
		flag_word |= UPF_DOT;
	    }
	    break;
	default:
	    *(rtn_spec++) = *(fmt++);
	    *rtn_spec = '\0';
	    (void) strcat(dest, spec);
	    return upf_parse(fmt, dest, spec, type, fnums);
	}
    }
    *rtn_spec = '\0';
    (void) strcat(dest, spec);
    return fmt;
}

char *uprintf(buf, upf_fmt, ap)
char *buf;			/* Buffer to write into   */
char *upf_fmt;			/* Format string          */
va_list *ap;			/* Argument list to parse */
/*
 * This routine parses the printf-style specification given in `upf_fmt'
 * and performs the necessary substitutions using the remaining
 * arguments given by `ap'.  The result string is written into
 * the buffer `buf'.  All standard printf directives are supported.
 * A directive the routine does not understand is left unchanged
 * in the result string.  The argument pointer is left after
 * the last argument required by the format string.  The routine returns
 * `buf'.
 */
{
    char upf_spec[MAXSPEC];	/* Returned specification    */
    char upf_field[MAXSPEC];	/* Final substituted field   */
    int upf_type;		/* Returned directive type   */
    int upf_fnums;		/* Number of star directives */

    /* Return types */
    int upf_f1;			/* First field width         */
    int upf_f2;			/* Second field width        */
    int upf_int;		/* Integer return type       */
    long upf_long;		/* Long return type          */
    unsigned int upf_uint;	/* Unsigned return type      */
    unsigned long upf_ulong;	/* Unsigned long return type */
    float upf_float;		/* Float return type         */
    double upf_double;		/* Double return type        */
    char upf_char;		/* Character return type     */
    char *upf_charptr;		/* String return type        */

    /* Start special processing */
    buf[0] = '\0';
    while (upf_fmt = upf_parse(upf_fmt, buf, upf_spec, &upf_type, &upf_fnums)) {
	switch (upf_type) {
	case UPF_INT:
	    if (upf_fnums != 1) {
		upf_int = va_arg(*ap, int);
		(void) sprintf(upf_field, upf_spec, upf_int);
	    } else {
		upf_f1 = va_arg(*ap, int);
		upf_int = va_arg(*ap, int);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_int);
	    }
	    break;
	case UPF_LONG:
	    if (upf_fnums != 1) {
		upf_long = va_arg(*ap, long);
		(void) sprintf(upf_field, upf_spec, upf_long);
	    } else {
		upf_f1 = va_arg(*ap, int);
		upf_long = va_arg(*ap, long);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_long);
	    }
	    break;
	case UPF_UINT:
	    if (upf_fnums != 1) {
		upf_uint = va_arg(*ap, unsigned int);
		(void) sprintf(upf_field, upf_spec, upf_uint);
	    } else {
		upf_f1 = va_arg(*ap, int);
		upf_uint = va_arg(*ap, unsigned int);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_uint);
	    }
	    break;
	case UPF_ULONG:
	    if (upf_fnums != 1) {
		upf_ulong = va_arg(*ap, unsigned long);
		(void) sprintf(upf_field, upf_spec, upf_long);
	    } else {
		upf_f1 = va_arg(*ap, int);
		upf_ulong = va_arg(*ap, unsigned long);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_ulong);
	    }
	    break;
	case UPF_FLOAT:
	    if (upf_fnums == 1) {
		upf_f1 = va_arg(*ap, int);
		upf_float = (float) va_arg(*ap, double);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_float);
	    } else if (upf_fnums == 2) {
		upf_f1 = va_arg(*ap, int);
		upf_f2 = va_arg(*ap, int);
		upf_float = (float) va_arg(*ap, double);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_f2, upf_float);
	    } else {
		upf_float = (float) va_arg(*ap, double);
		(void) sprintf(upf_field, upf_spec, upf_float);
	    }
	    break;
	case UPF_DOUBLE:
	    if (upf_fnums == 1) {
		upf_f1 = va_arg(*ap, int);
		upf_double = va_arg(*ap, double);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_double);
	    } else if (upf_fnums == 2) {
		upf_f1 = va_arg(*ap, int);
		upf_f2 = va_arg(*ap, int);
		upf_double = va_arg(*ap, double);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_f2, upf_double);
	    } else {
		upf_double = va_arg(*ap, double);
		(void) sprintf(upf_field, upf_spec, upf_double);
	    }
	    break;
	case UPF_CHAR:
	    if (upf_fnums != 1) {
		upf_char = (char) va_arg(*ap, int);
		(void) sprintf(upf_field, upf_spec, upf_char);
	    } else {
		upf_f1 = va_arg(*ap, int);
		upf_char = (char) va_arg(*ap, int);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_char);
	    }
	    break;
	case UPF_CHARPTR:
	    if (upf_fnums != 1) {
		upf_charptr = va_arg(*ap, char *);
		(void) sprintf(upf_field, upf_spec, upf_charptr);
	    } else {
		upf_f1 = va_arg(*ap, int);
		upf_charptr = va_arg(*ap, char *);
		(void) sprintf(upf_field, upf_spec, upf_f1, upf_charptr);
	    }
	    break;
	default:
	    upf_field[0] = '\0';
	    break;
	}
	(void) strcat(buf, upf_field);
    }
    return buf;
}



