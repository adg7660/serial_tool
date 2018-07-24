#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import signal
import serial
from serial.tools.list_ports import comports
import time
import os
import threading
import configparser
import logging

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QInputDialog, QFileDialog
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtCore import QTimer
from sscom_ui import Ui_MainWindow

#QMessageBox
# QMessageBox.information 信息框
# QMessageBox.question    问答框
# QMessageBox.warning     警告
# QMessageBox.critical    危险
# QMessageBox.about       关于

#logging
# FATAL       []致命错误
# CRITICAL    [50]特别糟糕的事情，如内存耗尽、磁盘空间为空，一般很少使用
# ERROR       [40]发生错误时，如IO操作失败或者连接问题
# WARNING     [30]发生很重要的事件，但是并不是错误时，如用户登录密码错误
# INFO        [20]处理请求或者状态变化等日常事务
# DEBUG       [10]调试过程中使用DEBUG等级，如算法中每个循环的中间状态
# NOTSET      [0]

sscom_logger        = logging.getLogger(__name__)
software_name       = 'VM系列工厂生产工具'
software_version    = 'V1.00'
write_id_success_flag = 'WIDS'

software_help_str = ('''
                        <!DOCTYPE html>
                            <html>
                                <head>
                                    <meta charset="utf-8">
                                    <title>帮助</title>
                                </head>
                                <body>
                                    <p>1、可查看生产log打印</p>
                                    <p>2、可写入设备ID</p>
                                    <p>2、可下载STM8/STM32系列的单片机程序</p>
                                    <p>3、可保存常用的AT命令，仅限8条</p>
                                    <p>4、可更改写ID命令，一般情况切勿更改</p>
                                    <p>5、可更改该软件的日志级别，仅用于软件调试</p>
                                </body>
                            </html>
                    ''')

software_about_str = ('''
                            <!DOCTYPE html>
                            <html>
                                <head>
                                    <meta charset="utf-8">
                                    <title>介绍</title>
                                </head>
                                <body>
                                    <p>此软件仅用于<b>北京大友智造科技有限公司</b>VM系列产品工厂生产。</p>
                                    <p>软件名称: %s</p>
                                    <p>软件版本号: %s</p>
                                </body>
                            </html>
                    ''' % (software_name, software_version))

