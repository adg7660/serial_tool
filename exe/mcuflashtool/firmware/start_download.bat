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

::��ʱ3��
::@ping 127.0.0.1 -n 3 >nul 

@ping 127.0.0.1 -n 2 >nul   
echo ��ֻ��ʾ������ 1

@ping 127.0.0.1 -n 2 >nul   
echo ��ֻ��ʾ������ 2

@ping 127.0.0.1 -n 2 >nul   
echo ��ֻ��ʾ������ 3

@ping 127.0.0.1 -n 2 >nul   
echo ��ֻ��ʾ������ 4

@ping 127.0.0.1 -n 2 >nul   
echo ��ֻ��ʾ������ 5

pause