/**
  ******************************************************************************
  * @file    Power.h
  * @brief   Battery monitor for the STM32F429 4G board.
  ******************************************************************************
  */

#ifndef __POWER_H
#define __POWER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>

/* PB1 = ADC1_IN9.  The divider ratio must be measured on the assembled board:
   Vbat = V(PA1) * (Rtop + Rbottom) / Rbottom.  The default assumes 1:1. */
#define POWER_VBAT_RATIO      2.0f

#define ADC_MAX_VALUE         4095.0f
#define ADC_REF_VOLTAGE       3.3f

#define BATTERY_MIN_VOLTAGE   3.30f
#define BATTERY_MAX_VOLTAGE   4.20f

typedef struct {
    float battery_voltage;
    float usb_voltage;
    int battery_percent;
    bool usb_inserted;
    bool valid;
} Power_Data_t;

void Power_Init(void);
void Power_StartTask(void);
void Power_TaskTick(void);
void Power_GetData(Power_Data_t *data);
float Power_ReadBatteryVoltage(void);
float Power_ReadUSBVoltage(void);
int Power_GetBatteryPercent(void);
bool Power_IsUSBInserted(void);

#ifdef __cplusplus
}
#endif

#endif /* __POWER_H */
