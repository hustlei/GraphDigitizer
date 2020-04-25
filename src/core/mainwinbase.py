# -*- coding: utf-8 -*-
"""Base class for Mainwin

Copyright (c) 2019 lileilei <hustlei@sina.cn>
"""
from PyQt5.QtCore import Qt, QSize, QPoint, QPointF
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import (QMainWindow, QApplication, QStyleFactory, QAction, QMenu, QToolBar, QWidget, QLabel,
                             QCheckBox, QComboBox, QTabWidget, QDockWidget, qApp, QSplitter, QTableView, QScrollArea,
                             QVBoxLayout)
from res import img_rc


class MainWinBase(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1024, 720)
        self.menubar = self.menuBar()
        self.statusbar = self.statusBar()
        self.mainTabWidget = QTabWidget()

        self.actions = {}
        self.menus = {}
        self.submenus = {}
        self.contexMenus = {}
        self.toolbars = {}
        self.status = {}
        self.docks = {}
        self.documents = {}

        self.createActions()
        self.themeCombo = QComboBox()
        self.createMenubar()
        self.createContexMenus()
        self.createToolbars()
        self.createStatusBar()
        self.createDocks()
        self.createMainWidget()

        self.setupUiActions()

    def createActions(self):
        def createAct(text, tip=None, shortcut=None, iconimg=None, checkable=False, slot=None):
            action = QAction(self.tr(text), self)
            if iconimg is not None:
                action.setIcon(QIcon(iconimg))
            if shortcut is not None:
                action.setShortcut(shortcut)
            if tip is not None:
                tip = self.tr(tip)
                action.setToolTip(tip)
                action.setStatusTip(tip)
            if checkable:
                action.setCheckable(True)
            if slot is not None:
                action.triggered.connect(slot)
            return action

        def keys2str(standardkey):
            return "".join(("(", QKeySequence(standardkey).toString(), ")"))

        # self.actions["new"] = createAct(self.tr("&New", "&New"),
        #                                 self.tr("new") + keys2str(QKeySequence.New), QKeySequence.New,
        #                                 ':appres.img/NewDocument.png')
        self.actions["import"] = createAct(self.tr("&Import Image"), self.tr("Import Image"), None,
                                           ':appres.img/importimage.png')
        self.actions["replaceimage"] = createAct(self.tr("&Replace Image"),
                                                 self.tr("Replace Image"), None, ':appres.img/replaceimage.png')
        self.actions["open"] = createAct(self.tr("&Open Project"),
                                         self.tr("Open") + keys2str(QKeySequence.Open), QKeySequence.Open,
                                         ':appres.img/open.png')
        self.actions["save"] = createAct(self.tr("&Save"),
                                         self.tr("Save") + keys2str(QKeySequence.Save), QKeySequence.Save,
                                         ':appres.img/save.png')
        self.actions["saveas"] = createAct(self.tr("&Save as..."), self.tr("Save as..."), None,
                                           ':appres.img/SaveAs.png')
        self.actions["export"] = createAct(self.tr("&ExportCurves"), self.tr("ExportCurves"), "Ctrl+Alt+E",
                                           ':appres.img/export.png')
        self.actions["close"] = createAct(self.tr("&Close"), self.tr("Close"))
        self.actions["exit"] = createAct(self.tr("&Exit"), self.tr("Exit"), "Ctrl+Q")
        self.actions["undo"] = createAct(self.tr("&Undo"),
                                         self.tr("Undo") + keys2str(QKeySequence.Undo), QKeySequence.Undo,
                                         ':appres.img/undo.png')
        self.actions["redo"] = createAct(self.tr("&Redo"),
                                         self.tr("Redo") + keys2str(QKeySequence.Redo), QKeySequence.Redo,
                                         ':appres.img/redo.png')
        self.actions["cut"] = createAct(self.tr("&Cut"),
                                        self.tr("Cut") + keys2str(QKeySequence.Cut), QKeySequence.Cut,
                                        ':appres.img/cut.png')
        self.actions["copy"] = createAct(self.tr("&Copy"),
                                         self.tr("Copy") + keys2str(QKeySequence.Copy), QKeySequence.Copy,
                                         ':appres.img/copy.png')
        self.actions["paste"] = createAct(self.tr("&Paste"),
                                          self.tr("Paste") + keys2str(QKeySequence.Paste), QKeySequence.Paste,
                                          ':appres.img/paste.png')
        self.actions["zoomin"] = createAct(self.tr("&ZoomIn"), self.tr("Zoom In"), "Ctrl++", ':appres.img/zoomin.png')
        self.actions["zoomout"] = createAct(self.tr("&ZoomOut"), self.tr("Zoom Out"), "Ctrl+-",
                                            ':appres.img/zoomout.png')
        self.actions["showgrid"] = createAct(self.tr("Show Axes &Grid"), self.tr("Show AxesGrid"), None,
                                             ':appres.img/grid.png',
                                             checkable=True)
        self.actions["select"] = createAct(self.tr("Select Mode"), self.tr("Select Mode"), None,
                                           ':appres.img/select.png', checkable=True)
        self.actions["axes"] = createAct(self.tr("Set &Axes points"), self.tr("Set Axes Points"), None,
                                         ':appres.img/axes.png', checkable=True)
        self.actions["curve"] = createAct(self.tr("&AddCurve"), self.tr("Add Curve"), None, ':appres.img/curve.png',
                                          checkable=True)
        self.actions["del"] = createAct(self.tr("&del point or curve"), self.tr("delete"), QKeySequence.Delete,
                                        ':appres.img/delete.png')
        self.actions["addcurve"] = createAct(self.tr("add a new curve"), self.tr("add a new curve"), QKeySequence.Delete,
                                        ':appres.img/new.png')
        self.actions["renamecurve"] = createAct(self.tr("change curve name"), self.tr("change curve name"), QKeySequence.Delete,
                                        ':appres.img/edit.png')

        # self.actions["DisableQss"] = createAct(self.tr("&DisableQss"), self.tr("DisableQss"), checkable=True)
        # self.actions["DisableQss"].setChecked(False)
        # self.actions["ShowColor"] = createAct(self.tr("&ColorPanel"),
        #                                       self.tr("ShowColorPanel"),
        #                                       None,
        #                                       ":appres.img/color.png",
        #                                       checkable=True)
        # self.actions["ShowColor"].setChecked(True)
        self.actions["showcurves"] = createAct(self.tr("&CurvePanel"),
                                               self.tr("ShowCurvesPanel"),
                                               None,
                                               ":appres.img/view2col2right.png",
                                               checkable=True)
        self.actions["showcurves"].setChecked(True)

        self.actions["config"] = createAct(self.tr("&Config"), self.tr("settings."), None, ":appres.img/config.png")

        self.actions["about"] = createAct(self.tr("&About"), self.tr("About"))

        # self.exitAct.triggered.connect(qApp.exit)#等价于qApp.quit
        self.actions["exit"].triggered.connect(self.close)

    def createMenubar(self):
        self.menus["File"] = QMenu(self.tr("&File"))
        self.menus["Edit"] = QMenu(self.tr("&Edit"))
        self.menus["Digit"] = QMenu(self.tr("&Digit"))
        self.menus["View"] = QMenu(self.tr("&View"))
        self.menus["Config"] = QMenu(self.tr("&Config"))
        self.menus["Help"] = QMenu(self.tr("&Help"))

        editMenu = QMenu(self.tr("Text"), self.menus["Edit"])
        editMenu.setIcon(QIcon(":appres.img/edit_whitepage.png"))
        editMenu.addAction(self.actions["undo"])
        editMenu.addAction(self.actions["redo"])
        # editMenu.addSeparator()
        # editMenu.addAction(self.actions["cut"])
        # editMenu.addAction(self.actions["copy"])
        # editMenu.addAction(self.actions["paste"])

        self.menus["File"].addAction(self.actions["import"])
        self.menus["File"].addAction(self.actions["replaceimage"])
        self.menus["File"].addAction(self.actions["open"])
        self.menus["File"].addAction(self.actions["save"])
        self.menus["File"].addAction(self.actions["saveas"])
        self.menus["File"].addAction(self.actions["export"])
        self.menus["File"].addAction(self.actions["close"])
        self.menus["File"].addSeparator()
        self.menus["File"].addAction(self.actions["exit"])

        self.menus["Edit"].addAction(self.actions["undo"])
        self.menus["Edit"].addAction(self.actions["redo"])

        self.menus["Digit"].addAction(self.actions["select"])
        self.menus["Digit"].addAction(self.actions["axes"])
        self.menus["Digit"].addAction(self.actions["curve"])

        self.menus["View"].addAction(self.actions["zoomin"])
        self.menus["View"].addAction(self.actions["zoomout"])
        self.menus["View"].addSeparator()
        self.menus["View"].addAction(self.actions["showgrid"])
        self.menus["View"].addAction(self.actions["showcurves"])

        self.menus["Config"].addAction(self.actions["config"])

        self.menus["Help"].addAction(self.actions["about"])

        for m in self.menus.values():
            self.menubar.addMenu(m)

    def createContexMenus(self):
        self.contexMenus["Edit"] = QMenu(self.tr("Edit"))
        self.contexMenus["Edit"].addAction(self.actions["cut"])
        self.contexMenus["Edit"].addAction(self.actions["copy"])
        self.contexMenus["Edit"].addAction(self.actions["paste"])

    def createToolbars(self):
        themeLabel = QLabel(self.tr("Theme "))
        # self.themeCombo = QComboBox()
        themeLabel.setToolTip(self.tr("Using system style."))
        self.themeCombo.setToolTip(self.tr("Select system style."))
        self.themeCombo.addItems(QStyleFactory.keys())
        self.themeCombo.setMinimumWidth(105)
        theme = QApplication.style().objectName()
        self.themeCombo.setCurrentIndex(self.themeCombo.findText(theme, Qt.MatchFixedString))
        # self.themeCombo.setEnabled(False)
        # themeCombo.activated[str].connect(qApp.setStyle)
        # themeCombo.currentTextChanged.connect(qApp.setStyle)
        # checkbox.stateChanged.connect(self.themeCombo.setEnabled)
        # checkbox.stateChanged.connect(lambda x:self.actions["DisableQss"].setChecked(checkbox.isChecked()))

        self.toolbars["Main"] = QToolBar(self.tr("Main", "toolbar"))
        self.toolbars["Main"].addWidget(themeLabel)
        self.toolbars["Main"].addWidget(self.themeCombo)

        self.toolbars["File"] = QToolBar(self.tr("File"))
        self.toolbars["File"].addAction(self.actions["import"])
        self.toolbars["File"].addAction(self.actions["open"])
        self.toolbars["File"].addAction(self.actions["save"])
        # self.toolbars["File"].addAction(self.actions["saveas"])
        self.toolbars["File"].addAction(self.actions["export"])

        self.toolbars["Edit"] = QToolBar(self.tr("Edit"))
        self.toolbars["Edit"].addAction(self.actions["undo"])
        self.toolbars["Edit"].addAction(self.actions["redo"])
        self.toolbars["Edit"].addAction(self.actions["del"])

        self.toolbars["Digitize"] = QToolBar(self.tr("Digitize"))
        self.toolbars["Digitize"].addAction(self.actions["select"])
        self.toolbars["Digitize"].addAction(self.actions["axes"])
        self.toolbars["Digitize"].addAction(self.actions["curve"])

        self.toolbars["Display"] = QToolBar(self.tr("Display"))
        self.toolbars["Display"].addAction(self.actions["zoomin"])
        self.toolbars["Display"].addAction(self.actions["zoomout"])
        self.toolbars["Display"].addAction(self.actions["showgrid"])

        self.toolbars["View"] = QToolBar(self.tr("View"))
        self.toolbars["View"].addAction(self.actions["showcurves"])

        for t in self.toolbars.values():
            self.addToolBar(t)

    def createStatusBar(self):
        self.statusbar.showMessage(self.tr("Ready"))
        # self.statusbar.addWidget(QWidget(),1)
        # self.status["date"] = QLabel()
        # self.statusbar.addPermanentWidget(self.status["date"])
        # self.status["date"].setText(QDate.currentDate().toString())
        # self.status["date"].setVisible(False)

        self.status["point"] = QLabel(self.tr("Point Coordinate: 0,0"))
        self.status["pixel"] = QLabel(self.tr("Pixel Location: 0,0"))
        self.status["point"].setMinimumWidth(200)
        self.status["pixel"].setMinimumWidth(200)
        # self.status["coding"].setAlignment(Qt.AlignCenter)
        self.statusbar.addPermanentWidget(self.status["point"])
        self.statusbar.addPermanentWidget(self.status["pixel"])

    def createDocks(self):
        self.docks["curves"] = QDockWidget(self.tr("curves"))
        self.docks["curves"].setMinimumSize(QSize(200, 200))
        self.docks["curves"].setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks["curves"])
        self.docks["curves"].visibilityChanged.connect(self.actions["showcurves"].setChecked)

        self.docktabwidget = QTabWidget(self.docks["curves"])
        self.docks["curves"].setWidget(self.docktabwidget)
        self.docktabwidget.setTabPosition(QTabWidget.South)
        self.axesTab = QScrollArea()
        self.curveTab = QSplitter(Qt.Vertical)
        self.docktabwidget.addTab(self.axesTab, "axes")
        self.docktabwidget.addTab(self.curveTab, "curve")
        self.docktabwidget.setCurrentIndex(1)

        self.axesTable = QTableView()
        self.curveTable = QTableView()
        self.pointsTable = QTableView()
        self.axesTab.setWidgetResizable(True)
        self.axesTab.setWidget(self.axesTable)
        w = QWidget()
        lay = QVBoxLayout()
        lay.setContentsMargins(0,0,0,0)
        self.curvePanelToolbar = QToolBar(self.curveTab)
        lay.addWidget(self.curvePanelToolbar)
        lay.addWidget(self.curveTable)
        w.setLayout(lay)
        self.curveTab.addWidget(w)
        self.curveTab.addWidget(self.pointsTable)
        self.curvePanelToolbar.addAction(self.actions["addcurve"])
        self.curvePanelToolbar.addAction(self.actions["renamecurve"])

    def createMainWidget(self):
        self.setCentralWidget(self.mainTabWidget)
        self.mainTabWidget.setTabBarAutoHide(True)

    def setupUiActions(self):
        self.actions["showcurves"].triggered.connect(self.docks["curves"].setVisible)
        self.themeCombo.currentTextChanged.connect(qApp.setStyle)

    ## misc func
    def updatePixelCoord(self, ptorx, y=None):
        if isinstance(ptorx, QPoint) or isinstance(ptorx, QPointF):
            self.status["pixel"].setText("Pixel Coordinate: {},{}".format(ptorx.x(), ptorx.y()))
        else:
            self.status["pixel"].setText("Pixel Coordinate: {},{}".format(ptorx, y))

    def updatePointCoord(self, ptorx, y=None):
        if isinstance(ptorx, QPoint) or isinstance(ptorx, QPointF):
            self.status["point"].setText("Point Coordinate: {:.0f},{:.0f}".format(ptorx.x(), ptorx.y()))
        else:
            self.status["point"].setText("Point Coordinate: {:.0f},{:.0f}".format(ptorx, y))
