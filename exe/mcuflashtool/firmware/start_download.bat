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

::延时3秒
::@ping 127.0.0.1 -n 3 >nul 

@ping 127.0.0.1 -n 2 >nul   
echo 这只是示例代码 1

@ping 127.0.0.1 -n 2 >nul   
echo 这只是示例代码 2

@ping 127.0.0.1 -n 2 >nul   
echo 这只是示例代码 3

@ping 127.0.0.1 -n 2 >nul   
echo 这只是示例代码 4

@ping 127.0.0.1 -n 2 >nul   
echo 这只是示例代码 5

pause