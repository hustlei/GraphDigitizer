# -*- coding: utf-8 -*-
"""Basic algebra Algorithm

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""

from scipy import interpolate
import numpy as np


def distToPoint(point, p):
    """return distance between point and p"""
    x, y = point
    x1, y1 = p
    return ((x1 - x) ** 2 + (y1 - y) ** 2) ** 0.5


def distToLine(point, p1, p2):
    """return distance from point to line(p1 to p2)"""
    x, y = point
    x1, y1 = p1
    x2, y2 = p2
    # vector
    vec1x, vec1y = x - x1, y - y1
    vec2x, vec2y = x2 - x1, y2 - y1
    # length of verctor and x for vecter
    modvec1x2 = abs(vec1x * vec2y - vec1y * vec2x)
    modvec1 = (vec1x ** 2 + vec1y ** 2) ** 0.5
    modvec2 = (vec2x ** 2 + vec2y ** 2) ** 0.5
    #
    sinx = modvec1x2 / modvec1 / modvec2
    #
    dist = modvec1 * sinx
    return dist


def perpendOnLine(point, p1, p2):
    """if the perpendicular foot from point to line(p1 to p2) is on line(p1 to p2), return 0
    if foot is outof line and outside of p1 return -1
    if foot is outof line and outside of p2 return 1
    """
    lineLenth = distToPoint(p1, p2)
    x, y = point
    x1, y1 = p1
    x2, y2 = p2
    # vector
    vec1x, vec1y = x - x1, y - y1
    vec2x, vec2y = x2 - x1, y2 - y1

    abcosx = vec1x * vec2x + vec1y * vec2y
    l2 = abcosx / lineLenth
    if l2 < 0:
        return -1
    if l2 > lineLenth:
        return 1
    return 0


def interp(xlist, ylist, newxlist, maxkind=2):
    d1 = {}
    for i in range(len(xlist)):
        d1[xlist[i]] = ylist[i]
    xlist = sorted(d1)
    ylist = []
    for x in xlist:
        ylist.append(d1[x])

    if len(xlist) <= maxkind:
        kind = len(xlist) - 1
    else:
        kind = maxkind
    yarray = interpolate.UnivariateSpline(xlist, ylist, k=kind, s=0)(newxlist)
    return list(np.round(yarray, 5))


def pointInsertPosition(ptitem, ptitems):
    """get the nearest position for new point
    return the predicted new index for new point in pointObj
    """
    l = len(ptitems)
    if l == 0:
        return 0
    if l == 1:
        return 1
    index = 0

    p = (ptitem.x(), ptitem.y())
    p1 = (ptitems[0].x(), ptitems[0].y())
    p2 = (ptitems[1].x(), ptitems[1].y())
    mindist = distToLine(p, p1, p2)
    for i in range(1, l - 1):
        p1 = p2
        p2 = (ptitems[i + 1].x(), ptitems[i + 1].y())
        dist = distToLine(p, p1, p2)
        pos = perpendOnLine(p, p1, p2)
        if pos == 0:
            if dist < mindist:
                mindist = dist
                index = i
    if index == 0:
        p1 = (ptitems[0].x(), ptitems[0].y())
        p2 = (ptitems[1].x(), ptitems[1].y())
        pos = perpendOnLine(p, p1, p2)
        dist = distToLine(p, p1, p2)
        length = distToPoint(p1, p2)
        if pos == 0 and dist < length / 4:
            return 1
        pstart = (ptitems[0].x(), ptitems[0].y())
        pend = (ptitems[-1].x(), ptitems[-1].y())
        d0 = distToPoint(p, pstart)
        d1 = distToPoint(p, pend)
        if pos == -1 and d0 < d1:
            return 0
        return l
    else:
        p1 = (ptitems[index].x(), ptitems[index].y())
        p2 = (ptitems[index + 1].x(), ptitems[index + 1].y())
        dist = distToLine(p, p1, p2)
        lenth = distToPoint(p1, p2)
        if dist < lenth / 2:
            return index + 1
    return l


def polyfit(x, y, degree=2):
    x = np.array(x)
    y = np.array(y)
    # xnew=np.linspace(15,20,4)
    # xnew = np.arange(0.5, 0.81, 0.005)
    if degree >= len(x):
        degree = len(x) - 1
    if len(x) < 2 or degree < 1:
        return [], []

    polyrst = np.polyfit(x, y, degree)

    error = np.abs(calPoly(polyrst, x) - y)

    return polyrst, error


def poly2str(poly, precision=5):
    degree = len(poly) - 1
    d = degree + 1
    text = ""
    for i in range(d):
        if i == 0:
            text += "{}x^{}".format(round(poly[i], precision), degree)
        elif degree == i:
            text += "{:+f}".format(round(poly[i], precision))
        elif degree - i == 1:
            text += "{:+f}x".format(round(poly[i], precision))
        else:
            text += "{:+f}x^{}".format(round(poly[i], precision), degree - i)
    return text


def calPoly(poly, x):
    degree = len(poly) - 1
    # def f1(rst,degree):
    y = 0
    d = degree + 1
    for i in range(d):
        y += poly[i] * x ** (degree - i)
    return y


if __name__ == "__main__":
    print(distToPoint((1, 1), (2, 2)))  # 1.414
    print(distToLine((8, 8), (5, 5), (10, 5)))  # 3
    print(perpendOnLine((3, 8), (5, 5), (10, 5)))  # -1
    print(perpendOnLine((8, 8), (5, 5), (10, 5)))  # 0
    print(perpendOnLine((13, 8), (5, 5), (10, 5)))  # 1

    print(perpendOnLine((1, 1), (2, 2), (3, 3)))  # -1

    print(interp([0, 2], [0, 2], [1, 4]))  # 1,4
    print(interp([2, 0], [2, 0], [1, 4]))  # 1,4
