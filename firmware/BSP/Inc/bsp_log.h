/**
  ******************************************************************************
  * @file    bsp_log.h
  * @brief   RAM log ring buffer readable through SWD (no UART needed).
  ******************************************************************************
  */

#ifndef __BSP_LOG_H
#define __BSP_LOG_H

#include <stdint.h>

#define BSP_LOG_SIZE 4096U

extern volatile uint32_t bsp_log_head;
extern char bsp_log_buf[BSP_LOG_SIZE];

void BSP_Log_Write(const char *data, uint32_t length);

#endif /* __BSP_LOG_H */
