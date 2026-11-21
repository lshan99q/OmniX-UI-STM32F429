# OmniX_UI · STM32F429VET6 移植版

把原本跑在 ESP32 上的 **OmniX_UI v1.4**（`Omni_UI.v1.4.zip` 根工程 `oled_ui`）完整移植到
**STM32F429VET6 + 4G 物联网开发板**，显示、按键、电源、菜单与动画全部按新硬件重写。

- UI 框架：OmniX_UI v1.4（多级菜单 / 磁贴 / 列表 / 窗口 / 淡入淡出 / 回弹动画 / 四种字号 / 中英文混排 / FPS / 暗色模式 / 亮度 / 充电动画）
- MCU：STM32F429VET6，Cortex-M4F，180 MHz，512 KB Flash / 256 KB SRAM
- 显示：SH1106（兼容 SSD1306）128×64，四线 SPI，SPI3
- 输入：5 个独立按键 + 五向开关（PA4/PA5 模拟）
- 电源：PB1（ADC1_IN9）电池分压检测
- 工具链：GNU Arm Embedded（`arm-none-eabi-gcc`）+ CMake + Ninja，无任何 IDE 依赖

> 原工程中依赖新板没有的硬件的入口已按你的要求删除：
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
| 五向开关 OUT1/OUT2 | PA4 / PA5 | ADC1_IN4 / IN5 |
| 电池检测 | PB1 | ADC1_IN9，默认 1:1 分压 |
| 状态灯 | PD15 | 低电平点亮，500 ms 心跳 |
| 蜂鸣器 | PB9 | TIM4_CH4，4 kHz PWM，开机短鸣 |
| 调试串口 | PA9 / PA10 | USART1，115200 8N1 |
| 4G EC600S | USART3 PD8/PD9，PWRKEY PC0，RESET PA8 | 本固件只初始化，不驱动 |
| WiFi ESP8266 | USART2 PD5/PD6，EN PD3，RST PA15 | 本固件保持 EN/RST 高，不驱动 |
| 外置 Flash | CS PA0，SPI3 | 本固件保持片选高；PB4 被 OLED DC 占用 |

### 按键操作

| 操作 | 按键 |
|---|---|
| 上 / 下 | KEY1(PE9) / KEY2(PE10)，或五向开关上/下 |
| 确认 | KEY3(PE15) 或 KEY0(PB2)，或五向开关右/中 |
| 返回 | KEY4(PB10)，或五向开关左 |

五向开关是 **模拟量**：`bsp_keys.c` 里按“偏离中值 2048 超过死区 550”判方向。
如果你的开关方向相反，改 `board.h` 里的 `BSP_JOY_INVERT_X/Y`；死区改 `BSP_JOY_DEADZONE`。
如果板子上的五向开关其实是数字量，把 `BSP_JOY_USE_ADC` 设为 0，用 KEY1…KEY4 操作。

## 二、编译

### 1. 安装工具链

