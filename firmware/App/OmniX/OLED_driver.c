/**
  ******************************************************************************
  * @file    OLED_driver.c
  * @brief   OmniX_UI OLED hardware layer for the STM32F429 4G board.
  *
  * The original ESP32 project used an I2C SSD1306.  This board has a 7-pin
  * SPI panel (SH1106 by default), so the transport, reset and init sequence
  * are replaced while the framebuffer API stays identical.
  ******************************************************************************
  */

#include "OLED.h"
#include "OLED_driver.h"
#include "board.h"
#include "bsp_oled.h"
#include "bsp.h"

uint8_t OLED_DisplayBuf[OLED_HEIGHT / 8][OLED_WIDTH];
bool OLED_ColorMode = true;

static void OLED_WriteCommand(uint8_t command)
{
    BSP_OLED_Transmit(0U, &command, 1U);
}

static void OLED_WriteData(uint8_t *data, uint8_t count)
{
    if (count == 0U) {
        return;
    }

    if (!OLED_ColorMode) {
        uint8_t inverted[OLED_WIDTH];
        for (uint8_t i = 0U; i < count; i++) {
            inverted[i] = (uint8_t)~data[i];
        }
        BSP_OLED_Transmit(1U, inverted, count);
    } else {
        BSP_OLED_Transmit(1U, data, count);
    }
}

void OLED_SetColorMode(bool colormode)
{
    OLED_ColorMode = colormode;
}

void OLED_SetCursor(uint8_t page, uint8_t x)
{
#if OMNIX_OLED_SH1106
    uint8_t column = (uint8_t)(x + SH1106_COLUMN_OFFSET);
#else
    uint8_t column = x;
#endif

    OLED_WriteCommand((uint8_t)(0xB0U | page));
    OLED_WriteCommand((uint8_t)(0x10U | ((column & 0xF0U) >> 4)));
    OLED_WriteCommand((uint8_t)(0x00U | (column & 0x0FU)));
}

void OLED_Init(void)
{
    /* The SPI bus and the reset pin are already initialised by BSP_Init();
       pulse reset again so a soft re-init also recovers a locked panel. */
    BSP_OLED_Reset();

    OLED_WriteCommand(0xAE);       /* display off */
    OLED_WriteCommand(0xD5);       /* clock divide / oscillator */
    OLED_WriteCommand(0x80);
    OLED_WriteCommand(0xA8);       /* multiplex ratio */
    OLED_WriteCommand(0x3F);
    OLED_WriteCommand(0xD3);       /* display offset */
    OLED_WriteCommand(0x00);
    OLED_WriteCommand(0x40);       /* start line 0 */
    OLED_WriteCommand(0xA1);       /* segment remap */
    OLED_WriteCommand(0xC8);       /* COM scan direction */
    OLED_WriteCommand(0xDA);       /* COM pins */
    OLED_WriteCommand(0x12);

#if OMNIX_OLED_SH1106
    OLED_WriteCommand(0xAD);       /* SH1106 DC-DC on */
    OLED_WriteCommand(0x8B);
#else
    OLED_WriteCommand(0x8D);       /* SSD1306 charge pump */
    OLED_WriteCommand(0x14);
    OLED_WriteCommand(0x20);       /* horizontal addressing */
    OLED_WriteCommand(0x00);
#endif

    OLED_WriteCommand(0x81);       /* contrast */
    OLED_WriteCommand(0xCF);
    OLED_WriteCommand(0xD9);       /* pre-charge */
    OLED_WriteCommand(0xF1);
    OLED_WriteCommand(0xDB);       /* VCOMH */
    OLED_WriteCommand(0x40);
    OLED_WriteCommand(0xA4);       /* resume RAM content */
    OLED_WriteCommand(0xA6);       /* normal (not inverted) */
    OLED_WriteCommand(0xAF);       /* display on */

    for (uint8_t i = 0U; i < (OLED_HEIGHT / 8U); i++) {
        for (uint8_t j = 0U; j < OLED_WIDTH; j++) {
            OLED_DisplayBuf[i][j] = 0x00U;
        }
    }
    OLED_Update();
}

void OLED_Update(void)
{
    for (uint8_t page = 0U; page < (OLED_HEIGHT / 8U); page++) {
        OLED_SetCursor(page, 0U);
        OLED_WriteData(OLED_DisplayBuf[page], OLED_WIDTH);
    }
}

void OLED_Brightness(int16_t brightness)
{
    if (brightness > 255) {
        brightness = 255;
    }
    if (brightness < 0) {
        brightness = 0;
    }

    OLED_WriteCommand(0x81);
    OLED_WriteCommand((uint8_t)brightness);
}

void OLED_UpdateArea(uint8_t x, uint8_t y, uint8_t width, uint8_t height)
{
    if ((x >= OLED_WIDTH) || (y >= OLED_HEIGHT)) {
        return;
    }
    if ((uint16_t)x + width > OLED_WIDTH) {
        width = (uint8_t)(OLED_WIDTH - x);
    }
    if ((uint16_t)y + height > OLED_HEIGHT) {
        height = (uint8_t)(OLED_HEIGHT - y);
    }

    uint8_t first_page = (uint8_t)(y / 8U);
    uint8_t last_page = (uint8_t)((y + height - 1U) / 8U);

    for (uint8_t page = first_page; page <= last_page; page++) {
        OLED_SetCursor(page, x);
        OLED_WriteData(&OLED_DisplayBuf[page][x], width);
    }
}
