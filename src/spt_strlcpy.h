/*-------------------------------------------------------------------------
 *
 * spt_strlcpy.h
 *    Definitions to use supplied strlcpy instead of builts ins useful
 *    for clang
 *
 * Copyright (c) 2010-2012 Daniele Varrazzo <daniele.varrazzo@gmail.com>
 *
 *-------------------------------------------------------------------------
 */

#ifndef SPT_STRLCPY_H
#define SPT_STRLCPY_H

#include "spt_config.h"
#include <stddef.h>

HIDDEN extern size_t spt_strlcpy(char *dst, const char *src, size_t siz);

#endif
