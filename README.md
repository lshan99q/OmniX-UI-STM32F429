# OmniX_UI 路 STM32F429VET6 绉绘鐗?
鎶婂師鏈窇鍦?ESP32 涓婄殑 **OmniX_UI v1.4**锛坄Omni_UI.v1.4.zip` 鏍瑰伐绋?`oled_ui`锛夊畬鏁寸Щ妞嶅埌
**STM32F429VET6 + 4G 鐗╄仈缃戝紑鍙戞澘**锛屾樉绀恒€佹寜閿€佺數婧愩€佽彍鍗曚笌鍔ㄧ敾鍏ㄩ儴鎸夋柊纭欢閲嶅啓銆?
- UI 妗嗘灦锛歄mniX_UI v1.4锛堝绾ц彍鍗?/ 纾佽创 / 鍒楄〃 / 绐楀彛 / 娣″叆娣″嚭 / 鍥炲脊鍔ㄧ敾 / 鍥涚瀛楀彿 / 涓嫳鏂囨贩鎺?/ FPS / 鏆楄壊妯″紡 / 浜害 / 鍏呯數鍔ㄧ敾锛?- MCU锛歋TM32F429VET6锛孋ortex-M4F锛?80 MHz锛?12 KB Flash / 256 KB SRAM
- 鏄剧ず锛歋H1106锛堝吋瀹?SSD1306锛?28脳64锛屽洓绾?SPI锛孲PI3
- 杈撳叆锛? 涓嫭绔嬫寜閿?+ 浜斿悜寮€鍏筹紙PA4/PA5 妯℃嫙锛?- 鐢垫簮锛歅B1锛圓DC1_IN9锛夌數姹犲垎鍘嬫娴?- 宸ュ叿閾撅細GNU Arm Embedded锛坄arm-none-eabi-gcc`锛? CMake + Ninja锛屾棤浠讳綍 IDE 渚濊禆

> 鍘熷伐绋嬩腑渚濊禆鏂版澘娌℃湁鐨勭‖浠剁殑鍏ュ彛宸叉寜浣犵殑瑕佹眰鍒犻櫎锛?> **SHT30 娓╂箍搴﹂〉銆佺孩澶栦竾鑳介仴鎺с€佹礂琛ｆ満鍔寔**锛堜互鍙?SHT30 椹卞姩銆乁SB 鐢靛帇 ADC 璇绘暟锛夈€?> 鐢甸噺椤典繚鐣欙紝鏀逛负鍙鐢垫睜 ADC銆?>
> 璇存槑锛氬帇缂╁寘鍐呯殑 `Geiger-Counter-V3-main` 鏄彟涓€涓嫭绔嬬殑 ESP32-C6 鐩栭潻璁℃暟鍣ㄥ伐绋?> 锛圥ixelUI + 楂樺帇绠★級锛屾湰鏉挎病鏈夌洊闈╃/楂樺帇鐢佃矾锛屽洜姝や笉鍦ㄦ湰娆♀€淥mniX_UI 绯荤粺 + UI鈥濈Щ妞嶈寖鍥村唴銆?
## 涓€銆佺‖浠舵槧灏?
| 鍔熻兘 | 寮曡剼 | 璇存槑 |
|---|---|---|
| OLED SCK | PB3 | SPI3_SCK锛孉F6 |
| OLED MOSI | PB5 | SPI3_MOSI锛孉F6 |
| OLED DC | PB4 | GPIO 杈撳嚭锛堜笌 SPI3_MISO 澶嶇敤锛岃鈥滄敞鎰忎簨椤光€濓級 |
| OLED CS | PD10 | GPIO 杈撳嚭锛屼綆鏈夋晥 |
| OLED RST | PA8 | 涓?4G `SRST` 鍏辩敤 |
| 鎸夐敭 KEY0鈥EY4 | PB2 / PE9 / PE10 / PE15 / PB10 | 鍐呴儴涓婃媺锛屼綆鏈夋晥 |
| 浜斿悜寮€鍏?OUT1/OUT2 | PA4 / PA5 | ADC1_IN4 / IN5 |
| 鐢垫睜妫€娴?| PB1 | ADC1_IN9锛岄粯璁?1:1 鍒嗗帇 |
| 鐘舵€佺伅 | PD15 | 浣庣數骞崇偣浜紝500 ms 蹇冭烦 |
| 铚傞福鍣?| PB9 | TIM4_CH4锛? kHz PWM锛屽紑鏈虹煭楦?|
| 璋冭瘯涓插彛 | PA9 / PA10 | USART1锛?15200 8N1 |
| 4G EC600S | USART3 PD8/PD9锛孭WRKEY PC0锛孯ESET PA8 | 鏈浐浠跺彧鍒濆鍖栵紝涓嶉┍鍔?|
| WiFi ESP8266 | USART2 PD5/PD6锛孍N PD3锛孯ST PA15 | 鏈浐浠朵繚鎸?EN/RST 楂橈紝涓嶉┍鍔?|
| 澶栫疆 Flash | CS PA0锛孲PI3 | 鏈浐浠朵繚鎸佺墖閫夐珮锛汸B4 琚?OLED DC 鍗犵敤 |

