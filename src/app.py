#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Class for application start

App class wrapped a QApplication, which will show splash and start gui.

Copyright (c) 2020 lileilei <hustlei@sina.cn>
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from core.mainwin import MainWin

os.chdir(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class App(QApplication):
    """Application to load splash and mainwindow"""
    def __init__(self):
        super().__init__(sys.argv)
        self.windows = {}
        # sys.setrecursionlimit(1500)

    def run(self, startEventLoop=True):
        """run the app, show splash and mainwindow

        Args:
            startEventLoop: if true, it will not start event loop, just for pytest
        """
        print("starting...")
        # Language.setTrans()
        # splash = SplashScreen("res/splash.png")
        # splash.loadProgress()
        self.windows["main"] = MainWin()
        self.windows["main"].show()
        # splash.finish(self.windows["main"])
        if startEventLoop:
            sys.exit(self.exec_())


def main():
    """main function for the program"""
    App().run()


if __name__ == "__main__":
    main()
