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
import pathlib
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtMultimedia import QSound, QCamera

""" QListwidgetitem for our preview """
class QWidget_Preview(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self)
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/PreviewItem.ui', self)

""" QWidget Class for using MediaViewer """
class MediaViewer(QWidget):
    # Configurations
    m_Directory = "/"
    m_Items_Per_Row = 2
    m_Media_Suffix = '.jpg', '.jpeg','.bmp','.gif','.png','.tif'

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self)
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/MediaViewer.ui', self)

        # if valid **kwargs are available we set class vars
        for _Key in kwargs:
            if hasattr(self, _Key):
                self.__setattr__(_Key, kwargs[_Key])

        self._CreatePreviewList()

    def _CreatePreviewList(self):
        """ create the preview list """
        _Path = self.m_Directory
        def _CalculateDirectory(f_Dir:str, f_Parent_Widget=None):
            """ recursive function that creates the preview widget like a tree structure """
            for _File in os.listdir(f_Dir):
                _Path = os.path.join(f_Dir, _File)
                # Step 1: If we have a folder we create a header
                if os.path.isdir(_Path):
                    # check if there is a media file in the folder
                    _Contains_Media = False
                    for _Check in os.listdir(_Path):
                        if os.path.isfile(os.path.join(_Path, _Check)) and pathlib.Path(os.path.join(_Path, _Check)).suffix.lower() in self.m_Media_Suffix:
                            _Contains_Media = True
                            break

                    _List = QListWidget()
                    if _Contains_Media == True:
                        # add qpushbutton as a folder header
                        _Button = QPushButton()
                        _Button.setStyleSheet("margin: 5px 0px;")
                        _Button.setText(_Path.replace(self.m_Directory, ""))
                        _Icon = QIcon()
                        _Icon.addFile(os.path.dirname(os.path.realpath(__file__)) + "/Images/Folder.png")
                        _Button.setIcon(_Icon)
                        _Button.setIconSize(QSize(24, 24))
                        self.Contents_Layout.addWidget(_Button)

                        # add qlistwidget for our pictures
                        _List = QListWidget()
                        _List.setViewMode(QListView.IconMode)
                        _List.setResizeMode(QListView.Adjust)
                        self.Contents_Layout.addWidget(_List)
                    # go one folder deeper
                    _CalculateDirectory(_Path, _List)

                # Step 2: If we have a file we create a preview picture
                if pathlib.Path(_Path).suffix.lower() not in (self.m_Media_Suffix):
                    continue

                _Widget = QWidget_Preview()
                _Widget.Preview.setStyleSheet("border: 1px solid #AAA;;")
                _Widget.Preview.setAlignment(Qt.AlignCenter)

                _ParentWidth = f_Parent_Widget.width() - (self.m_Items_Per_Row * _Widget.Delete.width()) - self.m_Items_Per_Row * 4

                _Image = QImage(os.path.join(_Path)).scaledToWidth(_ParentWidth/self.m_Items_Per_Row)
                _Preview = QPixmap.fromImage(_Image)
                _Widget.Preview.setPixmap(_Preview)

                _Item = QListWidgetItem()
                _Item.setSizeHint(_Widget.sizeHint())
                f_Parent_Widget.addItem(_Item)
                f_Parent_Widget.setItemWidget(_Item, _Widget)


        _CalculateDirectory(self.m_Directory)
