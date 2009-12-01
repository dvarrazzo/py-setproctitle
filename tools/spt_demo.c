#include "../src/spt_status.h"

#include <stdio.h>

int
main(int argc, char **argv)
{
    argv = save_ps_display_args(argc, argv);
    init_ps_display("hello, world");

    printf("title changed, press a key\n");
    getchar();

    set_ps_display("new title!", true);
    printf("title changed again, press a key to exit\n");
    getchar();

    return 0;
}

