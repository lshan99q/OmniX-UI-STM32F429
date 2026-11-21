# OmniX_UI · STM32F407 / STM32F429 移植版

把原本跑在 ESP32 上的 **OmniX_UI v1.4**（`Omni_UI.v1.4.zip` 根工程 `oled_ui`）完整移植到
**STM32F429VET6 / STM32F407VET6 + 4G 物联网开发板**，显示、按键、电源、菜单与动画全部按新硬件重写。

> ## ⚠️ 实测芯片不是 F429
>
> 用 ST-Link 读到的 **Chip ID = 0x413**，对应 **STM32F407 / F405**；F429 应该是 `0x419`。
> 这块板子实际焊的是 F407 系列（也可能是打磨成 F429 的片子）。
>
> - **本板请用 `-DMCU_FAMILY=F407` 构建**（168 MHz，128 KB 主 SRAM）
> - F429 构建保留：`-DMCU_FAMILY=F429`（180 MHz，192 KB 主 SRAM）
> - F429 固件在 F407 上会卡在 180 MHz Over-drive 初始化，不能直接跑

- UI 框架：OmniX_UI v1.4（多级菜单 / 磁贴 / 列表 / 窗口 / 淡入淡出 / 回弹动画 / 四种字号 / 中英文混排 / FPS / 暗色模式 / 亮度 / 充电动画）
- MCU：STM32F407VET6（实测）或 STM32F429VET6，Cortex-M4F，512 KB Flash
- 显示：SH1106（兼容 SSD1306）128×64，四线 SPI，SPI3
- 输入：五向开关 + KEY0–KEY4（实测五向开关接在 KEY0–KEY4 上）
- 电源：PB1（ADC1_IN9）电池分压检测
- 工具链：GNU Arm Embedded（`arm-none-eabi-gcc`）+ CMake + Ninja，无 IDE 依赖
- 调试：SWD 烧录；**没有 USB-TTL 也能通过 ST-Link 读 RAM 日志**

> 原工程中依赖新板没有的硬件的入口已删除：
> **SHT30 温湿度页、红外万能遥控、洗衣机劫持**（以及 SHT30 驱动、USB 电压 ADC 读数）。
> 电量页保留，改为只读电池 ADC。

## 一、硬件映射

| 功能 | 引脚 | 说明 |
|---|---|---|
| OLED SCK | PB3 | SPI3_SCK，AF6 |
| OLED MOSI | PB5 | SPI3_MOSI，AF6 |
| OLED DC | PB4 | GPIO 输出（与 SPI3_MISO 复用，见“注意事项”） |
| OLED CS | PD10 | GPIO 输出，低有效 |
| OLED RST | PA8 | 与 4G `SRST` 共用 |
| 按键 KEY0…KEY4 | PB2 / PE9 / PE10 / PE15 / PB10 | 内部上拉，低有效 |
| 五向开关 | KEY0–KEY4 | **实测：不是 PA4/PA5** |
| 电池检测 | PB1 | ADC1_IN9，默认 1:1 分压 |
| 状态灯 | PD15 | 低电平点亮，500 ms 心跳（本板未焊） |
| 蜂鸣器 | PB9 | TIM4_CH4，无源，开机 500 ms 提示音 |
| 调试串口 | PA9/PA10（USART1）或 PD5/PD6（USART2/CN1） | 115200 8N1 |
| 4G EC600S | USART3 PD8/PD9，PWRKEY PC0，RESET PA8 | 本固件只初始化，不驱动 |
| WiFi ESP8266 | USART2 PD5/PD6，EN PD3，RST PA15 | 本固件保持 EN/RST 高，不驱动 |
| 外置 Flash | CS PA0，SPI3 | 本固件保持片选高；PB4 被 OLED DC 占用 |

### 五向开关实测映射

| 方向 | 实际按键 | 固件动作 |
|---|---|---|
| 上 | KEY2 (PE10) | Up |
| 下 | KEY4 (PB10) | Down |
| 左 | KEY0 (PB2) | Back |
| 右 | KEY3 (PE15) | Enter |
| 中间 | KEY1 (PE9) | Enter |

