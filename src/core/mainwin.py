from core.graphicsView import GraphDigitGraphicsView
from .mainwinbase import MainWinBase


class MainWin(MainWinBase):
    def __init__(self):
        super(MainWin, self).__init__()

        # 图形控件
        self.view = GraphDigitGraphicsView()  # 创建视图窗口
        self.mainTabWidget.addTab(self.view, "main")
        self.view.graphicsPixmapItem.setPixmap(self.view.datas.img)
        self.view.scene.clearSelection()  # 【清除选择】
        self.view.sigMouseMovePoint.connect(self.slotMouseMovePoint)

    def slotMouseMovePoint(self, pt, ptscene):
        self.updatePixelCoord(pt.x(), pt.y())
        self.updatePointCoord(ptscene)
