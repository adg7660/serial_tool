::�ر�����Ļ���
@echo off

::���ô���λ�� 0x00240309 ǰ2�ֽ��Ǿ����ϱ߿򣬺����ֽ��Ǿ�����߿��´βŻ���Ч
set rr="HKCU\Console\%%SystemRoot%%_system32_cmd.exe"
reg delete %rr% /f>nul
reg add %rr% /v "WindowPosition" /t REG_DWORD /d 0x00000000 /f>nul

::���ô��ڱ���
title ��������-������ع���

::���ô��ڴ�С
mode con cols=80 lines=40

::���ô�����ɫΪ��ɫ
::color 2e
::color /?  ��ʾ��ɫ���ð���

::����
::echo.
::echo/

::��ͣ
::pause
::##############################  ���߰汾��Ϣ   ###############################
set hardware_ver=V680

::################################  ��������   #################################
::coflash��ִ���ļ���·��
set flashtool_path=..\flashtool\stm32_flashtool\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe

::����ģʽ
set download_mode=SWD

::bootloader·��
::set iap_path=.\bin\IAP.bin

::APP·��
::set app_path=.\bin\APP.bin

::bootloader��flash�е���ʼ��ַ
set iap_addr=0x8000000

::application��flash�е���ʼ��ַ
set app_addr=0x8005000

::�Զ���ȡiap��app��bin�ļ�·��;����汾��
setlocal enabledelayedexpansion
set FILES=
for %%i in (..\firmware\V680\*.bin) do (
    set FILES=%%i
    
    set path_temp="!FILES:~-13,3!"
    if !path_temp!=="IAP" (
        ::bootloader·��
        set iap_path=!FILES!
    )
    
    if !path_temp!=="APP" (
        ::APP·��
        set app_path=!FILES!
        set software_ver=!FILES:~-9,5!
    )
)


::################################  ��ʾ��Ϣ  ##################################
echo.
echo ***************************************************************************
        ::%flashtool_path% -V
echo.
echo �汾��Ϣ:
echo    Ӳ���汾:%hardware_ver%         ����汾:%software_ver%
echo.
echo ��������:
echo    ����ģʽ:%download_mode%
echo    ��������:%iap_path%   ��ַ:%iap_addr%
echo    Ӧ�ó���:%app_path%   ��ַ:%app_addr%
echo.
echo ***************************************************************************
echo.


::################################  ���س���  ##################################
echo.
echo ����������������. . .
::%flashtool_path%  -c port=%download_mode% reset=HWrst freq=4000 -e all
%flashtool_path% -vb 1 -c port=%download_mode% reset=HWrst freq=4000 -d %iap_path% %iap_addr%

echo.
echo Ӧ�ó�����������. . .
%flashtool_path% -vb 1 -c port=%download_mode% reset=HWrst freq=4000 -d %app_path% %app_addr% -v -hardRst

echo.

::��ʱ1s
::@ping 127.0.0.1 -n 1 >nul

::��ͣ
pause
