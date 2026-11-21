# 预编译固件

本目录由 `cmake --build build` 直接生成，与源提交和 CI 构建一致。

| 文件 | 用途 |
|---|---|
| `OmniX_STM32F429.hex` | ST-Link / STM32CubeProgrammer 烧录（推荐） |
| `OmniX_STM32F429.bin` | 从 `0x08000000` 开始的裸镜像，供量产工具使用 |
| `OmniX_STM32F429.elf` | 带调试符号，供 GDB / Ozone / STM32CubeIDE 调试 |
| `SHA256SUMS.txt` | 三个镜像的 SHA-256 |

## 烧录

```powershell
STM32_Programmer_CLI -c port=SWD -w OmniX_STM32F429.hex -v -rst
```

或：

```powershell
ST-LINK_CLI -c SWD -P OmniX_STM32F429.hex -V -Rst
```

## 构建信息

- 编译器：`arm-none-eabi-gcc 14.2.1`
- 选项：`-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -O2`
- Flash：81,168 B / 512 KB
- RAM：18,424 B / 192 KB（链接脚本预留 2 KB 堆 + 8 KB 栈）

## 校验

```powershell
Get-FileHash OmniX_STM32F429.hex -Algorithm SHA256
```

或对比 `SHA256SUMS.txt`。
