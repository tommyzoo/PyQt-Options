# -*- coding: utf-8 -*-
# Created by: PyQt5 UI code generator 5.14.1
#

import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSpacerItem,\
    QSizePolicy
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt5.QtGui import QColor, QIcon, QPainter, QEnterEvent, QPen, QFont

from your_widget import ContainWidget


Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)


def read_qss(style):
    """读取Qss文件"""
    with open(style, 'r', encoding='utf-8') as f:
        return f.read()


class TitleBar(QWidget):
    # 窗口最小化信号
    windowMinimumed = pyqtSignal()
    # 窗口最大化信号
    windowMaximumed = pyqtSignal()
    # 窗口还原信号
    windowNormaled = pyqtSignal()
    # 窗口关闭信号
    windowClosed = pyqtSignal()
    # 窗口移动
    windowMoved = pyqtSignal(QPoint)

    title_height = 38

    def __init__(self, parent=None):
        super().__init__(parent)
        # 支持qss设置背景
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.mPos = None
        self.iconSize = 20  # 图标的默认大小
        self.setContentsMargins(0,0,0,0)
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        # 布局
        layout = QHBoxLayout(self, spacing=0)
        layout.setContentsMargins(0, 0, 0, 0)
        # 窗口图标
        self.iconLabel = QLabel(self)
        self.iconLabel.setObjectName("icon_label")
