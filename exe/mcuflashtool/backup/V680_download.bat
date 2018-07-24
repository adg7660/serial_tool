::关闭命令的回显
@echo off

::设置窗口位置 0x00240309 前2字节是距离上边框，后两字节是距离左边框，下次才会生效
set rr="HKCU\Console\%%SystemRoot%%_system32_cmd.exe"
reg delete %rr% /f>nul
reg add %rr% /v "WindowPosition" /t REG_DWORD /d 0x00000000 /f>nul

::设置窗口标题
title 大友智造-软件下载工具

::设置窗口大小
mode con cols=80 lines=40

::设置窗口颜色为绿色
::color 2e
::color /?  显示颜色设置帮助

::换行
::echo.
::echo/

::暂停
::pause
::##############################  工具版本信息   ###############################
set hardware_ver=V680

::################################  参数配置   #################################
::coflash可执行文件的路径
set flashtool_path=..\flashtool\stm32_flashtool\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe

::下载模式
set download_mode=SWD

::bootloader路径
::set iap_path=.\bin\IAP.bin

::APP路径
::set app_path=.\bin\APP.bin

::bootloader在flash中的起始地址
set iap_addr=0x8000000

::application在flash中的起始地址
set app_addr=0x8005000

::自动获取iap、app的bin文件路径;软件版本号
setlocal enabledelayedexpansion
set FILES=
for %%i in (..\firmware\V680\*.bin) do (
    set FILES=%%i
    
    set path_temp="!FILES:~-13,3!"
    if !path_temp!=="IAP" (
        ::bootloader路径
        set iap_path=!FILES!
    )
    
    if !path_temp!=="APP" (
        ::APP路径
        set app_path=!FILES!
        set software_ver=!FILES:~-9,5!
    )
)


::################################  显示信息  ##################################
echo.
echo ***************************************************************************
        ::%flashtool_path% -V
echo.
echo 版本信息:
echo    硬件版本:%hardware_ver%         软件版本:%software_ver%
echo.
echo 下载配置:
echo    下载模式:%download_mode%
echo    引导程序:%iap_path%   地址:%iap_addr%
echo    应用程序:%app_path%   地址:%app_addr%
echo.
echo ***************************************************************************
echo.


::################################  下载程序  ##################################
echo.
echo 引导程序正在下载. . .
::%flashtool_path%  -c port=%download_mode% reset=HWrst freq=4000 -e all
%flashtool_path% -vb 1 -c port=%download_mode% reset=HWrst freq=4000 -d %iap_path% %iap_addr%

echo.
echo 应用程序正在下载. . .
%flashtool_path% -vb 1 -c port=%download_mode% reset=HWrst freq=4000 -d %app_path% %app_addr% -v -hardRst

echo.

::延时1s
::@ping 127.0.0.1 -n 1 >nul

::暂停
pause
