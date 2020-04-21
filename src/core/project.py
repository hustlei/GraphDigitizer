#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Data for project of the app

including all data when save project to file.

Copyright (c) 2019 lileilei <hustlei@sina.cn>
"""

import os
import dill
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from .enums import PointType

class Curve():
    def __init__(self, name):
        self.name = name
        self.sceneCoords = [] # x,y coords on GraphicsScenes
        self.digitCoords = [] # digitized points cooords
        self.pointType = PointType.cross
        self.pointColor = Qt.blue

class Datas():
    def __init__(self, imgpath=""):
        self.img = None
        self.imgScale = 1
        self.imgOriginSize = None
        self.imgSize = None
        self.axisx = {0:0,1:1}
        self.axisy = {0:0,1:1}
        self.curves = {"default": Curve("default")}

        self.setImgpath(imgpath)

    def setImgpath(self, imgpath):
        if imgpath:
            if os.path.exists(imgpath):
                self.img = QPixmap(imgpath)
                self.imgOriginSize = self.img.size()
                self.scaleImg()

    def scaleImg(self, imgScale=None):
        if imgScale and imgScale>0:
            self.imgScale = imgScale
        self.imgSize = self.imgOriginSize*self.imgScale
        self.img = self.img.scaled(self.imgSize, aspectRatioMode=Qt.KeepAspectRatio) #按比例缩放：


    @staticmethod
    def open(file):
        with open(file, 'rb') as f:
            data = dill.load(f)
        return data

    def save(self,file):
        with open(file, 'wb') as f:
            dill.dump(self, f)