- GNU Arm Embedded Toolchain 13.x 或更新（[ARM 官方](https://developer.arm.com/downloads/-/gnu-rm)，或 xPack 版本）
- CMake ≥ 3.20、Ninja

把 `arm-none-eabi-gcc` 所在目录加入 PATH，或者配置时传 `-DARM_TOOLCHAIN_PATH=...`。

### 2. 构建

```powershell
cmake -S . -B build -G Ninja -DARM_TOOLCHAIN_PATH="C:/Tools/arm-none-eabi"
cmake --build build
```

Windows 下也可以直接运行：

```powershell
./build.ps1 -ToolchainPath "C:/Tools/arm-none-eabi"
```

产物：

```
build/OmniX_STM32F429.elf
build/OmniX_STM32F429.hex
build/OmniX_STM32F429.bin
build/OmniX_STM32F429.map
```

本仓库同时提供已验证的预编译固件（见 `prebuilt/`）：

```
prebuilt/OmniX_STM32F429.hex
prebuilt/OmniX_STM32F429.bin
prebuilt/OmniX_STM32F429.elf
prebuilt/SHA256SUMS.txt
```

编译结果：**Flash 81,016 B / 512 KB（15.5%），RAM 18,376 B / 192 KB（9.4%）**。
工具链：`arm-none-eabi-gcc 14.2.1`，`-mcpu=cortex-m4 -mfloat-abi=hard -O2`。

### 3. 烧录

ST-Link + SWD（PA13/PA14）：

```powershell
STM32_Programmer_CLI -c port=SWD -w build/OmniX_STM32F429.hex -v -rst
```

或 ST-LINK_CLI：

```powershell
ST-LINK_CLI -c SWD -P build/OmniX_STM32F429.hex -V -Rst
```

### 4. 看日志

USART1（PA9=TX，PA10=RX）接 USB-TTL，115200 8N1，3.3 V 电平。
上电会打印主频、构建时间、电池电压，然后进入 UI。

## 三、与原 ESP32 工程的区别

| 项目 | ESP32 原版 | STM32F429 移植版 |
|---|---|---|
| OLED 接口 | I2C SSD1306（GPIO21/22） | SPI3 SH1106（PB3/PB5/PD10/DC=PB4/RST=PA8） |
| 显示驱动 | `OLED_driver.c` I2C | 重写为 SPI + SH1106 初始化/列偏移 |
| 按键 | 4 个 GPIO（35/33/32/15） | 5 键 + 五向开关模拟量，带去抖 |
| 时间基准 | `esp_timer` 20 ms 回调 | TIM6 20 ms 中断置标志，主循环执行 `OLED_UI_InterruptHandler()` |
| 延时 | FreeRTOS `vTaskDelay` | DWT 微秒延时 + `HAL_Delay` |
| 电源 | 电池 ADC + USB 电压 ADC | 仅电池 ADC（PB1）；USB 检测默认关闭 |
| 温湿度 | SHT30（I2C） | **删除**（新硬件无此器件） |
| 红外/洗衣机 | 红外发射相关入口 | **删除**（新硬件无红外） |
| 任务模型 | FreeRTOS 多任务 | 裸机主循环 + 定时器中断（功能等价，资源更省） |
| 文件系统/PSRAM | ESP32 NVS/PSRAM | 不使用；512 KB Flash 直接存放字库与图标 |

## 四、目录结构

```
.
├─ CMakeLists.txt
├─ cmake/arm-none-eabi.cmake
├─ build.ps1
├─ firmware/
│  ├─ Core/            # main、时钟、中断、newlib 桩
│  ├─ BSP/             # OLED SPI、按键、ADC、串口、蜂鸣器、LED
│  ├─ App/OmniX/       # OmniX_UI v1.4 源码 + 菜单数据 + 移植层
│  ├─ App/Services/    # Power（电池）
│  ├─ Drivers/         # STM32F4 HAL + CMSIS（ST 官方）
│  └─ Startup/         # startup_stm32f429xx.s + 链接脚本
└─ docs/               # 引脚与移植说明
```

## 五、注意事项（务必阅读）

1. **PB4 双职责**：OLED 的 DC 接在 PB4（SPI3_MISO）上。本固件把 PB4 当 GPIO 输出，
   因此没有同时使用外置 GD25Q128E。若以后要读 Flash，必须在读之前把 PB4 切回
   `GPIO_AF6_SPI3`，读完再切回 GPIO——两者不能同时工作（硬件文档第 6 章已说明）。
2. **PA8 共用**：OLED RST 与 4G `SRST` 同网络，`OLED_Init()` 拉低 PA8 会同时复位 4G。
   这是板级设计，不是软件 bug。
3. **五向开关阈值**：`PA4/PA5` 的电压分压比未在文档给出，默认按“两轴摇杆、中点 2048、
   死区 550”处理。若方向不对/不灵敏，按上面“按键操作”一节调宏。
4. **电池分压比**：`Power.h` 的 `POWER_VBAT_RATIO` 默认 2.0，必须按实际电阻改成
   `(Rtop+Rbottom)/Rbottom`，否则电量百分比不准。
5. **USB 插入检测默认关闭**：PD4 在硬件说明中是 USB-A VBUS 控制输出（推测），
   不能可靠判断充电插入。关闭后不会误进充电动画；要启用请把 `POWER_USB_DETECT` 设为 1，
   并确认 PD4 确实能作为输入。
6. **HSE 8 MHz**：若晶振不起振，固件自动退回 16 MHz HSI，串口仍能打印，但 UI 会变慢。
   先量 PH0/PH1。
7. **SH1106 vs SSD1306**：默认 SH1106（1.3 寸，列偏移 2）。若是 SSD1306 屏，把
   `board.h` 的 `OMNIX_OLED_SH1106` 改为 0。
8. **4G/WiFi 尚未接入 UI**：本仓库的目标是 UI 系统移植；EC600S/ESP8266 的 AT 驱动
   未包含。需要的话可在 `BSP` 下新增，不影响现有 UI。

## 六、许可与致谢

- UI 框架来自 **OmniX_UI / OLED_UI**（作者 bdth-7777777，Apache-2.0）：
  <https://github.com/bdth-7777777/OLED_UI>
- STM32F4 HAL / CMSIS：STMicroelectronics，BSD-3-Clause。
- 本移植版同样以 **Apache-2.0** 发布，见 [LICENSE](LICENSE)。