映射写在 `firmware/BSP/Src/bsp_keys.c` 的 `BSP_Key_Up/Down/Enter/Back()` 里。

## 二、编译

### 1. 安装工具链

GNU Arm Embedded Toolchain 13.x/14.x，CMake ≥ 3.20，Ninja。
把 `arm-none-eabi-gcc` 加入 PATH，或配置时传 `-DARM_TOOLCHAIN_PATH=...`。

### 2. 构建（本板：F407）

```powershell
cmake -S . -B build-f407 -G Ninja `
  -DARM_TOOLCHAIN_PATH="C:/Tools/arm-none-eabi" `
  -DMCU_FAMILY=F407 `
  -DDEBUG_UART_ON_USART2=ON
cmake --build build-f407
```

调试日志也可以走 USART1（不传 `DEBUG_UART_ON_USART2`）。

### 3. 构建（真正的 F429）

```powershell
cmake -S . -B build-f429 -G Ninja `
  -DARM_TOOLCHAIN_PATH="C:/Tools/arm-none-eabi" `
  -DMCU_FAMILY=F429
cmake --build build-f429
```

产物：

```
build-f407/OmniX_STM32F407.elf
build-f407/OmniX_STM32F407.hex
build-f407/OmniX_STM32F407.bin
build-f407/OmniX_STM32F407.map
```

本仓库同时提供已验证的预编译固件（见 `prebuilt/`）：

```
prebuilt/OmniX_STM32F407_uart2.hex   # 本板 F407，日志走 USART2/CN1
prebuilt/OmniX_STM32F407_uart2.bin
prebuilt/OmniX_STM32F429.hex         # 仅给真正的 F429
prebuilt/SHA256SUMS.txt
```

F407 实测构建：**Flash 82,248 B / 512 KB，RAM 22,480 B / 128 KB**（含 4 KB RAM 日志缓冲）。
工具链：`arm-none-eabi-gcc 14.2.1`，`-mcpu=cortex-m4 -mfloat-abi=hard -O2`。

## 三、烧录

ST-Link V2 + SWD（PA13/PA14/GND/NRST）。板子用 Type-C 自供电，ST-Link 的 3.3V/5V 不要接。

用 `st-flash`（本仓库调试用的 CLI，支持 Intel HEX）：

```powershell
st-flash --format ihex --reset --mass-erase write prebuilt/OmniX_STM32F407_uart2.hex
```

或 STM32CubeProgrammer：

```powershell
STM32_Programmer_CLI -c port=SWD -w prebuilt/OmniX_STM32F407_uart2.hex -v -rst
```

> 克隆版 ST-Link 若在 Windows 下报 `Found 0 stlink programmers`，用 Zadig 给
> `STM32 STLink` 安装 **WinUSB** 驱动即可（本机已实测）。

## 四、看日志（不需要 USB-TTL）

固件把 `printf` 同时写入一个 4 KB RAM 环形缓冲区，可以用 ST-Link 直接读出来：

```powershell
# 符号地址用 nm 查：
arm-none-eabi-nm build-f407/OmniX_STM32F407.elf | findstr "bsp_log_buf bsp_log_head"

