/*-------------------------------------------------------------------------
 *
 * c.h
 *    A few fundamental C definitions.
 *
 * Copyright (c) 2009-2010 Daniele Varrazzo <daniele.varrazzo@gmail.com>
 *-------------------------------------------------------------------------
 */

#ifndef C_H
#define C_H

#ifndef __cplusplus

#ifndef bool
typedef char bool;
#endif

#ifndef true
#define true	((bool) 1)
#endif

#ifndef false
#define false	((bool) 0)
#endif
#endif   /* not C++ */

#include <stddef.h>

#if !HAVE_DECL_STRLCPY
extern size_t strlcpy(char *dst, const char *src, size_t siz);
#endif

#ifdef WIN32
#include <Windows.h>
#endif

#endif /* C_H */
