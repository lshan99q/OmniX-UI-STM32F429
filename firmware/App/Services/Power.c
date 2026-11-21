/**
  ******************************************************************************
  * @file    Power.c
  * @brief   Battery monitor for the STM32F429 4G board.
  *
  * The original ESP32 firmware polled a battery ADC and a USB-voltage ADC.
  * This board only exposes the battery divider (PB1 / ADC1_IN9), so the USB
  * voltage reading is gone and USB insertion is either disabled or read from
  * PD4 when POWER_USB_DETECT is enabled in board.h.
  ******************************************************************************
  */

#include "Power.h"
#include "board.h"
#include "bsp_power.h"
#include "bsp.h"
#include <string.h>

static Power_Data_t power_data;
static bool power_initialized = false;
static uint32_t last_update_tick = 0U;

static int calculate_battery_percent(float vbat)
{
    if (vbat <= BATTERY_MIN_VOLTAGE) {
        return 0;
    }
    if (vbat >= BATTERY_MAX_VOLTAGE) {
        return 100;
    }
    return (int)((vbat - BATTERY_MIN_VOLTAGE) /
                 (BATTERY_MAX_VOLTAGE - BATTERY_MIN_VOLTAGE) * 100.0f);
}

static void power_update(void)
{
    uint16_t raw = BSP_Power_ReadAdcAvg(BATT_ADC_CHANNEL, 16U);

    power_data.battery_voltage =
        ((float)raw / ADC_MAX_VALUE) * ADC_REF_VOLTAGE * POWER_VBAT_RATIO;
    power_data.usb_voltage = 0.0f;
    power_data.usb_inserted = BSP_Power_UsbInserted();
    power_data.battery_percent = calculate_battery_percent(power_data.battery_voltage);
    power_data.valid = true;
    last_update_tick = HAL_GetTick();
}

void Power_Init(void)
{
    if (power_initialized) {
        return;
    }

    BSP_Power_Init();
    memset(&power_data, 0, sizeof(power_data));
    power_data.valid = false;
    power_initialized = true;
}

void Power_StartTask(void)
{
    Power_Init();
    power_update();
}

void Power_TaskTick(void)
{
    if (!power_initialized) {
        return;
    }

    if ((HAL_GetTick() - last_update_tick) >= 500U) {
        power_update();
    }
}

void Power_GetData(Power_Data_t *data)
{
    if (data != NULL) {
        memcpy(data, &power_data, sizeof(power_data));
    }
}

float Power_ReadBatteryVoltage(void)
{
    return power_data.battery_voltage;
}

float Power_ReadUSBVoltage(void)
{
    return power_data.usb_voltage;
}

int Power_GetBatteryPercent(void)
{
    return power_data.battery_percent;
}

bool Power_IsUSBInserted(void)
{
    return power_data.usb_inserted;
}
