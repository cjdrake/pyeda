/*
 * Uprintf - user controllable printf
 *
 * David Harrison
 * University of California, Berkeley
 * 1988
 *
 * Definitions for using uprintf.  Most people find it simpler
 * to do the definition themselves.
 */

#ifndef UPRINTF_H
#define UPRINTF_H

#include "copyright.h"
#include "ansi.h"

extern char *uprintf_pkg_name;
extern char *uprintf
  ARGS((char *buf, char *upf_fmt, va_list *ap));

#endif /* UPRINTF */
