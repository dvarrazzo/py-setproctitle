/*-------------------------------------------------------------------------
 *
 * setproctitle.c
 *    Python extension module to update and read the process title.
 *
 * Copyright (c) 2009 Daniele Varrazzo <daniele.varrazzo@gmail.com>
 *
 * The module allows Python code to access the functions get_ps_display()
 * and set_ps_display().  The process title initialization (functions
 * save_ps_display_args() and init_ps_display()) are called at module
 * initialization.
 *-------------------------------------------------------------------------
 */

#include "Python.h"
#include "spt_status.h"

#ifndef SPT_VERSION
#define SPT_VERSION unknown
#endif

/* defined in Modules/main.c but not publically declared */
void Py_GetArgcArgv(int *argc, char ***argv);

/* macro trick to stringify a macro expansion */
#define xstr(s) str(s)
#define str(s) #s

/* ----------------------------------------------------- */

static PyObject *spt_version;

static char spt_setproctitle__doc__[] =
"Change the process title."
;

static PyObject *
spt_setproctitle(PyObject *self /* Not used */, PyObject *args)
{
    const char *title;

    if (!PyArg_ParseTuple(args, "s", &title))
        return NULL;

    set_ps_display(title, true);

    Py_INCREF(Py_None);
    return Py_None;
}

static char spt_getproctitle__doc__[] =
"Get the current process title."
;

static PyObject *
spt_getproctitle(PyObject *self /* Not used */, PyObject *args)
{

    if (!PyArg_ParseTuple(args, ""))
        return NULL;

    int tlen;
    const char *title;
    title = get_ps_display(&tlen);

    return Py_BuildValue("s#", title, tlen);
}

/* List of methods defined in the module */

static struct PyMethodDef spt_methods[] = {
    {"setproctitle",    (PyCFunction)spt_setproctitle,  METH_VARARGS,   spt_setproctitle__doc__},
    {"getproctitle",    (PyCFunction)spt_getproctitle,  METH_VARARGS,   spt_getproctitle__doc__},

    {NULL,   (PyCFunction)NULL, 0, NULL}        /* sentinel */
};


/* return a concatenated version of a strings vector
 *
 * Return newly allocated heap space: clean it up with free()
 */
static char *
join_argv(int argc, char **argv)
{
    /* Calculate the final string length */
    int i;
    size_t len = 0;
    for (i = 0; i < argc; i++) {
        len += strlen(argv[i]) + 1;
    }

    char *buf = (char *)malloc(len);

    /* Copy the strings in the buffer joining with spaces */
    char *dest = buf;
    char *src;
    for (i = 0; i < argc; i++) {
        src = argv[i];
        while (*src) {
            *dest++ = *src++;
        }
        *dest++ = ' ';
    }
    *--dest = '\x00';

    return buf;
}


/* Initialization function for the module (*must* be called initsetproctitle) */

static char setproctitle_module_documentation[] =
"Allow customization of the process title."
;

void
initsetproctitle(void)
{
    PyObject *m, *d;

    /* Create the module and add the functions */
    m = Py_InitModule4("setproctitle", spt_methods,
        setproctitle_module_documentation,
        (PyObject*)NULL,PYTHON_API_VERSION);

    /* Add version string to the module*/
    d = PyModule_GetDict(m);
    spt_version = PyString_FromString(xstr(SPT_VERSION));
    PyDict_SetItemString(d, "__version__", spt_version);

    /* Initialize the process title */
#ifndef WIN32
    int argc;
    char **argv;
    Py_GetArgcArgv(&argc, &argv);
    save_ps_display_args(argc, argv);

    /* Set up the first title to fully initialize the code */
    char *init_title = join_argv(argc, argv);
    init_ps_display(init_title);
    free(init_title);
#else
    /* On Windows save_ps_display_args is a no-op
     * This is a good news, because Py_GetArgcArgv seems not usable.
     */
    LPTSTR init_title = GetCommandLine();
    init_ps_display(init_title);
#endif


    /* Check for errors */
    if (PyErr_Occurred())
        Py_FatalError("can't initialize module setproctitle");
}

