from enum import Enum,unique
from PyQt5.QtWidgets import QApplication,QGraphicsScene,QGraphicsView,QGraphicsRectItem,QMainWindow,QLabel,QGraphicsItem,QGraphicsEllipseItem
from PyQt5.QtCore import Qt,pyqtSignal,QPoint,QRectF
from PyQt5.QtGui import QPen, QPainterPath

@unique
class PointType(Enum):
    none = 0 # None
    point = 1 # 点 .
    bigpoint = 2 # ●
    plus = 3 # +
    minus = 4 # -
    vertical = 5 # |
    cross = 6# x
    star = 7 # 米
    crossvertical = 8 # x | 结合
    squre = 9 # ■
    prism = 10 # ■ 转45°
    trangle = 11 #▲
    circle = 12 # O
    
    pointincircle = 21# . in o
    plusincircle = 22# + in O
    crossincircle = 23# x in O
    pluswithcircle = 24
    crosswithcircle = 25
    # . in □
    # + in □
    # x in □
    
        
class QGraphicsPointItem(QGraphicsItem):
    """Item for point
    including kinds of point type, such as x o + · ect.
    and size can be changed."""
    def __init__(self, width=20, height=20, linewidth=2):
        super().__init__()
        self.pointType = PointType.crosswithcircle
        self.pointSize = (width, height)
        self.linewidth = linewidth
        self.pointColor = Qt.red
        
    def boundingRect(self):
        return QRectF(-self.pointSize[0]/2,-self.pointSize[1]/2,self.pointSize[0],self.pointSize[1])
        #return QRectF(-self.pointSize[0]/2-self.linewidth,-self.pointSize[1]/2-self.linewidth,self.pointSize[0]+self.linewidth*2,self.pointSize[1]+self.linewidth*2)
    
    def paint(self, painter, option, widget):
        painter.setPen(QPen(self.pointColor,self.linewidth))
        #painter.drawRect(self.boundingRect())
        if self.pointType is PointType.none:
            pass
        elif self.pointType is PointType.point:
            painter.drawPoint(0,0)
        elif self.pointType is PointType.bigpoint:
            rect = QRectF(-self.pointSize[0]/4,-self.pointSize[1]/4,self.pointSize[0]/2,self.pointSize[1]/2)
            # painter.drawEllipse(rect)
            paintPath = QPainterPath()
            paintPath.addEllipse(rect)
            painter.fillPath(paintPath,self.pointColor)
        elif self.pointType is PointType.plus:
            painter.drawLine(-self.pointSize[0]//2,0,self.pointSize[0]//2,0)
            painter.drawLine(0,-self.pointSize[1]//2,0,self.pointSize[1]//2)
        elif self.pointType is PointType.minus:
            painter.drawLine(-self.pointSize[0]//2,0,self.pointSize[0]//2,0)
        elif self.pointType is PointType.vertical:
            painter.drawLine(0,-self.pointSize[1]//2,0,self.pointSize[1]//2)
        elif self.pointType is PointType.cross:
            coord = (self.pointSize[0]*0.7071)//2
            painter.drawLine(-coord,-coord,coord,coord)
            painter.drawLine(-coord,coord,coord,-coord)
        elif self.pointType is PointType.star:
            coord = (self.pointSize[0]*0.7071)//2
            painter.drawLine(-self.pointSize[0]//2,0,self.pointSize[0]//2,0)
            painter.drawLine(0,-self.pointSize[1]//2,0,self.pointSize[1]//2)
            painter.drawLine(-coord,-coord,coord,coord)
            painter.drawLine(-coord,coord,coord,-coord)
        elif self.pointType is PointType.crossvertical:
            coord = (self.pointSize[0]*0.7071)//2
            painter.drawLine(0,-self.pointSize[1]//2,0,self.pointSize[1]//2)
            painter.drawLine(-coord,-coord,coord,coord)
            painter.drawLine(-coord,coord,coord,-coord)
        elif self.pointType is PointType.pointincircle:
            painter.drawPoint(0,0)
            painter.drawEllipse(self.boundingRect())
        elif self.pointType is PointType.plusincircle:
            painter.drawLine(-self.pointSize[0]//2,0,self.pointSize[0]//2,0)
            painter.drawLine(0,-self.pointSize[1]//2,0,self.pointSize[1]//2)
            painter.drawEllipse(self.boundingRect())
        elif self.pointType is PointType.crossincircle:
            painter.drawEllipse(self.boundingRect())
            coord = (self.pointSize[0]*0.7071)//2
            painter.drawLine(-coord,-coord,coord,coord)
            painter.drawLine(-coord,coord,coord,-coord)
        elif self.pointType is PointType.crosswithcircle:
            painter.drawEllipse(self.boundingRect())
            coord = (self.pointSize[0])//2
            painter.drawLine(-coord,-coord,coord,coord)
            painter.drawLine(-coord,coord,coord,-coord)