cmake_minimum_required(VERSION 3.20)

# The toolchain must be selected before project().
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/arm-none-eabi.cmake"
    CACHE FILEPATH "Toolchain file")

project(OmniX_STM32F429 C ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)

set(FW_DIR "${CMAKE_CURRENT_SOURCE_DIR}/firmware")

set(MCU_FLAGS
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard)

add_compile_options(
    ${MCU_FLAGS}
    -O2
    -g3
    -Wall
    -Wextra
    -Wno-unused-parameter
    -ffunction-sections
    -fdata-sections
    -fno-common)

set(MCU_FAMILY "F429" CACHE STRING "Target MCU family: F429 or F407")
if(MCU_FAMILY STREQUAL "F407")
    set(MCU_DEFINE STM32F407xx)
    set(STARTUP_FILE "${FW_DIR}/Startup/startup_stm32f407xx.s")
    set(LINKER_SCRIPT "${FW_DIR}/Startup/STM32F407VETx_FLASH.ld")
    set(FW_TARGET "OmniX_STM32F407")
else()
    set(MCU_DEFINE STM32F429xx)
    set(STARTUP_FILE "${FW_DIR}/Startup/startup_stm32f429xx.s")
    set(LINKER_SCRIPT "${FW_DIR}/Startup/STM32F429VETx_FLASH.ld")
    set(FW_TARGET "OmniX_STM32F429")
endif()

set(FW_SOURCES
    # Application
    ${FW_DIR}/Core/Src/main.c
    ${FW_DIR}/Core/Src/stm32f4xx_it.c
    ${FW_DIR}/Core/Src/syscalls.c
    ${FW_DIR}/Core/Src/system_stm32f4xx.c
    ${FW_DIR}/BSP/Src/bsp.c
    ${FW_DIR}/BSP/Src/bsp_oled.c
    ${FW_DIR}/BSP/Src/bsp_keys.c
    ${FW_DIR}/BSP/Src/bsp_power.c
    ${FW_DIR}/BSP/Src/bsp_serial.c
    ${FW_DIR}/BSP/Src/bsp_buzzer.c
    ${FW_DIR}/BSP/Src/bsp_led.c
    ${FW_DIR}/BSP/Src/bsp_log.c
    ${FW_DIR}/App/Services/Power.c
    # OmniX_UI v1.4
    ${FW_DIR}/App/OmniX/OLED_UI.c
    ${FW_DIR}/App/OmniX/OLED_UI_MenuData.c
    ${FW_DIR}/App/OmniX/OLED.c
    ${FW_DIR}/App/OmniX/OLED_Fonts.c
    ${FW_DIR}/App/OmniX/OLED_driver.c
    ${FW_DIR}/App/OmniX/OLED_UI_Driver.c
    # Startup
    ${STARTUP_FILE}
    # STM32F4 HAL (only the modules this firmware uses)
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc_ex.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_gpio.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_cortex.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_pwr.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_pwr_ex.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_spi.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_adc.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_adc_ex.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_tim.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_tim_ex.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_uart.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_dma.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash_ex.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_exti.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_i2c.c
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_i2c_ex.c
)

list(LENGTH FW_SOURCES FW_SOURCES_N)
message(STATUS "FW_DIR=[${FW_DIR}] TARGET=[${FW_TARGET}] N=[${FW_SOURCES_N}]")
add_executable(${FW_TARGET} ${FW_SOURCES})
target_include_directories(${FW_TARGET} PRIVATE
    ${FW_DIR}/Core/Inc
    ${FW_DIR}/BSP/Inc
    ${FW_DIR}/App/OmniX
    ${FW_DIR}/App/Services
    ${FW_DIR}/Drivers/STM32F4xx_HAL_Driver/Inc
    ${FW_DIR}/Drivers/CMSIS/Device/ST/STM32F4xx/Include
    ${FW_DIR}/Drivers/CMSIS/Include
)

target_compile_definitions(${FW_TARGET} PRIVATE
    ${MCU_DEFINE}
    USE_HAL_DRIVER
    HSE_VALUE=8000000U
)

option(DEBUG_UART_ON_USART2
       "Route the console to USART2 PD5/PD6 (CN1) for board bring-up" OFF)
if(DEBUG_UART_ON_USART2)
    target_compile_definitions(${FW_TARGET} PRIVATE DEBUG_UART_ON_USART2=1)
endif()

option(USE_SEMIHOSTING
       "Send printf over ST-Link semihosting (no USB-TTL required)" OFF)
if(USE_SEMIHOSTING)
    target_compile_definitions(${FW_TARGET} PRIVATE USE_SEMIHOSTING=1)
endif()
if(MCU_FAMILY STREQUAL "F407")
    target_compile_definitions(${FW_TARGET} PRIVATE TARGET_STM32F407=1)
endif()

target_link_options(${FW_TARGET} PRIVATE
    ${MCU_FLAGS}
    -T${LINKER_SCRIPT}
    -Wl,--gc-sections
    -Wl,-Map=${CMAKE_BINARY_DIR}/${FW_TARGET}.map
    -Wl,--print-memory-usage
    -specs=nano.specs
    -specs=nosys.specs
    -Wl,-u,_printf_float)

target_link_libraries(${FW_TARGET} PRIVATE m)

set_target_properties(${FW_TARGET} PROPERTIES
    SUFFIX ".elf"
    LINK_DEPENDS "${LINKER_SCRIPT}")

add_custom_command(TARGET ${FW_TARGET} POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex
            $<TARGET_FILE:${FW_TARGET}>
            ${CMAKE_BINARY_DIR}/${FW_TARGET}.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary
            $<TARGET_FILE:${FW_TARGET}>
            ${CMAKE_BINARY_DIR}/${FW_TARGET}.bin
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${FW_TARGET}>
    COMMENT "Generating HEX/BIN"
)
