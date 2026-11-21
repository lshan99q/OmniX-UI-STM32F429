/**
  ******************************************************************************
  * @file    bsp.h
  * @brief   Common board support helpers.
  ******************************************************************************
  */

#ifndef __BSP_H
#define __BSP_H

#include <stdint.h>
#include <stdbool.h>

void BSP_Init(void);
void BSP_DelayUs(uint32_t us);
void BSP_DelayMs(uint32_t ms);
uint32_t BSP_GetTick(void);
void BSP_ErrorHandler(void);

#endif /* __BSP_H */
