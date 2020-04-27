from PyQt5.QtCore import QObject, QSize, Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QStyle, QComboBox, QAbstractItemDelegate


class QPenStyleDelegate(QAbstractItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        test = index.data(Qt.DisplayRole)
        penStyle = index.data(Qt.UserRole)
        r = option.rect

        if (option.state & QStyle.State_Selected):
            painter.save()
            painter.setBrush(option.palette.highlight())
            painter.setPen(Qt.NoPen)
            painter.drawRect(option.rect)
            painter.setPen(QPen(option.palette.highlightedText(), 2, penStyle))
        else:
            painter.setPen(penStyle)

        painter.drawLine(0, r.y() + r.height() / 2, r.right(), r.y() + r.height() / 2)

        if (option.state & QStyle.State_Selected):
            painter.restore()

    def sizeHint(self,option,index):
        return QSize(100, 30)

class QLineComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(QPenStyleDelegate())

if __name__ == "__main__":
    from PyQt5.QtWidgets import *
    import sys
    app = QApplication(sys.argv)
    w = QLineComboBox()
    w.addItem("Solid",Qt.SolidLine)
    w.addItem("Dot",Qt.DotLine)
    w.currentIndexChanged.connect(lambda :print(w.currentData()))
    w.show()
    sys.exit(app.exec_())