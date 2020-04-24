from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout, QLabel, QLineEdit, QCheckBox,
                             QPushButton)
from PyQt5.QtCore import Qt, QPointF


class Axesdialog(QDialog):
    """dialog for setting axes coords"""
    current = None
    coordgeted = (None, None)

    @classmethod
    def getCoord(cls):
        if not cls.current:
            cls.current = Axesdialog()
        cls.coordgeted = (None, None)
        cls.current.exec_()
        return cls.coordgeted

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setWindowTitle(self.tr("axes coordinate"))
        self.resize(400,180)
        self.initUI()

    def initUI(self):
        vboxLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()
        formLayout = QFormLayout()

        titleLabel = QLabel("Please set at least 1 axis coordinate")
        self.xCheckBox = QCheckBox("set x coord:")
        self.yCheckBox = QCheckBox("set y coord:")
        self.xCheckBox.setChecked(True)
        self.yCheckBox.setChecked(True)
        self.xLineEdit = QLineEdit()
        self.yLineEdit = QLineEdit()
        okBtn = QPushButton(self.tr("OK"))
        okBtn.setDefault(True)
        cancelBtn = QPushButton(self.tr("Cancel"))

        formLayout.addRow(self.xCheckBox,self.xLineEdit)
        formLayout.addRow(self.yCheckBox,self.yLineEdit)
        hboxLayout.addStretch(1)
        hboxLayout.addWidget(okBtn)
        hboxLayout.addWidget(cancelBtn)
        vboxLayout.addStretch(1)
        vboxLayout.addWidget(titleLabel)
        vboxLayout.addStretch(1)
        vboxLayout.addLayout(formLayout)
        vboxLayout.addStretch(3)
        vboxLayout.addLayout(hboxLayout)
        self.setLayout(vboxLayout)

        self.xCheckBox.stateChanged.connect(self.xCheckChanged)
        self.yCheckBox.stateChanged.connect(self.yCheckChanged)
        okBtn.clicked.connect(self.apply)
        cancelBtn.clicked.connect(self.cancel)

    def showEvent(self, event):
        self.xCheckBox.setChecked(True)
        self.yCheckBox.setChecked(True)
        self.xLineEdit.setText("")
        self.yLineEdit.setText("")
        super().showEvent(event)

    def xCheckChanged(self, checked):
        self.xLineEdit.setEnabled(checked)
        if not checked:
            self.yCheckBox.setChecked(True)

    def yCheckChanged(self, checked):
        self.yLineEdit.setEnabled(checked)
        if not checked:
            self.xCheckBox.setChecked(True)

    def apply(self):
        if self.xCheckBox.isChecked():
            val = self.xLineEdit.text().strip()
            if val == "":
                x = None
            else:
                try:
                    x = float(val)
                except:
                    self.xLineEdit.setFocus()
                    self.xLineEdit.selectAll()
                    return
        if self.yCheckBox.isChecked():
            val = self.yLineEdit.text().strip()
            if val == "":
                y = None
            else:
                try:
                    y = float(val)
                except:
                    self.yLineEdit.setFocus()
                    self.yLineEdit.selectAll()
                    return
        Axesdialog.coordgeted = (x,y)
        self.close()
        return (x,y)

    def cancel(self):
        self.close()
        return (None, None)
