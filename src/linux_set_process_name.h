#ifndef HEADER_LINUX_SET_PROCESS_NAME_H_INCLUDED
#define HEADER_LINUX_SET_PROCESS_NAME_H_INCLUDED

#include "spt_config.h"

#include <stdbool.h>

HIDDEN bool linux_set_process_title(const char * title);
HIDDEN const char * linux_get_process_title();

#endif
