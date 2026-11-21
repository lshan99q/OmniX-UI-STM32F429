/**
  ******************************************************************************
  * @file    bsp_serial.h
  * @brief   USART1 debug console (PA9 TX / PA10 RX, 115200 8N1).
  ******************************************************************************
  */

#ifndef __BSP_SERIAL_H
#define __BSP_SERIAL_H

#include <stdint.h>

void BSP_Serial_Init(void);
void BSP_Serial_Write(const uint8_t *data, uint32_t length);
int  BSP_Serial_Printf(const char *format, ...);

#endif /* __BSP_SERIAL_H */
