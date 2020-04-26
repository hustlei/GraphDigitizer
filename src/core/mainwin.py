import os

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QFileDialog, QAbstractItemView, QItemDelegate

from core.graphicsView import GraphDigitGraphicsView
from .enums import OpMode
from .mainwinbase import MainWinBase
from .utils import nextName


class MainWin(MainWinBase):
    def __init__(self):
        super(MainWin, self).__init__()
        # 图形控件
        self.view = GraphDigitGraphicsView()  # 创建视图窗口
        self.mainTabWidget.addTab(self.view, "main")

        # actions
        self.view.sigMouseMovePoint.connect(self.slotMouseMovePoint)
        self.setupActions()

    def slotMouseMovePoint(self, pt, ptscene):
        self.updatePixelCoordStatus(pt.x(), pt.y())
        self.updatePointCoordStatus(ptscene)

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

        self.actions["del"].triggered.connect(self.view.deleteSelectedPoint)

        self.actions["select"].triggered.connect(lambda x: self.setMode(OpMode.select, x))
        self.actions["axesx"].triggered.connect(lambda x: (self.setMode(OpMode.axesx, x),
                                                           self.actions["showgrid"].setChecked(True)))
        self.actions["axesy"].triggered.connect(lambda x: (self.setMode(OpMode.axesy, x),
                                                           self.actions["showgrid"].setChecked(True)))
        self.actions["curve"].triggered.connect(lambda x: self.setMode(OpMode.curve, x))
        self.actions["zoomin"].triggered.connect(lambda: self.zoom(1.1))
        self.actions["zoomout"].triggered.connect(lambda: self.zoom(0.9))
        self.actions["showgrid"].setChecked(True)
        self.actions["showgrid"].triggered.connect(self.view.showGrid)

        self.actions["undo"].setEnabled(False)
        self.actions["redo"].setEnabled(False)

        self.axesxTable.setModel(self.view.axesxModel)
        self.axesyTable.setModel(self.view.axesyModel)
        self.curveTable.setModel(self.view.curveModel)
        self.pointsTable.setModel(self.view.pointsModel)
        self.axesxTable.setColumnWidth(0, 120)
        self.axesxTable.setColumnWidth(1, 100)
        self.axesyTable.setColumnWidth(0, 120)
        self.axesyTable.setColumnWidth(1, 100)
        self.curveTable.setColumnWidth(0, 45)
        self.curveTable.setColumnWidth(1, 120)
        self.curveTable.setColumnWidth(2, 45)
        self.pointsTable.setColumnWidth(0, 45)
        self.pointsTable.setColumnWidth(1, 80)
        self.pointsTable.setColumnWidth(2, 80)

        class ReadOnlyDelegate(QItemDelegate):
            def __init__(self, parent):
                super().__init__(parent)

            def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
                return None

        self.axesxTable.setItemDelegateForColumn(0, ReadOnlyDelegate(self.axesxTable))
        self.axesyTable.setItemDelegateForColumn(0, ReadOnlyDelegate(self.axesyTable))
        self.curveTable.setItemDelegateForColumn(1, ReadOnlyDelegate(self.curveTable))
        self.axesxTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.axesxTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.axesyTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.axesyTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.curveTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.curveTable.setSelectionMode(QAbstractItemView.SingleSelection)

        def selectedCurve():
            name = None
            try:
                name = self.view.curveModel.item(self.curveTable.selectedIndexes()[0].row(), 1).text()
            except:
                pass
            return name

        self.actions["addcurve"].triggered.connect(lambda: self.view.addCurve(nextName(selectedCurve())))
        self.actions["renamecurve"].triggered.connect(lambda: self.view.renameCurve(
            name=selectedCurve()))

        def changecurve(index):
            if index.column() == 0:
                for i in range(self.view.curveModel.rowCount()):
                    if i == index.row():
                        self.view.curveModel.item(i, 0).switch(True)
                        self.view.changeCurrentCurve(self.view.curveModel.item(i, 1).text())
                    else:
                        self.view.curveModel.item(i, 0).switch(False)

        self.curveTable.doubleClicked.connect(changecurve)
        # self.pointsTable.mov