class SSCOM_Window(QMainWindow, Ui_MainWindow):
    serial = serial.Serial()
    serial_lock_mutex = threading.Lock()
    refresh_flag = 1
    cfg_dir = './config'
    cfg_path = cfg_dir + '/dayosscom.cfg'
    sscom_cfg = configparser.ConfigParser()
    write_dev_id_cmd = ''
    mcu_bat_filepath = ''
    mcu_download_count = 0
    software_log_level  = logging.INFO
    software_log_handler = ''
    current_com = ''
    write_id_is_done = False
    write_id_check_count = 0
    serial_have_data = False

    def __init__(self):
        super(SSCOM_Window, self).__init__()

    def sscom_init(self):
        self.setupUi(self)
        self.setWindowTitle(software_name + ' ' + software_version)
        self.setWindowIcon(QIcon('.\logo\logo.ico'))

        self.open_btton_status = 0
        self.scanf_com()
        self.sscom_gui_connect()
        self.textEdit_rx_data.clear()
        #self.lineEdit_mcu_bat_file.setEnabled(False)
        self.lineEdit_mcu_bat_file.setFocusPolicy(False)

        self.statusBar()
        self.show()

        self.serial_recv_thread = threading.Thread(target=self.serial_receive_data)
        self.serial_recv_thread.setDaemon(True)
        self.serial_recv_thread.start()

        self.sscom_logging_init()
        self.check_sscom_cfg()
        self.statusBar().showMessage('已就绪!')

    def sscom_logging_init(self):
        flag = 0
        if os.path.exists('./logs') == False:
            os.mkdir('./logs')
            print('已创建logs文件夹')
            flag = 1

        #logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #第一步，创建一个logger
        #sscom_logger = logging.getLogger(__name__)
        sscom_logger.setLevel(level = self.software_log_level)                       #log等级总开关

        #第二步，创建一个handler，用于写入日志文件
        # cur_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        cur_time = time.strftime('%Y%m%d%H', time.localtime(time.time()))
        log_file_name = os.getcwd() + '/logs/' + cur_time + '.log'
        print(log_file_name)
        self.software_log_handler = logging.FileHandler(log_file_name, mode='a')
        self.software_log_handler.setLevel(self.software_log_level)                                    #输出到file的log等级的开关

        #第三步，定义handler的输出格式
        #formatter = logging.Formatter('[%(asctime)s] - %(name)s[line:%(lineno)d] - %(levelname)s[] - %(message)s')
        formatter = logging.Formatter('[%(asctime)s][line:%(lineno)d][%(levelname)s] --> %(message)s')
        self.software_log_handler.setFormatter(formatter)
        sscom_logger.addHandler(self.software_log_handler)

        sscom_logger.info('\r\n\r\n\r\n--------------------------> Start DayoSSCOM %s <--------------------------' % software_version)
        # sscom_logger.debug('this is a logger debug message')
        # sscom_logger.info('this is a logger info message')
        # sscom_logger.warning('this is a logger warning message')
        # sscom_logger.error('this is a logger error message')
        # sscom_logger.critical('this is a logger critical message')

        if flag == 1:
            sscom_logger.info('创建logs目录(create logs dir)')

    def sscom_gui_connect(self):
        self.pushButton_clear_rx.clicked.connect(self.textEdit_rx_data.clear)
        self.pushButton_savedata.clicked.connect(self.savedata_button_callback)
        self.pushButton_search.clicked.connect(self.search_button_callback)
        self.pushButton_atcmd_save.clicked.connect(self.atcmd_save_button_callback)
        self.pushButton_open_serial.clicked.connect(self.open_serial_button_callback)
        self.pushButton_start_download.clicked.connect(self.start_download_button_callback)
        self.pushButton_write_id.clicked.connect(self.write_id_button_callback)
        self.checkBox_id_crlf.stateChanged.connect(self.write_id_crlf_checkbox_callback)
        self.pushButton_refresh_serial.clicked.connect(self.refresh_serial_button_callback)

        self.checkBox_automatic_savedata.stateChanged.connect(self.automatic_savedata_checkbox_callback)

        self.comboBox_com.currentIndexChanged.connect(self.com_combobox_callback)
        self.comboBox_baudrate.setCurrentText('115200')
        self.comboBox_baudrate.currentIndexChanged.connect(self.baudrate_combobox_callback)

        self.pushButton_cmd1.clicked.connect(lambda:self.cmd_button_callback(1))
        self.pushButton_cmd2.clicked.connect(lambda:self.cmd_button_callback(2))
        self.pushButton_cmd3.clicked.connect(lambda:self.cmd_button_callback(3))
        self.pushButton_cmd4.clicked.connect(lambda:self.cmd_button_callback(4))
        self.pushButton_cmd5.clicked.connect(lambda:self.cmd_button_callback(5))
        self.pushButton_cmd6.clicked.connect(lambda:self.cmd_button_callback(6))
        self.pushButton_cmd7.clicked.connect(lambda:self.cmd_button_callback(7))
        self.pushButton_cmd8.clicked.connect(lambda:self.cmd_button_callback(8))

        self.action_Quit.setShortcut('Ctrl+Q')
        self.action_Quit.setStatusTip('退出应用程序')
        self.action_Quit.triggered.connect(self.close)

        self.actionabout.setStatusTip('软件介绍')
        self.actionabout.triggered.connect(self.about_action_callback)
        
        self.actionhelp.setStatusTip('帮助文件')
        self.actionhelp.triggered.connect(self.help_action_callback)

        self.actionWriteIDCmd.setStatusTip('设置写地址的指令(eg:AT+DEVID)')
        self.actionWriteIDCmd.triggered.connect(self.set_write_id_cmd_action_callback)

        #self.menuLogLevel.serStatusTip('设置软件log的输出级别')
        self.actionlogdebug.triggered.connect(lambda:self.log_level_action_callback(logging.DEBUG))
        self.actionloginfo.triggered.connect(lambda:self.log_level_action_callback(logging.INFO))
        self.actionlogwarning.triggered.connect(lambda:self.log_level_action_callback(logging.WARNING))
        self.actionlogerror.triggered.connect(lambda:self.log_level_action_callback(logging.ERROR))

        self.toolButton_mcu_bat_file.clicked.connect(self.select_mcu_bat_file_toolbutton_callback)

        self.actionloginfo.setChecked(True)

        # timer = threading.Timer(0.5, self.display_write_id_result)
        # timer.start()
        self.check_write_result_timer = QTimer(self)
        self.check_write_result_timer.timeout.connect(self.display_write_id_result)
        #self.check_write_result_timer.setSingleShot(True)  #单次
        
        self.display_serial_data_timer = QTimer(self)
        self.display_serial_data_timer.timeout.connect(self.display_serial_recv_data)
        self.display_serial_data_timer.start(0.001)
        
    def sscom_save_cfg(self):
        with open(self.cfg_path, 'w+') as sscom_cfg_fd:
            self.sscom_cfg.write(sscom_cfg_fd)

    def display_write_id_result(self):
        if self.write_id_is_done == True:
            self.write_id_check_count = 0
            self.check_write_result_timer.stop()
            QMessageBox.information(self, "消息", u"设备ID写入成功!")
            sscom_logger.info('设备ID写入成功')
        
        #15*100ms timeout
        if self.write_id_check_count >= 15:
            self.write_id_check_count = 0
            self.check_write_result_timer.stop()
            QMessageBox.critical(self, "消息", u"设备ID写入!!!失败!!!")
            sscom_logger.error('设备ID写入失败')
        else:
            self.write_id_check_count = self.write_id_check_count + 1

        self.write_id_is_done = False

    def set_action_checked(self, level, status):
        if level == logging.DEBUG:
            self.actionlogdebug.setChecked(status)
        elif level == logging.INFO:
            self.actionloginfo.setChecked(status)
        elif level == logging.WARNING:
            self.actionlogwarning.setChecked(status)
        elif level == logging.ERROR:
            self.actionlogerror.setChecked(status)

    def log_level_action_callback(self, level):
        if self.software_log_level != level:
            self.set_action_checked(self.software_log_level, False)
            self.set_action_checked(level, True)
            self.software_log_level = level

            self.sscom_cfg.set('LOG_LEVEL', 'level', str(self.software_log_level))
            self.sscom_save_cfg()
        else:
            self.set_action_checked(self.software_log_level, True)
        sscom_logger.warning('log level change to %d' % level)

        self.software_log_handler.setLevel(self.software_log_level)

    def scanf_com(self):
        plist = list(serial.tools.list_ports.comports())

        if len(plist) == 0:
            self.comboBox_com.addItems(['没有可用的端口!'])
        else:
            for i in range(len(plist)):
                com_str = list(plist[i])
                # print("%d:%s" %(i, com_str[1]))
                self.comboBox_com.addItems([com_str[0]])

    def savedata_button_callback(self):
        print('savedata_button_callback')

    def search_button_callback(self):
        print('search_button_callback')

    def atcmd_save_button_callback(self):
        self.save_at_cmd_to_file()

    def open_serial_button_callback(self):
        if self.open_btton_status == 1:
            self.serial_close()
            sscom_logger.debug('关闭串口:%s' % self.current_com)
        else:
            self.serial_open()
            sscom_logger.debug('打开串口:%s' % self.current_com)

    def start_download_button_callback(self):
        if self.mcu_bat_filepath == '':
            QMessageBox.warning(self, "警告", u"请选择要下载的文件!")
            sscom_logger.warning('下载文件路径为空！！！')
        else:
            self.mcu_download_thread = threading.Thread(target=self.mcu_download)
            self.mcu_download_thread.setDaemon(True)
            self.mcu_download_thread.start()

    def mcu_download(self):
        self.mcu_download_count = self.mcu_download_count + 1
        sscom_logger.info('mcu_download count %d', self.mcu_download_count)
        self.send_to_recv_window('开始下载单片机代码[%d]...\r\n' % self.mcu_download_count)
        os.system('call \"%s\"' % self.mcu_bat_filepath)

    def refresh_serial_button_callback(self):
        self.serial_close()
        self.current_com = self.comboBox_com.currentText()
        self.refresh_flag = 0
        self.comboBox_com.clear()
        self.scanf_com()
        self.comboBox_com.setCurrentText(self.current_com)
        self.refresh_flag = 1
        sscom_logger.info('refresh_serial_button_callback %s' % self.current_com)

    def write_id_button_callback(self):
        device_id = self.lineEdit_device_id.text()
        write_id_cmd = ''
        if device_id.isdigit() == False:
            QMessageBox.critical(self, "错误", u"设备ID必须为纯数字!")
            sscom_logger.warning('设备ID不为纯数字！！！')
            return

        if len(device_id) > 10:
            QMessageBox.critical(self, "错误", u"设备ID最大长度为10!")
            sscom_logger.warning('设备ID位数大于10！！！')
            return

        device_id = '0'*(10-len(device_id)) + device_id
        self.write_id_is_done = False
        if self.checkBox_id_crlf.isChecked() == True:
            write_id_cmd = self.write_dev_id_cmd + ' ' + device_id + '\r\n'
        else:
            write_id_cmd = self.write_dev_id_cmd + ' ' + device_id
        self.serial_send_data(write_id_cmd.encode())
        sscom_logger.info('write device id[%d] [%s %s][%s]' % (self.mcu_download_count, self.write_dev_id_cmd, device_id, self.checkBox_id_crlf.isChecked()))

        self.check_write_result_timer.start(100)

    def write_id_crlf_checkbox_callback(self):
        status = 'True'
        if self.checkBox_id_crlf.isChecked() == True:
            sscom_logger.info('写ID指令带回车换行')
            status = 'True'
        else:
            sscom_logger.info('写ID指令取消回车换行')
            status = 'False'

        self.sscom_cfg.set('WRITE_ID_CRLF', 'crlf', status)
        self.sscom_save_cfg()

    def automatic_savedata_checkbox_callback(self):
        if self.checkBox_automatic_savedata.isChecked() == True:
            print("automatic_savedata is select")
        else:
            print('automatic_savedata is cannel')

    def select_mcu_bat_file_toolbutton_callback(self):
        file_path = QFileDialog.getOpenFileName(self, '选择下载文件', './mcuflashtool/firmware/*.bat', 'ALL File(*.*);;Bat Files(*.bat);;Exe File(*.exe)')
        sscom_logger.info('选择的下载文件路径：%s' % file_path[0])

        self.mcu_bat_filepath = file_path[0]
        if self.mcu_bat_filepath != '':
            filename_str = self.mcu_bat_filepath.split('/')[-1]
            self.lineEdit_mcu_bat_file.setText(filename_str)

            self.sscom_cfg.set('MCU_BAT_PATH', 'bat_path', self.mcu_bat_filepath)
            self.sscom_save_cfg()
        else:
            sscom_logger.error('选择的下载文件路径为空！！！')

    def com_combobox_callback(self):
        if self.refresh_flag == 1:
            str = self.comboBox_com.currentText()
            self.send_to_recv_window('串口已改为' + str + '\r\n')
            sscom_logger.info('串口已改为%s' % str)

    def baudrate_combobox_callback(self):
        str = self.comboBox_baudrate.currentText()
        self.send_to_recv_window('串口波特率已改为' + str + '\r\n')
        sscom_logger.info('串口波特率已改为%s' % str)

    def send_to_recv_window(self, str):
        # if self.textEdit_rx_data.document().lineCount() > 20:
            # self.textEdit_rx_data.clear()
            # print('clear')
        # 避免后面的打印修改前面的打印
        self.textEdit_rx_data.moveCursor(QTextCursor.End)
        self.textEdit_rx_data.insertPlainText(str)
        self.textEdit_rx_data.moveCursor(QTextCursor.End)

    def serial_open(self):
        self.serial.port = self.comboBox_com.currentText()
        self.serial.baudrate = int(self.comboBox_baudrate.currentText())
        self.serial.bytesize = 8
        self.serial.stopbits = 1
        self.serial.parity = 'N'

        self.serial_lock_mutex.acquire()

        try:
            self.serial.open()
        except serial.serialutil.SerialException:
            QMessageBox.critical(self, "错误", u"%s已被其他程序打开!" % self.serial.port)
            sscom_logger.warning('%s已被其他程序打开!' % self.serial.port)
        else:
            self.open_btton_status = 1
            # print('current port %s %d' % (self.serial.port, self.serial.baudrate))
            if self.serial.isOpen() == True:
                self.send_to_recv_window('打开串口成功!\r\n')
                self.pushButton_open_serial.setText('关闭串口')
                # self.pushButton_open_serial.setEnabled(False)
            else:
                self.send_to_recv_window('打开串口失败!!!\r\n')
                sscom_logger.warning('%s打开串口失败!!!' % self.serial.port)
        finally:
            self.serial_lock_mutex.release()

    def serial_close(self):
        self.serial_lock_mutex.acquire()
        self.open_btton_status = 0
        self.serial.close()
        if self.serial.isOpen == True:
            self.send_to_recv_window('关闭串口失败!!!\r\n')
            sscom_logger.warning('%s关闭串口失败!!!' % self.serial.port)
        else:
            self.pushButton_open_serial.setText('打开串口')
            # self.pushButton_open_serial.setEnabled(True)
            self.send_to_recv_window('关闭串口成功!\r\n')
        self.serial_lock_mutex.release()
        
    def display_serial_recv_data(self):
        if self.serial_have_data == True:
            if self.last_data_str != '':
                self.send_to_recv_window(self.last_data_str)
                #print(self.last_data_str,end='')

            # check write id result
            if write_id_success_flag in self.last_data_str:
                self.write_id_is_done = True
            #time.sleep(0.01)
            self.last_data_str = ''
            self.last_data.clear()
            self.last_data_time = int(round(time.time() * 1000))
            self.serial_have_data = False

    def serial_receive_data(self):
        sscom_logger.info('already create serial thread')
        self.last_data = []
        self.last_data_str = ''
        self.last_data_time = (int(round(time.time() * 1000)))       # ms
        error_count = 0
        while True:
            self.serial_lock_mutex.acquire()
            if self.serial.isOpen() == True and self.serial_have_data == False:
                for byte in self.serial.read(self.serial.inWaiting()):
                    self.last_data.append(byte)

                if (len(self.last_data) > 512) or (int(round(time.time() * 1000)) - self.last_data_time) > 10:
                    try:
                        #对应的发送端传来的中文编码也应该是ansi，否则会乱码
                        #这里使用ignore参数，忽略错误
                        # self.last_data_str = bytes(self.last_data).decode('ansi', 'ignore')
                        self.last_data_str = bytes(self.last_data).decode('ansi')
                    except UnicodeDecodeError:
                        # 注释1：出现该异常时暂不处理，等待接收到完整的ansi码再打印，就不会出现中文打印乱码
                        # 注释2：加入一个错误计数器，防止一直出错，造成串口打印停止
                        error_count = error_count + 1
                        #print('error %d' % (error_count))
                        if error_count > 100:
                            self.serial_have_data = True
                            error_count = 0
                        pass
                    else:
                        self.serial_have_data = True
                        error_count = 0
            self.serial_lock_mutex.release()

    def serial_send_data(self, str):
        self.serial_lock_mutex.acquire()
        if self.serial.isOpen() == True:
            self.serial.write(str)
            # if str[-1]==10:
                # self.send_to_recv_window('>> ' + str.decode())
            # else:
                # self.send_to_recv_window(str.decode())
        else:
            self.send_to_recv_window('串口已被关闭!\r\n')
            sscom_logger.warning('%s串口已被关闭，禁止发送！' % self.serial.port)
        self.serial_lock_mutex.release()

    def cmd_button_callback(self, num):
        at_cmd_str = ''
        if num == 1:
            # if self.checkBox_hex_cmd8.isChecked() == True:
            at_cmd = self.lineEdit_cmd1.text()
        elif num == 2:
            at_cmd = self.lineEdit_cmd2.text()
        elif num == 3:
            at_cmd = self.lineEdit_cmd3.text()
        elif num == 4:
            at_cmd = self.lineEdit_cmd4.text()
        elif num == 5:
            at_cmd = self.lineEdit_cmd5.text()
        elif num == 6:
            at_cmd = self.lineEdit_cmd6.text()
        elif num == 7:
            at_cmd = self.lineEdit_cmd7.text()
        elif num == 8:
            at_cmd = self.lineEdit_cmd8.text()
        else:
            pass

        if at_cmd == '':
            QMessageBox.critical(self, "错误", u"指令不能为空!")
            sscom_logger.warning('AT cmd 不能为空！')
            return

        if self.checkBox_at_crlf.isChecked() == True:
            at_cmd_str = at_cmd + '\r\n'
        else:
            at_cmd_str = at_cmd

        self.serial_send_data(at_cmd_str.encode())
        sscom_logger.info('Send AT cmd %s [%s]' % (at_cmd, self.checkBox_at_crlf.isChecked()))

    def about_action_callback(self):
        QMessageBox.about(self, "关于", software_about_str)
        
    def help_action_callback(self):
        QMessageBox.information(self, "帮助", software_help_str)

    def set_write_id_cmd_action_callback(self):
        text, ok = QInputDialog.getText(self, '!!!请勿设置!!!',
            '请输入写地址命令:')

        if ok:
            if text == '':
                QMessageBox.critical(self, "错误", u"指令不能为空!")
                sscom_logger.warning('写入‘设置写ID命令’命令为空')
            else:
                self.write_dev_id_cmd = text
                self.sscom_cfg.set('WRITE_ID_CMD', 'at_cmd', self.write_dev_id_cmd)
                sscom_logger.warning('‘设置写ID命令’被修改为:%s' % self.write_dev_id_cmd)
                self.sscom_save_cfg()

    def check_sscom_cfg(self):
        if os.path.exists(self.cfg_dir) == False:
            os.mkdir(self.cfg_dir)
            sscom_logger.info('创建config文件夹')
        if os.path.exists(self.cfg_path) == False:
            cfg_fd = open(self.cfg_path, 'a+')
            # cfg_fd.write("******************************************\n")
            # cfg_fd.write("*               配置文件                 *\n")
            # cfg_fd.write("*               请勿修改                 *\n")
            # cfg_fd.write("******************************************\n\n\n")
            cfg_fd.close()

            # WRITE_ID_CMD
            self.write_dev_id_cmd = 'AT+DEVID'
            self.sscom_cfg.add_section('WRITE_ID_CMD')
            self.sscom_cfg.set('WRITE_ID_CMD', 'at_cmd', self.write_dev_id_cmd)

            # MCU Script path
            #self.mcu_bat_filepath = './'
            self.sscom_cfg.add_section('MCU_BAT_PATH')
            self.sscom_cfg.set('MCU_BAT_PATH', 'bat_path', '')

            # write id crlf
            self.sscom_cfg.add_section('WRITE_ID_CRLF')
            self.sscom_cfg.set('WRITE_ID_CRLF', 'crlf', 'False')

            # log level
            self.sscom_cfg.add_section('LOG_LEVEL')
            self.sscom_cfg.set('LOG_LEVEL', 'level', str(logging.INFO))

            # CMD
            for i in range(8):
                com_id_str = ('COM%d' % (i+1))
                at_cmd_str = ('AT+cmd%d %d' % (i+1, i+1))
                self.sscom_cfg.add_section(com_id_str)
                self.sscom_cfg.set(com_id_str, 'hex_check', 'False')
                self.sscom_cfg.set(com_id_str, 'at_cmd', at_cmd_str)

            self.sscom_save_cfg()

            sscom_logger.info('cfg文件可能被删,使用默认配置数据！！！')

        self.sscom_cfg.read(self.cfg_path)
        try:
            self.write_dev_id_cmd = self.sscom_cfg.get('WRITE_ID_CMD', 'at_cmd')
            self.mcu_bat_filepath = self.sscom_cfg.get('MCU_BAT_PATH', 'bat_path')
            self.checkBox_id_crlf.setChecked(self.sscom_cfg.getboolean('WRITE_ID_CRLF', 'crlf'))
            level = self.sscom_cfg.get('LOG_LEVEL', 'level')
            self.log_level_action_callback(int(level))
            if self.mcu_bat_filepath != '':
                filename_str = self.mcu_bat_filepath.split('/')[-1]
                self.lineEdit_mcu_bat_file.setText(filename_str)
        except configparser.NoSectionError:
            QMessageBox.critical(self, "错误", u"配置文件已损坏，请删除config文件夹!")
            sscom_logger.error('cfg文件已损坏，请删除config文件夹!')
            return
        else:
            sscom_logger.info('get at cmd table:')
            for i in range(8):
                com_id_str = ('COM%d' % (i+1))
                hex_check = self.sscom_cfg.getboolean(com_id_str, 'hex_check')
                at_cmd = self.sscom_cfg.get(com_id_str, 'at_cmd')
                sscom_logger.info('COM%d %s %s' % (i+1, at_cmd, hex_check))
                if 'COM1' == com_id_str:
                    self.checkBox_hex_cmd1.setChecked(hex_check)
                    self.lineEdit_cmd1.setText(at_cmd)
                elif 'COM2' == com_id_str:
                    self.checkBox_hex_cmd2.setChecked(hex_check)
                    self.lineEdit_cmd2.setText(at_cmd)
                elif 'COM3' == com_id_str:
                    self.checkBox_hex_cmd3.setChecked(hex_check)
                    self.lineEdit_cmd3.setText(at_cmd)
                elif 'COM4' == com_id_str:
                    self.checkBox_hex_cmd4.setChecked(hex_check)
                    self.lineEdit_cmd4.setText(at_cmd)

                elif 'COM5' == com_id_str:
                    self.checkBox_hex_cmd5.setChecked(hex_check)
                    self.lineEdit_cmd5.setText(at_cmd)
                elif 'COM6' == com_id_str:
                    self.checkBox_hex_cmd6.setChecked(hex_check)
                    self.lineEdit_cmd6.setText(at_cmd)
                elif 'COM7' == com_id_str:
                    self.checkBox_hex_cmd7.setChecked(hex_check)
                    self.lineEdit_cmd7.setText(at_cmd)
                elif 'COM8' == com_id_str:
                    self.checkBox_hex_cmd8.setChecked(hex_check)
                    self.lineEdit_cmd8.setText(at_cmd)
                else:
                    pass

    def save_at_cmd_to_file(self):
        sscom_logger.info('save at cmd table')
        for i in range(8):
            if i == 0:
                hex_check = self.checkBox_hex_cmd1.isChecked()
                at_cmd = self.lineEdit_cmd1.text()
            if i == 1:
                hex_check = self.checkBox_hex_cmd2.isChecked()
                at_cmd = self.lineEdit_cmd2.text()
            if i == 2:
                hex_check = self.checkBox_hex_cmd3.isChecked()
                at_cmd = self.lineEdit_cmd3.text()
            if i == 3:
                hex_check = self.checkBox_hex_cmd4.isChecked()
                at_cmd = self.lineEdit_cmd4.text()

            if i == 4:
                hex_check = self.checkBox_hex_cmd5.isChecked()
                at_cmd = self.lineEdit_cmd5.text()
            if i == 5:
                hex_check = self.checkBox_hex_cmd6.isChecked()
                at_cmd = self.lineEdit_cmd6.text()
            if i == 6:
                hex_check = self.checkBox_hex_cmd7.isChecked()
                at_cmd = self.lineEdit_cmd7.text()
            if i == 7:
                hex_check = self.checkBox_hex_cmd8.isChecked()
                at_cmd = self.lineEdit_cmd8.text()
            com_id_str = ('COM%d' % (i+1))
            self.sscom_cfg.set(com_id_str, 'hex_check', ('%s' % hex_check))
            self.sscom_cfg.set(com_id_str, 'at_cmd', at_cmd)
            sscom_logger.info('COM%d %s %s' % (i+1, at_cmd, hex_check))

        self.sscom_save_cfg()

if __name__ == '__main__':
    global sscom
    app = QApplication(sys.argv)
    sscom = SSCOM_Window()
    sscom.sscom_init()

    sys.exit(app.exec_())