### 鎸夐敭鎿嶄綔

| 鎿嶄綔 | 鎸夐敭 |
|---|---|
| 涓?/ 涓?| KEY1(PE9) / KEY2(PE10)锛屾垨浜斿悜寮€鍏充笂/涓?|
| 纭 | KEY3(PE15) 鎴?KEY0(PB2)锛屾垨浜斿悜寮€鍏冲彸/涓?|
| 杩斿洖 | KEY4(PB10)锛屾垨浜斿悜寮€鍏冲乏 |

浜斿悜寮€鍏虫槸 **妯℃嫙閲?*锛歚bsp_keys.c` 閲屾寜鈥滃亸绂讳腑鍊?2048 瓒呰繃姝诲尯 550鈥濆垽鏂瑰悜銆?濡傛灉浣犵殑寮€鍏虫柟鍚戠浉鍙嶏紝鏀?`board.h` 閲岀殑 `BSP_JOY_INVERT_X/Y`锛涙鍖烘敼 `BSP_JOY_DEADZONE`銆?濡傛灉鏉垮瓙涓婄殑浜斿悜寮€鍏冲叾瀹炴槸鏁板瓧閲忥紝鎶?`BSP_JOY_USE_ADC` 璁句负 0锛岀敤 KEY1鈥EY4 鎿嶄綔銆?
## 浜屻€佺紪璇?
### 1. 瀹夎宸ュ叿閾?
- GNU Arm Embedded Toolchain 13.x 鎴栨洿鏂帮紙[ARM 瀹樻柟](https://developer.arm.com/downloads/-/gnu-rm)锛屾垨 xPack 鐗堟湰锛?- CMake 鈮?3.20銆丯inja

鎶?`arm-none-eabi-gcc` 鎵€鍦ㄧ洰褰曞姞鍏?PATH锛屾垨鑰呴厤缃椂浼?`-DARM_TOOLCHAIN_PATH=...`銆?
### 2. 鏋勫缓

```powershell
cmake -S . -B build -G Ninja -DARM_TOOLCHAIN_PATH="C:/Tools/arm-none-eabi"
cmake --build build
```

Windows 涓嬩篃鍙互鐩存帴杩愯锛?
```powershell
./build.ps1 -ToolchainPath "C:/Tools/arm-none-eabi"
```

浜х墿锛?
```
build/OmniX_STM32F429.elf
build/OmniX_STM32F429.hex
build/OmniX_STM32F429.bin
build/OmniX_STM32F429.map
```

鏈粨搴撳悓鏃舵彁渚涘凡楠岃瘉鐨勯缂栬瘧鍥轰欢锛堣 `prebuilt/`锛夛細

```
prebuilt/OmniX_STM32F429.hex
prebuilt/OmniX_STM32F429.bin
prebuilt/OmniX_STM32F429.elf
prebuilt/SHA256SUMS.txt
```

缂栬瘧缁撴灉锛?*Flash 81,168 B / 512 KB锛?5.5%锛夛紝RAM 13,304 B / 192 KB锛?.8%锛?*銆?宸ュ叿閾撅細`arm-none-eabi-gcc 14.2.1`锛宍-mcpu=cortex-m4 -mfloat-abi=hard -O2`銆?
### 3. 鐑у綍

ST-Link + SWD锛圥A13/PA14锛夛細

