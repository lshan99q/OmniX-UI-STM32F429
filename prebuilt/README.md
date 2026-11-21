# 棰勭紪璇戝浐浠?
鏈洰褰曠敱 `cmake --build build` 鐩存帴鐢熸垚锛屾簮鎻愪氦涓?CI 鏋勫缓涓€鑷淬€?
| 鏂囦欢 | 鐢ㄩ€?|
|---|---|
| `OmniX_STM32F429.hex` | ST-Link / STM32CubeProgrammer 鐑у綍锛堟帹鑽愶級 |
| `OmniX_STM32F429.bin` | 浠?`0x08000000` 寮€濮嬬殑瑁搁暅鍍忥紝渚涢噺浜у伐鍏蜂娇鐢?|
| `OmniX_STM32F429.elf` | 甯﹁皟璇曠鍙凤紝渚?GDB / Ozone / STM32CubeIDE 璋冭瘯 |
| `SHA256SUMS.txt` | 涓変釜闀滃儚鐨?SHA-256 |

## 鐑у綍

```powershell
STM32_Programmer_CLI -c port=SWD -w OmniX_STM32F429.hex -v -rst
```

鎴栵細

```powershell
ST-LINK_CLI -c SWD -P OmniX_STM32F429.hex -V -Rst
```

## 鏋勫缓淇℃伅

- 缂栬瘧鍣細`arm-none-eabi-gcc 14.2.1`
- 閫夐」锛歚-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -O2`
- Flash锛?1,168 B / 512 KB
- RAM锛?3,304 B / 192 KB锛堥摼鎺ヨ剼鏈鐣?2 KB 鍫?+ 8 KB 鏍堬級

## 鏍￠獙

```powershell
Get-FileHash OmniX_STM32F429.hex -Algorithm SHA256
```

鎴栧姣?`SHA256SUMS.txt`銆?
