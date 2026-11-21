/**
  ******************************************************************************
  * @file    bsp_serial.c
  * @brief   USART1 debug console.
  ******************************************************************************
  */

#include "bsp_serial.h"
#include "board.h"
#include "bsp.h"
#include <stdarg.h>
#include <stdio.h>

static UART_HandleTypeDef huart1;

void BSP_Serial_Init(void)
{
    GPIO_InitTypeDef gpio = {0};

    __HAL_RCC_USART1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    gpio.Pin = DBG_TX_PIN | DBG_RX_PIN;
    gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Pull = GPIO_PULLUP;
    gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    gpio.Alternate = GPIO_AF7_USART1;
    HAL_GPIO_Init(GPIOA, &gpio);

    huart1.Instance = DBG_UART;
    huart1.Init.BaudRate = 115200U;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;

    if (HAL_UART_Init(&huart1) != HAL_OK) {
        BSP_ErrorHandler();
    }
}

void BSP_Serial_Write(const uint8_t *data, uint32_t length)
{
    if ((data != NULL) && (length > 0U)) {
        (void)HAL_UART_Transmit(&huart1, (uint8_t *)data, (uint16_t)length, 200U);
    }
}

int BSP_Serial_Printf(const char *format, ...)
{
    char buffer[192];
    va_list args;
    int length;

    va_start(args, format);
    length = vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);

    if (length > 0) {
        uint32_t to_send = ((uint32_t)length < sizeof(buffer)) ? (uint32_t)length : (sizeof(buffer) - 1U);
        BSP_Serial_Write((const uint8_t *)buffer, to_send);
    }

    return length;
}
