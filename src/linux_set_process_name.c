#include "linux_set_process_name.h"

#include <stdio.h>
#include <stdint.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>


#include <sys/prctl.h>
#include <sys/syscall.h>

#define DONE_IF(cond) if (cond) goto done;

static inline char * append_format(char * buf, char * buf_end, int field_size) {
    const char * fmt = NULL;
    if (field_size == sizeof(unsigned long long)) {
        fmt = "%llu";
    } else if (field_size == sizeof(unsigned long)) {
        fmt = "%lu";
    } else if (field_size == sizeof(unsigned int)) {
        fmt = "%u";
    } else if (field_size == sizeof(unsigned short)) {
        fmt = "%hu";
    } else if (field_size == 0) {
        fmt ="%*u";
    } else {
        return NULL;
    }
    size_t len = strlen(fmt);
    if (buf + len >= buf_end)
        return NULL;
    memcpy(buf, fmt, len);
    return buf + len;
}

static inline char * skip_fields(char * buf, int count) {
    char * buf_ptr = strchr(buf, ' ');
    for (int i = 0; i < count - 1; ++i) {
        if (!buf_ptr)
            return NULL;
        buf_ptr = strchr(buf_ptr + 1, ' ');
    }
    return buf_ptr + 1;
}

static char * read_all(int fd, size_t * size) {
    size_t line_size = 32;
    char * line = malloc(line_size);
    if (!line)
        return NULL;
    size_t offset = 0;
    for ( ; ; ) {
		ssize_t bytes_read = read(fd, line + offset, line_size - offset - 1);
        if (bytes_read == 0) {
            line[offset] = '\0';
            if (size)
                *size = offset;
            return line;
        }
        if (bytes_read < 0) {
            if (errno == EINTR)
                continue;
            break;
        }
        offset += bytes_read;
        if (offset + 1 == line_size) {
            if (SIZE_MAX / 2 > line_size)
                line_size *= 2;
            else if (SIZE_MAX - line_size > 4096)
                line_size += 4096;
            else 
                break;
            char * tmp_line = realloc(line, line_size);
            if (!tmp_line)
                break;
            line = tmp_line;
        }
	}
    free(line);
    return NULL;
}

static char * proctitle = NULL;

const char * linux_get_process_title() {

    enum {
        has_nothing,
        has_fd
    } state = has_nothing;

    if (proctitle)
        return proctitle;

    int fd = open("/proc/self/cmdline", O_RDONLY | O_CLOEXEC);
    DONE_IF(fd < 0);
    size_t size = 0;
    proctitle = read_all(fd, &size);
    DONE_IF(!proctitle);
    for(size_t i = 0; i < size - 1; ++i) {
        if (proctitle[i] == '\0')
            proctitle[i] = ' ';
    }
done:
    switch(state) {
        case has_fd: close(fd);
        case has_nothing: ;
    } 
    return proctitle;
}


bool linux_set_process_title(const char * title)
{
    typedef struct prctl_mm_map prctl_mm_map_t;
    
    enum {
        has_nothing,
        has_fd,
        has_buf
    } state = has_nothing;
    bool ret = false;

    /* sanity check that our struct matches kernel's */
    unsigned int struct_size;
    DONE_IF(prctl(PR_SET_MM, (unsigned long)(PR_SET_MM_MAP_SIZE), &struct_size,
                  (unsigned long)0, (unsigned long)0) != 0);
    DONE_IF(struct_size != sizeof(prctl_mm_map_t));

    
    int fd = open("/proc/self/stat", O_RDONLY | O_CLOEXEC);
    DONE_IF(fd < 0);
    ++state;

    char * buf = read_all(fd, NULL);
    DONE_IF(!buf);
    ++state;

    prctl_mm_map_t prctl_map;

    /* The column layout is:
       25 columns to ignore
       start_code
       end_code
       start_stack 
       19 columns to ignore
       start_data
       end_data
       start_brk
       2 columns to ignore
       env_start
       env_end
    */
    char * buf_ptr = skip_fields(buf, 25);
    DONE_IF(!buf_ptr);

    char format_buf[64]; /* 64 ought to be enough for the longest format */
    char * format = format_buf, * format_end = format_buf + sizeof(format_buf) - 1;
    DONE_IF(!(format = append_format(format, format_end, sizeof(prctl_map.start_code))));
    DONE_IF(!(format = append_format(format, format_end, sizeof(prctl_map.end_code))));
    DONE_IF(!(format = append_format(format, format_end, sizeof(prctl_map.start_stack))));
    *format = '\0';
    DONE_IF(sscanf(buf_ptr, format_buf, &prctl_map.start_code, &prctl_map.end_code, &prctl_map.start_stack) != 3);

    buf_ptr = skip_fields(buf_ptr, 19);
    DONE_IF(!buf_ptr);

    format = format_buf;
    DONE_IF(!(format = append_format(format, format_end, sizeof(prctl_map.start_data))));
    DONE_IF(!(format = append_format(format, format_end, sizeof(prctl_map.end_data))));
    DONE_IF(!(format = append_format(format, format_end, sizeof(prctl_map.start_brk))));
    DONE_IF(!(format = append_format(format, format_end, 0)));
    DONE_IF(!(format = append_format(format, format_end, 0)));
    DONE_IF(!(format = append_format(format, format_end, sizeof(prctl_map.env_start))));
    DONE_IF(!(format = append_format(format, format_end, sizeof(prctl_map.env_end))));
    *format = '\0';
    DONE_IF(sscanf(buf_ptr, format_buf, &prctl_map.start_data, &prctl_map.end_data, 
                   &prctl_map.start_brk, &prctl_map.env_start, &prctl_map.env_end) != 5);

    size_t full_title_len = strlen(title) + 1;

    char * tmp_proctitle = realloc(proctitle, full_title_len);
    DONE_IF(!tmp_proctitle);
    proctitle = tmp_proctitle;

    prctl_map.arg_start = (typeof(prctl_map.arg_start))proctitle;
    prctl_map.arg_end = prctl_map.arg_start + full_title_len;

    prctl_map.brk = syscall(__NR_brk, 0);

    prctl_map.auxv = NULL;
    prctl_map.auxv_size = 0;
    prctl_map.exe_fd = -1;

    DONE_IF(prctl(PR_SET_MM, (unsigned long)(PR_SET_MM_MAP), &prctl_map,
                  sizeof(prctl_map), (unsigned long)0) != 0);
    memcpy(proctitle, title, full_title_len);
    (void)prctl(PR_SET_NAME, title);

    ret = true;
done:
    switch(state) {
        case has_buf: free(buf);
        case has_fd: close(fd);
        case has_nothing: ;
    }   
    return ret;
}