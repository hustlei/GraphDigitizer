# -*- coding: utf-8 -*-
"""Fit curve Dialog

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QTextCursor, QTextTableFormat, QTextLength
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QToolBar, QComboBox, QSpinBox, \
    QLineEdit, QFormLayout, QTextEdit, QPushButton, QWidget, QGraphicsLineItem

from core.utils import str2num
from core.utils.algor import polyfit, calPoly, poly2str, interp


class InterpWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.interpCurveObjs = []
        self.view = None
        self.initData(self.view)
        self.presicion = 5
        #self.visibilityChanged.connect(self.visibileChanged)
        self.fitBtn.clicked.connect(self.interp)

    def initUI(self):
        self.toolbar = QToolBar(self)
        self.curveCombobox = QComboBox()
        self.curveCombobox.setMinimumWidth(150)
        self.curveCombobox.setMinimumHeight(22)
        self.fitBtn = QPushButton(self.tr("Interpolate"))
        self.toolbar.addWidget(self.curveCombobox)
        self.toolbar.addWidget(self.fitBtn)
        self.degreeComboBox = QComboBox()
        self.degreeComboBox.addItems(["1","2","3","4","5"])
        self.minXTextBox = QLineEdit()
        self.maxXTextBox = QLineEdit()
        self.stepXTextBox = QLineEdit()
        formlayout = QFormLayout()
        formlayout.addRow(self.tr("interpolation order"), self.degreeComboBox)
        formlayout.addRow(self.tr("x min"), self.minXTextBox)
        formlayout.addRow(self.tr("x max"), self.maxXTextBox)
        formlayout.addRow(self.tr("x step"), self.stepXTextBox)
        self.outTextBox = QTextEdit()

        lay = QVBoxLayout()
        # lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toolbar)
        lay.addLayout(formlayout)
        lay.addWidget(self.outTextBox)

        self.setLayout(lay)

    def initData(self, view):
        if view is None:
            return
        self.view = view
        self.curveCombobox.clear()
        # mainview = GraphDigitGraphicsView()
        # view.graphicsPixmapItem.setPixmap(view.graphicsPixmapItem.pixmap())

        self.reset()

        if self.view.proj.fitx[0] is not None:
            self.minXTextBox.setText(str(self.view.proj.fitx[0]))
        if self.view.proj.fitx[1] is not None:
            self.maxXTextBox.setText(str(self.view.proj.fitx[1]))
        if self.view.proj.fitx[2] is not None:
            self.stepXTextBox.setText(str(self.view.proj.fitx[2]))
        if self.view.proj.degree and self.view.proj.degree in [1,2,3,4,5]:
            self.degreeComboBox.setCurrentText(str(self.view.proj.degree))
        if self.view.proj.precision:
            self.presicion = self.view.proj.precision

    def reset(self):
        if not self.view:
            return
        if len(self.view.pointObjs) < 1:
            return

        last = self.curveCombobox.currentText()
        self.curveCombobox.clear()
        curvenames = list(self.view.curveObjs.keys())
        curvenames.reverse()
        self.curveCombobox.addItems(curvenames)
        self.curveCombobox.setCurrentText(last)

        for obj in self.interpCurveObjs:
            self.view.scene.removeItem(obj)
        self.interpCurveObjs.clear()

        self.outTextBox.setText("")

    def closeEvent(self, QCloseEvent):
        self.reset()

    def visibileChanged(self, v):
        self.reset()

    def interp(self):
        self.reset()
        curve = self.curveCombobox.currentText().strip()
        if self.view is None:
            return
        if curve not in self.view.pointObjs or len(self.view.pointObjs[curve]) < 2:
            return

        xs = []
        ys = []
        for item in self.view.pointObjs[curve]:
            xs.append(item.pos().x())
            ys.append(item.pos().y())
        xs, ys = self.view.pointToCoord(xs, ys)
        xmin = None
        xmax = None
        xstep = None
        if self.minXTextBox.text().strip():
            xmin = str2num(self.minXTextBox.text().strip())
            self.view.proj.fitx[0] = xmin
        if xmin is None:
            xmin = min(xs)
        if self.maxXTextBox.text().strip():
            xmax = str2num(self.maxXTextBox.text().strip())
            self.view.proj.fitx[1] = xmax
        if xmax is None:
            xmax = max(xs)
        if self.stepXTextBox.text().strip():
            xstep = str2num(self.stepXTextBox.text().strip())
            self.view.proj.fitx[2] = xstep
        if xstep is None:
            xstep = (xmax - xmin) / 15

        xnew = np.arange(xmin, xmax + xstep / 2, xstep)

        degree = int(self.degreeComboBox.currentText())
        self.view.proj.degree = degree
        self.view.proj.precision = self.presicion

        ynew = interp(xs,ys,xnew,degree)

        xpos, ypos = self.view.coordToPoint(xnew, ynew)
        for i in range(1, len(xpos)):
            line = QGraphicsLineItem(xpos[i - 1], ypos[i - 1], xpos[i], ypos[i])
            line.setZValue(10)
            line.setPen(QPen(Qt.yellow, 2, Qt.SolidLine))
            self.interpCurveObjs.append(line)
            self.view.scene.addItem(line)

        self.minXTextBox.setText(str(xmin))
        self.maxXTextBox.setText(str(xmax))
        self.stepXTextBox.setText(str(xstep))

        text = "interpolation points:\n\n"
        self.outTextBox.setText(text)

        cursor = QTextCursor(self.outTextBox.textCursor())
        cursor.movePosition(QTextCursor.End)  # move the end of documents
        ttf = QTextTableFormat()  # 创建表格对象格式
        ttf.setCellPadding(2)  # 单元格内文本和边框距离
        ttf.setCellSpacing(0)  # 单元格线宽
        ttf.setAlignment(Qt.AlignLeft)  # 表格对齐模式
        ttf.setBorder(0.5)
        # ttf.setColumnWidthConstraints(
        #     (QTextLength(QTextLength.PercentageLength, 50), QTextLength(QTextLength.PercentageLength, 50)))  # 百分比定义列宽
        ttf.setColumnWidthConstraints(
            (QTextLength(QTextLength.FixedLength, 75), QTextLength(QTextLength.FixedLength, 75)))  # 像素定义列宽
        table = cursor.insertTable(len(xnew)+1, 2, ttf)

        table.cellAt(0, 0).firstCursorPosition().insertHtml("<b>x</b>")
        table.cellAt(0, 1).firstCursorPosition().insertHtml("<b>y</b>")
        for i in range(len(xnew)):
            table.cellAt(i+1, 0).firstCursorPosition().insertText(str(round(xnew[i], self.presicion)))
            table.cellAt(i+1, 1).firstCursorPosition().insertText(str(round(ynew[i], self.presicion)))

        self.view.sigModified.emit(True)
