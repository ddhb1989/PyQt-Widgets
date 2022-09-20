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

        _Cam = Camera(m_Path_Save=r"C:\Users\V165994\Documents\GitHub\PyQt-Widgets\Images",
                      m_Barcode_Scan_Active=True,
                      m_Sound_Active=True,
                      m_Show_Preview=True,
                      m_Show_Folders=True)
        _Cam.m_Signal_Barcode_Found.connect(self.Bar)
        self.Layout.addWidget(_Cam)

    def Bar(self, result):
        print(result)

app = QtWidgets.QApplication(sys.argv)
window = Example()
app.exec_()