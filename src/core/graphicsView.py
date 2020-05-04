#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""GraphDigitGraphicsView, core widget for app

display, operate graph axes and curves on scene of GraphDigitGraphicsView.
operate digited data.

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""

import os

import numpy as np
from PyQt5.QtCore import pyqtSignal, QRectF, QPoint, QPointF, Qt, QItemSelectionModel, QModelIndex, QItemSelection
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPainter, QIcon, QPen, QPixmap, QColor
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem, QGraphicsLineItem,
                             QInputDialog, QLineEdit)

from core.enums import OpMode, PointType, RandItem
from core.graphicsItems import QGraphicsPointItem, QGraphicsAxesItem
from core.project import Digi
from core.utils import nextName
from core.utils.algor import *


class GraphDigitGraphicsView(QGraphicsView):
    sigMouseMovePoint = pyqtSignal(QPoint, QPointF)
    sigModified = pyqtSignal(bool)

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
        self.axesxObjs = {}
        self.axesyObjs = {}
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
        self.axesxSelectModel = QItemSelectionModel(self.axesxModel)
        self.axesySelectModel = QItemSelectionModel(self.axesyModel)
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
        self.curveModel.itemChanged.connect(self.changeCurveVisible)
        self.scene.selectionChanged.connect(self.slotSceneSeletChanged)

        # state
        self._lastCurve = None

    def load(self, proj):
        # image # only for load
        self.setGraphImage(proj.img)
        self.scaleGraphImage(proj.imgScale)
        # axes
        xadded = []
        yadded = []
        for xpos, xcoord in proj.data["axesxObjs"].items():
            if xpos in xadded:
                continue
            else:
                xadded.append(xpos)
            item = QGraphicsAxesItem(0, self.scene.sceneRect().y(), 0,
                                     self.scene.sceneRect().y() + self.scene.sceneRect().height())
            item.setPos(xpos, 0)
            item.axis = "x"
            item.setPen(QPen(Qt.red, 1, Qt.DashLine))
            self.scene.addItem(item)
            self.axesxObjs[item] = xcoord
            labelitem = QStandardItem("x:{}".format(xpos))
            labelitem.setData(item)
            self.axesxModel.appendRow([labelitem, QStandardItem(str(xcoord))])
            self.xNo += 1
            self.axesxModel.setVerticalHeaderItem(self.axesxModel.rowCount() - 1, QStandardItem("x{}".format(self.xNo)))
        for ypos, ycoord in proj.data["axesyObjs"].items():
            if ypos in yadded:
                continue
            else:
                yadded.append(ypos)
            item = QGraphicsAxesItem(self.scene.sceneRect().x(), 0,
                                     self.scene.sceneRect().x() + self.scene.sceneRect().width(), 0)
            item.setPos(0, ypos)
            item.axis = "y"
            item.setPen(QPen(Qt.red, 1, Qt.DashLine))
            self.scene.addItem(item)
            self.axesyObjs[item] = ycoord
            labelitem = QStandardItem("y:{}".format(ypos))
            labelitem.setData(item)
            self.axesyModel.appendRow([labelitem, QStandardItem(str(ycoord))])
        # curve
        for curve in proj.data["curves"]:
            self.pointObjs[curve] = []
            self.addCurve(curve)
            clr = RandItem.nextColor()
            for x, y in proj.data["curves"][curve]:
                ptitem = QGraphicsPointItem()
                ptitem.pointColor = clr
                ptitem.linewidth = 1
                ptitem.setPos(x, y)
                ptitem.parentCurve = curve
                ptitem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable
                                | QGraphicsItem.ItemIsMovable)
                i = pointInsertPosition(ptitem, self.pointObjs[self.currentCurve])
                self.pointObjs[self.currentCurve].insert(i, ptitem)
                self.scene.addItem(ptitem)
            self.updateCurve(curve)
        # grid
        self.calGridCoord()
        self.updateGrid()
        self.sigModified.emit(True)
        self.mode = OpMode.select

    def resetview(self):
        self.setGraphImage(None)
        for obj in self.axesxObjs:
            self.scene.removeItem(obj)
        self.axesxObjs = {}
        for obj in self.axesyObjs:
            self.scene.removeItem(obj)
        self.axesyObjs = {}
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
        self.axesxSelectModel.clear()
        self.axesySelectModel.clear()
        self.curveModel.setHorizontalHeaderLabels(["current", "name", "visible"])
        self.pointsModel.setHorizontalHeaderLabels(["order", "x", "y"])
        self.axesxModel.setHorizontalHeaderLabels(["position", "x"])
        self.axesyModel.setHorizontalHeaderLabels(["position", "y"])

        self.xNo = 0
        self.yNo = 0

        ###
        self.mode = OpMode.default
        # data manage
        self.proj.resetData(True)
        # init
        self.currentCurve = None
        self._lastCurve = None

    def dump(self):
        proj = self.proj
        proj.data["axesxObjs"] = {}  # [x1,x2,x3]
        proj.data["axesyObjs"] = {}  # [y1,y2,y3]
        proj.data["curves"] = {}  # {'default':(x1,y1),(x2,y2)}
        # axes
        for item, xcoord in self.axesxObjs.items():
            proj.data["axesxObjs"][item.pos().x()] = xcoord
        for item, ycoord in self.axesyObjs.items():
            proj.data["axesyObjs"][item.pos().y()] = ycoord
        # curve
        for curve in self.pointObjs:
            proj.data["curves"][curve] = []
            for item in self.pointObjs[curve]:
                proj.data["curves"][curve].append((item.x(), item.y()))

    def mouseMoveEvent(self, evt):
        pt = evt.pos()  # 获取鼠标坐标--view坐标
        self.sigMouseMovePoint.emit(pt, self.mapToScene(pt))  # 发送鼠标位置
        QGraphicsView.mouseMoveEvent(self, evt)
        item = self.scene.focusItem()
        if item:
            if isinstance(item, QGraphicsPointItem) and item.parentCurve:
                self.changeCurrentCurve(item.parentCurve)
                self.sigModified.emit(True)
            elif isinstance(item, QGraphicsAxesItem):
                if item.axis == "x":
                    if self.mode != OpMode.axesx:
                        self.scene.clearSelection()
                        return
                    self.axesxSelectModel.clearSelection()
                    self.axesySelectModel.clearSelection()
                    for i in range(self.axesxModel.rowCount()):
                        if self.axesxModel.item(i, 0).data() is item:
                            parent = QModelIndex()
                            topleftindex = self.axesxModel.index(i, 0, parent)  # self.axesxModel.item(i,0).index()
                            rightbottomindex = self.axesxModel.index(i, 1, parent)
                            self.axesxSelectModel.select(QItemSelection(topleftindex, rightbottomindex),
                                                         QItemSelectionModel.Select)
                            self.axesxModel.item(i, 0).setText("x:{}".format(evt.pos().x()))
                            break

                    item.setLine(0, self.scene.sceneRect().y(), 0,
                                 self.scene.sceneRect().y() + self.scene.sceneRect().height())
                    item.setPos(self.mapToScene(evt.pos()).x(), 0)
                    self.sigModified.emit(True)
                    self.calGridCoord()
                    self.updateGrid()

                elif item.axis == "y":
                    if self.mode != OpMode.axesy:
                        self.scene.clearSelection()
                        return
                    self.axesxSelectModel.clearSelection()
                    self.axesySelectModel.clearSelection()
                    for i in range(self.axesyModel.rowCount()):
                        if self.axesyModel.item(i, 0).data() is item:
                            topleftindex = self.axesyModel.index(i, 0)  # self.axesxModel.item(i,0).index()
                            rightbottomindex = self.axesyModel.index(i, 1)
                            self.axesySelectModel.select(QItemSelection(topleftindex, rightbottomindex),
                                                         QItemSelectionModel.Select)
                            self.axesyModel.item(i, 0).setText("y:{}".format(evt.pos().y()))
                            break

                    item.setLine(self.scene.sceneRect().x(), 0,
                                 self.scene.sceneRect().x() + self.scene.sceneRect().width(), 0)
                    item.setPos(0, self.mapToScene(evt.pos()).y())
                    self.sigModified.emit(True)
                    self.calGridCoord()
                    self.updateGrid()

        # self.updateCurve(self.currentCurve)
        # self.repaint()
        # self.setDragMode(QGraphicsView.NoDrag) #(RubberBandDrag) #ScrollHandDrag) #NoDrag)

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
            self.axesxSelectModel.clear()
            self.axesySelectModel.clear()
            for axisitem in self.axesxObjs:
                if ptscene.x() == axisitem.pos().x():
                    return
            item = QGraphicsAxesItem(0, self.scene.sceneRect().y(), 0,
                                     self.scene.sceneRect().y() + self.scene.sceneRect().height())
            item.setPos(ptscene.x(), 0)
            item.axis = "x"
            item.setPen(QPen(Qt.red, 1, Qt.DashLine))
            self.scene.addItem(item)
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)

            xs = list(self.axesxObjs.values())
            if not self.axesxObjs:
                nextx = 0
            elif len(self.axesxObjs) == 1:
                nextx = xs[0] + 0.1
            else:
                nextx = 2 * xs[-1] - xs[-2]
            x, okPressed = QInputDialog.getDouble(self, self.tr("set x coordiniate"),
                                                  self.tr("set the x coord for axis"), nextx, decimals=3)
            if okPressed and x not in self.axesxObjs.values():
                self.axesxObjs[item] = x
                labelItem = QStandardItem("x:{}".format(item.pos().x()))
                labelItem.setData(item)
                self.axesxModel.appendRow([labelItem, QStandardItem(str(x))])
                self.calGridCoord("x")
                self.updateGrid()
                # item.setSelected(True)
                for i in range(self.axesxModel.rowCount()):
                    if self.axesxModel.item(i, 0).data() is item:
                        topleftindex = self.axesxModel.index(i, 0)  # self.axesxModel.item(i,0).index()
                        rightbottomindex = self.axesxModel.index(i, 1)
                        self.axesxSelectModel.select(QItemSelection(topleftindex, rightbottomindex),
                                                     QItemSelectionModel.Select)
                        break
                self.sigModified.emit(True)
                self.scene.clearSelection()
            else:
                self.scene.removeItem(item)
        elif self.mode is OpMode.axesy and clicked:
            self.axesxSelectModel.clear()
            self.axesySelectModel.clear()
            for axisitem in self.axesxObjs:
                if ptscene.y() == axisitem.pos().y():
                    return
            item = QGraphicsAxesItem(self.scene.sceneRect().x(), 0,
                                     self.scene.sceneRect().x() + self.scene.sceneRect().width(), 0)
            item.setPos(0, ptscene.y())
            item.axis = "y"
            item.setPen(QPen(Qt.red, 1, Qt.DashLine))
            self.scene.addItem(item)
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)

            ys = list(self.axesyObjs.values())
            if not self.axesyObjs:
                nexty = 0
            elif len(self.axesyObjs) == 1:
                nexty = ys[0] + 0.1
            else:
                nexty = 2 * ys[-1] - ys[-2]
            y, okPressed = QInputDialog.getDouble(self, self.tr("set y coordiniate"),
                                                  self.tr("set the y coord for axis"), nexty, decimals=3)
            if okPressed and y not in self.axesyObjs.values():
                self.axesyObjs[item] = y
                labelItem = QStandardItem("y:{}".format(item.pos().y()))
                labelItem.setData(item)
                self.axesyModel.appendRow([labelItem, QStandardItem(str(y))])
                self.calGridCoord("y")
                self.updateGrid()
                # item.setSelected(True)

                for i in range(self.axesyModel.rowCount()):
                    if self.axesyModel.item(i, 0).data() is item:
                        topleftindex = self.axesyModel.index(i, 0)  # self.axesxModel.item(i,0).index()
                        rightbottomindex = self.axesyModel.index(i, 1)
                        self.axesySelectModel.select(QItemSelection(topleftindex, rightbottomindex),
                                                     QItemSelectionModel.Select)
                        break
                self.sigModified.emit(True)
            else:
                self.scene.removeItem(item)
        elif self.mode is OpMode.curve and clicked:
            self.sigMouseMovePoint.emit(event.pos(), ptscene)
            if len(self.curveObjs) == 0:
                self.addCurve('curve1')
            if self.currentCurve not in self.pointObjs:
                self.pointObjs[self.currentCurve] = []

            ptitem = QGraphicsPointItem()
            ptitem.pointColor = Qt.blue
            ptitem.linewidth = 1
            ptitem.setPos(ptscene)
            ptitem.parentCurve = self.currentCurve
            # ptitem.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable
            #                 | QGraphicsItem.ItemIsMovable)
            self.scene.addItem(ptitem)

            i = pointInsertPosition(ptitem, self.pointObjs[self.currentCurve])
            self.pointObjs[self.currentCurve].insert(i, ptitem)
            self.updateCurve(self.currentCurve, Qt.red)
            self.sigModified.emit(True)
            ptitem.setSelected(True)

            # item1=QGraphicsRectItem(rect)  #创建矩形---以场景为坐标
            # item1.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)  #给图元设置标志
            # QGraphicsItem.ItemIsSelectable---可选择
            # QGraphicsItem.ItemIsFocusable---可设置焦点
            # QGraphicsItem.ItemIsMovable---可移动
            # QGraphicsItem.ItemIsPanel---
            # self.scene.addItem(item1)  #给场景添加图元

    def slotSceneSeletChanged(self):
        items = self.scene.selectedItems()
        if len(items) != 1:  # ony allow select one item
            self.scene.clearSelection()
            return
        # item = items[0]

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
                        self.sigModified.emit(True)
                        break
        if curvechange:
            self.updateCurve(curvechange)

        if isinstance(item, QGraphicsAxesItem):
            if item.axis == "x":
                for line in self.axesxObjs:
                    if line is item:
                        for i in range(self.axesxModel.rowCount()):
                            if self.axesxModel.item(i,
                                                    0).data() is item:  # float(self.axesxModel.item(i, 0).text().strip("x:")) == line.pos().x():
                                self.axesxModel.removeRow(i)
                                break
                        self.axesxObjs.pop(line)
                        self.scene.removeItem(line)
                        self.sigModified.emit(True)
                        break
            elif item.axis == "y":
                for line in self.axesyObjs:
                    if line is item:
                        for i in range(self.axesyModel.rowCount()):
                            if float(self.axesyModel.item(i, 0).text().strip("y:")) == line.pos().y():
                                self.axesyModel.removeRow(i)
                                break
                        self.axesyObjs.pop(line)
                        self.scene.removeItem(line)
                        self.sigModified.emit(True)
                        break
            self.calGridCoord()
            self.updateGrid()

    def deleteSelectedItem(self):
        pointitems = self.scene.selectedItems()
        if len(pointitems) == 1:
            self.deleteItem(pointitems[0])

    def setGraphImage(self, imgfile):
        if not isinstance(imgfile, str):
            self.graphicsPixmapItem.setPixmap(QPixmap())
        elif os.path.exists(imgfile):
            self.proj.img = imgfile
            img = QPixmap(imgfile)
            self.graphicsPixmapItem.setPixmap(img)
            self.scene.setSceneRect(0, 0, img.width(), img.height())
            self.scene.clearSelection()  # 【清除选择】
            self.sigModified.emit(True)
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
        self.sigModified.emit(True)

    def addCurve(self, name=None):
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
        item3.setCheckState(Qt.Checked)
        self.curveModel.appendRow([item1, item2, item3])
        self.changeCurrentCurve(name)
        self.sigModified.emit(True)

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
                        self.sigModified.emit(True)

    def showCurve(self, curvename, visible=True):
        for pts in self.pointObjs[curvename]:
            pts.setVisible(visible)
        for line in self.curveObjs[curvename]:
            line.setVisible(visible)

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

        lastitems = []
        if name in self.curveObjs:
            lastitems = self.curveObjs[name]
            if not isinstance(lastitems, list):
                lastitems = []

        if name in self.pointObjs:
            pointItems = self.pointObjs[name]
        else:
            pointItems = []
        points = []
        for ptitem in pointItems:
            points.append(ptitem.pos())

        self.curveObjs[name] = []
        if len(points) > 1:
            for i in range(1, len(points)):
                l = QGraphicsLineItem(points[i - 1].x(), points[i - 1].y(), points[i].x(), points[i].y())
                l.setPen(color)
                l.setZValue(10)
                # l.setFlag(QGraphicsItem.ItemIsSelectable)
                self.curveObjs[name].append(l)
                self.scene.addItem(l)

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

        if mode in ("x", "all") and len(self.axesxObjs) >= 2:
            axesxcoord = list(self.axesxObjs.values())
            xmin = min(axesxcoord) if self.proj.gridx[0] is None else min(self.proj.gridx[0], min(axesxcoord))
            xmax = max(axesxcoord) if self.proj.gridx[1] is None else max(self.proj.gridx[1], max(axesxcoord))
            if self.proj.gridx[2] is None:
                if len(self.axesxObjs) == 2:
                    xstep = (xmax - xmin) / 5
                else:
                    axesStep = round(abs(axesxcoord[1] - axesxcoord[0]), 5)
                    for i in range(2, len(axesxcoord)):
                        st = round(abs(axesxcoord[i] - axesxcoord[i - 1]), 5)
                        if axesStep > st:
                            axesStep = st
                    xstep = axesStep
            else:
                xstep = self.proj.gridx[2]
            n = int(round((xmax - xmin) / xstep, 0)) + 1
            gridxcoord = list(np.linspace(xmin, xmax, n))
        else:
            gridxcoord = []

        if mode in ("y", "all") and len(self.axesyObjs) >= 2:
            axesycoord = list(self.axesyObjs.values())
            ymin = min(axesycoord) if self.proj.gridy[0] is None else min(self.proj.gridy[0], min(axesycoord))
            ymax = max(axesycoord) if self.proj.gridy[1] is None else max(self.proj.gridy[1], max(axesycoord))
            if self.proj.gridy[2] is None:
                if len(self.axesyObjs) == 2:
                    ystep = (ymax - ymin) / 5
                else:
                    axesStep = round(abs(axesycoord[1] - axesycoord[0]), 5)
                    for i in range(2, len(axesycoord)):
                        st = round(axesycoord[i] - axesycoord[i - 1], 5)
                        if axesStep > st:
                            axesStep = st
                    ystep = axesStep
            else:
                ystep = self.proj.gridy[2]

            n = int(round((ymax - ymin) / ystep, 0)) + 1
            gridycoord = list(np.linspace(ymin, ymax, n))
            # gridycoord = list(np.arange(ymin, ymax, ystep)) + [ymax]
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
            clr = QColor(self.proj.gridColor)
            clr.setAlphaF(self.proj.gridOpacity)
            for x in self.gridxpos:
                line = QGraphicsLineItem(x, self.gridypos[0], x, self.gridypos[-1])
                line.setZValue(5)
                line.setPen(QPen(clr, self.proj.gridLineWidth, self.proj.gridLineType))
                self.gridObjs.append(line)
                self.scene.addItem(line)
            for y in self.gridypos:
                line = QGraphicsLineItem(self.gridxpos[0], y, self.gridxpos[-1], y)
                line.setZValue(5)
                line.setPen(QPen(clr, self.proj.gridLineWidth, self.proj.gridLineType))
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

    def axisvalid(self):
        """if there are axes with same coord value,
        or if there are axes at the save position,
        return False"""
        a = len(self.axesxObjs)
        b = len(set(self.axesxObjs.values()))
        if a != b:
            return False
        a = len(self.axesyObjs)
        b = len(set(self.axesyObjs.values()))
        if a != b:
            return False
        xs = []
        for item in self.axesxObjs:
            xs.append(item.pos().x())
        ys = []
        for item in self.axesyObjs:
            ys.append(item.pos().y())
        a = len(xs)
        b = len(set(xs))
        if a != b:
            return False
        a = len(ys)
        b = len(set(ys))
        if a != b:
            return False

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
            if self.curveModel.item(i, 1).text() == name:
                self.curveModel.item(i, 0).switch(True)
            else:
                self.curveModel.item(i, 0).switch(False)

        self.currentCurve = name
        self.updateCurve(self._lastCurve)
        self.updateCurve(self.currentCurve, Qt.red)
        self.updateCurvePoints(name)

    def changeCurveVisible(self, item):
        if item.index().column() == 2:
            visible = item.checkState()
            curvename = self.curveModel.item(item.index().row(), 1).text()
            self.showCurve(curvename, visible)

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
        if len(self.axesxObjs) >= 2:
            gridxs = []
            for item in self.axesxObjs:
                gridxs.append(item.pos().x())
            coordx = list(self.axesxObjs.values())
            xCoords = interp(gridxs, coordx, xlist)
        else:
            xCoords = xlist

        if len(self.axesyObjs) >= 2:
            gridys = []
            for item in self.axesyObjs:
                gridys.append(item.pos().y())
            coordy = list(self.axesyObjs.values())
            yCoords = interp(gridys, coordy, ylist)
        else:
            yCoords = ylist

        return (xCoords, yCoords)

    def coordToPoint(self, xlist, ylist):
        if len(self.axesxObjs) >= 2:
            gridxpos = []
            for item in self.axesxObjs:
                gridxpos.append(item.pos().x())
            coordx = list(self.axesxObjs.values())
            xposs = interp(coordx, gridxpos, xlist)
        else:
            xposs = xlist

        if len(self.axesyObjs) >= 2:
            gridypos = []
            for item in self.axesyObjs:
                gridypos.append(item.pos().y())
            coordy = list(self.axesyObjs.values())
            yposs = interp(coordy, gridypos, ylist)
        else:
            yposs = ylist

        return (xposs, yposs)


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
