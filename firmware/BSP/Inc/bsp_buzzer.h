/**
  ******************************************************************************
  * @file    bsp_buzzer.h
  * @brief   Passive buzzer on PB9 / TIM4_CH4.
  ******************************************************************************
  */

#ifndef __BSP_BUZZER_H
#define __BSP_BUZZER_H

#include <stdint.h>

void BSP_Buzzer_Init(void);
void BSP_Buzzer_Tone(uint16_t frequency_hz, uint16_t duration_ms);
void BSP_Buzzer_Off(void);

#endif /* __BSP_BUZZER_H */
