# serial_tool
Python3+PyQt5的串口工具，具有stm32、stm8的下载功能

目录结构
.
│  debug_execute.bat                :用于程序调试的脚本，双击即可运行程序
│  py_to_exe.bat                    :用于最后生成exe文件的脚本
│  Readme.md
│  sscom_main.py                    :main
│  sscom_ui.py                      :通过qtDesigner生成的ui文件，转化后的python文件
│
├─exe
│  │  sscom_main.exe                :最后生成的可执行文件
│  │
│  ├─logo                           :软件所需的logo
│  │      images.qrc
│  │      logo.ico
│  │      logo.jpg
│  │
│  └─mcuflashtool                   :给单片机下载的示例代码
│          start_download.bat
│
├─logo                              :调试时用得logo
│      images.qrc
│      logo.ico
│      logo.jpg
│
└─tools
    │  ui_to_py.bat                 :用于将ui文件转化为py文件
    │
    └─ui
            dayo-sscom.ui           :使用qtDesigner软件画的界面

1、首先需要安装python 32bit版本（使用32bit版打包出来的程序才支持在32/64位系统上运行）
2、打开命令行窗口，执行以下指令安装软件编写过程中所需的pack
    (1)安装PyQt包，用于界面编程
        pip install PyQt5

    (2)安装PyQt5 tools(D:\python365-32bit\Lib\site-packages\pyqt5-tools 此目录下回产生界面设计的软件designer.exe)
        pip install pyqt5-tools

    (3)安装串口包，用于串口通信
        pip install pyserial

    (4)安装打包软件，用于最后生成exe文件
        pip install pyinstaller

