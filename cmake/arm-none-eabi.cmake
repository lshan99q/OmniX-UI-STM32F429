# CMake toolchain for the GNU Arm Embedded (arm-none-eabi) compiler.
#
# Override the compiler location with:
#   cmake -DARM_TOOLCHAIN_PATH="C:/path/to/arm-none-eabi" ...
# or put arm-none-eabi-gcc on PATH before configuring.

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

if(ARM_TOOLCHAIN_PATH)
  set(_arm_prefix "${ARM_TOOLCHAIN_PATH}/bin/arm-none-eabi-")
else()
  set(_arm_prefix "arm-none-eabi-")
endif()

if(WIN32)
  set(_arm_ext ".exe")
else()
  set(_arm_ext "")
endif()

set(CMAKE_C_COMPILER   "${_arm_prefix}gcc${_arm_ext}")
set(CMAKE_ASM_COMPILER "${_arm_prefix}gcc${_arm_ext}")
set(CMAKE_CXX_COMPILER "${_arm_prefix}g++${_arm_ext}")
set(CMAKE_AR           "${_arm_prefix}ar${_arm_ext}")
set(CMAKE_OBJCOPY      "${_arm_prefix}objcopy${_arm_ext}")
set(CMAKE_OBJDUMP      "${_arm_prefix}objdump${_arm_ext}")
set(CMAKE_SIZE         "${_arm_prefix}size${_arm_ext}")
set(CMAKE_RANLIB       "${_arm_prefix}ranlib${_arm_ext}")

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
