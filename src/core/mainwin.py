
from enum import Enum, unique
from core.graphicsItems import *
from core.graphicsView import QMyGraphicsView
from core.project import Datas


@unique
class OpMode(Enum):
    """current mode such as: draw point, move point, move scene etc."""
    default = 0
    selectmode = 1
    axismode = 2
    pointmode = 3
    curvemode = 4


class MainWin(QMainWindow):
    def __init__(self):
        super(MainWin, self).__init__()
        self.resize(960, 720)
        # self.mode = OpMode.drawpoint
        self.datas = Datas()
        ####
        self.datas.setImgpath(r"C:\Users\lei\Desktop\1.png")
        ####
        self.currentCurve = 'default'
        # 状态栏
        self.statusbar = self.statusBar()
        self.labviewcorrd = QLabel('view坐标:')
        self.labviewcorrd.setMinimumWidth(150)
        self.labscenecorrd = QLabel('scene坐标：')
        self.labscenecorrd.setMinimumWidth(150)
        self.labitemcorrd = QLabel('item坐标：')
        self.labitemcorrd.setMinimumWidth(150)
        self.statusbar.addWidget(self.labviewcorrd)
        self.statusbar.addWidget(self.labscenecorrd)
        #self.statusbar.addWidget(self.labitemcorrd)

        # 图形控件
        self.view = QMyGraphicsView()  # 创建视图窗口
        self.setCentralWidget(self.view)
        self.initView()

    def initView(self):
        for pos, color in zip([-50, 0, 50], [Qt.red, Qt.yellow, Qt.blue]):
            item = QGraphicsEllipseItem(-50, -50, 100, 100)  # 创建椭圆--场景坐标
            # 参数1 参数2  矩形左上角坐标
            # 参数3 参数4 矩形的宽和高
            item.setPos(pos, 0)  # 给图元设置在场景中的坐标(移动图元)--图元中心坐标
            item.setBrush(color)  # 设置画刷
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)
            self.view.scene.addItem(item)
        self.view.scene.clearSelection()  # 【清除选择】
        self.view.sigMouseMovePoint.connect(self.slotMouseMovePoint)

        self.view.graphicsPixmapItem.setPixmap(self.datas.img)

    def slotMouseMovePoint(self, pt):
        self.labviewcorrd.setText('view坐标:{},{}'.format(pt.x(), pt.y()))
        ptscene = self.view.mapToScene(pt)  # 把view坐标转换为场景坐标
        self.labscenecorrd.setText('scene坐标:{:.0f},{:.0f}'.format(ptscene.x(), ptscene.y()))
        item = self.view.scene.itemAt(ptscene, self.view.transform())  # 在场景某点寻找图元--最上面的图元
        # 返回值：图元地址
        # 参数1 场景点坐标
        # 参数2 ？？？？
        if item != None:
            ptitem = item.mapFromScene(ptscene)  # 把场景坐标转换为图元坐标
            self.labitemcorrd.setText('item坐标:{:.0f},{:.0f}'.format(ptitem.x(), ptitem.y()))

    def mousePressEvent(self, event):
        item = QGraphicsPointItem()
        pts = self.view.mapToScene(event.pos())
        item.setPos(pts)
        self.datas.curves[self.currentCurve].sceneCoords.append(item)
        item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)
        self.view.scene.addItem(item)
