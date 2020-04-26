
from enum import Enum,unique

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
    plus = 3  # +
    minus = 4  # -
    vertical = 5  # |
    cross = 6  # x
    star = 7  # 米
    crossvertical = 8  # x | 结合
    squre = 9  # ■
    prism = 10  # ■ 转45°
    trangle = 11  # ▲
    circle = 12  # O

    pointincircle = 21  # . in o
    plusincircle = 22  # + in O
    crossincircle = 23  # x in O
    pluswithcircle = 24
    crosswithcircle = 25
    # . in □
    # + in □
    # x in □