st-flash read log.bin  0x200017a0 4096
st-flash read head.bin 0x200027a0 4
```

然后用 `tools/watch_keys.py` 或任意脚本按 head 拼接环形缓冲区并解码 UTF-8。
本机实测输出示例：

```
[selftest] UID       : 001A003B-30345109-32303836
[selftest] MCU flash : 512 KB
[selftest] SYSCLK    : 168000000 Hz (PLL), HCLK 168000000 Hz
[selftest] keys      : U/D/E/B = 1/1/1/1
[selftest] 5-way     : OUT1/OUT2 raw=3, KEY0..4 mask=0x1F
[key] U/D/E/B=0111 out=3 pressed=0x8 raw=0x1B
[hb] t=19s keys U/D/E/B=1111 out=3 bat=16mV
```

也可以接 USB-TTL 到 CN1 的 **5 脚（USART2_TX）/7 脚（USART2_RX）/GND**，115200 8N1。

## 五、与原 ESP32 工程的区别

| 项目 | ESP32 原版 | 本移植版 |
|---|---|---|
| OLED 接口 | I2C SSD1306（GPIO21/22） | SPI3 SH1106（PB3/PB5/PD10/DC=PB4/RST=PA8） |
| 显示驱动 | `OLED_driver.c` I2C | 重写为 SPI + SH1106 初始化/列偏移 |
| 按键 | 4 个 GPIO | 五向开关（KEY0–KEY4）+ 独立键，20 ms 去抖 |
| 时间基准 | `esp_timer` 20 ms 回调 | TIM6 20 ms 中断置标志，主循环执行 `OLED_UI_InterruptHandler()` |
| 延时 | FreeRTOS `vTaskDelay` | DWT 微秒延时 + `HAL_Delay` |
| 电源 | 电池 ADC + USB 电压 ADC | 仅电池 ADC（PB1）；USB 检测默认关闭 |
| 温湿度 | SHT30（I2C） | **删除**（新硬件无此器件） |
| 红外/洗衣机 | 红外发射相关入口 | **删除**（新硬件无红外） |
| 任务模型 | FreeRTOS 多任务 | 裸机主循环 + 定时器中断 |
| 调试 | USB/JTAG | SWD + RAM 日志；可选 USART1/USART2 |

## 六、目录结构

```
.
├─ CMakeLists.txt
├─ cmake/arm-none-eabi.cmake
├─ build.ps1
├─ firmware/
│  ├─ Core/            # main、时钟、中断、newlib 桩
│  ├─ BSP/             # OLED SPI、按键、ADC、串口、蜂鸣器、LED、RAM 日志
│  ├─ App/OmniX/       # OmniX_UI v1.4 源码 + 菜单数据 + 移植层
│  ├─ App/Services/    # Power（电池）
│  ├─ Drivers/         # STM32F4 HAL + CMSIS（ST 官方）
│  └─ Startup/         # startup_stm32f407xx.s / f429、链接脚本
├─ docs/               # 引脚、移植、上板调试说明
├─ prebuilt/           # 预编译 HEX/BIN
└─ tools/              # 本机调试脚本（可选）
```

## 七、注意事项

1. **芯片型号**：本板实测 `0x413`（F407/F405），默认构建必须是 `MCU_FAMILY=F407`；换成真正的 F429 才用 F429 构建。
2. **PB4 双职责**：OLED DC 与 SPI3_MISO 同脚，本固件不使用外置 GD25Q128E；以后读 Flash 必须切回 AF6 并加互斥。
3. **PA8 共用**：OLED RST 与 4G `SRST` 同网络，OLED 复位会同时复位 4G。
4. **五向开关**：实测接在 KEY0–KEY4，不是文档写的 PA4/PA5；方向映射见上表。若你的板子接线不同，改 `bsp_keys.c` 的四个 getter。
5. **电池分压比**：`Power.h` 的 `POWER_VBAT_RATIO` 默认 2.0，必须按实际电阻改成 `(Rtop+Rbottom)/Rbottom`。
6. **USB 插入检测默认关闭**：PD4 是 USB-A VBUS 控制输出，不能可靠判断充电插入。
7. **HSE 8 MHz**：若晶振不起振，固件退回 16 MHz HSI；串口日志仍可读，但 UI 变慢。
8. **SH1106 vs SSD1306**：默认 SH1106（列偏移 2）；SSD1306 屏把 `board.h` 的 `OMNIX_OLED_SH1106` 改为 0。
9. **4G/WiFi**：只做安全初态，未接入 UI；需要时在 `BSP` 下新增 AT 驱动。

## 八、许可与致谢

- UI 框架来自 **OmniX_UI / OLED_UI**（作者 bdth-7777777，Apache-2.0）：
  <https://github.com/bdth-7777777/OLED_UI>
- STM32F4 HAL / CMSIS：STMicroelectronics，BSD-3-Clause。
- 本移植版同样以 **Apache-2.0** 发布，见 [LICENSE](LICENSE)。
