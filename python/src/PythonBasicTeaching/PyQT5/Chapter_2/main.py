# -*- coding: utf-8 -*-

import sys
import os
import time
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QListView, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSlot

from MarkQtUI import Ui_MainWindow


class Mark(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        # 繼承Ui_MainWindow 也就是 mark_tool 內的 class
        super(Mark, self).__init__(parent)

        # 建立ui介面
        self.setupUi(self)
        # 這功能主要是點擊了這個按鈕要執行什麼？
        # self.clickTestButton 這個 function 在 MarkQtUI.Ui_MainWindow內
        # 因為已經繼承了Ui_MainWindow，因此執行 self.Test_Button
        # 點擊了時候會套用下方的function test_button_clicked，會將值輸出
        # 如果沒有這行，點擊按鈕不會有任何的動作
        self.clickTestButton.clicked.connect(self.test_button_clicked)

    def logv2(self, title, msg):
        """
        :param title: log 的 開頭
        :param msg: 你想顯示的訊息
        :return: [2020/02/28 14:35:29][test] Hi
        """
        timeStr = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        log_message = '[' + str(timeStr) + '][' + title + '] ' + str(msg)
        # print(log_message)  # 如果你把註解拿掉，你的終端機就會顯示 Log
        return log_message

    def test_button_clicked(self):
        """
        當我們每點擊一次 self.clickTestButton 按鈕的時候，就會執行這裡
        每點擊一次就會顯示在我們剛建立起來的 self.displayListWidget (List Widget)
        類似：[2020/02/28 14:40:38][PyQt5教學] 有問題可以問我喔！
        """
        self.displayListWidget.addItem(self.logv2('PyQt5教學', '有問題可以問我喔！'))  # 顯示在我們剛建立的 List Widget內
        self.displayListWidget.scrollToBottom()  # 這行很重要，如果你沒加這行，你的如果超過self.displayListWidget範圍的話，他是不會往下執行的


if __name__ == "__main__":
    
    # 第一行必備，系統呼叫
    app = QApplication(sys.argv)

    # 指定 Mark Class 會先執行__init__
    window = Mark()

    # 將GUI介面顯示出來
    window.show()

    # 關閉系統
    sys.exit(app.exec_())
