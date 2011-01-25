/*-------------------------------------------------------------------------
 *
 * spt_python.c
 *    A simple function for the module debugging.
 *
 * Copyright (c) 2009-2011 Daniele Varrazzo <daniele.varrazzo@gmail.com>
 *
 * Debug logging is enabled if the extension is compiled with the
 * SPT_DEBUG symbol and is emitted on stdout.
 *
 *-------------------------------------------------------------------------
 */

#include <stdarg.h>
#include <stdio.h>

void spt_debug(const char *fmt, ...)
{

#ifdef SPT_DEBUG

    va_list ap;

    fprintf(stderr, "[SPT]: ");
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fprintf(stderr, "\n");

#endif

}
