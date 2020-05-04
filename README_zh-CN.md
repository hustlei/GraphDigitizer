简体中文 | [English](README.md)

# GraphDigitizer
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c56545257f004369849d4b07f90f3f12)](https://app.codacy.com/manual/hustlei/GraphDigitizer?utm_source=github.com&utm_medium=referral&utm_content=hustlei/GraphDigitizer&utm_campaign=Badge_Grade_Dashboard)
[<img alt="Platform:win|osx|linux" src="https://raw.githubusercontent.com/hustlei/QssStylesheetEditor/master/docs/assets/badge/platform.svg?sanitize=true" onerror="this.src='https://hustlei.github.io/assets/badge/platform.svg';this.onerror=null" />](https://github.com/hustlei/GraphDigitizer)

<br>

曲线图（图片或扫描件）数字化的工具软件。

ps：本人经常遇到需要使用扫描的曲线图，但是十分不便，所以就想把曲线图数字化，变成数据表。找到了Engauge Digitizer等软件，但是呢，这些软件坐标系都只能用三个点设置，导致扫描的图片数字化后坐标系都不准，所以我就自己编写了GraphDigitizer。如果你的曲线图坐标轴都没有变形，比例很准确，用Engauge Digitizer等软件反而更方便。

# screenshot

![GUI(v0.2) screeshot](https://github.com/hustlei/GraphDigitizer/blob/master/docs/assets/screenshot/graphdigitizer_v0.2.png?raw=true  "GUI(v0.2)")

# 功能简介

+ x坐标轴及y坐标轴均可以设置多个点
+ 根据坐标轴设置，推断坐标轴各个点位置，并以网格形式显示
+ 可以缩放曲线图图片
+ 导出 csv 格式数据
+ 支持切换系统主题(xp, vista etc.)

# 支持的操作系统平台

+ Windows (maybe won't run on xp)
+ macOS
+ Linux
+ UNIX


# 安装

1. 下载 GraphDigitizer 代码
2. 运行 `pip install -r requirements.txt` 命令
3. 运行 `python bootstrapper.py` or `python app.py` 命令打开软件

# 使用步骤

1. 导入曲线图背景
2. 缩放曲线图（可以不缩放）
3. 设置坐标轴
4. 绘制曲线
5. 导出数据

# License
You can use this software for free in open source projects that are licensed under the GPL. but there is an exception: if you only use it to generate qss file for commercial product, the product's source code can be shipped with whatever license you want.

If you don't want to open your code up to the public, you can purchase a commercial license, and also should purchase a commercial license for PyQt5.
