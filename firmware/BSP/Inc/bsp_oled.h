/**
  ******************************************************************************
  * @file    bsp_oled.h
  * @brief   Low-level SPI transport for the 128x64 OLED.
  *
  * SPI3 is shared with the external GD25Q128E.  PB4 is the OLED DC pin and is
  * also SPI3_MISO, so the flash is kept deselected by this firmware; a future
  * flash driver must switch PB4 back to AF6 before reading.
  ******************************************************************************
  */

#ifndef __BSP_OLED_H
#define __BSP_OLED_H

#include <stdint.h>

void BSP_OLED_Init(void);
void BSP_OLED_Reset(void);
void BSP_OLED_Transmit(uint8_t dc_level, const uint8_t *data, uint16_t length);

#endif /* __BSP_OLED_H */
