#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Bernhard Hofer  -   bernhard.hofer@voestalpine.com
#
# Camera Widget with integrated Barcode scanner and the ability to take pictures
# and videos
#
# modules needed
# pip install opencv-python
# pip install pyzbar
# TODO: Folder organisation!
# Check if Preview deleteion works and file gets deleted
# ---------------------------------------------------------------------------
import cv2
import time
import os
from glob import glob
from pyzbar.pyzbar import decode

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtMultimedia import QSound

import numpy as np

class PopUp_NewFolder(QtWidgets.QWidget):
    m_Signal_FolderName = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi('QtCamera/Interface/PopUp-NewFolder.ui', self)
        self.show()

        # center window
        self.setContentsMargins(0, 0, 0, 0)
        self.move(parent.frameGeometry().center()-self.frameGeometry().center())

        # add bindings
        self.pushButton_Save.clicked.connect(lambda e, x=self.lineEdit_FolderName: self.m_Signal_FolderName.emit(self.lineEdit_FolderName.text()))
        self.pushButton_Save.clicked.connect(lambda e: self.deleteLater())
        self.pushButton_Close.clicked.connect(lambda e: self.deleteLater())

class VideoThread(QThread):
    # define some signals
    m_Signal_Frame = pyqtSignal(np.ndarray)         # signal that contains the image
    m_Signal_CamerasAvailable = pyqtSignal(list)    # signal available cameras
    m_Signal_Codes = pyqtSignal(list)                # signal qr codes
    m_Signal_Picture_Taken = pyqtSignal(str)        # signal returns name of picture

    # config variables
    m_Barcode_Scan = True
    m_Path_Save = "/"

    # class vars
    m_Cameras_Available = []
    m_Camera_Current = 0
    m_Camera_Run = True

    def run(self):
        # get available cameras
        self.m_Cameras_Available = self._GetAvailableCameras()
        self.m_Signal_CamerasAvailable.emit(self.m_Cameras_Available)

        # start cam
        self.m_Camera_Run = True
        self.m_Cap = cv2.VideoCapture(self.m_Camera_Current, cv2.CAP_DSHOW)
        while self.m_Camera_Run:
            # get image from cam
            ret, self.m_CV_Img = self.m_Cap.read()

            if ret != True: # continue if cam is not ready
                continue

            self.m_Signal_Frame.emit(self.m_CV_Img)

            # continue if no barcodes to scan
            if self.m_Barcode_Scan == False:
                continue

            # scan for qr and barcode
            _Codes = decode(self.m_CV_Img)
            if len(_Codes) > 0:
                _List = []
                for _Code in _Codes:
                    _List.append(_Code.data.decode('utf-8'))
                self.m_Signal_Codes.emit(_List)
                self.StopCamera()

    def TakePicture(self):
        """ take/save a picture """
        if not hasattr(self, "m_CV_Img"): # webcam is not loaded
            return

        # try to create directory
        if not os.path.exists(self.m_Path_Save):
            os.makedirs(self.m_Path_Save)

        try:
            _Filename = self.m_Path_Save + '\\' + str(int(time.time())) + '.jpg'
            cv2.imwrite(_Filename, self.m_CV_Img)
            self.m_Signal_Picture_Taken.emit(_Filename)
        except Exception as e:
            print(e)


    def StopCamera(self):
        """ stop camera """
        self.m_Camera_Run = False

    def ChangeCamera(self):
        """ change camera index """
        self.m_Camera_Current = 0 if self.m_Camera_Current >= len(self.m_Cameras_Available)-1 else self.m_Camera_Current+1
        self.m_Cap = cv2.VideoCapture(self.m_Camera_Current, cv2.CAP_DSHOW)

    def _GetAvailableCameras(self):
        """
        get all available cameras
        :return: list with all available camera indexes
        """
        _Cameras = []
        _i = 0
        while True:
            self.m_Cap = cv2.VideoCapture(_i, cv2.CAP_DSHOW)
            # no camera is available we break the loop
            if not self.m_Cap.read()[0]:
                break
            # if a cam is available we continue the loop
            _Cameras.append(_i)
            self.m_Cap.release()
            _i += 1
        return _Cameras

