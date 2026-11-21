/**
  ******************************************************************************
  * @file    bsp_log.c
  * @brief   Circular console mirror kept in RAM so a debugger can read it.
  ******************************************************************************
  */

#include "bsp_log.h"

volatile uint32_t bsp_log_head = 0U;
char bsp_log_buf[BSP_LOG_SIZE];

void BSP_Log_Write(const char *data, uint32_t length)
{
    for (uint32_t i = 0U; i < length; i++) {
        bsp_log_buf[bsp_log_head] = data[i];
        bsp_log_head++;
        if (bsp_log_head >= BSP_LOG_SIZE) {
            bsp_log_head = 0U;
        }
    }
}
