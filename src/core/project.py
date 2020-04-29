# -*- coding: utf-8 -*-
"""Data for project of the app

some setting datas for project.

Copyright (c) 2019 lileilei <hustlei@sina.cn>
"""

import os
import dill
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from .enums import PointType


class Curve():
    def __init__(self):
        self.points = []  # scene coord for open project
        self.pointType = PointType.cross
        self.pointColor = Qt.blue
        self.lineWidth = 1


class Digi():
    """Project data for app

    img and grid data used by app directly.
    data only used for app save and open
    """

    def __init__(self, imgpath=""):
        # data input directly by user
        # chart image
        self.img = None  # QPixmap, set by setImgpath
        self.imgScale = 1
        # axes
        self.axesxs = []
        self.axesys = []
        # grid
        self.gridx = [None, None, None]  # min max step
        self.gridy = [None, None, None]  # min max step
        self.gridLineType = Qt.DotLine
        self.gridLineWidth = 1
        self.gridColor = Qt.gray
        # data for save and load, including point,curve coords got by mouse on graphicsview
        self.data = {}
        self.resetData()

        if os.path.exists(imgpath):
            self.img = imgpath

    def resetData(self, newproject=False):
        if newproject:
            self.img = None  # QPixmap, set by setImgpath
            self.imgScale = 1
            # axes
            self.axesxs = []
            self.axesys = []
            # grid
            self.gridx = [None, None, None]  # min max step
            self.gridy = [None, None, None]  # min max step
            self.gridLineType = Qt.DotLine
            self.gridLineWidth = 1
            self.gridColor = Qt.gray

        self.data["axesxObjs"] = []  # [x1,x2,x3]
        self.data["axesyObjs"] = []  # [y1,y2,y3]
        self.data["curves"] = {}  # {'default':(x1,y1),(x2,y2)}

    @staticmethod
    def open(file):
        with open(file, 'rb') as f:
            data = dill.load(f)
        return data

    def save(self, file):
        with open(file, 'wb') as f:
            dill.dump(self, f)
