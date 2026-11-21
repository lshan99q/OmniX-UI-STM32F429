/**
  ******************************************************************************
  * @file    OLED_driver.h
  * @brief   Hardware layer of the OmniX_UI OLED driver.
  *
  * Target: 128x64 SH1106 (default) or SSD1306, four-wire SPI on SPI3.
  ******************************************************************************
  */

#ifndef __OLED_DRIVER_H
#define __OLED_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <stdio.h>
#include <stdarg.h>

void OLED_Init(void);
void OLED_SetColorMode(bool colormode);
void OLED_Update(void);
void OLED_UpdateArea(uint8_t X, uint8_t Y, uint8_t Width, uint8_t Height);
void OLED_Brightness(int16_t Brightness);

#endif /* __OLED_DRIVER_H */
