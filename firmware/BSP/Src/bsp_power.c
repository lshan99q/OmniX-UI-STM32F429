/**
  ******************************************************************************
  * @file    bsp_power.c
  * @brief   ADC1 driver for battery voltage and the analog five-way switch.
  ******************************************************************************
  */

#include "bsp_power.h"
#include "board.h"
#include "bsp.h"

static ADC_HandleTypeDef hadc1;
static bool adc_ready = false;

void BSP_Power_Init(void)
{
    GPIO_InitTypeDef gpio = {0};

    if (adc_ready) {
        return;
    }

    __HAL_RCC_ADC1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    /* PB1 = ADC1_IN9, PA4 = ADC1_IN4, PA5 = ADC1_IN5. */
    gpio.Mode = GPIO_MODE_ANALOG;
    gpio.Pull = GPIO_NOPULL;
    gpio.Pin = BATT_PIN;
    HAL_GPIO_Init(BATT_PORT, &gpio);
    gpio.Pin = JOY1_PIN | JOY2_PIN;
    HAL_GPIO_Init(GPIOA, &gpio);

    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = DISABLE;
    hadc1.Init.ContinuousConvMode = DISABLE;
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.NbrOfDiscConversion = 0;
    hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = 1;
    hadc1.Init.DMAContinuousRequests = DISABLE;
    hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;

    if (HAL_ADC_Init(&hadc1) != HAL_OK) {
        BSP_ErrorHandler();
    }
    adc_ready = true;

#if POWER_USB_DETECT
    __HAL_RCC_GPIOD_CLK_ENABLE();
    gpio.Pin = USB_DETECT_PIN;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = USB_DETECT_ACTIVE_HIGH ? GPIO_PULLDOWN : GPIO_PULLUP;
    HAL_GPIO_Init(USB_DETECT_PORT, &gpio);
#endif
}

uint16_t BSP_Power_ReadAdc(uint32_t channel)
{
    ADC_ChannelConfTypeDef config = {0};

    if (!adc_ready) {
        return 0U;
    }

    config.Channel = channel;
    config.Rank = 1U;
    config.SamplingTime = ADC_SAMPLETIME_480CYCLES;
    config.Offset = 0U;

    if (HAL_ADC_ConfigChannel(&hadc1, &config) != HAL_OK) {
        return 0U;
    }

    if (HAL_ADC_Start(&hadc1) != HAL_OK) {
        return 0U;
    }

    if (HAL_ADC_PollForConversion(&hadc1, 10U) != HAL_OK) {
        (void)HAL_ADC_Stop(&hadc1);
        return 0U;
    }

    uint16_t value = (uint16_t)HAL_ADC_GetValue(&hadc1);
    (void)HAL_ADC_Stop(&hadc1);
    return value;
}

uint16_t BSP_Power_ReadAdcAvg(uint32_t channel, uint8_t samples)
{
    uint32_t sum = 0U;

    if (samples == 0U) {
        samples = 1U;
    }

    for (uint8_t i = 0U; i < samples; i++) {
        sum += BSP_Power_ReadAdc(channel);
    }

    return (uint16_t)(sum / samples);
}

bool BSP_Power_UsbInserted(void)
{
#if POWER_USB_DETECT
    GPIO_PinState state = HAL_GPIO_ReadPin(USB_DETECT_PORT, USB_DETECT_PIN);
    bool high = (state == GPIO_PIN_SET);
    return USB_DETECT_ACTIVE_HIGH ? high : !high;
#else
    return false;
#endif
}
