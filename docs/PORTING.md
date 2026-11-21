# 移植说明

## 1. 范围

源工程是 `Omni_UI.v1.4.zip` 根目录的 `oled_ui` 工程（OmniX_UI v1.4）：

- `Hardware/OLED_UI.c`、`OLED_UI.h`：UI 框架（菜单、磁贴、列表、窗口、动画、FPS）
- `Hardware/OLED.c`、`OLED_Fonts.c`：绘图与字库（8/12/16/20 px，UTF-8 中文）
- `Hardware/OLED_UI_MenuData.c`：所有菜单页面
- `Hardware/Power.c`、`SHT30.c`：系统服务
- `User/main.c`：ESP-IDF 入口

压缩包里的 `Geiger-Counter-V3-main` 是另一个独立的 ESP32-C6 盖革计数器工程（PixelUI +
高压管），其硬件在本板上不存在，因此不在本次移植范围内。

## 2. 保留 / 删除

保留：

- 全部 UI 框架能力：磁贴主菜单、列表菜单、单选、窗口、进度条、淡入淡出、回弹动画、
  超长文本滚动、超长列表、小区域菜单、FPS、暗色模式、亮度调节、充电动画
- 字体 demo：8/12/16/20 px，中英文混排
- 设置页、关于页、More demo 页
- 电量页（改为单电池 ADC）

删除（新板无对应硬件）：

| 功能 | 原实现 | 处理 |
|---|---|---|
| SHT30 温湿度 | I2C1，GPIO18/19，后台任务 | 删除页面、菜单入口、驱动、任务 |
| 红外万能遥控 | 只有入口，无实现 | 删除入口 |
| 洗衣机劫持 | 红外码回调桩 + 页面 | 删除页面、入口、回调 |
| USB 电压 ADC | GPIO13 / ADC2 | 删除读数与显示行 |
| FreeRTOS 任务 | SHT30/Power 后台任务 | 改为主循环轮询（500 ms） |
| ESP-IDF `esp_timer` | 20 ms 回调 | TIM6 20 ms 中断 + 主循环处理 |

## 3. 平台替换点

| 原接口 | STM32 实现 | 文件 |
|---|---|---|
| `OLED_WriteCommand/Data`（I2C） | SPI3 阻塞发送，CS/DC 手动控制 | `App/OmniX/OLED_driver.c` |
| `OLED_GPIO_Init` | `BSP_OLED_Init`（SPI3 + GPIO + 复位） | `BSP/Src/bsp_oled.c` |
| `OLED_Init` | SH1106 初始化序列 + 清屏 | `App/OmniX/OLED_driver.c` |
| `OLED_Brightness` | `0x81` 对比度命令 | 同上 |
| `Key_Get*Status` | 去抖后的 5 键 + 五向开关 | `BSP/Src/bsp_keys.c` |
| `Timer_Init` | TIM6 20 ms 更新中断 | `App/OmniX/OLED_UI_Driver.c` |
| `Delay_us/ms/s` | DWT / `HAL_Delay` | 同上 |
| `Power_*` | ADC1_IN9 + 可选 PD4 | `App/Services/Power.c` |
| `SHT30_*` | 删除 | — |
| `app_main` + FreeRTOS | `main()` 裸机主循环 | `Core/Src/main.c` |

## 4. 时序

- `OLED_UI_InterruptHandler()` 必须每 20 ms 调用一次。TIM6 中断只置位
  `ui_tick_pending`，主循环用 `OLED_UI_TakeTick()` 取走并执行，避免在 ISR 里修改
  菜单状态与渲染共享的全局变量。
- 主循环每 10 ms 调一次 `BSP_Keys_Scan()` 做 20 ms 去抖；`OLED_UI_KeyAndEncoderRecord()`
  内部按 50 Hz 采样计算长按（`PRESS_TIME * 50`）。
- 全屏刷新 8 页 × 128 字节，SPI 5.625 MHz 约 1.5 ms。

## 5. 内存

- `.data/.bss`：UI 全局状态、1 KB 显存、菜单表、栈 4 KB、堆 1 KB。
- 字库和图标在 Flash（只读），512 KB 足够；构建结束会打印 `size`。
- 链接脚本预留 192 KB SRAM；CCM 64 KB 可在需要时放栈或大缓冲（DMA 不可达）。

## 6. 新增硬件驱动时的约定

1. 引脚只写在 `Core/Inc/board.h`，不要散落在驱动里。
2. 外设初始化放在 `BSP_Init()`，驱动只做协议。
3. 若要用外置 Flash（PB4 作 MISO）：
   - 读之前把 PB4 切成 `GPIO_AF6_SPI3`；
   - 读完切回 GPIO 输出并恢复 DC 电平；
   - 读 Flash 期间不能刷屏，必须加互斥（本工程是单主循环，天然串行）。
4. 4G/WiFi 的 AT 解析建议放独立 `BSP/Src/bsp_modem.c` / `bsp_wifi.c`，用 USART3/USART2
   中断 + 环形缓冲，避免阻塞 20 ms UI 节拍。
