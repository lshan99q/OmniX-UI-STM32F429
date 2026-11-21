/**
  ******************************************************************************
  * @file    bsp_oled.c
  * @brief   SPI3 transport for the SH1106/SSD1306 OLED.
  ******************************************************************************
  */

#include "bsp_oled.h"
#include "board.h"
#include "bsp.h"

static SPI_HandleTypeDef hspi3;

void BSP_OLED_Init(void)
{
    GPIO_InitTypeDef gpio = {0};

    /* SPI3 and the three control pins. */
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOD_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_SPI3_CLK_ENABLE();

    gpio.Pin = OLED_SCK_PIN | OLED_MOSI_PIN;
    gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    gpio.Alternate = GPIO_AF6_SPI3;
    HAL_GPIO_Init(GPIOB, &gpio);

    /* PB4 = OLED DC, not SPI3_MISO in this firmware. */
    gpio.Pin = OLED_DC_PIN;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    gpio.Alternate = 0;
    HAL_GPIO_Init(OLED_DC_PORT, &gpio);
    HAL_GPIO_WritePin(OLED_DC_PORT, OLED_DC_PIN, GPIO_PIN_RESET);

    gpio.Pin = OLED_CS_PIN;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(OLED_CS_PORT, &gpio);
    HAL_GPIO_WritePin(OLED_CS_PORT, OLED_CS_PIN, GPIO_PIN_SET);

    gpio.Pin = OLED_RST_PIN;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(OLED_RST_PORT, &gpio);
    HAL_GPIO_WritePin(OLED_RST_PORT, OLED_RST_PIN, GPIO_PIN_SET);

    hspi3.Instance = OLED_SPI;
    hspi3.Init.Mode = SPI_MODE_MASTER;
    hspi3.Init.Direction = SPI_DIRECTION_2LINES;
    hspi3.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi3.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi3.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi3.Init.NSS = SPI_NSS_SOFT;
    /* APB1 = 45 MHz, /8 = 5.625 MHz: comfortably inside the SH1106 limit. */
    hspi3.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_8;
    hspi3.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi3.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi3.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    hspi3.Init.CRCPolynomial = 10;

    if (HAL_SPI_Init(&hspi3) != HAL_OK) {
        BSP_ErrorHandler();
    }

    BSP_OLED_Reset();
}

void BSP_OLED_Reset(void)
{
    HAL_GPIO_WritePin(OLED_RST_PORT, OLED_RST_PIN, GPIO_PIN_RESET);
    BSP_DelayMs(20);
    HAL_GPIO_WritePin(OLED_RST_PORT, OLED_RST_PIN, GPIO_PIN_SET);
    BSP_DelayMs(20);
}

void BSP_OLED_Transmit(uint8_t dc_level, const uint8_t *data, uint16_t length)
{
    if (length == 0U) {
        return;
    }

    HAL_GPIO_WritePin(OLED_DC_PORT, OLED_DC_PIN,
                      dc_level ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(OLED_CS_PORT, OLED_CS_PIN, GPIO_PIN_RESET);

    if (HAL_SPI_Transmit(&hspi3, (uint8_t *)data, length, 1000U) != HAL_OK) {
        hspi3.ErrorCode = HAL_SPI_ERROR_NONE;
        hspi3.State = HAL_SPI_STATE_READY;
    }

    HAL_GPIO_WritePin(OLED_CS_PORT, OLED_CS_PIN, GPIO_PIN_SET);
}
