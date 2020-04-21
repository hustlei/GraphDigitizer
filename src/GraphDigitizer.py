import sys
from PyQt5.QtWidgets import QApplication,QGraphicsScene,QGraphicsView,QGraphicsRectItem,QMainWindow,QLabel,QGraphicsItem,QGraphicsEllipseItem
from PyQt5.QtCore import Qt,pyqtSignal,QPoint,QRectF
from PyQt5.QtGui import QPen
from enum import Enum,unique
from graphicsItems import *

class QMyGraphicsView(QGraphicsView):
    sigMouseMovePoint=pyqtSignal(QPoint)
    #自定义信号sigMouseMovePoint，当鼠标移动时，在mouseMoveEvent事件中，将当前的鼠标位置发送出去
    #QPoint--传递的是view坐标
    def __init__(self,parent=None):
        super(QMyGraphicsView,self).__init__(parent)

    def mouseMoveEvent(self, evt):
        pt=evt.pos()  #获取鼠标坐标--view坐标
        self.sigMouseMovePoint.emit(pt) #发送鼠标位置
        QGraphicsView.mouseMoveEvent(self, evt)
        
@unique
class OpMode(Enum):
    """current mode such as: draw point, move point, move scene etc."""
    default = 0
    selection = 1
    drawpoint = 2

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(600,400)
        self.mode = OpMode.drawpoint
        self.curves = {'default':[]}
        self.currentCurve = 'default'
        # 状态栏
        self.statusbar=self.statusBar()
        self.labviewcorrd=QLabel('view坐标:')
        self.labviewcorrd.setMinimumWidth(150)
        self.labscenecorrd=QLabel('scene坐标：')
        self.labscenecorrd.setMinimumWidth(150)
        self.labitemcorrd = QLabel('item坐标：')
        self.labitemcorrd.setMinimumWidth(150)
        self.statusbar.addWidget(self.labviewcorrd)
        self.statusbar.addWidget(self.labscenecorrd)
        self.statusbar.addWidget(self.labitemcorrd)
        
        # 图形控件
        self.view = QMyGraphicsView()  #创建视图窗口
        self.setCentralWidget(self.view)
        self.initView()
        
    def initView(self):
        rect=QRectF(-200,-100,400,200)
        self.scene=QGraphicsScene(rect)  #创建场景
        #参数：场景区域
        #场景坐标原点默认在场景中心---场景中心位于界面中心
        self.view.setScene(self.scene)  #给视图窗口设置场景

        #item1=QGraphicsRectItem(rect)  #创建矩形---以场景为坐标
        #item1.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)  #给图元设置标志
        #QGraphicsItem.ItemIsSelectable---可选择
        #QGraphicsItem.ItemIsFocusable---可设置焦点
        #QGraphicsItem.ItemIsMovable---可移动
        #QGraphicsItem.ItemIsPanel---
        #self.scene.addItem(item1)  #给场景添加图元
        for pos,color in zip([rect.left(),0,rect.right()],[Qt.red,Qt.yellow,Qt.blue]):
            item=QGraphicsEllipseItem(-50,-50,100,100)  #创建椭圆--场景坐标
            #参数1 参数2  矩形左上角坐标
            #参数3 参数4 矩形的宽和高
            item.setPos(pos,0)  #给图元设置在场景中的坐标(移动图元)--图元中心坐标
            item.setBrush(color)  #设置画刷
            item.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)
            self.scene.addItem(item)
        self.scene.clearSelection()  #【清除选择】
        self.view.sigMouseMovePoint.connect(self.slotMouseMovePoint)

    def slotMouseMovePoint(self,pt):
        self.labviewcorrd.setText('view坐标:{},{}'.format(pt.x(),pt.y()))
        ptscene=self.view.mapToScene(pt)  #把view坐标转换为场景坐标
        self.labscenecorrd.setText('scene坐标:{:.0f},{:.0f}'.format(ptscene.x(),ptscene.y()))
        item=self.scene.itemAt(ptscene,self.view.transform())  #在场景某点寻找图元--最上面的图元
        #返回值：图元地址
        #参数1 场景点坐标
        #参数2 ？？？？
        if item != None:
            ptitem=item.mapFromScene(ptscene)  #把场景坐标转换为图元坐标
            self.labitemcorrd.setText('item坐标:{:.0f},{:.0f}'.format(ptitem.x(),ptitem.y()))
            
    def mousePressEvent(self, event):
        if self.mode is OpMode.drawpoint:
            if not self.curves[self.currentCurve]:
                self.curves[self.currentCurve] = []
            item = QGraphicsPointItem()
            pts = self.view.mapToScene(event.pos())
            item.setPos(pts)
            self.curves[self.currentCurve].append(item)
            item.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)
            self.scene.addItem(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())