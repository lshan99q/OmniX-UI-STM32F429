/**
  ******************************************************************************
  * @file    OLED_UI_Driver.c
  * @brief   STM32F429 platform layer for OmniX_UI.
  *
  * A 20 ms TIM6 interrupt provides the UI timebase.  The handler itself is
  * executed from the main loop (not from the ISR) because OmniX_UI updates
  * menu state that the renderer also touches.
  ******************************************************************************
  */

#include "OLED_UI_Driver.h"
#include "stm32f4xx_hal.h"
#include "bsp.h"
#include "bsp_keys.h"

static TIM_HandleTypeDef htim6;
static volatile uint8_t ui_tick_pending = 0U;

void Timer_Init(void)
{
    __HAL_RCC_TIM6_CLK_ENABLE();

    htim6.Instance = TIM6;
    /* APB1 timer clock = 90 MHz, /9000 = 10 kHz, /200 = 20 ms. */
    htim6.Init.Prescaler = 8999U;
    htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim6.Init.Period = 199U;
    htim6.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;

    if (HAL_TIM_Base_Init(&htim6) != HAL_OK) {
        BSP_ErrorHandler();
    }

    HAL_NVIC_SetPriority(TIM6_DAC_IRQn, 5U, 0U);
    HAL_NVIC_EnableIRQ(TIM6_DAC_IRQn);

    if (HAL_TIM_Base_Start_IT(&htim6) != HAL_OK) {
        BSP_ErrorHandler();
    }
}

void OLED_UI_TimerIRQHandler(void)
{
    if ((__HAL_TIM_GET_FLAG(&htim6, TIM_FLAG_UPDATE) != RESET) &&
        (__HAL_TIM_GET_IT_SOURCE(&htim6, TIM_IT_UPDATE) != RESET)) {
        __HAL_TIM_CLEAR_IT(&htim6, TIM_IT_UPDATE);
        ui_tick_pending = 1U;
    }
}

uint8_t OLED_UI_TakeTick(void)
{
    if (ui_tick_pending != 0U) {
        ui_tick_pending = 0U;
        return 1U;
    }
    return 0U;
}

void Key_Init(void)
{
    BSP_Keys_Init();
}

void Encoder_Init(void)
{
}

void Encoder_Enable(void)
{
}

void Encoder_Disable(void)
{
}

int16_t Encoder_Get(void)
{
    return 0;
}

void Delay_us(uint32_t xus)
{
    BSP_DelayUs(xus);
}

void Delay_ms(uint32_t xms)
{
    BSP_DelayMs(xms);
}

void Delay_s(uint32_t xs)
{
    BSP_DelayMs(xs * 1000U);
}
