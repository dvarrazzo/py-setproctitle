/*-------------------------------------------------------------------------
 *
 * spt_setup.c
 *    Initalization code for the spt_status.c module functions.
 *
 * Copyright (c) 2009-2011 Daniele Varrazzo <daniele.varrazzo@gmail.com>
 *
 *-------------------------------------------------------------------------
 */

#include "spt_setup.h"

#include "spt.h"
#include "spt_status.h"

/* Darwin doesn't export environ */
#if defined(__darwin__)
#include <crt_externs.h>
#define environ (*_NSGetEnviron())
#else
extern char **environ;
#endif

#ifndef WIN32

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


#ifndef IS_PY3K

/* Return a copy of argv referring to the original arg area.
 *
 * python -m messes up with arg (issue #8): ensure to have a vector to the
 * original args or save_ps_display_args() will stop processing too soon.
 *
 * Return a buffer allocated with malloc: should be cleaned up with free()
 * (it is never released though).
 */
static char **
fix_argv(int argc, char **argv)
{
    char **buf = (char **)malloc(argc * sizeof(char *));
    int i;
    char *ptr = argv[0];
    for (i = 0; i < argc; ++i) {
        buf[i] = ptr;
        ptr += strlen(ptr) + 1;
    }

    return buf;
}

#else

/* Return a copy of argv[0] encoded in the default encoding.
 *
 * Return a newly allocated buffer to be released with free()
 */
static char *
get_encoded_arg0(wchar_t *argv0)
{
    PyObject *ua = NULL, *ba = NULL;
    char *rv = NULL;

    if (!(ua = PyUnicode_FromWideChar(argv0, -1))) {
        spt_debug("failed to convert argv[0] to unicode");
        goto exit;
    }

    if (!(ba = PyUnicode_AsEncodedString(
            ua, PyUnicode_GetDefaultEncoding(), "strict"))) {
        spt_debug("failed to encode argv[0]");
        goto exit;
    }

    rv = strdup(PyBytes_AsString(ba));

exit:
    PyErr_Clear();
    Py_XDECREF(ua);
    Py_XDECREF(ba);

    return rv;
}

/* Find the original arg buffer starting from the env position.
 *
 * Return nonzero if found.
 *
 * Required on Python 3 as Py_GetArgcArgv doesn't return pointers to the
 * original area.
 */
static int
find_argv_from_env(int *argc_o, char ***argv_o)
{
    int rv = 0;
    int argc;
    wchar_t **argv;
    char **buf = NULL;
    char *arg0 = NULL;

    /* Find the number of parameters. */
    Py_GetArgcArgv(&argc, &argv);
    if (argc <= 0 || argv == NULL) {
        spt_debug("no good news from Py_GetArgcArgv");
        goto exit;
    }

    buf = (char **)malloc((argc + 1) * sizeof(char *));
    buf[argc] = NULL;

    /* Walk back from environ until you find argc-1 null-terminated strings.
     * Don't look for argv[0] as it's probably not preceded by 0. */
    int i;
    char *ptr = environ[0];
    char *limit = ptr - 8192;  /* TODO: empiric limit: should use MAX_ARG */
    --ptr;
    for (i = argc - 1; i >= 1; --i) {
        if (*ptr) {
            spt_debug("zero %d not found", i);
            goto error;
        }
        --ptr;
        while (*ptr && ptr > limit) { --ptr; }
        if (ptr <= limit) {
            spt_debug("failed to found arg %d start", i);
            goto error;
        }
        buf[i] = (ptr + 1);
    }

    /* The first arg has not a zero in front. But what we have is reliable
     * enough (modulo its encoding). Check if it is exactly what found.
     *
     * The check is known to fail on OS X with locale C if there are
     * non-ascii characters in the executable path. See Python issue #9167
     */
    arg0 = get_encoded_arg0(argv[0]);
    if (!arg0) { goto error; }
    ptr -= strlen(arg0);

    if (ptr <= limit) {
        spt_debug("failed to found argv[0] start");
        goto error;
    }
    if (strcmp(ptr, arg0)) {
        spt_debug("failed to recognize argv[0]");
        goto error;
    }

    /* We have all the pieces of the jigsaw. */
    buf[0] = ptr;
    *argc_o = argc;
    *argv_o = buf;
    rv = 1;

    goto exit;

error:
    if (buf) { free(buf); }

exit:
    if (arg0) { free(arg0); }

    return rv;
}

#endif  /* IS_PY3K */

/* Find the original arg buffer, return nonzero if found.
 *
 * If found, set argc to the number of arguments, argv to an array
 * of pointers to the single arguments. The array is allocated via malloc.
 *
 * The function overcomes two Py_GetArgcArgv shortcomings:
 * - some python parameters mess up with the original argv, e.g. -m
 *   (see issue #8)
 * - with Python 3, argv is a decoded copy and doesn't point to
 *   the original area.
 */
static int
get_argc_argv(int *argc, char ***argv)
{
    int rv = false;

#ifdef IS_PY3K
    if (!(rv = find_argv_from_env(argc, argv))) {
        spt_debug("get_argc_argv failed");
    }
#else
    Py_GetArgcArgv(argc, argv);
    if (*argc <= 0 || *argv == NULL) {
        spt_debug("no good news from Py_GetArgcArgv");
        return rv;
    }

    *argv = fix_argv(*argc, *argv);
    rv = true;
#endif

    return rv;
}

#endif  /* WIN32 */


/* Initialize the module internal functions.
 *
 * The function reproduces the initialization performed by PostgreSQL
 * to be able to call the functions in pg_status.c
 *
 * The function should be called only once in the process lifetime.
 * so is called at module initialization. After the function is called,
 * set_ps_display() can be used.
 */
void
spt_setup(void)
{
#ifndef WIN32
    int argc = 0;
    char **argv = NULL;

    if (!get_argc_argv(&argc, &argv)) {
        spt_debug("setup failed");
        return;
    }

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

}

