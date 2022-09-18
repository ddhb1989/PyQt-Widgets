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

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QImage,QPixmap

class Camera(QtWidgets.QWidget):
    # Signls
    m_Signal_Barcode = pyqtSignal(list)             # if barcodes are found they get returned as a list in this signal
    m_Signal_Kill = pyqtSignal(bool)                # signal that gets triggerd when camera turns off

    # Configurations
    m_Barcode_Scan_Active = False                   # True/False - activates barcode/qrscan
    m_Barcode_Sound_Active = True                   # True/False - activates barcode beep
    m_Location_Save = ""                            # Path where pictures should be saved
    m_Time_Refresh = 10                             # refresh time of the camera viewer
    m_Time_Kill = 5 * 60 * 100000                     # the timer when we kill the camera to free memory

    # Status and cache vars
    m_Cameras_Available = []                        # list of all available camera indexes
    m_Camera_IsActive = False                       # status var if cam is active

    # Timers
    m_Timer_Refresh = QTimer()                      # QTimer that refreshes Cam viewer frame
    m_Timer_Kill = QTimer()                         # QTimer that kills the camera after a certain time of not being used

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

        # get all available cams
        self.m_Cameras_Available = self._GetAvailableCameras()

        # no camera available: we stop here
        if len(self.m_Cameras_Available) == 0:
            print("Sorry but no cameras are available")
            return

        # hide change button if there is only one cam
        if len(self.m_Cameras_Available) == 1:
            self.pushButton_Change.hide()

        # start camera
        self._StartCamera()

    def _GetAvailableCameras(self):
        """
        get all available cameras
        :return: list with all available camera indexes
        """
        _Cameras = []
        _i = 0
        while True:
            self.m_Cap = cv2.VideoCapture(_i)
            # no camera is available we break the loop
            if not self.m_Cap.read()[0]:
                break

            # if a cam is available we continue the loop
            _Cameras.append(_i)
            self.m_Cap.release()
            _i += 1
        return _Cameras

    def _StartCamera(self):
        """ start camera stream """
        # start the timer for refreshing cam viewer
        self.m_Timer = QTimer()
        self.m_Timer.timeout.connect(self._Refresh_Frame)
        self.m_Timer.start(self.m_Timer_Refresh)

    def _KillCamera(self):
        """ kill camera """
        # emit signal
        self.m_Signal_Kill.emit(True)
        self.m_Camera_IsActive = False

    def _ChangeCamera(self):
        """ kill camera """
        print("Kill")

    def _TakePicture(self):
        """ kill camera """
        print("Kill")

    def _Refresh_Frame(self):
        """ refresh the camera viewer frame """
        print("hkhk")
        ret, image = self.m_Cap.read()
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        """"# get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))"""

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