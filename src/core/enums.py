# -*- coding: utf-8 -*-
"""enums for OperationMode of app and PointType of drawing points.

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""

from enum import Enum, unique
from random import random, choice, randint

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


@unique
class OpMode(Enum):
    """current mode such as: draw point, move point, move scene etc."""
    default = "default"
    select = "select"
    axesx = "axesx"
    axesy = "axesy"
    grid = "grid"
    curve = "curve"


@unique
class PointType(Enum):
    none = 0  # None
    point = 1  # 点 .
    bigpoint = 2  # ●
    plus = 3  # +     ***
    minus = 4  # -
    vertical = 5  # |
    cross = 6  # x    ***
    star = 7  # 米
    crossvertical = 8  # x | 结合
    squre = 9  # ■
    prism = 10  # ■ 转45°
    trangle = 11  # ▲
    circle = 12  # O

    pointincircle = 21  # . in o   ***
    plusincircle = 22  # + in O   ***
    crossincircle = 23  # x in O  ***
    pluswithcircle = 24  # ***
    crosswithcircle = 25  # ***
    # . in □
    # + in □
    # x in □


colorlist = [Qt.red, Qt.blue, Qt.cyan, Qt.green, Qt.white, Qt.darkRed, Qt.darkGreen, Qt.darkBlue, Qt.cyan, Qt.darkCyan,
             Qt.magenta, Qt.darkMagenta, Qt.yellow, Qt.darkYellow, Qt.green, QColor("pink"), QColor("gold"),
             QColor("orangered"), QColor("orange"), QColor("brown"), QColor("chocolate")]
pointTypeList = [PointType.plus, PointType.cross, PointType.pointincircle, PointType.plusincircle,
                 PointType.crossincircle, PointType.pluswithcircle, PointType.crosswithcircle]


class RandItem():
    clr = None
    ptType = None

    def __init__(self, items):
        self.items = items
        self.func = self.nextitem(items)

    def updateItem(self, items):
        self.items = items
        self.func = self.nextitem(items)

    def nextitem(self,items):
        i = 0
        j = len(items)
        while i < j:
            yield items[i]
            i += 1
            if i == j:
                i = 0

    def next(self):
        return next(self.func)

    def rand(self):
        return choice(self.items)

    @staticmethod
    def nextColor():
        if RandItem.clr is None:
            RandItem.clr = RandItem(colorlist)
        return RandItem.clr.next()

    @staticmethod
    def RandColor():
        return choice(colorlist)

    @staticmethod
    def nextPointType():
        if RandItem.ptType is None:
            RandItem.ptType = RandItem(pointTypeList)
        return RandItem.ptType.next()

    @staticmethod
    def RandPointType():
        return choice(pointTypeList)


if __name__ == "__main__":
    print(RandItem.nextColor())
    print(RandItem.nextColor())
    print(RandItem.nextColor())
    print(RandItem.RandColor())
    print(RandItem.RandColor())
    print(RandItem.RandColor())
