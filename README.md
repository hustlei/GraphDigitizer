English | [简体中文](README_zh-CN.md)

# GraphDigitizer
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c56545257f004369849d4b07f90f3f12)](https://app.codacy.com/manual/hustlei/GraphDigitizer?utm_source=github.com&utm_medium=referral&utm_content=hustlei/GraphDigitizer&utm_campaign=Badge_Grade_Dashboard)
[<img alt="Platform:win|osx|linux" src="https://raw.githubusercontent.com/hustlei/QssStylesheetEditor/master/docs/assets/badge/platform.svg?sanitize=true" onerror="this.src='https://hustlei.github.io/assets/badge/platform.svg';this.onerror=null" />](https://github.com/hustlei/GraphDigitizer)

<br>

Digtize the graph(figure/chart) from image format, such as graph scanned from book.

# screenshot

![GUI(v0.2) screeshot](https://github.com/hustlei/GraphDigitizer/blob/master/docs/assets/screenshot/graphdigitizer_v0.2.png?raw=true  "GUI(v0.2)")

# Features

+ Setting multiple x-axis values or y-axis values
+ Display axes grid predict by x-ais and y-axis setting
+ Scale background(graph) image
+ fiting any digitized curve by polynomials
+ Export csv format curve points data
+ Switch different system themes (xp, vista etc.)

# Platform

+ Windows (maybe won't run on xp)
+ macOS
+ Linux
+ UNIX


# Install

Follow the steps as below:

1. download the GraphDigitizer Code.
2. run `pip install -r requirements.txt` install dependencies.
3. run `python bootstrapper.py` or `python app.py` to start app.

# Usage 

1. import graph image
2. scale graph(background) image
3. setting x-axis and y-axis
4. add curves
5. export digitized data

# License
You can use this software for free in open source projects that are licensed under the GPL. but there is an exception: if you only use it to generate qss file for commercial product, the product's source code can be shipped with whatever license you want.

If you don't want to open your code up to the public, you can purchase a commercial license, and also should purchase a commercial license for PyQt5.
