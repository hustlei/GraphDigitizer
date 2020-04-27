# -*- coding: utf-8 -*-
"""Basic algebra Algorithm

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""

from scipy import interpolate


def distToPoint(point, p):
    """return distance between point and p"""
    x, y = point
    x1, y1 = p
    return ((x1 - x)**2 + (y1 - y)**2)**0.5


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
    modvec1 = (vec1x**2 + vec1y**2)**0.5
    modvec2 = (vec2x**2 + vec2y**2)**0.5
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


def interp(xlist, ylist, newxlist, maxkind=3):
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
    return list(yarray)


if __name__ == "__main__":
    print(distToPoint((1, 1), (2, 2)))  # 1.414
    print(distToLine((8, 8), (5, 5), (10, 5)))  # 3
    print(perpendOnLine((3, 8), (5, 5), (10, 5)))  # -1
    print(perpendOnLine((8, 8), (5, 5), (10, 5)))  # 0
    print(perpendOnLine((13, 8), (5, 5), (10, 5)))  # 1

    print(perpendOnLine((1, 1), (2, 2), (3, 3)))  # -1

    print(interp([0, 2], [0, 2], [1, 4]))  # 1,4
    print(interp([2, 0], [2, 0], [1, 4]))  # 1,4
