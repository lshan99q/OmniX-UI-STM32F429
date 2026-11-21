/**
  ******************************************************************************
  * @file    bsp_keys.h
  * @brief   Five-way switch + five push buttons, debounced.
  *
  * All getters return 0 when the direction/key is active and 1 when released,
  * matching the active-low convention used by OmniX_UI.
  ******************************************************************************
  */

#ifndef __BSP_KEYS_H
#define __BSP_KEYS_H

#include <stdint.h>

void BSP_Keys_Init(void);
void BSP_Keys_Scan(void);

uint8_t BSP_Key_Up(void);
uint8_t BSP_Key_Down(void);
uint8_t BSP_Key_Enter(void);
uint8_t BSP_Key_Back(void);
uint8_t BSP_Keys_JoyRaw(void);
uint8_t BSP_Keys_RawMask(void);

#endif /* __BSP_KEYS_H */
