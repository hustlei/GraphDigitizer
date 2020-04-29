#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""GraphDigitGraphicsView, core widget for app

display, operate graph axes and curves on scene of GraphDigitGraphicsView.
operate digited data.

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""

import os

import numpy as np
from PyQt5.QtCore import pyqtSignal, QRectF, QPoint, QPointF, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPainter, QIcon, QPen, QPixmap
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem, QGraphicsLineItem,
                             QInputDialog, QLineEdit)

from core.enums import OpMode, PointType, RandItem
from core.graphicsItems import QGraphicsPointItem, QGraphicsAxesItem
from core.project import Digi
from core.utils import nextName
from core.utils.algor import *


class GraphDigitGraphicsView(QGraphicsView):
    sigMouseMovePoint = pyqtSignal(QPoint, QPointF)

    # 自定义信号sigMouseMovePoint，当鼠标移动时，在mouseMoveEvent事件中，将当前的鼠标位置发送出去
    # QPoint--传递的是view坐标
    def __init__(self, parent=None):
        super(GraphDigitGraphicsView, self).__init__(parent)
        # scene
        rect = QRectF(0, 0, 800, 600)
        self.scene = QGraphicsScene(rect)  # 创建场景 参数：场景区域
        self.setScene(self.scene)  # 给视图窗口设置场景
        # image
        self.graphicsPixmapItem = QGraphicsPixmapItem()  # chart image
        self.scene.addItem(self.graphicsPixmapItem)
        # setAntialias
        self.setRenderHint(QPainter.Antialiasing)
        # image object stored in project data
        # item objects storage
        self.axesxObjs = []
        self.axesyObjs = []
        self.gridObjs = []
        self.curveObjs = {}
        self.pointObjs = {}
        # axis coord stored in project data
        # grid setting stored in project data
        # grid position
        self.gridxpos = []
        self.gridypos = []
        # axes curve and point datamodel
        self.axesxModel = QStandardItemModel()
        self.axesyModel = QStandardItemModel()
        self.curveModel = QStandardItemModel()
        self.pointsModel = QStandardItemModel()

        self.curveModel.setHorizontalHeaderLabels(["current", "name", "visible"])
        self.pointsModel.setHorizontalHeaderLabels(["order", "x", "y"])
        self.axesxModel.setHorizontalHeaderLabels(["position", "x"])
        self.axesyModel.setHorizontalHeaderLabels(["position", "y"])

        ###
        self.xNo = 0
        self.yNo = 0

        ###
        self.mode = OpMode.default
        # data manage
        self.proj = Digi()

        # init
        self.currentCurve = None
        self.pointsModel.itemChanged.connect(self.changePointOrder)

        # state
        self.modified = False
        self._lastCurve = None

    def load(self, proj):
        # image # only for load
        self.setGraphImage(proj.img)
        self.scaleGraphImage(proj.imgScale)
        # axes
        for x in proj.data["axesxObjs"]:
            item = QGraphicsAxesItem(x, self.scene.sceneRect().y(), x,
                                     self.scene.sceneRect().y() + self.scene.sceneRect().height())
            item.Axis = "x"
            item.setPen(QPen(Qt.red, 1, Qt.DashLine))
            self.scene.addItem(item)
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)
            self.axesxObjs.append(item)
            self.xNo += 1
            self.axesxModel.appendRow([QStandardItem("x{}".format(self.xNo)), QStandardItem(str(x))])
        for y in proj.data["axesyObjs"]:
            item = QGraphicsAxesItem(self.scene.sceneRect().x(), y,
                                     self.scene.sceneRect().x() + self.scene.sceneRect().width(), y)
            item.Axis = "y"
            item.setPen(QPen(Qt.red, 1, Qt.DashLine))
            self.scene.addItem(item)
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)
            self.axesyObjs.append(item)
            self.yNo += 1
            self.axesyModel.appendRow([QStandardItem("y{}".format(self.yNo)), QStandardItem(str(y))])
        # curve
        for curve in proj.data["curves"]:
            self.pointObjs[curve] = []
            self.addCurveToTable(curve)
            clr = RandItem.nextColor()
            for x, y in proj.data["curves"][curve]:
                ptitem = QGraphicsPointItem()
                ptitem.pointColor = clr
                ptitem.linewidth = 1
                ptitem.setPos(x, y)
                ptitem.parentCurve = curve
                ptitem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable
                                | QGraphicsItem.ItemIsMovable)
                i = self.newPointIndex(ptitem)
                self.pointObjs[self.currentCurve].insert(i, ptitem)
                self.scene.addItem(ptitem)
        self.updateCurve(curve)
        # grid
        self.calGridCoord()
        self.updateGrid()

    def resetview(self):
        self.xNo, self.yNo = 0, 0
        self.setGraphImage(None)
        for obj in self.axesxObjs:
            self.scene.removeItem(obj)
        self.axesxObjs = []
        for obj in self.axesyObjs:
            self.scene.removeItem(obj)
        self.axesyObjs = []
        for obj in self.gridObjs:
            self.scene.removeItem(obj)
        self.gridObjs = []
        for curve in self.curveObjs:
            for obj in self.curveObjs[curve]:
                self.scene.removeItem(obj)
        self.curveObjs = {}
        for curve in self.pointObjs:
            for obj in self.pointObjs[curve]:
                self.scene.removeItem(obj)
        self.pointObjs = {}
        self.axesxModel.clear()
        self.axesyModel.clear()
        self.curveModel.clear()
        self.pointsModel.clear()

    def dump(self):
        proj = self.proj
        # axes
        for item in self.axesxObjs:
            proj.data["axesxObjs"].append((item.line().x1()))
        for item in self.axesyObjs:
            proj.data["axesyObjs"].append((item.line().y1()))
        # curve
        for curve in self.pointObjs:
            proj.data["curves"][curve] = []
            for item in self.pointObjs[curve]:
                proj.data["curves"][curve].append((item.x(), item.y()))

    def setGraphImage(self, imgfile):
        if not isinstance(imgfile, str):
            self.graphicsPixmapItem.setPixmap(QPixmap())
        elif os.path.exists(imgfile):
            self.proj.img = imgfile
            img = QPixmap(imgfile)
            self.graphicsPixmapItem.setPixmap(img)
            self.scene.setSceneRect(0, 0, img.width(), img.height())
            self.scene.clearSelection()  # 【清除选择】
            return True
        else:
            return False

    def scaleGraphImage(self, scale=1):
        if scale and scale > 0:
            self.proj.imgScale = scale
        self.graphicsPixmapItem.setScale(scale)
        if self.graphicsPixmapItem.pixmap().width() > 0 and self.graphicsPixmapItem.pixmap().height() > 0:
            self.scene.setSceneRect(0, 0, self.graphicsPixmapItem.pixmap().width() * scale,
                                    self.graphicsPixmapItem.pixmap().height() * scale)
        self.scene.clearSelection()  # 【清除选择】

    def addCurveToTable(self, name=None):
        if not name:
            name = nextName(self.currentCurve)
        while (name in self.curveObjs):
            name = nextName(name)
        self.curveObjs[name] = []
        self.pointObjs[name] = []
        item1 = IconItem()
        item2 = QStandardItem(name)
        item3 = QStandardItem()
        item1.setEditable(False)
        item3.setCheckable(True)
        item3.setAutoTristate(False)
        item3.setEditable(False)
        self.curveModel.appendRow([item1, item2, item3])
        self.changeCurrentCurve(name)

    def renameCurve(self, newname=None, name=None):
        if name not in self.curveObjs:
            name = self.currentCurve
        if not newname:
            newname, okPressed = QInputDialog.getText(self, self.tr("change curve name"),
                                                      self.tr("Curve to be renamed:{}".format(name)), QLineEdit.Normal,
                                                      name)
        if okPressed and newname != '':
            if newname != name:
                self.curveObjs[newname] = self.curveObjs.pop(name)
                self.pointObjs[newname] = self.pointObjs.pop(name)
                for i in range(self.curveModel.rowCount()):
                    item = self.curveModel.item(i, 1)
                    if item.text() == name:
                        item.setText(newname)

    def mouseMoveEvent(self, evt):
        pt = evt.pos()  # 获取鼠标坐标--view坐标
        self.sigMouseMovePoint.emit(pt, self.mapToScene(pt))  # 发送鼠标位置
        QGraphicsView.mouseMoveEvent(self, evt)
        item = self.scene.focusItem()
        if item:
            if isinstance(item, QGraphicsPointItem) and item.parentCurve:
                self.changeCurrentCurve(item.parentCurve)

            elif isinstance(item, QGraphicsAxesItem):
                if item.Axis == "x":
                    x = item.line().x1()
                    item.setLine(x, self.scene.sceneRect().y(), x,
                                 self.scene.sceneRect().y() + self.scene.sceneRect().height())
                elif item.Axis == "y":
                    y = item.line().y1()
                    item.setLine(self.scene.sceneRect().x(), y,
                                 self.scene.sceneRect().x() + self.scene.sceneRect().width(),y)

        # self.updateCurve(self.currentCurve)
        # self.repaint()
        # self.setDragMode(QGraphicsView.NoDrag) #(RubberBandDrag) #ScrollHandDrag) #NoDrag)
        # if self.mode is OpMode.axesx:
        #     self.updateAxis("x")
        # if self.mode is OpMode.axesy:
        #     self.updateAxis("y")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.__pressPt = event.pos()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        ptscene = self.mapToScene(event.pos())
        # item = self.scene.itemAt(ptscene, self.transform())
        clicked = True if event.pos() == self.__pressPt else False
        if self.mode is OpMode.select:
            pass
            # super().mousePressEvent(event)
        elif self.mode is OpMode.axesx and clicked:
            item = QGraphicsAxesItem(ptscene.x(),
                                     self.scene.sceneRect().y(), ptscene.x(),
                                     self.scene.sceneRect().y() + self.scene.sceneRect().height())
            item.Axis = "x"
            item.setPen(QPen(Qt.red, 1, Qt.DashLine))
            self.scene.addItem(item)
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)

            x, okPressed = QInputDialog.getDouble(self, self.tr("set x coordiniate"),
                                                  self.tr("set the x coord for axis"))
            if okPressed and x not in self.proj.axesxs:
                self.proj.axesxs.append(x)
                self.axesxObjs.append(item)
                self.xNo += 1
                self.axesxModel.appendRow([QStandardItem("x{}".format(self.xNo)), QStandardItem(str(x))])
                self.calGridCoord("x")
                self.updateGrid()
                item.setSelected(True)
            else:
                self.scene.removeItem(item)
        elif self.mode is OpMode.axesy and clicked:
            item = QGraphicsAxesItem(self.scene.sceneRect().x(), ptscene.y(),
                                     self.scene.sceneRect().x() + self.scene.sceneRect().width(), ptscene.y())
            item.Axis = "y"
            item.setPen(QPen(Qt.red, 1, Qt.DashLine))
            self.scene.addItem(item)
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)

            y, okPressed = QInputDialog.getDouble(self, self.tr("set y coordiniate"),
                                                  self.tr("set the y coord for axis"))
            if okPressed and y not in self.proj.axesys:
                self.axesyObjs.append(item)
                self.proj.axesys.append(y)
                self.calGridCoord("y")
                self.updateGrid()
                self.axesyModel.appendRow([QStandardItem("y{}".format(self.yNo)), QStandardItem(str(y))])
                item.setSelected(True)
            else:
                self.scene.removeItem(item)
        elif self.mode is OpMode.curve and clicked:
            self.sigMouseMovePoint.emit(event.pos(), ptscene)
            if len(self.curveObjs) == 0:
                self.addCurveToTable('curve1')
            ptitem = QGraphicsPointItem()
            ptitem.pointColor = Qt.blue
            ptitem.linewidth = 1
            ptitem.setPos(ptscene)
            ptitem.parentCurve = self.currentCurve
            ptitem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable
                            | QGraphicsItem.ItemIsMovable)

            if self.currentCurve not in self.pointObjs:
                self.pointObjs[self.currentCurve] = []

            i = self.newPointIndex(ptitem)
            self.pointObjs[self.currentCurve].insert(i, ptitem)
            self.updateCurve(self.currentCurve, Qt.red)
            self.scene.addItem(ptitem)
            ptitem.setSelected(True)

            # item1=QGraphicsRectItem(rect)  #创建矩形---以场景为坐标
            # item1.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)  #给图元设置标志
            # QGraphicsItem.ItemIsSelectable---可选择
            # QGraphicsItem.ItemIsFocusable---可设置焦点
            # QGraphicsItem.ItemIsMovable---可移动
            # QGraphicsItem.ItemIsPanel---
            # self.scene.addItem(item1)  #给场景添加图元

    def newPointIndex(self, ptitem):
        """get the nearest position for new point
        return the predicted new index for new point in pointObj
        """
        l = len(self.pointObjs[self.currentCurve])
        if l == 0:
            return 0
        if l == 1:
            return 1
        index = 0

        p = (ptitem.x(), ptitem.y())
        p1 = (self.pointObjs[self.currentCurve][0].x(), self.pointObjs[self.currentCurve][0].y())
        p2 = (self.pointObjs[self.currentCurve][1].x(), self.pointObjs[self.currentCurve][1].y())
        mindist = distToLine(p, p1, p2)
        for i in range(1, l - 1):
            p1 = p2
            p2 = (self.pointObjs[self.currentCurve][i + 1].x(), self.pointObjs[self.currentCurve][i + 1].y())
            dist = distToLine(p, p1, p2)
            pos = perpendOnLine(p, p1, p2)
            if pos == 0:
                if dist < mindist:
                    mindist = dist
                    index = i
        if index == 0:
            p1 = (self.pointObjs[self.currentCurve][0].x(), self.pointObjs[self.currentCurve][0].y())
            p2 = (self.pointObjs[self.currentCurve][1].x(), self.pointObjs[self.currentCurve][1].y())
            pos = perpendOnLine(p, p1, p2)
            dist = distToLine(p, p1, p2)
            length = distToPoint(p1, p2)
            if pos == 0 and dist < length / 4:
                return 1
            pstart = (self.pointObjs[self.currentCurve][0].x(), self.pointObjs[self.currentCurve][0].y())
            pend = (self.pointObjs[self.currentCurve][-1].x(), self.pointObjs[self.currentCurve][-1].y())
            d0 = distToPoint(p, pstart)
            d1 = distToPoint(p, pend)
            if pos == -1 and d0 < d1:
                return 0
            return l
        else:
            p1 = (self.pointObjs[self.currentCurve][index].x(), self.pointObjs[self.currentCurve][index].y())
            p2 = (self.pointObjs[self.currentCurve][index + 1].x(), self.pointObjs[self.currentCurve][index + 1].y())
            dist = distToLine(p, p1, p2)
            lenth = distToPoint(p1, p2)
            if dist < lenth / 2:
                return index + 1
        return l

    def deleteItem(self, item):
        """delete point on curve or axis object"""
        curvechange = None
        if isinstance(item, QGraphicsPointItem):
            for curvename, pointitems in self.pointObjs.items():
                for ptitem in pointitems:
                    if ptitem is item:
                        curvechange = curvename
                        pointitems.remove(ptitem)
                        self.scene.removeItem(item)
                        break
        if curvechange:
            self.updateCurve(curvechange)


        if isinstance(item, QGraphicsAxesItem):
            for i, line in enumerate(self.axesxObjs):
                if line is item:
                    self.axesxModel.removeRow(i)
                    self.proj.axesxs.pop(i)
                    self.axesxObjs.remove(line)
                    self.scene.removeItem(line)
            for i, line in enumerate(self.axesyObjs):
                if line is item:
                    self.axesyModel.removeRow(i)
                    self.proj.axesys.pop(i)
                    self.axesyObjs.remove(line)
                    self.scene.removeItem(line)

    def deleteSelectedItem(self):
        pointitems = self.scene.selectedItems()
        if len(pointitems) == 1:
            self.deleteItem(pointitems[0])

    def updateCurve(self, name, color=Qt.black):
        # if name in self.curveObjs:
        #     curveitem = self.curveObjs[name]
        # else:
        #     curveitem = QGraphicsPathItem()
        #     self.scene.addItem(curveitem)
        # # path=curveitem.path()
        # path = QPainterPath()
        #
        # pointItems = self.curvePointObjs[name]
        # if len(pointItems) > 0:
        #     path.moveTo(pointItems[0].pos())
        # for pointitem in pointItems[1:]:
        #     path.lineTo(pointitem.pos())
        # curveitem.setPath(path)
        # curveitem.update(curveitem.boundingRect())
        # curveitem.prepareGeometryChange()
        # self.scene.update()
        # self.viewport().repaint()
        # self.viewport().update()

        if not isinstance(name, str):
            return

        curveitems = []
        if name in self.curveObjs:
            curveitems = self.curveObjs[name]
            if not isinstance(curveitems, list):
                curveitems = []
        lastitems = curveitems.copy()

        if name in self.pointObjs:
            pointItems = self.pointObjs[name]
        else:
            pointItems = []
        points = []
        for ptitem in pointItems:
            points.append(ptitem.pos())

        if len(points) > 1:
            for i in range(1, len(points)):
                l = QGraphicsLineItem(points[i - 1].x(), points[i - 1].y(), points[i].x(), points[i].y())
                l.setPen(color)
                # l.setFlag(QGraphicsItem.ItemIsSelectable)
                curveitems.append(l)
                self.scene.addItem(l)
        self.curveObjs[name] = curveitems

        for line in lastitems:
            self.scene.removeItem(line)

        self.updateCurvePoints(name)

    def showAxes(self, visible=True):
        if visible:
            for line in self.axesxObjs:
                line.setVisible(True)
            for line in self.axesyObjs:
                line.setVisible(True)
        else:
            for line in self.axesxObjs:
                line.setVisible(False)
            for line in self.axesyObjs:
                line.setVisible(False)

    def showGrid(self, visible=True):
        if visible:
            for line in self.gridObjs:
                line.setVisible(True)
        else:
            for line in self.gridObjs:
                line.setVisible(False)

    def calGridCoord(self, mode="all"):
        """calc the coord and pixel position of gridx list and gridy list"""
        if len(self.proj.axesxs) < 2 or len(self.proj.axesys) < 2:
            self.gridxpos, self.gridypos = [], []
            return

        if mode in ("x", "all"):
            axesxpos = []
            for o in self.axesxObjs:
                axesxpos.append(o.line().x1())
            xmin = min(self.proj.axesxs) if self.proj.gridx[0] is None else self.proj.gridx[0]
            xmax = max(self.proj.axesxs) if self.proj.gridx[1] is None else self.proj.gridx[1]
            if self.proj.gridx[2] is None:
                if len(self.axesxObjs) == 2:
                    xstep = (xmax - xmin) / 5
                else:
                    axesStep = abs(self.proj.axesxs[1] - self.proj.axesxs[0])
                    for i in range(2, len(self.proj.axesxs)):
                        st = abs(self.proj.axesxs[i] - self.proj.axesxs[i - 1])
                        if axesStep > st:
                            axesStep = st
                    xstep = axesStep
            else:
                xstep = self.proj.gridx[2]
            gridxcoord = list(np.arange(xmin, xmax, xstep)) + [xmax]
        else:
            gridxcoord = []

        if mode in ("y", "all"):
            axesy = []
            for o in self.axesyObjs:
                axesy.append(o.line().y1())
            ymin = min(self.proj.axesys) if self.proj.gridy[0] is None else self.proj.gridy[0]
            ymax = max(self.proj.axesys) if self.proj.gridy[1] is None else self.proj.gridy[1]
            if self.proj.gridy[2] is None:
                if len(self.axesyObjs) == 2:
                    ystep = (ymax - ymin) / 5
                else:
                    axesStep = self.proj.axesys[1] - self.proj.axesys[0]
                    for i in range(2, len(self.proj.axesys)):
                        st = self.proj.axesys[i] - self.proj.axesys[i - 1]
                        if axesStep > st:
                            axesStep = st
                    ystep = axesStep
            else:
                ystep = self.proj.gridy[2]
            gridycoord = list(np.arange(ymin, ymax, ystep)) + [ymax]
        else:
            gridycoord = []

        xpos, ypos = self.coordToPoint(gridxcoord, gridycoord)
        if mode in ["x", "all"]:
            self.gridxpos = xpos
        if mode in ["y", "all"]:
            self.gridypos = ypos
        return

    def updateGrid(self):
        for line in self.gridObjs:
            self.scene.removeItem(line)

        if self.gridxpos and self.gridypos:
            for x in self.gridxpos:
                line = QGraphicsLineItem(x, self.gridypos[0], x, self.gridypos[-1])
                line.setPen(QPen(self.proj.gridColor, self.proj.gridLineWidth, self.proj.gridLineType))
                self.gridObjs.append(line)
                self.scene.addItem(line)
            for y in self.gridypos:
                line = QGraphicsLineItem(self.gridxpos[0], y, self.gridxpos[-1], y)
                line.setPen(QPen(self.proj.gridColor, self.proj.gridLineWidth, self.proj.gridLineType))
                self.gridObjs.append(line)
                self.scene.addItem(line)

    def updateCurvePoints(self, name):
        extra = len(self.pointObjs[name]) - self.pointsModel.rowCount()
        if extra > 0:
            for i in range(extra):
                item1 = QStandardItem()
                item2 = QStandardItem()
                item3 = QStandardItem()
                item2.setEditable(False)
                item3.setEditable(False)
                self.pointsModel.appendRow([item1, item2, item3])
        elif extra < 0:
            j = self.pointsModel.rowCount()
            i = j + extra
            self.pointsModel.removeRows(i, -extra)

        for i in range(self.pointsModel.rowCount()):
            pt = self.pointObjs[name][i]
            self.pointsModel.item(i, 0).setText(str(i + 1))
            xlist, ylist = self.pointToCoord([pt.x()], [pt.y()])
            self.pointsModel.item(i, 1).setText(str(round(xlist[0], 6)))
            self.pointsModel.item(i, 2).setText(str(round(ylist[0], 6)))

    def calcCurveCoords(self):
        """calculate datas for export"""
        data = {}
        for curve in self.pointObjs:
            data[curve] = ([], [])
            for item in self.pointObjs[curve]:
                data[curve][0].append(item.x())
                data[curve][1].append(item.y())
            data[curve] = self.pointToCoord(data[curve][0], data[curve][1])
        return data

    def exportToCSVtext(self):
        """return text in csv format, like following:
        curve1
        x,1,2,3
        y,2,3,4
        """
        text = ""
        data = self.calcCurveCoords()
        for curve in data:
            text += curve
            text += "\nx,"
            for x in data[curve][0]:
                text += str(x) + ','
            text += "\ny,"
            for y in data[curve][1]:
                text += str(y) + ','
            text += "\n"
        return text

    def changeCurrentCurve(self, name=None):
        self._lastCurve = self.currentCurve
        if name is None:
            name = self.currentCurve
            if name is None:
                return
        for i in range(self.curveModel.rowCount()):
            if self.curveModel.item(i,1).text() == name:
                self.curveModel.item(i,0).switch(True)
            else:
                self.curveModel.item(i, 0).switch(False)

        self.currentCurve = name
        self.updateCurve(self._lastCurve)
        self.updateCurve(self.currentCurve, Qt.red)
        self.updateCurvePoints(name)

    def changePointOrder(self, item):
        row = item.row()
        if item.column() != 0:
            return
        newindex = item.text()
        if not newindex.isdigit():
            return
        newindex = int(newindex)
        if newindex == row + 1:
            return
        if newindex > self.pointsModel.rowCount():
            newindex = self.pointsModel.rowCount()
        newindex -= 1

        self.pointObjs[self.currentCurve].insert(newindex, self.pointObjs[self.currentCurve].pop(row))
        self.updateCurve(self.currentCurve)
        self.updateCurvePoints(self.currentCurve)

    # def curvetabChanged(self, item):
    #     i = item.row()
    #     j = item.column()
    #     if j == 0:
    #         if item.checkState() is Qt.Checked:
    #             self.curveModel.item(i,0).setCheckState(Qt.Checked)
    #             return
    #         else:
    #             for k in range(self.curveModel.rowCount()):
    #                 if k == i:
    #                     #self.curveModel.item(k,0).setCheckState(Qt.Checked)
    #                     newcurrent = self.curveModel.item(k,1).text()
    #                     print(self.curveModel.item(k,0).checkState())
    #                 else:
    #                     self.curveModel.item(k,0).setCheckState(Qt.Unchecked)
    #     if newcurrent and newcurrent != self.currentCurve:
    #         self.changeCurrentCurve(newcurrent)

    def pointToCoord(self, xlist, ylist):
        if len(self.proj.axesxs) < 2 or len(self.proj.axesys) < 2:
            return (xlist, ylist)

        gridxs = []
        for item in self.axesxObjs:
            gridxs.append(item.line().x1())
        coordx = self.proj.axesxs
        xCoords = interp(gridxs, coordx, xlist)

        gridys = []
        for item in self.axesyObjs:
            gridys.append(item.line().y1())
        coordy = self.proj.axesys
        yCoords = interp(gridys, coordy, ylist)

        return (xCoords, yCoords)

    def coordToPoint(self, xlist, ylist):
        if len(self.proj.axesxs) < 2 or len(self.proj.axesys) < 2:
            return (xlist, ylist)
        gridxs = []
        for item in self.axesxObjs:
            gridxs.append(item.line().x1())
        coordx = self.proj.axesxs
        gridys = []
        for item in self.axesyObjs:
            gridys.append(item.line().y1())
        coordy = self.proj.axesys
        xposs = interp(coordx, gridxs, xlist)
        yposs = interp(coordy, gridys, ylist)
        return (xposs, yposs)

        if len(self.proj.axesxs) < 2 or len(self.proj.axesys) < 2:
            return (xlist, ylist)
        pixx = self.proj.axesxs.keys()
        coordx = self.proj.axesxs.values()
        pixy = self.proj.axesys.keys()
        coordy = self.proj.axesys.values()
        xPixs = interp(coordx, pixx, xlist)
        yPixs = interp(coordy, pixy, ylist)
        return (xPixs, yPixs)


class IconItem(QStandardItem):
    """for current curve"""

    def __init__(self):
        super().__init__()
        self.setCheckable(False)
        self.setAutoTristate(False)
        # self.setFlags(Qt.NoItemFlags)
        self.iconon = QIcon(":appres.img/yes.png")
        self.iconoff = QIcon(":appres.img/none.png")
        self.isOn = False
        self.setIcon(self.iconoff)

    def switch(self, isOn):
        if self.isOn == isOn:
            return
        if isOn:
            # self.setText("●")
            self.setIcon(self.iconon)
        else:
            self.setIcon(self.iconoff)
        self.isOn = isOn
