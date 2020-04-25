import os

from PyQt5.QtCore import pyqtSignal, QRectF, QPoint, QPointF, Qt
from PyQt5.QtGui import QCursor, QPainterPath, QStandardItemModel, QStandardItem, QPainter, QIcon
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem,
                             QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsLineItem, QInputDialog, QLineEdit,
                             QMessageBox)
from core.enums import OpMode, PointType
from core.graphicsItems import QGraphicsPointItem
from core.project import ProjData
from core.dialogs.pick import Axesdialog
from core.utils import nextName


class GraphDigitGraphicsView(QGraphicsView):
    sigMouseMovePoint = pyqtSignal(QPoint, QPointF)

    # 自定义信号sigMouseMovePoint，当鼠标移动时，在mouseMoveEvent事件中，将当前的鼠标位置发送出去
    # QPoint--传递的是view坐标
    def __init__(self, parent=None):
        super(GraphDigitGraphicsView, self).__init__(parent)
        self.initView()
        self.setRenderHint(QPainter.Antialiasing)
        # item objects storage
        self.axesPts = []
        self.gridLines = {}
        self.curveObjs = {}
        self.curvePointObjs = {}
        # axes curve and point datamodel
        self.axesModel = QStandardItemModel()
        self.curveModel = QStandardItemModel()
        self.pointsModel = QStandardItemModel()

        self.axesModel.setHorizontalHeaderLabels(["position", "x", "y"])
        self.curveModel.setHorizontalHeaderLabels(["current", "name", "visible"])
        self.pointsModel.setHorizontalHeaderLabels(["order", "x", "y"])

        ###
        self.mode = OpMode.default
        # data manage
        self.datas = ProjData()

        # init
        self.currentCurve = 'default'
        self.addCurve('default')

    def initView(self):
        # scene
        rect = QRectF(0, 0, 800, 600)
        self.scene = QGraphicsScene(rect)  # 创建场景 参数：场景区域
        self.setScene(self.scene)  # 给视图窗口设置场景
        # image
        self.graphicsPixmapItem = QGraphicsPixmapItem()  # chart image
        self.scene.addItem(self.graphicsPixmapItem)

        # test

        # for pos,color in zip([rect.left(),0,rect.right()],[Qt.red,Qt.yellow,Qt.blue]):
        #     item=QGraphicsEllipseItem(-50,-50,100,100)  #创建椭圆--场景坐标
        #     #参数1 参数2  矩形左上角坐标
        #     #参数3 参数4 矩形的宽和高
        #     item.setPos(pos,0)  #给图元设置在场景中的坐标(移动图元)--图元中心坐标
        #     item.setBrush(color)  #设置画刷
        #     item.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)
        #     self.scene.addItem(item)

    def setGraphImage(self, imgfile):
        if os.path.exists(imgfile):
            self.datas.setImgpath(imgfile)
            self.graphicsPixmapItem.setPixmap(self.datas.img)
            self.scene.clearSelection()  # 【清除选择】
            return True
        else:
            return False

    def addCurve(self, name=None):
        if not name:
            name = nextName(self.currentCurve)
        while(name in self.curveObjs):
            name = nextName(name)
        self.curveObjs[name] = []
        self.curvePointObjs[name] = []
        item1 = IconItem()
        item2 = QStandardItem(name)
        item3 = QStandardItem()
        item1.setEditable(False)
        item3.setCheckable(True)
        item3.setAutoTristate(False)
        item3.setEditable(False)
        self.curveModel.appendRow([item1, item2, item3])
        self.currentCurve = name
        if self.curveModel.rowCount() == 1:
            self.curveModel.item(0,0).switch(True)

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
                self.curvePointObjs[newname] = self.curvePointObjs.pop(name)
                for i in range(self.curveModel.rowCount()):
                    item = self.curveModel.item(i, 1)
                    if item.text() == name:
                        item.setText(newname)

    def mouseMoveEvent(self, evt):
        pt = evt.pos()  # 获取鼠标坐标--view坐标
        self.sigMouseMovePoint.emit(pt, self.mapToScene(pt))  # 发送鼠标位置
        QGraphicsView.mouseMoveEvent(self, evt)
        self.updateCurve(self.currentCurve)
        self.repaint()
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
        elif self.mode is OpMode.axes:
            item = QGraphicsPointItem()
            item.pointType = PointType.plus
            item.linewidth = 2
            item.setPos(ptscene)
            self.scene.addItem(item)
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)

            (x, y) = Axesdialog.getCoord()
            if x != None or y != None:
                if x:
                    self.datas.axisx[ptscene.x()] = x
                else:
                    x = ""
                if y:
                    self.datas.axisy[ptscene.y()] = y
                else:
                    y = ""
                self.axesPts.append(item)
                self.axesModel.appendRow(
                    [QStandardItem("({},{})".format(ptscene.x(), ptscene.y())), QStandardItem(str(x)),
                     QStandardItem(str(y))])
                item.setSelected(True)
            else:
                self.scene.removeItem(item)
        elif self.mode is OpMode.curve and clicked:
            ptitem = QGraphicsPointItem()
            ptitem.pointColor = Qt.blue
            ptitem.linewidth = 1
            ptitem.setPos(ptscene)
            ptitem.setFlags(
                QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)
            self.scene.addItem(ptitem)

            if self.currentCurve not in self.curvePointObjs:
                self.curvePointObjs[self.currentCurve] = []
            self.curvePointObjs[self.currentCurve].append(ptitem)
            self.updateCurve(self.currentCurve)
            self.updateCurvePoints(self.currentCurve)
            self.sigMouseMovePoint.emit(event.pos(), ptscene)
            ptitem.setSelected(True)

        # item1=QGraphicsRectItem(rect)  #创建矩形---以场景为坐标
        # item1.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)  #给图元设置标志
        # QGraphicsItem.ItemIsSelectable---可选择
        # QGraphicsItem.ItemIsFocusable---可设置焦点
        # QGraphicsItem.ItemIsMovable---可移动
        # QGraphicsItem.ItemIsPanel---
        # self.scene.addItem(item1)  #给场景添加图元

    def deletePoint(self, pointItem):
        curvechange = None
        for name, items in self.curvePointObjs.items():
            for ptitem in items:
                if ptitem is pointItem:
                    curvechange = name
                    items.remove(ptitem)
        self.scene.removeItem(pointItem)
        if curvechange:
            self.updateCurve(curvechange)

    def deleteSelectedPoint(self):
        pointitems = self.scene.selectedItems()
        if len(pointitems) == 1:
            self.deletePoint(pointitems[0])

    def updateCurve(self, name):
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

        curveitem = []
        if name in self.curveObjs:
            curveitem = self.curveObjs[name]
        if not isinstance(curveitem, list):
            curveitem = []
        lastitems = curveitem.copy()

        if name in self.curvePointObjs:
            pointItems = self.curvePointObjs[name]
        else:
            pointItems = []
        points = []
        for ptitem in pointItems:
            points.append(ptitem.pos())

        if len(points) > 1:
            for i in range(1, len(points)):
                l = QGraphicsLineItem(points[i - 1].x(), points[i - 1].y(), points[i].x(), points[i].y())
                # l.setFlag(QGraphicsItem.ItemIsSelectable)
                curveitem.append(l)

        self.curveObjs[name] = curveitem
        for line in curveitem:
            self.scene.addItem(line)

        for line in lastitems:
            self.scene.removeItem(line)

    def displayCurvePoints(self, curvename):
        self.pointsModel.clear()
        for pt in self.curvePointObjs[curvename]:
            item1 = QStandardItem()
            item2 = QStandardItem(str(pt.x()))
            item3 = QStandardItem(str(pt.y()))
            self.pointsModel.appendRow([item1, item2, item3])

    def updateCurvePoints(self, name):
        extra = len(self.curvePointObjs[name]) - self.pointsModel.rowCount()
        if extra > 0:
            for i in range(extra):
                item1 = QStandardItem()
                item2 = QStandardItem()
                item3 = QStandardItem()
                self.pointsModel.appendRow([item1, item2, item3])
        elif extra < 0:
            j = self.curveModel.rowCount() - 1
            i = j+extra
            self.pointsModel.removeRows(i, j)

        for i in range(self.pointsModel.rowCount()):
            pt = self.curvePointObjs[name][i]
            self.pointsModel.item(i,1).setText(str(pt.x()))
            self.pointsModel.item(i,2).setText(str(pt.y()))

    def changeCurrentCurve(self, name=None):
        if name != self.currentCurve or name==None:
            self.displayCurvePoints(name)
            self.currentCurve = name

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