#         self.iconLabel.setScaledContents(True)
        layout.addWidget(self.iconLabel)
        # 窗口标题
        self.titleLabel = QLabel(self)
        self.titleLabel.setObjectName("title_label")
        self.titleLabel.setMargin(2)
        layout.addWidget(self.titleLabel)
        # 中间伸缩条
        layout.addSpacerItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # 利用Webdings字体来显示图标
        font = self.font() or QFont()
        font.setFamily('Webdings')
        # 最小化按钮
        self.buttonMinimum = QPushButton(
            '0', self, clicked=self.windowMinimumed.emit, font=font, objectName='buttonMinimum')
        layout.addWidget(self.buttonMinimum)
        # 最大化/还原按钮
        self.buttonMaximum = QPushButton(
            '1', self, clicked=self.showMaximized, font=font, objectName='buttonMaximum')
        layout.addWidget(self.buttonMaximum)
        # 关闭按钮
        self.buttonClose = QPushButton(
            'r', self, clicked=self.windowClosed.emit, font=font, objectName='buttonClose')
        layout.addWidget(self.buttonClose)
        # 设置右边按钮的大小
        self.buttonMinimum.setFixedWidth(40)
        self.buttonMaximum.setFixedWidth(40)
        self.buttonClose.setFixedWidth(40)

        # 初始高度
        self.setHeight(40)
        self.setStyleSheet("""
            QWidget{background-color: rgb(60,63,65);}
            QLabel{color:rgb(187, 187, 187);}
            QPushButton{background-color: rgb(60,63,65);border:none;color:rgb(187, 187, 187);}
            QPushButton::hover{background-color: rgb(80,83,85);}
            #buttonClose::hover{background-color: rgb(199, 84, 80);}
        """)

    def showMaximized(self):
        if self.buttonMaximum.text() == '1':
            # 最大化
            self.buttonMaximum.setText('2')
            self.windowMaximumed.emit()
        else:  # 还原
            self.buttonMaximum.setText('1')
            self.windowNormaled.emit()

    def setHeight(self, height=38):
        """设置标题栏高度"""
        self.title_height = height
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.buttonMinimum.setFixedHeight(height)
        self.buttonMaximum.setFixedHeight(height)
        self.buttonClose.setFixedHeight(height)

    def setTitle(self, title):
        """设置标题"""
        self.titleLabel.setText(title)

    def setIcon(self, icon):
        """设置图标"""
        self.iconLabel.setPixmap(icon.pixmap(self.iconSize, self.iconSize))

    def setIconSize(self, size):
        """设置图标大小"""
        self.iconSize = size

    def enterEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super(TitleBar, self).enterEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            super(TitleBar, self).mouseDoubleClickEvent(event)
            self.showMaximized()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.mPos:
            self.windowMoved.emit(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()


class MainWin(QWidget):
    """主窗口"""
    Margins = 5
    status = 1
    content_widget = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("surface_win")

        # 鼠标状态
        self._pressed = False
        self.Direction = None
        # 鼠标跟踪
        self.setMouseTracking(True)
        self.resize(1400, 902)

        # 去除原生边框和标题
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 基础布局
        self.title_bar = TitleBar(self)
        self.content_widget = ContainWidget(self)
        self.content_widget.setAutoFillBackground(True)
        self.content_widget.installEventFilter(self)

        # 标题栏信号连接
        self.title_bar.windowClosed.connect(self.close)
        self.title_bar.windowMoved.connect(self.move)
        self.title_bar.windowMinimumed.connect(self.showMinimized)
        self.title_bar.windowNormaled.connect(self.showNormal)
        self.title_bar.windowMaximumed.connect(self.showMaximized)
        self.windowTitleChanged.connect(self.title_bar.setTitle)

    def setTitleBarHeight(self, height=38):
        """设置标题栏高度"""
        self.title_bar.setHeight(height)

    def setIconSize(self, size):
        """设置图标的大小"""
        self.title_bar.setIconSize(size)

    def move(self, pos):
        if self.windowState() == Qt.WindowMaximized or self.windowState() == Qt.WindowFullScreen:
            # 最大化或者全屏则不允许移动
            return
        super().move(pos)

    def showMaximized(self):
        """最大化,要去除上下左右边界,如果不去除则边框地方会有空隙"""
        super().showMaximized()

    def showNormal(self):
        """还原,要保留上下左右边界,否则没有边框无法调整"""
        super().showNormal()

    def eventFilter(self, obj, event):
        """事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式"""
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        print("resize")
        if not self.isMaximized():
            self.title_bar.setGeometry(self.Margins,
                                       self.Margins,
                                       self.width()-self.Margins*2,
                                       self.title_bar.title_height)
            self.content_widget.setGeometry(self.Margins,
                                            self.Margins + self.title_bar.title_height,
                                            self.width() - self.Margins*2,
                                            self.height()-self.Margins*2-self.title_bar.title_height,
                                            )
        else:
            self.title_bar.setGeometry(0, 0, self.width(), self.title_bar.title_height)
            self.content_widget.setGeometry(0,
                                            self.title_bar.title_height,
                                            self.width(),
                                            self.height()-self.title_bar.title_height)

    def paintEvent(self, event):
        """由于是全透明背景窗口,重绘事件中绘制透明度为1的难以发现的边框,用于调整窗口大小"""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 0, 0, 3), self.Margins))
        painter.drawRect(QRect(self.Margins//2,
                               self.Margins//2,
                               self.width()-self.Margins,
                               self.height()-self.Margins))

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._mpos = event.pos()
            self._pressed = True

    def mouseReleaseEvent(self, event):
        """鼠标弹起事件"""
        super().mouseReleaseEvent(event)
        self._pressed = False
        self.Direction = None

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super().mouseMoveEvent(event)
        pos = event.pos()
        xPos, yPos = pos.x(), pos.y()
        wm, hm = self.width() - self.Margins, self.height() - self.Margins
        if self.isMaximized() or self.isFullScreen():
            self.Direction = None
            self.setCursor(Qt.ArrowCursor)
            return
        if event.buttons() == Qt.LeftButton and self._pressed:
            self._resizeWidget(pos)
            return
        if xPos <= self.Margins and yPos <= self.Margins:
            # 左上角
            self.Direction = LeftTop
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= xPos <= self.width() and hm <= yPos <= self.height():
            # 右下角
            self.Direction = RightBottom
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= xPos and yPos <= self.Margins:
            # 右上角
            self.Direction = RightTop
            self.setCursor(Qt.SizeBDiagCursor)
        elif xPos <= self.Margins and hm <= yPos:
            # 左下角
            self.Direction = LeftBottom
            self.setCursor(Qt.SizeBDiagCursor)
        elif 0 <= xPos <= self.Margins and self.Margins <= yPos <= hm:
            # 左边
            self.Direction = Left
            self.setCursor(Qt.SizeHorCursor)
        elif wm <= xPos <= self.width() and self.Margins <= yPos <= hm:
            # 右边
            self.Direction = Right
            self.setCursor(Qt.SizeHorCursor)
        elif self.Margins <= xPos <= wm and 0 <= yPos <= self.Margins:
            # 上面
            self.Direction = Top
            self.setCursor(Qt.SizeVerCursor)
        elif self.Margins <= xPos <= wm and hm <= yPos <= self.height():
            # 下面
            self.Direction = Bottom
            self.setCursor(Qt.SizeVerCursor)

    def _resizeWidget(self, pos):
        """调整窗口大小"""
        if self.Direction == None:
            return
        mpos = pos - self._mpos
        xPos, yPos = mpos.x(), mpos.y()
        geometry = self.geometry()
        x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
        if self.Direction == LeftTop:  # 左上角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
        elif self.Direction == RightBottom:  # 右下角
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
        elif self.Direction == RightTop:  # 右上角
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos.setX(pos.x())
        elif self.Direction == LeftBottom:  # 左下角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos.setY(pos.y())
        elif self.Direction == Left:  # 左边
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return
        elif self.Direction == Right:  # 右边
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            else:
                return
        elif self.Direction == Top:  # 上面
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return
        elif self.Direction == Bottom:  # 下面
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
            else:
                return
        self.setGeometry(x, y, w, h)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWin()
    win.title_bar.setTitle("自定义窗口移动拉伸")
    win.show()
    sys.exit(app.exec_())