#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Bernhard Hofer  -   Mail@Bernhard-Hofer.at
#
# QtMediaWidget QThreads
# ---------------------------------------------------------------------------
import os
import cv2
import mimetypes
import stat
from PyQt5.Qt import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage


"""
Load all Files from a Folder
"""
class Files_LoadAllFilesFromFolder(QThread):

    m_Directory: str = "/"     # folder that we are going through

    m_Structure: dict = {}      # data holder for our files

    m_Signal_Result = pyqtSignal(dict)

    def run(self):
        self.m_Structure = {}
        self._Recursive_Walk(self.m_Directory)
        self.m_Signal_Result.emit(self.m_Structure)

    def _HasHiddenAttribute(self, f_Path: str):
        """
        check if a file or folder has hidden attributes
        :param f_Path: path to file/folder
        :return:
        """
        try: # try to get stats... or hide file anyway
            return bool(os.stat(f_Path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
        except:
            return True

    def _Recursive_Walk(self, f_Dir: str=""):
        """ walk through a directory and fill our m_Structure """
        if not os.path.isdir(f_Dir):
            raise ValueError("'{}' as var f_Dir in method Qthread Files_LoadAllFilesFromFolder::_Recursive_Walk must be a directory".format(f_Dir))

        # add relative path to our m_Structure
        _Relative_Path = f_Dir.replace(self.m_Directory, "")
        if _Relative_Path not in self.m_Structure:
            self.m_Structure[_Relative_Path] = []

        # load files from folder
        for _File in os.listdir(f_Dir):
            # skip hidden files and folders
            if self._HasHiddenAttribute(os.path.join(f_Dir, _File)):
                continue

            # folder: go recursive
            if os.path.isdir(os.path.join(f_Dir, _File)):
                self._Recursive_Walk(os.path.join(f_Dir, _File))

            # if you are not a file we dont need ya! Go away!
            if mimetypes.guess_type(os.path.join(f_Dir, _File))[0] == None:
                continue

            # no video or image? Go away
            _Type = mimetypes.guess_type(os.path.join(f_Dir, _File))[0].split("/")[0]
            if _Type not in ("video", "image"):
                continue

            # WTF are you?
            if not os.path.isfile(os.path.join(f_Dir, _File)):
                continue

            self.m_Structure[_Relative_Path].append(os.path.join(_Relative_Path, _File))

        # check if this folder was empty and remove it again from list
        if len(self.m_Structure[_Relative_Path]) == 0:
            del self.m_Structure[_Relative_Path]


"""
Calculate a Preview Image
"""
class Files_CalculatePreview(QThread):
    m_File: str = ""
    m_PreviewHeight: int = 0                                  # size of the preview images... got from QTMediaViewer:m_PreviewHeight
    m_Signal_Preview: pyqtSignal = pyqtSignal(QPixmap)      # signal for the preview image
    m_Signal_MediaType: str = pyqtSignal(str)               # signal with the label of the image type

    def run(self):
        """ try to create a preview from video.. if it fails we think it is a picture"""
        _MimeType = mimetypes.guess_type(self.m_File)[0]
        if _MimeType.startswith('image'):
            _Image = QImage(self.m_File, _MimeType.split("/")[1])
            _Image = _Image.scaledToHeight(self.m_PreviewHeight, Qt.FastTransformation)
            _Preview = QPixmap.fromImage(_Image)
            self.m_Signal_Preview.emit(_Preview)
            self.m_Signal_MediaType.emit("picture")

        if _MimeType.startswith('video'):
            _Cap = cv2.VideoCapture(self.m_File)
            _Cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            _, _Image = _Cap.retrieve()
            rgb_image = cv2.cvtColor(_Image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            _Image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            _Image = _Image.scaledToHeight(self.m_PreviewHeight, Qt.FastTransformation)

            self.m_Signal_Preview.emit(QPixmap.fromImage(_Image))
            self.m_Signal_MediaType.emit("video")
            cv2.destroyAllWindows()

"""
Rename a File on the Fly
"""
class File_OnTheFlyRename(QThread):
    # needed vars
    m_Original: str = ""    # path to original file
    m_NewName: str = ""         # how should we rename it?

    m_Signal_NewName: pyqtSignal = pyqtSignal(str)  # signal with the new filename when everything works fine
    m_Signal_Error: pyqtSignal = pyqtSignal(str)    # error message if something went wrong

    def run(self):
        try:
            os.rename(self.m_Original, self.m_NewName)
            self.m_Signal_NewName.emit(self.m_NewName)
        except Exception as e:
            self.m_Signal_Error.emit("Datei konnten nicht umbenannt werden.\n\n{}".format(e))
