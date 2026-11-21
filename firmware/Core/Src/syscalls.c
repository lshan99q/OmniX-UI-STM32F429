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
#include "bsp_log.h"

#if defined(USE_SEMIHOSTING)
/* ARM semihosting SYS_WRITE: r0=0x05, r1=handle(1=stdout), r2=buf, r3=len.
   st-util --semihosting / a real GDB server services the BKPT over SWD, so
   the console works even when no USB-TTL is fitted. */
static int semihost_write(int handle, const char *buf, int len)
{
    register int r0 __asm__("r0") = 0x05;
    register int r1 __asm__("r1") = handle;
    register const char *r2 __asm__("r2") = buf;
    register int r3 __asm__("r3") = len;

    __asm__ volatile("bkpt 0xAB"
                     : "+r"(r0)
                     : "r"(r1), "r"(r2), "r"(r3)
                     : "memory");
    return r0;
}

int _write(int file, char *ptr, int len)
{
    (void)file;
    BSP_Log_Write(ptr, (uint32_t)len);
    return semihost_write(1, ptr, len);
}
#else
int _write(int file, char *ptr, int len)
{
    (void)file;
    BSP_Log_Write(ptr, (uint32_t)len);
    BSP_Serial_Write((const uint8_t *)ptr, (uint32_t)len);
    return len;
}
#endif

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
    /* Must match _Min_Stack_Size in the linker script (8 KB). */
    const uint32_t guard = 8192U;

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
