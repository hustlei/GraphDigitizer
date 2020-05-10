# -*- coding: utf-8 -*-
"""Fit curve Dialog

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QTextCursor, QTextTableFormat, QTextLength
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QToolBar, QComboBox, QSpinBox, \
    QLineEdit, QFormLayout, QTextEdit, QPushButton, QWidget, QGraphicsLineItem, QTabWidget

from core.utils import str2num
from core.utils.algor import polyfit, calPoly, poly2str
from core.widgets.fit import FitWidget
from core.widgets.inerpolation import InterpWidget


class FitDockWidget(QDockWidget):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(self.tr("Fit && Interpolation"))
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.tabWidget = QTabWidget(self)
        self.setWidget(self.tabWidget)

        self.fit = FitWidget()
        self.tabWidget.addTab(self.fit,"Fit curve")
        self.interp = InterpWidget()
        self.tabWidget.addTab(self.interp,"Interpolation curve")

    def reset(self):
        self.fit.reset()
        self.interp.reset()

    def initData(self, view):
        self.fit.initData(view)
        self.interp.initData(view)
