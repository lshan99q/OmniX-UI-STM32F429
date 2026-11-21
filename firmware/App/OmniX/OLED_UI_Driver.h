/**
  ******************************************************************************
  * @file    OLED_UI_Driver.h
  * @brief   Platform abstraction used by OmniX_UI.
  *
  * Replace the bodies in OLED_UI_Driver.c when porting to another MCU.
  ******************************************************************************
  */

#ifndef __OLED_UI_DRIVER_H
#define __OLED_UI_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

#include "bsp_keys.h"

/* Active-low key getters expected by OmniX_UI. */
#define Key_GetEnterStatus()    BSP_Key_Enter()
#define Key_GetBackStatus()     BSP_Key_Back()
#define Key_GetUpStatus()       BSP_Key_Up()
#define Key_GetDownStatus()     BSP_Key_Down()

void Timer_Init(void);
void OLED_UI_TimerIRQHandler(void);
uint8_t OLED_UI_TakeTick(void);
void Key_Init(void);

void Encoder_Init(void);
void Encoder_Enable(void);
void Encoder_Disable(void);
int16_t Encoder_Get(void);

void Delay_us(uint32_t xus);
void Delay_ms(uint32_t xms);
void Delay_s(uint32_t xs);

#endif /* __OLED_UI_DRIVER_H */
