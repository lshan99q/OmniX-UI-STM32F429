/**
  ******************************************************************************
  * @file    bsp_buzzer.c
  * @brief   Passive buzzer on PB9 / TIM4_CH4.
  ******************************************************************************
  */

#include "bsp_buzzer.h"
#include "board.h"
#include "bsp.h"

static TIM_HandleTypeDef htim4;

void BSP_Buzzer_Init(void)
{
    GPIO_InitTypeDef gpio = {0};
    TIM_OC_InitTypeDef oc = {0};

    __HAL_RCC_TIM4_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    gpio.Pin = BEEP_PIN;
    gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    gpio.Alternate = GPIO_AF2_TIM4;
    HAL_GPIO_Init(BEEP_PORT, &gpio);

    htim4.Instance = BEEP_TIM;
    htim4.Init.Prescaler = 89U;          /* 90 MHz / 90 = 1 MHz */
    htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim4.Init.Period = 249U;            /* 1 MHz / 250 = 4 kHz */
    htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim4.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;

    if (HAL_TIM_PWM_Init(&htim4) != HAL_OK) {
        BSP_ErrorHandler();
    }

    oc.OCMode = TIM_OCMODE_PWM1;
    oc.Pulse = 0U;
    oc.OCPolarity = TIM_OCPOLARITY_HIGH;
    oc.OCFastMode = TIM_OCFAST_DISABLE;

    if (HAL_TIM_PWM_ConfigChannel(&htim4, &oc, BEEP_TIM_CHANNEL) != HAL_OK) {
        BSP_ErrorHandler();
    }

    (void)HAL_TIM_PWM_Start(&htim4, BEEP_TIM_CHANNEL);
    BSP_Buzzer_Off();
}

void BSP_Buzzer_Tone(uint16_t frequency_hz, uint16_t duration_ms)
{
    if (frequency_hz < 100U) {
        frequency_hz = 100U;
    }
    if (frequency_hz > 10000U) {
        frequency_hz = 10000U;
    }

    uint32_t period = 1000000UL / frequency_hz;

    __HAL_TIM_SET_PRESCALER(&htim4, 89U);
    __HAL_TIM_SET_AUTORELOAD(&htim4, period - 1U);
    __HAL_TIM_SET_COMPARE(&htim4, BEEP_TIM_CHANNEL, period / 2U);
    __HAL_TIM_SET_COUNTER(&htim4, 0U);

    BSP_DelayMs(duration_ms);
    BSP_Buzzer_Off();
}

void BSP_Buzzer_Off(void)
{
    __HAL_TIM_SET_COMPARE(&htim4, BEEP_TIM_CHANNEL, 0U);
}
