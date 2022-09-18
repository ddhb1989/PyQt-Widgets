#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Bernhard Hofer  -   Mail@Bernhard-hofer.at
#
# Example File for QtSnake
# ---------------------------------------------------------------------------
import sys
from PyQt5 import QtWidgets, uic

from QtSnake import Game

class Example(QtWidgets.QMainWindow):
    def __init__(self):
        super(Example, self).__init__()
        uic.loadUi('Example.ui', self)
        self.show()

        self.Layout.addWidget(Game.Game())

app = QtWidgets.QApplication(sys.argv)
window = Example()
app.exec_()