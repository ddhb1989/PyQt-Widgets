#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Bernhard Hofer  -   Mail@Bernhard-hofer.at
#
# Example File for QtCamera
# ---------------------------------------------------------------------------
import sys
from PyQt5 import QtWidgets, uic

from QtCamera.Camera import Camera

class Example(QtWidgets.QMainWindow):
    def __init__(self):
        super(Example, self).__init__()
        uic.loadUi('Example.ui', self)
        self.show()

        _Cam = Camera()
        self.Layout.addWidget(_Cam)

    def boing(self, e):
        print(e)
app = QtWidgets.QApplication(sys.argv)
window = Example()
app.exec_()