```powershell
STM32_Programmer_CLI -c port=SWD -w build/OmniX_STM32F429.hex -v -rst
```

鎴?ST-LINK_CLI锛?
```powershell
ST-LINK_CLI -c SWD -P build/OmniX_STM32F429.hex -V -Rst
```

### 4. 鐪嬫棩蹇?
USART1锛圥A9=TX锛孭A10=RX锛夋帴 USB-TTL锛?15200 8N1锛?.3 V 鐢靛钩銆?涓婄數浼氭墦鍗颁富棰戙€佹瀯寤烘椂闂淬€佺數姹犵數鍘嬶紝鐒跺悗杩涘叆 UI銆?
## 涓夈€佷笌鍘?ESP32 宸ョ▼鐨勫尯鍒?
| 椤圭洰 | ESP32 鍘熺増 | STM32F429 绉绘鐗?|
|---|---|---|
| OLED 鎺ュ彛 | I2C SSD1306锛圙PIO21/22锛?| SPI3 SH1106锛圥B3/PB5/PD10/DC=PB4/RST=PA8锛?|
| 鏄剧ず椹卞姩 | `OLED_driver.c` I2C | 閲嶅啓涓?SPI + SH1106 鍒濆鍖?鍒楀亸绉?|
| 鎸夐敭 | 4 涓?GPIO锛?5/33/32/15锛?| 5 閿?+ 浜斿悜寮€鍏虫ā鎷熼噺锛屽甫鍘绘姈 |
| 鏃堕棿鍩哄噯 | `esp_timer` 20 ms 鍥炶皟 | TIM6 20 ms 涓柇缃爣蹇楋紝涓诲惊鐜墽琛?`OLED_UI_InterruptHandler()` |
| 寤舵椂 | FreeRTOS `vTaskDelay` | DWT 寰寤舵椂 + `HAL_Delay` |
| 鐢垫簮 | 鐢垫睜 ADC + USB 鐢靛帇 ADC | 浠呯數姹?ADC锛圥B1锛夛紱USB 妫€娴嬮粯璁ゅ叧闂?|
| 娓╂箍搴?| SHT30锛圛2C锛?| **鍒犻櫎**锛堟柊纭欢鏃犳鍣ㄤ欢锛?|
| 绾㈠/娲楄。鏈?| 绾㈠鍙戝皠鐩稿叧鍏ュ彛 | **鍒犻櫎**锛堟柊纭欢鏃犵孩澶栵級 |
| 浠诲姟妯″瀷 | FreeRTOS 澶氫换鍔?| 瑁告満涓诲惊鐜?+ 瀹氭椂鍣ㄤ腑鏂紙鍔熻兘绛変环锛岃祫婧愭洿鐪侊級 |
| 鏂囦欢绯荤粺/PSRAM | ESP32 NVS/PSRAM | 涓嶄娇鐢紱512 KB Flash 鐩存帴瀛樻斁瀛楀簱涓庡浘鏍?|

## 鍥涖€佺洰褰曠粨鏋?
```
.
鈹溾攢 CMakeLists.txt
鈹溾攢 cmake/arm-none-eabi.cmake
鈹溾攢 build.ps1
鈹溾攢 firmware/
鈹? 鈹溾攢 Core/            # main銆佹椂閽熴€佷腑鏂€乶ewlib 妗?鈹? 鈹溾攢 BSP/             # OLED SPI銆佹寜閿€丄DC銆佷覆鍙ｃ€佽渹楦ｅ櫒銆丩ED
鈹? 鈹溾攢 App/OmniX/       # OmniX_UI v1.4 婧愮爜 + 鑿滃崟鏁版嵁 + 绉绘灞?鈹? 鈹溾攢 App/Services/    # Power锛堢數姹狅級
鈹? 鈹溾攢 Drivers/         # STM32F4 HAL + CMSIS锛圫T 瀹樻柟锛?鈹? 鈹斺攢 Startup/         # startup_stm32f429xx.s + 閾炬帴鑴氭湰
鈹斺攢 docs/               # 寮曡剼涓庣Щ妞嶈鏄?```

