/**
  ******************************************************************************
  * @file    stm32f4xx_it.c
  * @brief   Interrupt handlers for the OmniX_UI STM32F429 port.
  ******************************************************************************
  */

#include "stm32f4xx_hal.h"
#include "bsp.h"
#include "bsp_led.h"
#include "OLED_UI_Driver.h"

void NMI_Handler(void)
{
}

void HardFault_Handler(void)
{
    __disable_irq();
    BSP_Led_Set(true);
    for (;;) {
    }
}

void MemManage_Handler(void)
{
    HardFault_Handler();
}

void BusFault_Handler(void)
{
    HardFault_Handler();
}

void UsageFault_Handler(void)
{
    HardFault_Handler();
}

void SVC_Handler(void)
{
}

void DebugMon_Handler(void)
{
}

void PendSV_Handler(void)
{
}

void SysTick_Handler(void)
{
    HAL_IncTick();
}

void TIM6_DAC_IRQHandler(void)
{
    OLED_UI_TimerIRQHandler();
}
