# 上板调试：ST-Link 烧录 + 无 USB-TTL 读日志

本文记录本板（实测 STM32F407，Chip ID 0x413）的实测步骤。

## 1. 接线

```
ST-Link SWDIO -> PA13 / CN1 SWDIO
ST-Link SWCLK -> PA14 / CN1 SWCLK
ST-Link GND   -> GND
ST-Link NRST  -> NRST（可选）
ST-Link 3.3V/5V -> 不接（板子 Type-C 自供电）
```

Type-C 上电后先量 3.3V 对 GND，应为 3.3V 左右。

## 2. Windows 驱动（克隆版 ST-Link）

若 `st-info --probe` 报 `Found 0 stlink programmers`，设备管理器里 ST-Link 带黄色感叹号：

1. 用 [Zadig](https://zadig.akeo.ie/)（管理员运行）
2. Options → List All Devices
3. 选 `STM32 STLink`（USB ID `0483` / `3748`）
4. 目标驱动选 `WinUSB`，点 `Install Driver`
5. 拔插 ST-Link

装完后 `st-info --probe` 应显示：

```
Found 1 stlink programmers
  chipid: 0x413
  dev-type: STM32F4x5_F4x7
```

## 3. 烧录

```powershell
st-flash --format ihex --reset --mass-erase write prebuilt/OmniX_STM32F407_uart2.hex
```

正常输出：

```
Flash written and verified! jolly good!
```

## 4. 不需要 USB-TTL 的日志

固件把 `printf` 同时写进 4 KB RAM 环形缓冲区（`bsp_log_buf` / `bsp_log_head`）。
用 ST-Link 读出来即可：

```powershell
# 地址以 nm 为准
arm-none-eabi-nm build-f407/OmniX_STM32F407.elf | findstr "bsp_log_buf bsp_log_head"

st-flash read log.bin  0x200017a0 4096
st-flash read head.bin 0x200027a0 4
```

`head` 是写指针；把 `log[head..4095] + log[0..head-1]` 拼起来，按 UTF-8 解码。
本仓库的 `tools/watch_keys.py` 每 1 秒轮询一次，并打印新增的 `[key]` / `[hb]` 行。

## 5. 本板实测结果

```
[selftest] UID       : 001A003B-30345109-32303836
[selftest] MCU flash : 512 KB
[selftest] SYSCLK    : 168000000 Hz (PLL), HCLK 168000000 Hz
[selftest] 5-way     : OUT1/OUT2 raw=3, KEY0..4 mask=0x1F
[ui] OmniX_UI started, battery=0% (0.02 V)
```

五向开关逐键掩码（`raw=0x..`，bit0..4 = KEY0..KEY4，1=按下）：

| 方向 | 原始掩码 | 键 |
|---|---|---|
| 上 | 0x1B | KEY2 |
| 下 | 0x0F | KEY4 |
| 左 | 0x1E | KEY0 |
| 右 | 0x17 | KEY3 |
| 中间 | 0x1D | KEY1 |

固件已按此映射到 Up/Down/Back/Enter，见 `firmware/BSP/Src/bsp_keys.c`。

## 6. 已知现象

- 电池未接时 `bat=0mV`，正常。
- PD15 LED、4G、ESP8266、OLED 未焊时不影响启动和 SWD 日志。
- 蜂鸣器 500 ms 提示音已实测可响。
- 芯片是 F407，不是 F429；F429 构建会卡在 Over-drive。
