# 引脚与板级连接

本文只列本固件实际使用的信号。完整 100 脚定义见 `STM32引脚功能表.xlsx`。

## 显示（SH1106 / SSD1306 128×64，四线 SPI）

| 信号 | MCU 引脚 | 模式 | 备注 |
|---|---|---|---|
| SCK | PB3 | AF6 (SPI3_SCK) | 5.625 MHz |
| MOSI | PB5 | AF6 (SPI3_MOSI) | |
| DC | PB4 | GPIO 输出 | 与 SPI3_MISO 同脚；本固件不复用 Flash |
| CS | PD10 | GPIO 输出，低有效 | |
| RST | PA8 | GPIO 输出 | 与 4G `SRST` 同网络 |

初始化序列按 SH1106 编写（`0xAD/0x8B` 开 DC-DC，列偏移 +2）。
若屏是 SSD1306，把 `firmware/Core/Inc/board.h` 中 `OMNIX_OLED_SH1106` 改为 `0`。

## 按键

| 名称 | 引脚 | 内部上拉 | 功能 |
|---|---|---|---|
| KEY0 | PB2 | 是 | 确认（备用） |
| KEY1 | PE9 | 是 | 上 |
| KEY2 | PE10 | 是 | 下 |
| KEY3 | PE15 | 是 | 确认 |
| KEY4 | PB10 | 是 | 返回 |
| OUT1 | PA4 | 模拟 | 五向开关 X |
| OUT2 | PA5 | 模拟 | 五向开关 Y |

五向开关默认按两轴摇杆处理：中点 2048，死区 550。
`board.h` 中可改 `BSP_JOY_DEADZONE`、`BSP_JOY_INVERT_X/Y`、`BSP_JOY_USE_ADC`。

上电时会对 PA4/PA5 做 8 次采样：若噪声超过 250 LSB 或两路都停在电源轨，判定为悬空/数字开关并自动禁用五向开关，避免菜单自己乱跳；此时请用 KEY1…KEY4。

## 电源

| 信号 | 引脚 | 说明 |
|---|---|---|
| ADC_BAT | PB1 / ADC1_IN9 | 电池分压，`POWER_VBAT_RATIO` 默认 2.0 |
| USB_PWR | PD4 | 输出，控制 USB-A VBUS；默认关闭检测 |

## 人机

| 信号 | 引脚 | 说明 |
|---|---|---|
| LED | PD15 | 低电平点亮，500 ms 心跳 |
| BEEP | PB9 / TIM4_CH4 | 4 kHz PWM，开机 70 ms 短鸣 |

## 通信（本固件只做安全初态，不驱动协议）

| 模块 | 信号 | 初态 |
|---|---|---|
| EC600S | USART3 PD8/PD9，PWRKEY PC0 | PWRKEY 低（模块关） |
| EC600S | RESET PA8 | 与 OLED 复位共用 |
| ESP8266 | USART2 PD5/PD6，EN PD3，RST PA15 | EN=1，RST=1 |
| GD25Q128E | CS PA0，SPI3 | CS=1（不选中） |

## 调试

| 信号 | 引脚 | 参数 |
|---|---|---|
| USART1_TX | PA9 | 115200 8N1 |
| USART1_RX | PA10 | 115200 8N1 |
| SWDIO | PA13 | ST-Link |
| SWCLK | PA14 | ST-Link |
| NRST | 引脚 14 | CN1 |

## 时钟

- HSE：8 MHz（PH0/PH1），PLL M=8 / N=360 / P=2 / Q=7 → 180 MHz
- APB1 = 45 MHz，APB2 = 90 MHz，Flash latency 5，开启 Over-drive
- LSE：32.768 kHz（PC14/PC15），本固件未使用 RTC
