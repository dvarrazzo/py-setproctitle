/*-------------------------------------------------------------------------
 *
 * spt_setup.c
 *    Initalization code for the spt_status.c module functions.
 *
 * Copyright (c) 2009-2010 Daniele Varrazzo <daniele.varrazzo@gmail.com>
 *
 *-------------------------------------------------------------------------
 */

#include "spt_setup.h"

#include "spt.h"
#include "spt_status.h"

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
    int argc;
    char **argv;
    Py_GetArgcArgv(&argc, &argv);
    argv = fix_argv(argc, argv);
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

