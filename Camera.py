#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Bernhard Hofer  -   Mail@Bernhard-hofer.at
#
# Example File for QtCamera
# ---------------------------------------------------------------------------
import sys
import os
from PyQt5 import QtWidgets, uic
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
import sys
sys.excepthook = except_hook
from QtCamera.Camera import Camera

class Example(QtWidgets.QMainWindow):
    def __init__(self):
        super(Example, self).__init__()
        uic.loadUi('Example.ui', self)
        self.show()

        _Cam = Camera(m_Path_Save=os.path.dirname(os.path.realpath(__file__))+ "/Images",
                      m_Barcode_Scan_Active=True,
                      m_Sound_Active=True,
                      m_Show_Preview=True,
                      m_Show_Folders=True,
                      m_Preview_Scale=80,
                      m_Force_Cam=1)
        _Cam.m_Signal_Barcode_Found.connect(self.Bar)
        self.Layout.addWidget(_Cam)

    def Bar(self, result):
        print(result)

app = QtWidgets.QApplication(sys.argv)
window = Example()
app.exec_()