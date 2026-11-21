/**
  ******************************************************************************
  * @file    syscalls.c
  * @brief   Newlib stubs: printf goes to USART1, a small heap backs newlib.
  ******************************************************************************
  */

#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include "bsp_serial.h"

int _write(int file, char *ptr, int len)
{
    (void)file;
    BSP_Serial_Write((const uint8_t *)ptr, (uint32_t)len);
    return len;
}

int _read(int file, char *ptr, int len)
{
    (void)file;
    (void)ptr;
    (void)len;
    return 0;
}

int _close(int file)
{
    (void)file;
    return -1;
}

int _fstat(int file, struct stat *st)
{
    (void)file;
    st->st_mode = S_IFCHR;
    return 0;
}

int _isatty(int file)
{
    (void)file;
    return 1;
}

int _lseek(int file, int ptr, int dir)
{
    (void)file;
    (void)ptr;
    (void)dir;
    return 0;
}

int _kill(int pid, int sig)
{
    (void)pid;
    (void)sig;
    errno = EINVAL;
    return -1;
}

int _getpid(void)
{
    return 1;
}

extern char _end;
extern char _estack;

static char *heap_end = 0;

void *_sbrk(int incr)
{
    char *prev_heap_end;
    const uint32_t guard = 4096U;

    if (heap_end == 0) {
        heap_end = &_end;
    }

    prev_heap_end = heap_end;

    if ((uint32_t)(heap_end + incr) > ((uint32_t)&_estack - guard)) {
        errno = ENOMEM;
        return (void *)-1;
    }

    heap_end += incr;
    return (void *)prev_heap_end;
}
