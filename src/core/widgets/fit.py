# -*- coding: utf-8 -*-
"""Fit curve Dialog

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QToolBar, QComboBox, QSpinBox, \
    QLineEdit, QFormLayout, QTextEdit, QPushButton, QWidget, QGraphicsLineItem

from core.utils import str2num
from core.utils.algor import polyfit, calPoly, poly2str


class FitDockWidget(QDockWidget):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(self.tr("Fit Curves"))
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.initUI()
        self.fitCurveObjs = []
        self.view = None
        self.initData(self.view)
        self.presicion = 5
        self.visibilityChanged.connect(self.visibileChanged)
        self.fitBtn.clicked.connect(self.fit)

    def initUI(self):
        self.toolbar = QToolBar(self)
        self.curveCombobox = QComboBox()
        self.curveCombobox.setMinimumWidth(150)
        self.curveCombobox.setMinimumHeight(26)
        self.fitBtn = QPushButton(self.tr("fit"))
        self.toolbar.addWidget(self.curveCombobox)
        self.toolbar.addWidget(self.fitBtn)
        self.degreeSpinBox = QSpinBox()
        self.minXTextBox = QLineEdit()
        self.maxXTextBox = QLineEdit()
        self.stepXTextBox = QLineEdit()
        formlayout = QFormLayout()
        formlayout.addRow(self.tr("fit degree"), self.degreeSpinBox)
        formlayout.addRow(self.tr("x min"), self.minXTextBox)
        formlayout.addRow(self.tr("x max"), self.maxXTextBox)
        formlayout.addRow(self.tr("x step"), self.stepXTextBox)
        self.outTextBox = QTextEdit()

        lay = QVBoxLayout()
        # lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toolbar)
        lay.addLayout(formlayout)
        lay.addWidget(self.outTextBox)


        w = QWidget(self)
        w.setLayout(lay)
        self.setWidget(w)

    def initData(self, view):
        if view is None:
            return
        self.view = view
        self.curveCombobox.clear()
        # mainview = GraphDigitGraphicsView()
        view.graphicsPixmapItem.setPixmap(view.graphicsPixmapItem.pixmap())

        self.reset()

        if self.view.proj.fitx[0] is not None:
            self.minXTextBox.setText(str(self.view.proj.fitx[0]))
        if self.view.proj.fitx[1] is not None:
            self.maxXTextBox.setText(str(self.view.proj.fitx[1]))
        if self.view.proj.fitx[2] is not None:
            self.stepXTextBox.setText(str(self.view.proj.fitx[2]))
        if self.view.proj.degree:
            self.degreeSpinBox.setValue(self.view.proj.degree)
        if self.view.proj.precision:
            self.presicion = self.view.proj.precision

    def reset(self):
        if not self.view:
            return
        if len(self.view.pointObjs) < 1:
            return

        self.curveCombobox.clear()
        curvenames = list(self.view.curveObjs.keys())
        curvenames.reverse()
        self.curveCombobox.addItems(curvenames)

        for obj in self.fitCurveObjs:
            self.view.scene.removeItem(obj)
        self.fitCurveObjs.clear()

        self.outTextBox.setText("")

    def closeEvent(self, QCloseEvent):
        self.reset()

    def visibileChanged(self, v):
        self.reset()

    def fit(self):
        self.reset()
        curve = self.curveCombobox.currentText().strip()
        if self.view is None:
            return
        if curve not in self.view.pointObjs or len(self.view.pointObjs) < 2:
            return

        xs = []
        ys = []
        for item in self.view.pointObjs[curve]:
            xs.append(item.pos().x())
            ys.append(item.pos().y())
        xs,ys = self.view.pointToCoord(xs,ys)
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

        xnew = np.arange(xmin, xmax+xstep/2, xstep)

        degree = self.degreeSpinBox.value()
        self.view.proj.degree = degree
        self.view.proj.precision = self.presicion

        poly, error = polyfit(xs, ys, degree)
        if poly==[]:
            return
        ynew = calPoly(poly, xnew)

        xpos, ypos = self.view.coordToPoint(xnew, ynew)
        for i in range(1, len(xpos)):
            line = QGraphicsLineItem(xpos[i - 1], ypos[i - 1], xpos[i], ypos[i])
            line.setZValue(10)
            line.setPen(QPen(Qt.yellow, 2, Qt.SolidLine))
            self.fitCurveObjs.append(line)
            self.view.scene.addItem(line)

        self.minXTextBox.setText(str(xmin))
        self.maxXTextBox.setText(str(xmax))
        self.stepXTextBox.setText(str(xstep))

        text = "fitted polynomial:\n"
        text += poly2str(poly) + "\n\n"
        text += "max err:" + str(np.max(error)) + "\n\n"
        text += "fitted points:\n   x  ,   y\n"
        for x, y in zip(xnew, ynew):
            text += "{},{}\n".format(round(x,self.presicion), round(y,self.presicion))

        self.outTextBox.setText(text)
        self.view.sigModified.emit(True)


if __name__ == "__main__":
    from PyQt5.QtWidgets import *
    import sys

    app = QApplication(sys.argv)
    win = QMainWindow()
    win.addDockWidget(FitDockWidget())
    win.show()
    sys.exit(app.exec_())
