
import re

def incDigitStr(digitstr):
    """if '123' given, return '124'
    """
    if digitstr == "":
        return "1"
    try:
        return str(int(digitstr)+1)
    except:
        return digitstr

def nextName(name):
    """if 'd1' given, return 'd2'
    if 'ddd' given, return 'ddd1'
    """
    if not isinstance(name, str):
        return None
    if not name[-1].isdigit():
        return name+"1"
    return re.sub(r"\d+$", lambda matchobj: incDigitStr(matchobj.group(0)), name)


if __name__ == "__main__":
    print(nextName("aaa"))
    print(nextName("aaa12"))