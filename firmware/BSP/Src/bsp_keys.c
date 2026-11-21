/**
  ******************************************************************************
  * @file    bsp_keys.c
  * @brief   Debounced five-way switch and five push buttons.
  *
  * Default mapping:
  *   KEY1 (PE9)  = UP          KEY2 (PE10) = DOWN
  *   KEY3 (PE15) = ENTER       KEY4 (PB10) = BACK
  *   KEY0 (PB2)  = ENTER (alternate)
  *   Five-way    = UP/DOWN, LEFT=BACK, RIGHT/centre=ENTER
  *
  * The two joystick outputs are analog on this board (PA4/PA5).  If your
  * switch is wired as plain GPIO, set BSP_JOY_USE_ADC to 0 in board.h.
  ******************************************************************************
  */

#include "bsp_keys.h"
#include "bsp_power.h"
#include "board.h"

typedef struct {
    GPIO_TypeDef *port;
    uint16_t pin;
    uint8_t stable;
    uint8_t counter;
} bsp_key_t;

static bsp_key_t keys[5] = {
    {KEY0_PORT, KEY0_PIN, 1U, 0U},
    {KEY1_PORT, KEY1_PIN, 1U, 0U},
    {KEY2_PORT, KEY2_PIN, 1U, 0U},
    {KEY3_PORT, KEY3_PIN, 1U, 0U},
    {KEY4_PORT, KEY4_PIN, 1U, 0U},
};

/* Debounced joystick directions, active-high bits. */
#define JOY_UP_BIT    0x01U
#define JOY_DOWN_BIT  0x02U
#define JOY_LEFT_BIT  0x04U
#define JOY_RIGHT_BIT 0x08U

static uint8_t joy_stable = 0U;
static uint8_t joy_candidate = 0U;
static uint8_t joy_counter = 0U;

static uint8_t joy_decode(void)
{
#if BSP_JOY_USE_ADC
    int32_t x = (int32_t)BSP_Power_ReadAdc(ADC_CHANNEL_4);
    int32_t y = (int32_t)BSP_Power_ReadAdc(ADC_CHANNEL_5);
    int32_t dx = x - 2048;
    int32_t dy = y - 2048;
    uint8_t dir = 0U;

#if BSP_JOY_INVERT_X
    dx = -dx;
#endif
#if BSP_JOY_INVERT_Y
    dy = -dy;
#endif

    if ((dx > (int32_t)BSP_JOY_DEADZONE) && (dx >= (dy < 0 ? -dy : dy))) {
        dir = JOY_RIGHT_BIT;
    } else if ((dx < -(int32_t)BSP_JOY_DEADZONE) && (-dx >= (dy < 0 ? -dy : dy))) {
        dir = JOY_LEFT_BIT;
    } else if (dy < -(int32_t)BSP_JOY_DEADZONE) {
        dir = JOY_UP_BIT;
    } else if (dy > (int32_t)BSP_JOY_DEADZONE) {
        dir = JOY_DOWN_BIT;
    }

    return dir;
#else
    return 0U;
#endif
}

void BSP_Keys_Init(void)
{
    GPIO_InitTypeDef gpio = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOE_CLK_ENABLE();

    gpio.Pin = KEY0_PIN | KEY4_PIN;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOB, &gpio);

    gpio.Pin = KEY1_PIN | KEY2_PIN | KEY3_PIN;
    HAL_GPIO_Init(GPIOE, &gpio);

    if (BSP_JOY_USE_ADC) {
        gpio.Pin = JOY1_PIN | JOY2_PIN;
        gpio.Mode = GPIO_MODE_ANALOG;
        gpio.Pull = GPIO_NOPULL;
        HAL_GPIO_Init(GPIOA, &gpio);
    }

    for (uint32_t i = 0U; i < 5U; i++) {
        keys[i].stable = (HAL_GPIO_ReadPin(keys[i].port, keys[i].pin) == GPIO_PIN_SET) ? 1U : 0U;
        keys[i].counter = 0U;
    }
    joy_stable = joy_candidate = joy_decode();
    joy_counter = 0U;
}

void BSP_Keys_Scan(void)
{
    for (uint32_t i = 0U; i < 5U; i++) {
        uint8_t pressed = (HAL_GPIO_ReadPin(keys[i].port, keys[i].pin) == GPIO_PIN_RESET) ? 1U : 0U;
        if (pressed != keys[i].stable) {
            if (++keys[i].counter >= 2U) {
                keys[i].stable = pressed;
                keys[i].counter = 0U;
            }
        } else {
            keys[i].counter = 0U;
        }
    }

    uint8_t dir = joy_decode();
    if (dir != joy_candidate) {
        joy_candidate = dir;
        joy_counter = 0U;
    } else if (++joy_counter >= 2U) {
        joy_stable = joy_candidate;
        joy_counter = 2U;
    }
}

uint8_t BSP_Key_Up(void)
{
    return (keys[1].stable || (joy_stable & JOY_UP_BIT)) ? 0U : 1U;
}

uint8_t BSP_Key_Down(void)
{
    return (keys[2].stable || (joy_stable & JOY_DOWN_BIT)) ? 0U : 1U;
}

uint8_t BSP_Key_Enter(void)
{
    return (keys[3].stable || keys[0].stable || (joy_stable & JOY_RIGHT_BIT)) ? 0U : 1U;
}

uint8_t BSP_Key_Back(void)
{
    return (keys[4].stable || (joy_stable & JOY_LEFT_BIT)) ? 0U : 1U;
}
