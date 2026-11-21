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
#include "bsp_keys.h"
#include "bsp_power.h"
#include "Power.h"
#include "OLED_UI.h"
#include "OLED_UI_MenuData.h"
#include "OLED_UI_Driver.h"
#include "OLED_driver.h"

/* Defined in OLED_UI.c; the brightness window edits it directly. */
extern int16_t OLED_UI_Brightness;

static void SystemClock_Config(void);
static void Error_Handler(void);
static void Board_SelfTest(void);

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

    BSP_Buzzer_Tone(2700U, 500U);

    Power_Init();
    Power_StartTask();

    /* Runs before the display is touched: the board can be validated over
       USART1 even with the OLED, 4G and ESP8266 footprints still empty. */
    Board_SelfTest();

    OLED_UI_Init(&MainMenuPage);

    /* SH1106 panels are noticeably dimmer than SSD1306 at the same contrast;
       180 keeps the stock UI readable while leaving headroom for the slider. */
    OLED_UI_Brightness = 180;
    OLED_Brightness(OLED_UI_Brightness);

    printf("[ui] OmniX_UI started, battery=%d%% (%.2f V)\r\n",
           Power_GetBatteryPercent(), (double)Power_ReadBatteryVoltage());

    uint32_t led_tick = HAL_GetTick();
    uint32_t diag_tick = HAL_GetTick();
    uint8_t last_key_state = 0xFFU;

    for (;;) {
        BSP_Keys_Scan();

        {
            uint8_t key_state = 0U;
            key_state |= (BSP_Key_Up() == 0U) ? 0x08U : 0U;
            key_state |= (BSP_Key_Down() == 0U) ? 0x04U : 0U;
            key_state |= (BSP_Key_Enter() == 0U) ? 0x02U : 0U;
            key_state |= (BSP_Key_Back() == 0U) ? 0x01U : 0U;
            if (key_state != last_key_state) {
                last_key_state = key_state;
                printf("[key] U/D/E/B=%d%d%d%d out=%u pressed=0x%X raw=0x%02X\r\n",
                       BSP_Key_Up(), BSP_Key_Down(), BSP_Key_Enter(), BSP_Key_Back(),
                       BSP_Keys_JoyRaw(), key_state, BSP_Keys_RawMask());
            }
        }

        if (OLED_UI_TakeTick()) {
            OLED_UI_InterruptHandler();
        }

        OLED_UI_MainLoop();
        Power_TaskTick();

        if ((HAL_GetTick() - led_tick) >= 500U) {
            led_tick = HAL_GetTick();
            BSP_Led_Toggle();
        }

        /* 2 s heartbeat: key levels and battery are visible on the console
           without any display fitted. */
        if ((HAL_GetTick() - diag_tick) >= 2000U) {
            diag_tick = HAL_GetTick();
            printf("[hb] t=%lus keys U/D/E/B=%d%d%d%d out=%u bat=%lumV\r\n",
                   (unsigned long)(HAL_GetTick() / 1000U),
                   BSP_Key_Up(), BSP_Key_Down(), BSP_Key_Enter(), BSP_Key_Back(),
                   BSP_Keys_JoyRaw(),
                   (unsigned long)(Power_ReadBatteryVoltage() * 1000.0f));
        }

        HAL_Delay(10U);
    }
}

/**
  * @brief  Console-only board check.  Keeps working with no OLED / modem / WiFi.
  */
static void Board_SelfTest(void)
{
    uint32_t uid0 = HAL_GetUIDw0();
    uint32_t uid1 = HAL_GetUIDw1();
    uint32_t uid2 = HAL_GetUIDw2();
    uint16_t flash_kb = *(__IO uint16_t *)FLASHSIZE_BASE;
    uint32_t clock_src = __HAL_RCC_GET_SYSCLK_SOURCE();
    const char *clock_name;
    uint16_t raw = BSP_Power_ReadAdcAvg(BATT_ADC_CHANNEL, 8U);
    float vbat = ((float)raw / 4095.0f) * 3.3f * POWER_VBAT_RATIO;

    switch (clock_src) {
        case RCC_SYSCLKSOURCE_STATUS_HSI: clock_name = "HSI"; break;
        case RCC_SYSCLKSOURCE_STATUS_HSE: clock_name = "HSE"; break;
        case RCC_SYSCLKSOURCE_STATUS_PLLCLK: clock_name = "PLL"; break;
        default: clock_name = "?"; break;
    }

    BSP_Keys_Scan();

    printf("\r\n[selftest] ---------------- board check ----------------\r\n");
    printf("[selftest] UID       : %08lX-%08lX-%08lX\r\n",
           (unsigned long)uid0, (unsigned long)uid1, (unsigned long)uid2);
    printf("[selftest] MCU flash : %u KB\r\n", (unsigned)flash_kb);
    printf("[selftest] SYSCLK    : %lu Hz (%s), HCLK %lu Hz\r\n",
           (unsigned long)SystemCoreClock, clock_name,
           (unsigned long)HAL_RCC_GetHCLKFreq());
    printf("[selftest] UART1     : 115200 8N1 OK (PA9/PA10)\r\n");
    printf("[selftest] keys      : U/D/E/B = %d/%d/%d/%d (0=pressed)\r\n",
           BSP_Key_Up(), BSP_Key_Down(), BSP_Key_Enter(), BSP_Key_Back());
    printf("[selftest] 5-way     : OUT1/OUT2 raw=%u, KEY0..4 mask=0x%02X\r\n",
           BSP_Keys_JoyRaw(), BSP_Keys_RawMask());
    printf("[selftest] BAT raw   : %u  -> %.2f V (ratio %.2f)\r\n",
           (unsigned)raw, (double)vbat, (double)POWER_VBAT_RATIO);
    printf("[selftest] LED PD15  : heartbeat after this banner\r\n");
    printf("[selftest] BEEP PB9  : short tone after this banner\r\n");
    printf("[selftest] --------------------------------------------------\r\n");

    BSP_Buzzer_Tone(2700U, 500U);
    BSP_Led_Set(true);
    BSP_DelayMs(100);
    BSP_Led_Set(false);
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
#if defined(TARGET_STM32F407)
    osc.PLL.PLLN = 336U;   /* 168 MHz, F407 maximum */
#else
    osc.PLL.PLLN = 360U;   /* 180 MHz, F429 with over-drive */
#endif
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

#if !defined(TARGET_STM32F407)
    /* 180 MHz needs over-drive on the STM32F42x/43x; the F407 tops out at
       168 MHz and has no over-drive. */
    if (HAL_PWREx_EnableOverDrive() != HAL_OK) {
        Error_Handler();
    }
#endif

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
