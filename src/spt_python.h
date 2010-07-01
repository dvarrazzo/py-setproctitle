/*-------------------------------------------------------------------------
 *
 * spt_python.h
 *    Include and customize Python definitions.
 *
 * Copyright (c) 2010 Daniele Varrazzo <daniele.varrazzo@gmail.com>
 *
 *-------------------------------------------------------------------------
 */

#ifndef SPT_PYTHON_H
#define SPT_PYTHON_H

#include <Python.h>

/* Things change a lot here... */
#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#endif

#ifdef IS_PY3K
#define CHAR_T wchar_t
#define STRLEN wcslen
#define CHAR_FMT "u"
#else
#define CHAR_T char
#define STRLEN strlen
#define CHAR_FMT "s"
#endif

/* defined in Modules/main.c but not publically declared */
void Py_GetArgcArgv(int *argc, CHAR_T ***argv);

/* Mangle the module name into the name of the module init function */
#ifdef IS_PY3K
#define INIT_MODULE(m) PyInit_ ## m
#else
#define INIT_MODULE(m) init ## m
#endif

#endif   /* SPT_PYTHON_H */
