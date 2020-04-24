import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

from core.graphicsView import GraphDigitGraphicsView
from .enums import OpMode
from .mainwinbase import MainWinBase


class MainWin(MainWinBase):
    def __init__(self):
        super(MainWin, self).__init__()
        # 图形控件
        self.view = GraphDigitGraphicsView()  # 创建视图窗口
        self.mainTabWidget.addTab(self.view, "main")

        #actions
        self.view.sigMouseMovePoint.connect(self.slotMouseMovePoint)
        self.setupActions()

    def slotMouseMovePoint(self, pt, ptscene):
        self.updatePixelCoord(pt.x(), pt.y())
        self.updatePointCoord(ptscene)

    ## action funcs
    def new(self):
        """create new GraphDigitGrapicsView"""
        self.view = GraphDigitGraphicsView()

    def importimage(self, file=None):  # _参数用于接收action的event参数,bool类型
        if not file:
            file, _ = QFileDialog.getOpenFileName(
                self, self.tr("Import Image"), "",
                "Images (*.png *.jpg *.jpep *.gif);;Bitmap Image(*.bmp *.xpm *.xbm *.pbm *.pgm);;all(*.*)")  # _是filefilter
        if os.path.exists(file):
            self.statusbar.showMessage(self.tr("importing image..."))
            ok = self.view.setGraphImage(file)
            if ok:
                self.statusbar.showMessage(self.tr("import successfully"))
            else:
                self.statusbar.showMessage(self.tr("import failed"))
        else:
            self.statusbar.showMessage(self.tr("image file not found."))


    def zoom(self, factor=1):
        self.view.scale(factor, factor)

    def setMode(self, mode, checked):
        if not checked:
            self.view.mode = OpMode.default
        else:
            lastmode = self.view.mode
            self.view.mode = mode
            if lastmode != OpMode.default:
                self.actions[lastmode.name].setChecked(False)
        if self.view.mode == OpMode.default or self.view.mode == OpMode.select:
            self.view.setCursor(Qt.ArrowCursor)
        else:
            self.view.setCursor(Qt.CrossCursor)

    def tst(self):
        print("test")

    def setupActions(self):
        self.actions["import"].triggered.connect(self.importimage)
        self.actions["close"].triggered.connect(self.new)

        self.actions["select"].triggered.connect(lambda x:self.setMode(OpMode.select, x))
        self.actions["axes"].triggered.connect(lambda x:self.setMode(OpMode.axes, x))
        self.actions["curve"].triggered.connect(lambda x:self.setMode(OpMode.curve, x))

        self.actions["zoomin"].triggered.connect(lambda :self.zoom(1.1))
        self.actions["zoomout"].triggered.connect(lambda :self.zoom(0.9))
        #self.actions["grid"].triggered.connect(lambda x:self.setMode(OpMode.grid, x))

        self.actions["undo"].setEnabled(False)
        self.actions["redo"].setEnabled(False)
