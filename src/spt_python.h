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

/* defined in Modules/main.c but not publically declared */
void Py_GetArgcArgv(int *argc, char ***argv);

#endif   /* SPT_PYTHON_H */
