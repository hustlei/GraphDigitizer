#!/usr/bin/python3
"""Mainwindow for app

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""

import os

import dill
from PyQt5.QtCore import Qt, QModelIndex, QMetaEnum
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QFileDialog, QAbstractItemView, QItemDelegate, QInputDialog, QDialog, QLabel, QFormLayout, \
    QSpinBox, QDialogButtonBox, QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QDoubleSpinBox, QMessageBox, qApp, \
    QLineEdit, QGraphicsItem

from core.graphicsView import GraphDigitGraphicsView
from .enums import OpMode
from .mainwinbase import MainWinBase
from .project import Digi
from .utils import nextName, str2num
from .utils.fileop import FileOp
from .widgets.custom import QLineComboBox, QColorComboBox


class MainWin(MainWinBase):
    def __init__(self):
        super(MainWin, self).__init__()
        self.ver = "v0.30"
        self.title = "GraphDigitizer " + self.ver
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon("res/app.ico"))
        # 图形控件
        self.view = GraphDigitGraphicsView()  # 创建视图窗口
        self.mainTabWidget.addTab(self.view, "main")

        # actions
        self.view.sigMouseMovePoint.connect(self.slotMouseMovePoint)
        self.fileop = FileOp()
        self.setupActions()
        self.file = None
        self.new()
        self.docks["fit"].initData(self.view)
        self.view.sigNewCurveAdded.connect(self.docks["fit"].reset)

    def slotMouseMovePoint(self, pt, ptscene):
        self.updatePixelCoordStatus(pt.x(), pt.y())
        self.updatePointCoordStatus(ptscene)

    def slotModified(self, modified):
        if modified:
            self.actions["save"].setEnabled(True)
        else:
            self.actions["save"].setEnabled(False)

    # action funcs
    def new(self):
        """create new GraphDigitGrapicsView"""
        self.docks["fit"].reset()
        self.view.resetview()
        self.initAxesAndCurveTable()
        self.file = None
        self.view.sigModified.emit(False)
        self.setWindowTitle(self.title)

    def importimage(self, file=None):  # _参数用于接收action的event参数,bool类型
        if not file:
            file, _ = QFileDialog.getOpenFileName(
                self, self.tr("Import Image"), "",
                "Images (*.png *.jpg *.jpep *.gif);;Bitmap Image(*.bmp *.xpm *.xbm *.pbm *.pgm);;all(*.*)"
            )  # _是filefilter
        if os.path.exists(file):
            self.statusbar.showMessage(self.tr("importing image..."))
            ok = self.view.setGraphImage(file)
            add2tmp = self.fileop.addImage(file)
            if ok and add2tmp:
                self.statusbar.showMessage(self.tr("import successfully"))
                self.actions["showoriginalgraph"].trigger()
            else:
                self.statusbar.showMessage(self.tr("import failed"))
        else:
            self.statusbar.showMessage(self.tr("image file not found."))

    def zoom(self, factor=1):
        self.view.scale(factor, factor)

    def changeMode(self, mode, checked):
        if not checked:
            self.view.mode = OpMode.default
        else:
            lastmode = self.view.mode
            self.view.mode = mode
            if lastmode != OpMode.default:
                self.actions[lastmode.name].setChecked(False)
        if self.view.mode == OpMode.default or self.view.mode == OpMode.select:
            self.view.setCursor(Qt.ArrowCursor)
            self.view.showAxes(False)
        else:
            self.view.setCursor(Qt.CrossCursor)
            if self.view.mode == OpMode.axesx:
                self.view.showAxes(True)
                self.docktabwidget.setCurrentIndex(0)
                self.view.scene.clearSelection()
                for item in self.view.axesyObjs:
                    item.setVisible(False)
                    # item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    # item.setFlag(QGraphicsItem.ItemIsFocusable, False)
                    # item.setFlag(QGraphicsItem.ItemIsMovable, False)
                for item in self.view.axesxObjs:
                    item.setVisible(True)
                    # item.setFlags(
                    #     QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)
            elif self.view.mode == OpMode.axesy:
                self.view.showAxes(True)
                self.docktabwidget.setCurrentIndex(0)
                self.view.scene.clearSelection()
                for item in self.view.axesyObjs:
                    item.setVisible(True)
                    # item.setFlags(
                    #    QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsMovable)
                for item in self.view.axesxObjs:
                    item.setVisible(False)
                    # item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    # item.setFlag(QGraphicsItem.ItemIsFocusable, False)
                    # item.setFlag(QGraphicsItem.ItemIsMovable, False)
            else:
                self.view.showAxes(False)
                self.docktabwidget.setCurrentIndex(1)
                self.view.scene.clearSelection()

    def setupActions(self):
        self.actions["import"].triggered.connect(self.importimage)
        self.actions["export"].triggered.connect(self.export)
        self.actions["open"].triggered.connect(self.open)
        self.actions["save"].triggered.connect(self.save)
        self.actions["saveas"].triggered.connect(self.saveas)
        self.actions["close"].triggered.connect(self.new)

        self.actions["del"].triggered.connect(self.view.deleteSelectedItem)

        self.actions["select"].triggered.connect(lambda x: self.changeMode(OpMode.select, x))
        self.actions["axesx"].triggered.connect(lambda x: (self.changeMode(OpMode.axesx, x)))
        self.actions["axesy"].triggered.connect(lambda x: (self.changeMode(OpMode.axesy, x)))
        self.actions["curve"].triggered.connect(lambda x: self.changeMode(OpMode.curve, x))
        self.actions["zoomin"].triggered.connect(lambda: self.zoom(1.1))
        self.actions["zoomout"].triggered.connect(lambda: self.zoom(0.9))
        self.actions["showgrid"].triggered.connect(self.view.showGrid)

        self.actions["undo"].setEnabled(False)
        self.actions["redo"].setEnabled(False)

        self.actions["scalegraph"].triggered.connect(self.scalegraph)
        self.actions["gridsetting"].triggered.connect(self.gridsetting)

        self.axesxTable.setModel(self.view.axesxModel)
        self.axesyTable.setModel(self.view.axesyModel)
        self.curveTable.setModel(self.view.curveModel)
        self.pointsTable.setModel(self.view.pointsModel)

        self.initAxesAndCurveTable()

        def selectedCurve():
            name = None
            try:
                name = self.view.curveModel.item(self.curveTable.selectedIndexes()[0].row(), 1).text()
            except:
                pass
            return name

        self.actions["addcurve"].triggered.connect(lambda: self.view.addCurve())
        self.actions["renamecurve"].triggered.connect(lambda: self.view.renameCurve(name=selectedCurve()))
        self.actions["delcurve"].triggered.connect(lambda: self.view.delCurve(name=selectedCurve()))

        def changecurvetable(index):
            if index.column() == 0:
                self.view.changeCurrentCurve(self.view.curveModel.item(index.row(), 1).text())
            elif index.column() == 1:
                self.view.renameCurve(name=self.view.curveModel.item(index.row(), 1).text())

        self.curveTable.doubleClicked.connect(changecurvetable)

        # show or not show background
        def hidegraph():
            self.actions["hidegraph"].setChecked(True)
            self.actions["showoriginalgraph"].setChecked(False)
            self.view.graphicsPixmapItem.setVisible(False)

        self.actions["hidegraph"].triggered.connect(hidegraph)

        def showoriginalgraph():
            self.actions["hidegraph"].setChecked(False)
            self.actions["showoriginalgraph"].setChecked(True)
            self.view.graphicsPixmapItem.setVisible(True)

        self.actions["showoriginalgraph"].triggered.connect(showoriginalgraph)
        self.actions["showoriginalgraph"].setChecked(True)

        self.view.sigModified.connect(self.slotModified)

        # help
        aboutText = "<b><center>" + self.title + "</center></b><br><br>"
        aboutText += self.tr(
            "This software is for digitizing graph(such as figures scanned from book).<br><br>")
        aboutText += self.tr(
            "author: lileilei<br>website: <a href='https://github.com/hustlei/GraphDigitizer'>https"
            "://github.com/hustlei/GraphDigitizer</a><br><br>welcome anyone to communicate with me: hustlei@sina.cn ")
        aboutText += "<br>copyright &copy; 2020, lileilei@WuHan."
        self.actions["about"].triggered.connect(lambda: QMessageBox.about(self, "about", aboutText))
        import webbrowser
        self.actions["help"].triggered.connect(lambda: webbrowser.open("https://github.com/hustlei/GraphDigitizer"))

    def initAxesAndCurveTable(self):
        self.axesxTable.setColumnWidth(0, 120)
        self.axesxTable.setColumnWidth(1, 100)
        self.axesyTable.setColumnWidth(0, 120)
        self.axesyTable.setColumnWidth(1, 100)
        self.curveTable.setColumnWidth(0, 50)
        self.curveTable.setColumnWidth(1, 120)
        self.curveTable.setColumnWidth(2, 50)
        self.pointsTable.setColumnWidth(0, 45)
        self.pointsTable.setColumnWidth(1, 80)
        self.pointsTable.setColumnWidth(2, 80)
        self.axesxTable.verticalHeader().setVisible(False)
        self.axesyTable.verticalHeader().setVisible(False)
        self.curveTable.verticalHeader().setVisible(False)
        self.pointsTable.verticalHeader().setVisible(False)

        class ReadOnlyDelegate(QItemDelegate):
            def __init__(self, parent):
                super().__init__(parent)

            def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
                return None

        self.axesxTable.setSelectionModel(self.view.axesxSelectModel)
        self.axesyTable.setSelectionModel(self.view.axesySelectModel)
        self.axesxTable.setItemDelegateForColumn(0, ReadOnlyDelegate(self.axesxTable))
        self.axesyTable.setItemDelegateForColumn(0, ReadOnlyDelegate(self.axesyTable))
        self.curveTable.setItemDelegateForColumn(1, ReadOnlyDelegate(self.curveTable))
        self.axesxTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.axesxTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.axesyTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.axesyTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.curveTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.curveTable.setSelectionMode(QAbstractItemView.SingleSelection)

    def scalegraph(self):
        scale, ok = QInputDialog.getDouble(self, self.tr("scale the graph"),
                                           self.tr("set the scale value:"), 1, 0.01, 100, 2)
        if ok:
            self.view.scaleGraphImage(scale)

    def gridsetting(self):
        dialog = QDialog(self)
        layout = QVBoxLayout(dialog)

        xgroup = QGroupBox(self.tr("grid parameter for axis x"), self)
        form = QFormLayout(xgroup)
        xmintextbox = QLineEdit(dialog)
        xmaxtextbox = QLineEdit(dialog)
        xsteptextbox = QLineEdit(dialog)
        form.addRow(self.tr("minimum value:"), xmintextbox)
        form.addRow(self.tr("maximum value:"), xmaxtextbox)
        form.addRow(self.tr("step value:"), xsteptextbox)

        ygroup = QGroupBox(self.tr("grid parameter for axis y"), self)
        form = QFormLayout(ygroup)
        ymintextbox = QLineEdit(dialog)
        ymaxtextbox = QLineEdit(dialog)
        ysteptextbox = QLineEdit(dialog)
        form.addRow(self.tr("minimum value:"), ymintextbox)
        form.addRow(self.tr("maximum value:"), ymaxtextbox)
        form.addRow(self.tr("step value:"), ysteptextbox)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(xgroup)
        hbox1.addWidget(ygroup)

        lineCombo = QLineComboBox()
        lineCombo.addItem(self.tr("SolidLine"), Qt.SolidLine)
        lineCombo.addItem(self.tr("DashLine"), Qt.DashLine)
        lineCombo.addItem(self.tr("DotLine"), Qt.DotLine)
        lineCombo.addItem(self.tr("DashDotLine"), Qt.DashDotLine)
        lineCombo.addItem(self.tr("DashDotDotLine"), Qt.DashDotDotLine)
        colorCombo = QColorComboBox()
        spinboxWidth = QSpinBox(dialog)
        spinboxOpacity = QDoubleSpinBox(dialog)
        spinboxOpacity.setRange(0, 1)
        spinboxOpacity.setSingleStep(0.1)

        gridlinegroup = QGroupBox(self.tr("grid line properties"), self)
        hbox2 = QHBoxLayout()
        gridlinegroup.setLayout(hbox2)
        form1 = QFormLayout()
        form2 = QFormLayout()
        hbox2.addLayout(form1)
        hbox2.addLayout(form2)
        # colorCombo.addItems(QColor.colorNames())
        # colorCombo.setCurrentText("red")
        form1.addRow(QLabel("LineType"), lineCombo)
        form1.addRow(QLabel("GridColor"), colorCombo)
        form2.addRow(QLabel("GridWidth"), spinboxWidth)
        form2.addRow(QLabel("Opacity"), spinboxOpacity)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, dialog)

        layout.addLayout(hbox1)
        layout.addWidget(gridlinegroup)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)

        lineCombo.setCurrentIndex(lineCombo.findData(self.view.proj.gridLineType))
        if not isinstance(self.view.proj.gridColor, QColor):
            self.view.proj.gridColor = QColor(self.view.proj.gridColor)
        colorCombo.setCurrentIndex(colorCombo.findData(self.view.proj.gridColor.name()))
        spinboxWidth.setValue(self.view.proj.gridLineWidth)
        spinboxOpacity.setValue(self.view.proj.gridOpacity)
        xmintextbox.setText(str(self.view.proj.gridx[0]) if self.view.proj.gridx[0] is not None else "")
        xmaxtextbox.setText(str(self.view.proj.gridx[1]) if self.view.proj.gridx[1] is not None else "")
        xsteptextbox.setText(str(self.view.proj.gridx[2]) if self.view.proj.gridx[2] is not None else "")
        ymintextbox.setText(str(self.view.proj.gridy[0]) if self.view.proj.gridy[0] is not None else "")
        ymaxtextbox.setText(str(self.view.proj.gridy[1]) if self.view.proj.gridy[1] is not None else "")
        ysteptextbox.setText(str(self.view.proj.gridy[2]) if self.view.proj.gridy[2] is not None else "")

        if dialog.exec() == QDialog.Accepted:
            self.view.proj.gridx = [str2num(xmintextbox.text()), str2num(xmaxtextbox.text()),
                                    str2num(xsteptextbox.text())]
            self.view.proj.gridy = [str2num(ymintextbox.text()), str2num(ymaxtextbox.text()),
                                    str2num(ysteptextbox.text())]
            self.view.proj.gridLineWidth = spinboxWidth.value()
            self.view.proj.gridColor = QColor(colorCombo.currentData())  # .currentText())
            self.view.proj.gridLineType = lineCombo.currentData()
            self.view.proj.gridOpacity = spinboxOpacity.value()
            self.view.calGridCoord()
            self.view.updateGrid()
            self.view.sigModified.emit(True)

    def export(self, file=None):
        if not file:
            file, _ = QFileDialog.getSaveFileName(self, self.tr("Export Curves"), "",
                                                  "CSV (*.csv);;all(*.*)")  # _是filefilter
        if file:
            if not self.view.axisvalid():
                QMessageBox.information(self, "export error", self.tr(
                    "there are axes with the same coordinate, please check, the exported data may be not accurate"),
                                        QMessageBox.Ok,
                                        QMessageBox.Ok)
            try:
                with open(file, "w", encoding="utf8") as f:
                    f.write(self.view.exportToCSVtext())
                self.statusbar.showMessage(self.tr("export successfully."))
            except Exception as e:
                self.statusbar.showMessage(self.tr("export failure:{}".format(e.args)))
        else:
            self.statusbar.showMessage(self.tr("export failure."))

    def save(self):
        self.saveas(self.file)

    def saveas(self, file=None):
        if not file:
            file, _ = QFileDialog.getSaveFileName(self, self.tr("save project"), "",
                                                  "digi (*.digi);;all(*.*)")  # _是filefilter
        if file:
            self.file = file
            # store data to proj
            self.view.dump()
            # save digi.dump
            with open(self.fileop.datafile, 'wb') as datafile:
                dill.dump(self.view.proj, datafile)
            self.fileop.save(file)
            self.view.sigModified.emit(False)
            self.setWindowTitle(self.title+"  -  "+self.file)
            self.statusbar.showMessage(self.tr("save successfully."))
        else:
            self.statusbar.showMessage(self.tr("save failure."))

    def open(self, file=None):
        if not file:
            file, _ = QFileDialog.getOpenFileName(self, self.tr("open project"), "",
                                                  "digi (*.digi);;all(*.*)")  # _是filefilter
        if file:
            try:
                if self.fileop.open(file):
                    self.new()
                    self.view.setGraphImage(self.fileop.imgfile)
                    # self.importimage(self.fileop.imgfile)
                    if os.path.exists(self.fileop.datafile):
                        with open(self.fileop.datafile, 'rb') as f:
                            self.view.proj = dill.load(f)
                            tmp = Digi()  # update old project format to new version
                            for k, v in tmp.__dict__.items():
                                if k not in self.view.proj.__dict__:
                                    self.view.proj.__dict__[k] = v
                            self.view.load(self.view.proj)
                            self.docks["fit"].initData(self.view)
                    self.file = file
                    self.view.sigModified.emit(False)
                    self.actions["select"].trigger()
                    self.setWindowTitle(self.title+"  -  "+self.file)
                    self.statusbar.showMessage(self.tr("open successfully."))
                else:
                    self.statusbar.showMessage(self.tr("open failure"))
            except Exception as e:
                self.statusbar.showMessage(self.tr("open failure:{}").format(e.args))
        else:
            self.statusbar.showMessage(self.tr("nothing opened"))

    def closeEvent(self, e):
        if self.actions["save"].isEnabled():
            msg = QMessageBox(QMessageBox.Question, self.title,
                              self.tr("Current file hasn't been saved, do you want to save?"),
                              QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Cancel)
            msg.button(QMessageBox.Save).setText(self.tr("Save"))
            msg.button(QMessageBox.Discard).setText(self.tr("Discard"))
            msg.button(QMessageBox.Cancel).setText(self.tr("Cancel"))
            ret = msg.exec_()
            if ret in (QMessageBox.Save, QMessageBox.Yes):
                self.save()
                self.fileop.close()
                qApp.exit()
            elif ret in (QMessageBox.Discard, QMessageBox.No):
                # self.updateSpecialConfig()
                # self.config.save()
                self.fileop.close()
                qApp.exit()
            else:
                e.ignore()
        # else:
        # self.updateSpecialConfig()
        # self.config.saveDefault()
