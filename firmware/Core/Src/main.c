/**
  ******************************************************************************
  * @file    main.c
  * @brief   OmniX_UI v1.4 port to the STM32F429VET6 4G IoT board.
  *
  * Target : STM32F429VET6, 180 MHz, 512 KB flash, 256 KB SRAM
  * Display: SH1106 / SSD1306 128x64, SPI3 (SCK PB3, MOSI PB5, DC PB4,
  *          CS PD10, RST PA8)
  * Input  : KEY0..KEY4 + analog five-way switch (PA4/PA5)
  * Power  : battery divider PB1 (ADC1_IN9)
  *
  * The UI core, widgets, fonts and menu pages are the unmodified OmniX_UI
  * v1.4 sources; only the hardware layer (display, keys, power) is new.
  ******************************************************************************
  */

#include "stm32f4xx_hal.h"
#include <stdio.h>
#include "board.h"
#include "bsp.h"
#include "bsp_serial.h"
#include "bsp_led.h"
#include "bsp_buzzer.h"
#include "Power.h"
#include "OLED_UI.h"
#include "OLED_UI_MenuData.h"
#include "OLED_UI_Driver.h"
#include "OLED_driver.h"

/* Defined in OLED_UI.c; the brightness window edits it directly. */
extern int16_t OLED_UI_Brightness;

static void SystemClock_Config(void);
static void Error_Handler(void);

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    BSP_Init();

    printf("\r\n==============================================\r\n");
    printf(" OmniX_UI v1.4 - STM32F429VET6 4G IoT Board\r\n");
    printf(" SYSCLK %lu Hz, HCLK %lu Hz\r\n",
           (unsigned long)SystemCoreClock,
           (unsigned long)HAL_RCC_GetHCLKFreq());
    printf(" Build: %s %s\r\n", __DATE__, __TIME__);
    printf("==============================================\r\n");

    BSP_Buzzer_Tone(2200U, 70U);

    Power_Init();
    Power_StartTask();

    OLED_UI_Init(&MainMenuPage);

    /* SH1106 panels are noticeably dimmer than SSD1306 at the same contrast;
       180 keeps the stock UI readable while leaving headroom for the slider. */
    OLED_UI_Brightness = 180;
    OLED_Brightness(OLED_UI_Brightness);

    printf("[ui] OmniX_UI started, battery=%d%% (%.2f V)\r\n",
           Power_GetBatteryPercent(), (double)Power_ReadBatteryVoltage());

    uint32_t led_tick = HAL_GetTick();

    for (;;) {
        BSP_Keys_Scan();

        if (OLED_UI_TakeTick()) {
            OLED_UI_InterruptHandler();
        }

        OLED_UI_MainLoop();
        Power_TaskTick();

        if ((HAL_GetTick() - led_tick) >= 500U) {
            led_tick = HAL_GetTick();
            BSP_Led_Toggle();
        }

        HAL_Delay(10U);
    }
}

/**
  * @brief  HSE 8 MHz -> PLL -> 180 MHz SYSCLK.
  *         Falls back to the 16 MHz HSI when the crystal does not start.
  */
static void SystemClock_Config(void)
{
    RCC_OscInitTypeDef osc = {0};
    RCC_ClkInitTypeDef clk = {0};

    __HAL_RCC_PWR_CLK_ENABLE();

    osc.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    osc.HSEState = RCC_HSE_ON;
    osc.PLL.PLLState = RCC_PLL_ON;
    osc.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    osc.PLL.PLLM = 8U;
    osc.PLL.PLLN = 360U;
    osc.PLL.PLLP = RCC_PLLP_DIV2;
    osc.PLL.PLLQ = 7U;

    if (HAL_RCC_OscConfig(&osc) != HAL_OK) {
        /* Crystal missing or not populated: run from the internal HSI so the
           board still boots and the console explains what happened. */
        osc.OscillatorType = RCC_OSCILLATORTYPE_HSI;
        osc.HSEState = RCC_HSE_OFF;
        osc.HSIState = RCC_HSI_ON;
        osc.PLL.PLLState = RCC_PLL_OFF;
        if (HAL_RCC_OscConfig(&osc) != HAL_OK) {
            Error_Handler();
        }

        clk.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                        RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
        clk.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
        clk.AHBCLKDivider = RCC_SYSCLK_DIV1;
        clk.APB1CLKDivider = RCC_HCLK_DIV1;
        clk.APB2CLKDivider = RCC_HCLK_DIV1;

        if (HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_0) != HAL_OK) {
            Error_Handler();
        }
        return;
    }

    /* 180 MHz needs over-drive on the STM32F42x/43x. */
    if (HAL_PWREx_EnableOverDrive() != HAL_OK) {
        Error_Handler();
    }

    clk.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                    RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    clk.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    clk.AHBCLKDivider = RCC_SYSCLK_DIV1;
    clk.APB1CLKDivider = RCC_HCLK_DIV4;
    clk.APB2CLKDivider = RCC_HCLK_DIV2;

    if (HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_5) != HAL_OK) {
        Error_Handler();
    }
}

static void Error_Handler(void)
{
    __disable_irq();
    BSP_Led_Set(true);
    for (;;) {
    }
}