## 浜斻€佹敞鎰忎簨椤癸紙鍔″繀闃呰锛?
1. **PB4 鍙岃亴璐?*锛歄LED 鐨?DC 鎺ュ湪 PB4锛圫PI3_MISO锛変笂銆傛湰鍥轰欢鎶?PB4 褰?GPIO 杈撳嚭锛?   鍥犳娌℃湁鍚屾椂浣跨敤澶栫疆 GD25Q128E銆傝嫢浠ュ悗瑕佽 Flash锛屽繀椤诲湪璇讳箣鍓嶆妸 PB4 鍒囧洖
   `GPIO_AF6_SPI3`锛岃瀹屽啀鍒囧洖 GPIO鈥斺€斾袱鑰呬笉鑳藉悓鏃跺伐浣滐紙纭欢鏂囨。绗?6 绔犲凡璇存槑锛夈€?2. **PA8 鍏辩敤**锛歄LED RST 涓?4G `SRST` 鍚岀綉缁滐紝`OLED_Init()` 鎷変綆 PA8 浼氬悓鏃跺浣?4G銆?   杩欐槸鏉跨骇璁捐锛屼笉鏄蒋浠?bug銆?3. **浜斿悜寮€鍏抽槇鍊?*锛歚PA4/PA5` 鐨勭數鍘嬪垎鍘嬫瘮鏈湪鏂囨。缁欏嚭锛岄粯璁ゆ寜鈥滀袱杞存憞鏉嗐€佷腑鐐?2048銆?   姝诲尯 550鈥濆鐞嗐€傝嫢鏂瑰悜涓嶅/涓嶇伒鏁忥紝鎸変笂闈⑩€滄寜閿搷浣溾€濅竴鑺傝皟瀹忋€?4. **鐢垫睜鍒嗗帇姣?*锛歚Power.h` 鐨?`POWER_VBAT_RATIO` 榛樿 2.0锛屽繀椤绘寜瀹為檯鐢甸樆鏀规垚
   `(Rtop+Rbottom)/Rbottom`锛屽惁鍒欑數閲忕櫨鍒嗘瘮涓嶅噯銆?5. **USB 鎻掑叆妫€娴嬮粯璁ゅ叧闂?*锛歅D4 鍦ㄧ‖浠惰鏄庝腑鏄?USB-A VBUS 鎺у埗杈撳嚭锛堟帹娴嬶級锛?   涓嶈兘鍙潬鍒ゆ柇鍏呯數鎻掑叆銆傚叧闂悗涓嶄細璇繘鍏呯數鍔ㄧ敾锛涜鍚敤璇锋妸 `POWER_USB_DETECT` 璁句负 1锛?   骞剁‘璁?PD4 纭疄鑳戒綔涓鸿緭鍏ャ€?6. **HSE 8 MHz**锛氳嫢鏅舵尟涓嶈捣鎸紝鍥轰欢鑷姩閫€鍥?16 MHz HSI锛屼覆鍙ｄ粛鑳芥墦鍗帮紝浣?UI 浼氬彉鎱€?   鍏堥噺 PH0/PH1銆?7. **SH1106 vs SSD1306**锛氶粯璁?SH1106锛?.3 瀵革紝鍒楀亸绉?2锛夈€傝嫢鏄?SSD1306 灞忥紝鎶?   `board.h` 鐨?`OMNIX_OLED_SH1106` 鏀逛负 0銆?8. **4G/WiFi 灏氭湭鎺ュ叆 UI**锛氭湰浠撳簱鐨勭洰鏍囨槸 UI 绯荤粺绉绘锛汦C600S/ESP8266 鐨?AT 椹卞姩
   鏈寘鍚€傞渶瑕佺殑璇濆彲鍦?`BSP` 涓嬫柊澧烇紝涓嶅奖鍝嶇幇鏈?UI銆?
## 鍏€佽鍙笌鑷磋阿

- UI 妗嗘灦鏉ヨ嚜 **OmniX_UI / OLED_UI**锛堜綔鑰?bdth-7777777锛孉pache-2.0锛夛細
  <https://github.com/bdth-7777777/OLED_UI>
- STM32F4 HAL / CMSIS锛歋TMicroelectronics锛孊SD-3-Clause銆?- 鏈Щ妞嶇増鍚屾牱浠?**Apache-2.0** 鍙戝竷锛岃 [LICENSE](LICENSE)銆?