class Camera(QtWidgets.QWidget):
    # Configurations
    m_Barcode_Scan_Active = False                   # True/False - activates barcode/qrscan
    m_Sound_Active = True                           # True/False - activates sound
    m_Path_Save = "/"                               # Path where pictures should be saved
    m_Show_Preview = True                           # hide or show the taken pictures
    m_Show_Folders = True                           # hide or show the folder tree

    # signals
    m_Signal_Barcode_Found = pyqtSignal(list)       # signal if a barcodes was found

    # Status and cache vars
    m_Cameras_Available = []                        # list of all available camera indexes

    # Threads
    m_Thread_Video = VideoThread()

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi('QtCamera/Interface/Camera.ui', self)

        # if valid **kwargs are available we set class vars
        for _Key in kwargs:
            if hasattr(self, _Key):
                self.__setattr__(_Key, kwargs[_Key])

        # add bindings
        self.pushButton_Close.clicked.connect(self._KillCamera)
        self.pushButton_Change.clicked.connect(self._ChangeCamera)
        self.pushButton_Picture.clicked.connect(self._TakePicture)
        self.Folder_Tree.itemClicked.connect(self._Event_Folder_Click)

        # prepare interface
        self.Hide_Button_Change()
        self.Hide_Button_Video()
        if self.m_Show_Preview == False:
            self.Hide_Preview()
        else:
            self.Show_Preview()
        if self.m_Show_Folders == False:
            self.Hide_Folders()
        else:
            self.Show_Folders()
            self._CreateDirectoryTree()

        # start camera thread
        self.m_Thread_Video.m_Path_Save = self.m_Path_Save
        self.m_Thread_Video.m_Barcode_Scan = self.m_Barcode_Scan_Active
        self.m_Thread_Video.m_Sound_Active = self.m_Sound_Active

        # connect signals
        self.m_Thread_Video.m_Signal_Frame.connect(self._UpdateFrame)   # updates frame
        self.m_Thread_Video.m_Signal_CamerasAvailable.connect(self._UpdateAvailableCameras) # updates interfac
        self.m_Thread_Video.m_Signal_Codes.connect(self._CodesFound)    # some barcodes found
        self.m_Thread_Video.m_Signal_Picture_Taken.connect(self._PictureTaken)  # picture was taken

        self.m_Thread_Video.start()

    def _CreateDirectoryTree(self):
        """ create directory tree """
        self.Folder_Tree.clear()
        def _CreateTree(f_Path, f_Parent, _Depth=0):
            _Item = QtWidgets.QTreeWidgetItem(f_Parent)
            _Item.setText(0, "Neuen Ordner erstellen...")

            _Dir = glob(f_Path + "/*/", recursive=True)
            if len(_Dir) == 0:
                return

            for _Folder in _Dir:
                _Item = QtWidgets.QTreeWidgetItem(f_Parent)
                _Item.setText(0, os.path.basename(os.path.normpath(_Folder)))

                _CreateTree(_Folder, _Item)

        _CreateTree(self.m_Path_Save, self.Folder_Tree)

    def _Event_Folder_Click(self, f_Event):
        _Path = self.m_Path_Save

        _Item = f_Event
        while _Item.parent() is not None:
            _Path += "/" + _Item.parent().text(0)
            _Item = _Item.parent()

        # create a new folder
        if f_Event.text(0) == "Neuen Ordner erstellen...":
            def _CreateFolder(f_Folder):
                print(_Path + "/" + f_Folder)
                try:
                    os.mkdir(_Path + "/" + f_Folder)
                    self.m_Thread_Video.m_Path_Save = _Path + "/" + f_Folder
                except:
                    QtWidgets.QMessageBox.information(self, "Fehler", "Der Ordner konnte nicht erstellt werden.!" + str(e), QtWidgets.QMessageBox.Ok)
                self._CreateDirectoryTree()

            _PopUp = PopUp_NewFolder(self)
            _PopUp.m_Signal_FolderName.connect(_CreateFolder)
        else: # set folder as saving directory
            _Path += "/" + f_Event.text(0)
            self.m_Thread_Video.m_Path_Save = _Path

    def _CodesFound(self, f_Result:list):
        """
        some codes are found in the scanner
        :param f_Result: list with all found codes
        :return:
        """
        if self.m_Sound_Active == True:
            QSound.play("QtCamera/Sounds/Scan.wav")

        self.m_Signal_Barcode_Found.emit(f_Result)
        self._KillCamera()

    def _PictureTaken(self, f_Result:str):
        """
        picture was taken
        :param f_Result: path to file
        :return:
        """
        if self.m_Sound_Active == True:
            QSound.play("QtCamera/Sounds/Shutter.wav")

        _Frame = QtWidgets.QFrame()
        _VLayout = QtWidgets.QVBoxLayout(_Frame)
        # preview picture
        _Picture = QImage(f_Result).scaledToWidth(200, Qt.FastTransformation)
        _Label = QtWidgets.QLabel()
        _Label.setPixmap(QPixmap.fromImage(_Picture))
        _VLayout.addWidget(_Label)

        # add delete button
        _Button = QtWidgets.QPushButton()
        _Button.setText("Bild löschen")
        _Button.mouseReleaseEvent = lambda e, x=_Frame, y=f_Result: self._DeletePictureFromPreview(x, y)

        _VLayout.addWidget(_Button)
        self.Preview_Layout.insertWidget(0, _Frame)

    def _UpdateFrame(self, f_CV_Img):
        """Updates the image_label with a new opencv image"""
        rgb_image = cv2.cvtColor(f_CV_Img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(1920, 1080, Qt.KeepAspectRatio)
        self.CameraViewer.setPixmap(QPixmap.fromImage(p))

    def _DeletePictureFromPreview(self, f_Frame:QtWidgets.QFrame, f_File:str):
        """
        delete a picture from the preview list
        :param f_Frame: Frame to delete
        :param f_File: filename to delete
        :return:
        """
        _R = QtWidgets.QMessageBox.question(self, 'Bist du dir sicher?', "Willst du dieses Bild wirklich löschen?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if _R == QtWidgets.QMessageBox.No:
            return

        # delete frame
        f_Frame.deleteLater()

        #delete file
        try:
            os.remove(f_File)
        except:
            QtWidgets.QMessageBox.information(self, "Fehler", "Die Datei konnte nicht gelöscht werden.\nDer Zugriff wurde verweigert!", QtWidgets.QMessageBox.Ok)

    def _KillCamera(self):
        """ kill camera """
        # emit signal
        self.m_Signal_Kill.emit(True)
        self.m_Thread_Video.StopCamera()

    def _ChangeCamera(self):
        """ kill camera """
        self.m_Thread_Video.ChangeCamera()

    def _TakePicture(self):
        """ Take a picture """
        self.m_Thread_Video.TakePicture()


    def _UpdateAvailableCameras(self, f_Result:list):
        """ connected method for Video thread that returns available cameras """
        # only one cam -> hide change cam button
        self.m_Cameras_Available = f_Result
        if len(self.m_Cameras_Available) > 1:
            self.pushButton_Change.show()

    """
    Public methods for some manipulations
    """

    def Hide_Button_Close(self):
        """ hides the close button """
        self.pushButton_Close.hide()

    def Hide_Button_Change(self):
        """ hides the change cam button """
        self.pushButton_Change.hide()

    def Hide_Button_Video(self):
        """ hides the take video button """
        self.pushButton_Video.hide()

    def Hide_Button_Picture(self):
        """ hides the take picture button """
        self.pushButton_Close.hide()

    def Hide_Preview(self):
        """ hides preview of taken pictures """
        self.Preview_Header.hide()
        self.Preview_Scrollarea.hide()

    def Hide_Folders(self):
        """ hides directory tree """
        self.Folder_Header.hide()
        self.Folder_Scrollarea.hide()

    def Show_Button_Close(self):
        """ show the close button """
        self.pushButton_Close.show()

    def Show_Button_Change(self):
        """ show the change cam button """
        self.pushButton_Change.show()

    def Show_Button_Video(self):
        """ show the take video button """
        self.pushButton_Video.show()

    def Show_Button_Picture(self):
        """ show the take picture button """
        self.pushButton_Close.show()

    def Show_Preview(self):
        """ show preview of taken pictures """
        self.Preview_Header.show()
        self.Preview_Scrollarea.show()

    def Show_Folders(self):
        """ show directory tree """
        self.Folder_Header.show()
        self.Folder_Scrollarea.show()