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
set stvp_path=..\flashtool\stm8_flashtool\STVP\STVP_CmdLine.exe

::set app_path=.\bin\APP.hex

::�Զ���ȡiap��app��bin�ļ�·��;����汾��
setlocal enabledelayedexpansion
set FILES=
for %%i in (..\firmware\V600\*.hex) do (
    set FILES=%%i

    set path_temp="!FILES:~-13,3!"
    if !path_temp!=="APP" (
        ::APP·��
        set app_path=!FILES!
        set software_ver=!FILES:~-9,5!
    )
)

::################################  ��ʾ��Ϣ  ##################################
echo.
echo ***********************************��ʼ����***********************************
echo.
echo ����汾��%software_ver%
REM %stvp_path% -BoardName=ST-LINK -Port=USB -ProgMode=SWIM -Device=STM8L15xC8 -verbose -no_loop -no_log -progress -warn_protect -FileProg=%app_path%
%stvp_path% -BoardName=ST-LINK -Port=USB -ProgMode=SWIM -Device=STM8L15xC8 -verbose -no_loop -no_log -warn_protect -FileProg=%app_path%
echo.

echo.
echo *************************���ؽ����������Ƿ���ִ���*************************

echo.
pause