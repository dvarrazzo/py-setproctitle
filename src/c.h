
/*
 * bool
 *		Boolean value, either true or false.
 *
 * XXX for C++ compilers, we assume the compiler has a compatible
 * built-in definition of bool.
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


#if !HAVE_DECL_STRLCPY
#include <stddef.h>
extern size_t strlcpy(char *dst, const char *src, size_t siz);
#endif

#endif /* C_H */
