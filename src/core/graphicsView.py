from PyQt5.QtCore import pyqtSignal, QRectF, QPoint
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem


class QMyGraphicsView(QGraphicsView):
    sigMouseMovePoint = pyqtSignal(QPoint)

    # 自定义信号sigMouseMovePoint，当鼠标移动时，在mouseMoveEvent事件中，将当前的鼠标位置发送出去
    # QPoint--传递的是view坐标
    def __init__(self, parent=None):
        super(QMyGraphicsView, self).__init__(parent)
        rect=QRectF(0,0,800,600)
        self.scene = QGraphicsScene(rect)  # 创建场景
        # 参数：场景区域
        # 场景坐标原点默认在场景中心---场景中心位于界面中心
        self.setScene(self.scene)  # 给视图窗口设置场景
        self.graphicsPixmapItem = QGraphicsPixmapItem()

        item1=QGraphicsRectItem(rect)  #创建矩形---以场景为坐标
        # item1.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable)  #给图元设置标志
        # QGraphicsItem.ItemIsSelectable---可选择
        # QGraphicsItem.ItemIsFocusable---可设置焦点
        # QGraphicsItem.ItemIsMovable---可移动
        # QGraphicsItem.ItemIsPanel---
        self.scene.addItem(item1)  #给场景添加图元
        self.scene.addItem(self.graphicsPixmapItem)

    def mouseMoveEvent(self, evt):
        pt = evt.pos()  # 获取鼠标坐标--view坐标
        self.sigMouseMovePoint.emit(pt)  # 发送鼠标位置
        QGraphicsView.mouseMoveEvent(self, evt)