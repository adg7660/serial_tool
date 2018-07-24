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
set stvp_path=..\flashtool\stm8_flashtool\STVP\STVP_CmdLine.exe

::set app_path=.\bin\APP.hex

::自动获取iap、app的bin文件路径;软件版本号
setlocal enabledelayedexpansion
set FILES=
for %%i in (..\firmware\V600\*.hex) do (
    set FILES=%%i

    set path_temp="!FILES:~-13,3!"
    if !path_temp!=="APP" (
        ::APP路径
        set app_path=!FILES!
        set software_ver=!FILES:~-9,5!
    )
)

::################################  显示信息  ##################################
echo.
echo ***********************************开始下载***********************************
echo.
echo 软件版本：%software_ver%
REM %stvp_path% -BoardName=ST-LINK -Port=USB -ProgMode=SWIM -Device=STM8L15xC8 -verbose -no_loop -no_log -progress -warn_protect -FileProg=%app_path%
%stvp_path% -BoardName=ST-LINK -Port=USB -ProgMode=SWIM -Device=STM8L15xC8 -verbose -no_loop -no_log -warn_protect -FileProg=%app_path%
echo.

echo.
echo *************************下载结束，请检查是否出现错误*************************

echo.
pause