#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Bernhard Hofer  -   Mail@Bernhard-Hofer.at
#
# Media Viewer Widget
#
# IMPORTANT: os.listdir is the fastest way to scan directories
#
# TODO: Dont Forget QFileSystemwatcher for automatic reloading if directorry changes
# ---------------------------------------------------------------------------
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtMultimedia import QSound, QCamera


""" QWidget Class for using MediaViewer """
class MediaViewer(QtWidgets.QWidget):
    # Configurations
    m_Directory = "/"

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/MediaViewer.ui', self)

        # if valid **kwargs are available we set class vars
        for _Key in kwargs:
            if hasattr(self, _Key):
                self.__setattr__(_Key, kwargs[_Key])

        self._CreatePreviewList()

    def _CreatePreviewList(self):
        """ create the preview list """
        _Path = self.m_Directory
        def _CalculateDirectory(_Dir):
            """ recursive function that creates the preview widget like a tree structure """
            for _File in os.listdir(_Dir):
                _Path = os.path.join(_Dir, _File)
                # Step 1: If we have a folder we create a header
                if os.path.isdir(_Path):
                    _Button = QtWidgets.QPushButton()
                    _Button.setText(_Path.replace(self.m_Directory, ""))
                    _Icon = QIcon()
                    _Icon.addFile(os.path.dirname(os.path.realpath(__file__)) + "/Images/Folder.png")
                    _Button.setIcon(_Icon)
                    _Button.setIconSize(QSize(24, 24))

                    self.Contents_Layout.addWidget(_Button)

                    # go one folder deeper
                    _CalculateDirectory(_Path)

                # Step 2: If we have a file we create a preview picture

            """for _File in f_Files:
                _Path = os.path.join(_Path, _File)
                if os.path.isdir(_Path):
                    print(_Path)
                    _CalculateDirectory(os.listdir(_Path))"""

        _CalculateDirectory(self.m_Directory)
