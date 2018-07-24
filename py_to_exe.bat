@echo off

::winpython
::D:\WinPython\python-3.6.5.amd64\Scripts\pyinstaller.exe --path D:\WinPython\python-3.6.5.amd64\Lib\site-packages\PyQt5\Qt\bin -Fw -i G:\ZMB-Self\Code\Python\dayo-sscom\logo\logo.ico G:\ZMB-Self\Code\Python\dayo-sscom\sscom_main.py --distpath .\exe\

::32bit python
D:\python365-32bit\Scripts\pyinstaller.exe --path D:\python365-32bit\Lib\site-packages\PyQt5\Qt\bin -Fw -i .\logo\logo.ico .\sscom_main.py --distpath .\exe\

REM D:\python35\Scripts\pyinstaller.exe --path D:\python35\Lib\site-packages\PyQt5\Qt\bin -Fw C:\Users\Captain\Desktop\Dayo\Dayo_SSCOM.py --distpath .\exe\
pause