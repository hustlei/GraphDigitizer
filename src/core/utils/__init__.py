# -*- coding: utf-8 -*-
"""util for basic tools, such as algorithm,specical string operations.

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""

import re


def incDigitStr(digitstr):
    """if '123' given, return '124'
    """
    if digitstr == "":
        return "1"
    try:
        return str(int(digitstr) + 1)
    except:
        return digitstr


def nextName(name):
    """if 'd1' given, return 'd2'
    if 'ddd' given, return 'ddd1'
    """
    if not isinstance(name, str):
        name = "curve"
    if not name[-1].isdigit():
        return name + "1"
    return re.sub(r"\d+$", lambda matchobj: incDigitStr(matchobj.group(0)), name)

def str2num(s):
    s = s.strip()
    try:
        if s.lower() == "nan":
            return None
        return float(s)
    except:
        return None

if __name__ == "__main__":
    print(nextName("aaa"))
    print(nextName("aaa12"))
