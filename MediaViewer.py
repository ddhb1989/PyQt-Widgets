#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Bernhard Hofer  -   Mail@Bernhard-Hofer.at
#
# Example File for QtCamera
# ---------------------------------------------------------------------------
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
import sys
sys.excepthook = except_hook

import os
from PyQt5 import QtWidgets, uic
from QtMediaViewer.MediaViewer import MediaViewer

class Example(QtWidgets.QMainWindow):
    def __init__(self):
        super(Example, self).__init__()
        uic.loadUi('Example.ui', self)
        self.show()
        print(os.path.dirname(os.path.realpath(__file__))+ "/QtMediaViewer/")
        _Viewer = MediaViewer(m_Directory=r"J:\ETZ\2_FB\1_EMaschinen\2_M E-Maschinen\16_EHW_Workflow\2_Offene Auftraege\80038415",#os.path.dirname(os.path.realpath(__file__)) + "/QtMediaViewer/Testalbum",
                              m_PreviewHeight=100)

        self.Layout.addWidget(_Viewer)



app = QtWidgets.QApplication(sys.argv)
window = Example()
app.exec_()