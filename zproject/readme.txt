

## 目录分配解释
Stm32F103_FreeRTOS_Project          一级目录，基于F103系列建立的工程框架
Stm32F407_FreeRTOS_Project          一级目录，基于F407系列建立的工程框架

# MSP的相关公用文件
Stm32Fxxx_FreeRTOS_Project\Msp_Common_hal\APL
Stm32Fxxx_FreeRTOS_Project\Msp_Common_hal\DRV
Stm32Fxxx_FreeRTOS_Project\Msp_Common_hal\HAL
Stm32Fxxx_FreeRTOS_Project\Msp_Common_hal\MSP
Stm32Fxxx_FreeRTOS_Project\Msp_Common_hal\PKG

# 芯片级别示例工程
Stm32F103_FreeRTOS_Project\Stm32F103C8T6\HAL\Bsp_Common\APL
Stm32F103_FreeRTOS_Project\Stm32F103C8T6\HAL\Bsp_Common\DRV         板级公用文件，通过宏配置 来进行 引脚配置，最好只包含 STM32 库的头文件
Stm32F103_FreeRTOS_Project\Stm32F103C8T6\HAL\Template\Project\mdk
Stm32F103_FreeRTOS_Project\Stm32F103C8T6\HAL\Template\Project\iar
Stm32F103_FreeRTOS_Project\Stm32F103C8T6\STD\Bsp_Common
Stm32F103_FreeRTOS_Project\Stm32F103C8T6\STD\Template\Project\mdk
Stm32F103_FreeRTOS_Project\Stm32F103C8T6\STD\Template\Project\iar

同上
Stm32F407_FreeRTOS_Project\Stm32F407ZGT6\xxxxxxxxxxx

# 板级工程
Stm32F103_FreeRTOS_Project\Stm32F103C8T6\            基于这个目录的拷贝，生成如下示例
Stm32F103_FreeRTOS_Project\EmbedfireEBFC48\          或者如下，对于开发板，引脚链接固定
Stm32F103_FreeRTOS_Project\EmbedfireEBFC48_xxxx\              对于引脚开发板，引脚链接不固定

## 配置
统一读取 BOARD_CONFIG_XX
