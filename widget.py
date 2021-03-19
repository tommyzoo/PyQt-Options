# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt


class Widget(QWidget):
    pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Widget()
    win.show()
    sys.exit(app.exec_())