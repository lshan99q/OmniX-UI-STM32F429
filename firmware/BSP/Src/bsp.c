/**
  ******************************************************************************
  * @file    bsp.c
  * @brief   Board bring-up and common helpers.
  ******************************************************************************
  */

#include "bsp.h"
#include "board.h"
#include "bsp_led.h"
#include "bsp_keys.h"
#include "bsp_power.h"
#include "bsp_serial.h"
#include "bsp_buzzer.h"
#include "bsp_oled.h"

void BSP_Init(void)
{
    GPIO_InitTypeDef gpio = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOD_CLK_ENABLE();
    __HAL_RCC_GPIOE_CLK_ENABLE();
    __HAL_RCC_SYSCFG_CLK_ENABLE();
    __HAL_RCC_PWR_CLK_ENABLE();

    /* Enable the DWT cycle counter for the microsecond delay. */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    /* Keep the ESP8266 out of reset and enabled; the UI does not use it yet,
       but a floating EN/IO0 is a common source of boot current and noise. */
    HAL_GPIO_WritePin(ESP_EN_PORT, ESP_EN_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(ESP_RST_PORT, ESP_RST_PIN, GPIO_PIN_SET);
    gpio.Pin = ESP_EN_PIN;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(ESP_EN_PORT, &gpio);
    gpio.Pin = ESP_RST_PIN;
    HAL_GPIO_Init(ESP_RST_PORT, &gpio);

    /* 4G PWRKEY is left low (module off).  The shared PA8 reset line is driven
       by the OLED reset sequence below. */
    HAL_GPIO_WritePin(MODEM_PWRKEY_PORT, MODEM_PWRKEY_PIN, GPIO_PIN_RESET);
    gpio.Pin = MODEM_PWRKEY_PIN;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(MODEM_PWRKEY_PORT, &gpio);

    /* USB-A VBUS switch off by default. */
    HAL_GPIO_WritePin(USB_DETECT_PORT, USB_DETECT_PIN, GPIO_PIN_RESET);
    gpio.Pin = USB_DETECT_PIN;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(USB_DETECT_PORT, &gpio);

    /* External flash deselected (high). */
    HAL_GPIO_WritePin(FLASH_CS_PORT, FLASH_CS_PIN, GPIO_PIN_SET);
    gpio.Pin = FLASH_CS_PIN;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(FLASH_CS_PORT, &gpio);

    BSP_Serial_Init();
    BSP_Led_Init();
    BSP_Power_Init();
    BSP_Keys_Init();
    BSP_Buzzer_Init();
    BSP_OLED_Init();
}

void BSP_DelayUs(uint32_t us)
{
    uint32_t start = DWT->CYCCNT;
    uint32_t cycles = us * (SystemCoreClock / 1000000U);
    while ((DWT->CYCCNT - start) < cycles) {
        __NOP();
    }
}

void BSP_DelayMs(uint32_t ms)
{
    HAL_Delay(ms);
}

uint32_t BSP_GetTick(void)
{
    return HAL_GetTick();
}

void BSP_ErrorHandler(void)
{
    __disable_irq();
    BSP_Led_Set(true);
    for (;;) {
    }
}
