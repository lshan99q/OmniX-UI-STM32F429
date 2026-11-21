/**
  ******************************************************************************
  * @file    bsp_led.c
  * @brief   Status LED on PD15.
  ******************************************************************************
  */

#include "bsp_led.h"
#include "board.h"

void BSP_Led_Init(void)
{
    GPIO_InitTypeDef gpio = {0};

    __HAL_RCC_GPIOD_CLK_ENABLE();

    gpio.Pin = LED_PIN;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(LED_PORT, &gpio);

    BSP_Led_Set(false);
}

void BSP_Led_Set(bool on)
{
#if LED_ACTIVE_LOW
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, on ? GPIO_PIN_RESET : GPIO_PIN_SET);
#else
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, on ? GPIO_PIN_SET : GPIO_PIN_RESET);
#endif
}

void BSP_Led_Toggle(void)
{
    HAL_GPIO_TogglePin(LED_PORT, LED_PIN);
}
