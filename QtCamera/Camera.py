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
# ---------------------------------------------------------------------------
import cv2
from pyzbar.pyzbar import decode

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, Qt
from PyQt5.QtGui import QImage,QPixmap

import numpy as np

class VideoThread(QThread):
    m_Signal_Frame = pyqtSignal(np.ndarray)         # signal that contains the image
    m_Signal_CamerasAvailable = pyqtSignal(list)    # signal available cameras
    m_Signal_Codes = pyqtSignal(list)               # signal qr codes

    m_Cameras_Available = []
    m_Camera_Current = 0
    m_Camera_Run = True

    m_Barcode_Scan = True

    def run(self):
        # get available cameras
        self.m_Cameras_Available = self._GetAvailableCameras()
        self.m_Signal_CamerasAvailable.emit(self.m_Cameras_Available)

        # start cam
        self.m_Camera_Run = True
        self.m_Cap = cv2.VideoCapture(self.m_Camera_Current, cv2.CAP_DSHOW)
        while self.m_Camera_Run:
            ret, cv_img = self.m_Cap.read()
            if ret != True:
                continue

            self.m_Signal_Frame.emit(cv_img)

            # continue if no barcodes to scan
            if self.m_Barcode_Scan == False:
                continue

            # scan for qr and barcode
            for _Barcode in decode(cv_img):
                print(_Barcode)
                self.m_Signal_Codes.emit(_Barcode.data.decode('utf-8'))
                self.StopCamera()





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
    # Signls
    m_Signal_Barcode = pyqtSignal(list)             # if barcodes are found they get returned as a list in this signal
    m_Signal_Kill = pyqtSignal(bool)                # signal that gets triggerd when camera turns off

    # Configurations
    m_Barcode_Scan_Active = False                   # True/False - activates barcode/qrscan
    m_Barcode_Sound_Active = True                   # True/False - activates barcode beep
    m_Location_Save = ""                            # Path where pictures should be saved
    m_Time_Kill = 5 * 60 * 100000                    # the timer when we kill the camera to free memory

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
        self.pushButton_Video.hide()    # not implemented yet

        # start camera thread
        self.m_Thread_Video.m_Signal_Frame.connect(self._UpdateFrame)
        self.m_Thread_Video.m_Signal_CamerasAvailable.connect(self._UpdateAvailableCameras)
        self.m_Thread_Video.start()

    def _UpdateFrame(self, f_CV_Img):
        """Updates the image_label with a new opencv image"""
        rgb_image = cv2.cvtColor(f_CV_Img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(1280, 1024, Qt.KeepAspectRatio)
        self.CameraViewer.setPixmap(QPixmap.fromImage(p))

    def _KillCamera(self):
        """ kill camera """
        # emit signal
        self.m_Signal_Kill.emit(True)
        self.m_Thread_Video.StopCamera()

    def _ChangeCamera(self):
        """ kill camera """
        self.m_Thread_Video.ChangeCamera()

    def _TakePicture(self):
        """ kill camera """
        print("Kill")

    def _UpdateAvailableCameras(self, f_Result:list):
        """ connected method for Video thread that returns available cameras """
        # only one cam -> hide change cam button
        self.m_Cameras_Available = f_Result
        if len(self.m_Cameras_Available) == 1:
            self.pushButton_Change.hide()

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
