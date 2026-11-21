/**
  ******************************************************************************
  * @file    bsp_power.h
  * @brief   ADC helpers for the battery divider and the five-way switch.
  ******************************************************************************
  */

#ifndef __BSP_POWER_H
#define __BSP_POWER_H

#include <stdint.h>
#include <stdbool.h>

void BSP_Power_Init(void);
uint16_t BSP_Power_ReadAdc(uint32_t channel);
uint16_t BSP_Power_ReadAdcAvg(uint32_t channel, uint8_t samples);
bool BSP_Power_UsbInserted(void);

#endif /* __BSP_POWER_H */
