/**
  ******************************************************************************
  * @file    bsp_led.h
  * @brief   Status LED on PD15 (active low).
  ******************************************************************************
  */

#ifndef __BSP_LED_H
#define __BSP_LED_H

#include <stdbool.h>

void BSP_Led_Init(void);
void BSP_Led_Set(bool on);
void BSP_Led_Toggle(void);

#endif /* __BSP_LED_H */
