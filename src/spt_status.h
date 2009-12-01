/*-------------------------------------------------------------------------
 *
 * spt_status.h
 *
 * Declarations for spt_status.c
 *
 *-------------------------------------------------------------------------
 */

#ifndef SPT_STATUS_H
#define SPT_STATUS_H

#include "c.h"

extern bool update_process_title;

extern char **save_ps_display_args(int argc, char **argv);

extern void init_ps_display(const char *initial_str);

extern void set_ps_display(const char *activity, bool force);

extern const char *get_ps_display(int *displen);

#endif   /* SPT_STATUS_H */

