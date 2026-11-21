# 预编译固件

本目录由 `cmake --build` 直接生成。

| 文件 | 目标 | 说明 |
|---|---|---|
| `OmniX_STM32F407_uart2.hex` | **本板 F407** | 推荐烧录用，日志走 USART2/CN1 |
| `OmniX_STM32F407_uart2.bin` | 本板 F407 | 从 `0x08000000` 开始的裸镜像 |
| `OmniX_STM32F429.hex` | 真正的 F429 | 180 MHz + Over-drive |
| `OmniX_STM32F429.bin` | 真正的 F429 | 裸镜像 |
| `OmniX_STM32F429.elf` | 真正的 F429 | 带调试符号 |
| `SHA256SUMS.txt` | — | 全部镜像的 SHA-256 |

> 本板实测 **Chip ID 0x413 = STM32F407/F405**，请优先使用 `F407_uart2` 文件。
> F429 固件在 F407 上会卡在 Over-drive 初始化。

## 烧录

```powershell
st-flash --format ihex --reset --mass-erase write OmniX_STM32F407_uart2.hex
```

或：

```powershell
STM32_Programmer_CLI -c port=SWD -w OmniX_STM32F407_uart2.hex -v -rst
```

## 构建信息

- 编译器：`arm-none-eabi-gcc 14.2.1`
- F407：168 MHz，Flash 82,248 B / 512 KB，RAM 22,480 B / 128 KB
- F429：180 MHz，Flash 81,168 B / 512 KB，RAM 18,376 B / 192 KB
- 链接脚本预留 2 KB 堆 + 8 KB 栈；F407 额外有 4 KB RAM 日志缓冲

## 校验

对比 `SHA256SUMS.txt`，或：

```powershell
Get-FileHash OmniX_STM32F407_uart2.hex -Algorithm SHA256
```
