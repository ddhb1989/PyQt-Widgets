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

# TODO: Open Preview picture Maybe in our own Picture viewer Widget?
# Sound on video recording?===???
# ---------------------------------------------------------------------------
import cv2
import time
import os
from glob import glob
from pyzbar.pyzbar import decode

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtMultimedia import QSound, QCamera

import numpy as np

class PopUp_NewFolder(QtWidgets.QWidget):
    m_Signal_FolderName = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/PopUp-NewFolder.ui', self)
        self.show()

        # center window
        self.setContentsMargins(0, 0, 0, 0)
        self.move(parent.frameGeometry().center()-self.frameGeometry().center())

        # add bindings
        self.lineEdit_FolderName.setFocus()
        self.pushButton_Save.clicked.connect(lambda e, x=self.lineEdit_FolderName: self.m_Signal_FolderName.emit(self.lineEdit_FolderName.text()))
        self.pushButton_Save.clicked.connect(lambda e: self.deleteLater())
        self.pushButton_Close.clicked.connect(lambda e: self.deleteLater())
        self.lineEdit_FolderName.returnPressed.connect(self.pushButton_Save.click)

class PopUp_DeletePicture(QtWidgets.QWidget):
    m_Signal_Ack = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/PopUp-Delete.ui', self)
        self.show()

        # center window
        self.setContentsMargins(0, 0, 0, 0)
        self.move(parent.frameGeometry().center()-self.frameGeometry().center())

        # add bindings
        self.pushButton_Save.clicked.connect(lambda e: self.m_Signal_Ack.emit(True))
        self.pushButton_Save.clicked.connect(lambda e: self.deleteLater())
        self.pushButton_Close.clicked.connect(lambda e: self.deleteLater())

class VideoThread(QThread):
    # define some signals
    m_Signal_Frame = pyqtSignal(np.ndarray)         # signal that contains the image
    m_Signal_CamerasAvailable = pyqtSignal(list)    # signal available cameras
    m_Signal_Codes = pyqtSignal(list)                # signal qr codes
    m_Signal_Picture_Taken = pyqtSignal(str)        # signal returns name of picture
    m_Signal_Video_Taken = pyqtSignal(str)          # video # signal returns name of picture

    # config variables
    m_Barcode_Scan = True
    m_Path_Save = "/"
    m_Preview_Scale = 100
    m_Force_Cam = 0

    # class vars
    m_Cameras_Available = []
    m_Camera_Current = 0
    m_Camera_Run = True
    m_Video_Recording_Started = False

    def run(self):
        # get available cameras
        self.m_Cameras_Available = self._GetAvailableCameras()
        self.m_Signal_CamerasAvailable.emit(self.m_Cameras_Available)

        # start cam
        self.m_Camera_Run = True
        if self.m_Force_Cam in self.m_Cameras_Available:
            self.m_Camera_Current = self.m_Force_Cam
        else:
            self.m_Camera_Current = 0
        self.m_Cap = cv2.VideoCapture(self.m_Camera_Current, cv2.CAP_DSHOW)
        self.m_Cap.set(3, 1280)
        self.m_Cap.set(4, 720)
        while self.m_Camera_Run:
            # get image from cam
            ret, self.m_CV_Img = self.m_Cap.read()

            if ret != True: # continue if cam is not ready
                continue

            # resize image to a scale factor
            _Width = int(self.m_CV_Img.shape[1] * self.m_Preview_Scale / 100)
            _Height = int(self.m_CV_Img.shape[0] * self.m_Preview_Scale / 100)

            # resize image
            _Resized = cv2.resize(self.m_CV_Img, (_Width, _Height), interpolation=cv2.INTER_AREA)
            self.m_Signal_Frame.emit(_Resized)

            if self.m_Video_Recording_Started == True:
                self.m_Video_Writer.write(self.m_CV_Img)
                continue # <- we skip barcode scanning in video recording mode

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

    def RecordVideo(self):
        """ record a video """
        if not hasattr(self, "m_CV_Img"): # webcam is not loaded
            return
        
        # try to create directory
        if not os.path.exists(self.m_Path_Save):
            os.makedirs(self.m_Path_Save)

        # if recording is running we stop it here
        if self.m_Video_Recording_Started == True:
            self.m_Video_Recording_Started = False
            self.m_Video_Writer.release()
            self.m_Signal_Video_Taken.emit(self.m_Video_Filename)
            return

        # prepare our writer
        _Width = int(self.m_Cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        _Height = int(self.m_Cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.m_Video_Filename = _Filename = self.m_Path_Save + '\\' + str(int(time.time())) + '.mp4'
        self.m_Video_Writer = cv2.VideoWriter(self.m_Video_Filename, cv2.VideoWriter_fourcc(*'DIVX'), 20, (_Width, _Height))
        self.m_Video_Recording_Started = True

    def StopCamera(self):
        """ stop camera """
        self.m_Camera_Run = False
        self.m_Cap.release()

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
        while _i < len(QCamera.availableDevices()):
            _Cameras.append(_i)
            _i += 1

        return _Cameras

class Camera(QtWidgets.QWidget):
    # Configurations
    m_Barcode_Scan_Active = False                   # True/False - activates barcode/qrscan
    m_Sound_Active = True                           # True/False - activates sound
    m_Path_Save = "/"                               # Path where pictures should be saved
    m_Show_Preview = True                           # hide or show the taken pictures
    m_Show_Folders = True                           # hide or show the folder tree
    m_Preview_Scale = 100                           # scale factor of the cam viewer
    m_Force_Cam = 0                                 # force a specific camera to be used
    m_Kill_Timer = 5*60*1000                        # force the cam to shutdown

    # signals
    m_Signal_Barcode_Found = pyqtSignal(list)       # signal if a barcodes was found
    m_Signal_Kill = pyqtSignal(bool)                # signal that gets triggerd when camera gets killed

    # Status and cache vars
    m_Cameras_Available = []                        # list of all available camera indexes

    # Threads
    m_Thread_Video = VideoThread()

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/Camera.ui', self)

        # if valid **kwargs are available we set class vars
        for _Key in kwargs:
            if hasattr(self, _Key):
                self.__setattr__(_Key, kwargs[_Key])

        # start kill timer
        self.m_Timer_Kill = QTimer()
        self.m_Timer_Kill.timeout.connect(self._KillCamera)
        self.m_Timer_Kill.start(self.m_Kill_Timer)

        # add bindings
        self.pushButton_Close.clicked.connect(self._KillCamera)
        self.pushButton_Change.clicked.connect(self._ChangeCamera)
        self.pushButton_Picture.clicked.connect(self._TakePicture)
        self.pushButton_Video.clicked.connect(self._RecordVideo)
        self.Folder_Tree.itemClicked.connect(self._Event_Folder_Click)

        # prepare interface
        self.Hide_Button_Change()
        if self.m_Show_Preview == False:
            self.Hide_Preview()
            self.pushButton_Picture.hide()
            self.pushButton_Video.hide()
        else:
            self.Show_Preview()
            self.pushButton_Picture.show()
            self.pushButton_Video.show()
        if self.m_Show_Folders == False:
            self.Hide_Folders()
        else:
            self.Show_Folders()
            self._CreateDirectoryTree()
        # hide right frame if not needed
        if self.m_Show_Folders == False and self.m_Show_Preview == False:
            self.Frame_Right.hide()
        else:
            self.Frame_Right.show()

        # start camera thread
        self.m_Thread_Video.m_Path_Save = self.m_Path_Save
        self.m_Thread_Video.m_Barcode_Scan = self.m_Barcode_Scan_Active
        self.m_Thread_Video.m_Sound_Active = self.m_Sound_Active
        self.m_Thread_Video.m_Preview_Scale = self.m_Preview_Scale
        self.m_Thread_Video.m_Force_Cam = self.m_Force_Cam

        # connect signals
        self.m_Thread_Video.m_Signal_Frame.connect(self._UpdateFrame)   # updates frame
        self.m_Thread_Video.m_Signal_CamerasAvailable.connect(self._UpdateAvailableCameras) # updates interfac
        self.m_Thread_Video.m_Signal_Codes.connect(self._CodesFound)    # some barcodes found
        self.m_Thread_Video.m_Signal_Picture_Taken.connect(self._PictureTaken)  # picture was taken
        self.m_Thread_Video.m_Signal_Video_Taken.connect(self._VideoTaken)  # picture was taken

        self.m_Thread_Video.start()

    def _CreateDirectoryTree(self):
        """ create directory tree """
        self.Folder_Tree.clear()
        def _CreateTree(f_Path, f_Parent, _Depth=0):
            _Item = QtWidgets.QTreeWidgetItem(f_Parent)
            _Item.setText(0, "Neuen Ordner erstellen...")
            _Icon = QIcon()
            _Icon.addFile(os.path.dirname(os.path.realpath(__file__)) + "/Images/Add-Folder.png")
            _Item.setIcon(0, _Icon)

            _Dir = glob(f_Path + "/*/", recursive=True)
            if len(_Dir) == 0:
                return

            for _Folder in _Dir:
                _Item = QtWidgets.QTreeWidgetItem(f_Parent)
                _Item.setText(0, os.path.basename(os.path.normpath(_Folder)))
                _Icon = QIcon()
                _Icon.addFile(os.path.dirname(os.path.realpath(__file__)) + "/Images/Folder.png")
                _Item.setIcon(0, _Icon)

                _CreateTree(_Folder, _Item)

        _CreateTree(self.m_Path_Save, self.Folder_Tree)

    def _CodesFound(self, f_Result:list):
        """
        some codes are found in the scanner
        :param f_Result: list with all found codes
        :return:
        """
        if self.m_Sound_Active == True:
            QSound.play(os.path.dirname(os.path.realpath(__file__)) + "/Sounds/Scan.wav")

        self.m_Signal_Barcode_Found.emit(f_Result)
        self._KillCamera()

    def _VideoTaken(self, f_Result:str):
        """
        video was taken
        :param f_Result: path to file
        :return:
        """
        if self.m_Sound_Active == True:
            QSound.play(os.path.dirname(os.path.realpath(__file__)) + "/Sounds/Shutter.wav")

        # get frame for thumbnail
        _Cap = cv2.VideoCapture(f_Result)
        _Tot_Frames = int(_Cap.get(cv2.CAP_PROP_FRAME_COUNT) * 0.94)
        if not _Cap.isOpened() and _Tot_Frames <= 0: # something went wrong
            return
        _Cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        _, _Image = _Cap.retrieve()

        rgb_image = cv2.cvtColor(_Image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888).scaledToWidth(250, Qt.FastTransformation)

        _Frame = QtWidgets.QFrame()
        _VLayout = QtWidgets.QVBoxLayout(_Frame)
        # preview picture
        #_Picture = QImage(f_Result).scaledToWidth(250, Qt.FastTransformation)
        _Label = QtWidgets.QLabel()
        _Label.setAlignment(Qt.AlignCenter)
        _Label.setPixmap(QPixmap.fromImage(convert_to_Qt_format))
        _VLayout.addWidget(_Label)

        # add delete button
        _Button = QtWidgets.QPushButton()
        _Button.setText("Video löschen")
        _Button.setStyleSheet("QPushButton { border: 1px solid#A2a2a2; background: #FF7F7F; color: #1a82b1;font-size:14pt; font-family: voestalpine; padding:10px 10px; text-align:left;}")
        _Button.mouseReleaseEvent = lambda e, x=_Frame, y=f_Result: self._DeleteMediaFromPreview(x, y)
        # icon
        _Icon = QIcon()
        _Icon.addFile(os.path.dirname(os.path.realpath(__file__)) + "/Images/Delete-Picture.png", QSize(32, 32))
        _Button.setIcon(_Icon)

        _VLayout.addWidget(_Button)
        self.Preview_Layout.insertWidget(0, _Frame)

    def _PictureTaken(self, f_Result:str):
        """
        picture was taken
        :param f_Result: path to file
        :return:
        """
        if self.m_Sound_Active == True:
            QSound.play(os.path.dirname(os.path.realpath(__file__)) + "/Sounds/Shutter.wav")

        _Frame = QtWidgets.QFrame()
        _VLayout = QtWidgets.QVBoxLayout(_Frame)
        # preview picture
        _Picture = QImage(f_Result).scaledToWidth(250, Qt.FastTransformation)
        _Label = QtWidgets.QLabel()
        _Label.setAlignment(Qt.AlignCenter)
        _Label.setPixmap(QPixmap.fromImage(_Picture))
        _VLayout.addWidget(_Label)

        # add delete button
        _Button = QtWidgets.QPushButton()
        _Button.setText("Bild löschen")
        _Button.setStyleSheet("QPushButton { border: 1px solid#A2a2a2; background: #FF7F7F; color: #1a82b1;font-size:14pt; font-family: voestalpine; padding:10px 10px; text-align:left;}")
        _Button.mouseReleaseEvent = lambda e, x=_Frame, y=f_Result: self._DeleteMediaFromPreview(x, y)
        # icon
        _Icon = QIcon()
        _Icon.addFile(os.path.dirname(os.path.realpath(__file__)) + "/Images/Delete-Picture.png", QSize(32, 32))
        _Button.setIcon(_Icon)

        _VLayout.addWidget(_Button)
        self.Preview_Layout.insertWidget(0, _Frame)

    def _UpdateFrame(self, f_CV_Img):
        """Updates the image_label with a new opencv image"""
        rgb_image = cv2.cvtColor(f_CV_Img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.CameraViewer.setPixmap(QPixmap.fromImage(convert_to_Qt_format))

    def _DeleteMediaFromPreview(self, f_Frame:QtWidgets.QFrame, f_File:str):
        """
        delete a picture from the preview list
        :param f_Frame: Frame to delete
        :param f_File: filename to delete
        :return:
        """
        def _Delete(f_Bool):
            try:
                os.remove(f_File)
            except:
                QtWidgets.QMessageBox.information(self, "Fehler", "Die Datei konnte nicht gelöscht werden.\nDer Zugriff wurde verweigert!", QtWidgets.QMessageBox.Ok)
            f_Frame.deleteLater()

        _PopUp = PopUp_DeletePicture(self)
        _PopUp.m_Signal_Ack.connect(_Delete)

    def _KillCamera(self):
        """ kill camera """
        # if we record stop recording
        if self.m_Thread_Video.m_Video_Recording_Started == True:
            self._RecordVideo()
        self.m_Signal_Kill.emit(True)
        self.m_Thread_Video.StopCamera()

    def _ChangeCamera(self):
        """ kill camera """
        # if we record stop recording
        if self.m_Thread_Video.m_Video_Recording_Started == True:
            self._RecordVideo()
        self.m_Thread_Video.ChangeCamera()

    def _TakePicture(self):
        """ Take a picture """
        # if we record stop recording
        if self.m_Thread_Video.m_Video_Recording_Started == True:
            self._RecordVideo()
        self.m_Thread_Video.TakePicture()

    def _RecordVideo(self):
        """ record a video """
        # show text in image
        if not hasattr(self, "RecordingLabel"): # define recording button
            self.RecordingLabel = QtWidgets.QPushButton(self.CameraViewer)
            self.RecordingLabel.setText("Aufnahme läuft...")
            _Icon = QIcon()
            _Icon.addFile(os.path.dirname(os.path.realpath(__file__)) + "/Images/Button-Rec.png")
            self.RecordingLabel.setIcon(_Icon)

        # start recording
        self.m_Thread_Video.RecordVideo()

        if self.pushButton_Video.text() == "Video aufnehmen":
            self.pushButton_Video.setText("Aufnahme stoppen")
            self.RecordingLabel.show()
        else:
            self.pushButton_Video.setText("Video aufnehmen")
            self.RecordingLabel.hide()


    def _UpdateAvailableCameras(self, f_Result:list):
        """ connected method for Video thread that returns available cameras """
        # only one cam -> hide change cam button
        self.m_Cameras_Available = f_Result
        if len(self.m_Cameras_Available) > 1:
            self.pushButton_Change.show()

    def _Event_Folder_Click(self, f_Event):
        _Path = self.m_Path_Save

        _Item = f_Event
        while _Item.parent() is not None:
            _Path += "/" + _Item.parent().text(0)
            _Item = _Item.parent()

        # create a new folder
        if f_Event.text(0) == "Neuen Ordner erstellen...":
            def _CreateFolder(f_Folder):
                try:
                    if not os.path.exists(_Path):
                        os.makedirs(_Path)

                    os.mkdir(_Path + "/" + f_Folder)
                    self.m_Thread_Video.m_Path_Save = _Path + "/" + f_Folder
                    self.label_CurrentFolder.setText("Aktuelles Verzeichnis: {}".format((_Path + "/" + f_Folder).replace(self.m_Path_Save, "")))
                except Exception as e:
                    QtWidgets.QMessageBox.information(self, "Fehler", "Der Ordner konnte nicht erstellt werden.!\n\n" + str(e), QtWidgets.QMessageBox.Ok)
                self._CreateDirectoryTree()

            _PopUp = PopUp_NewFolder(self)
            _PopUp.m_Signal_FolderName.connect(_CreateFolder)
        else: # set folder as saving directory
            _Path += "/" + f_Event.text(0)
            # update interface
            self.label_CurrentFolder.setText("Aktuelles Verzeichnis: {}".format(_Path.replace(self.m_Path_Save, "")))
            self.m_Thread_Video.m_Path_Save = _Path

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
        self.Footer.hide()

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
        self.Footer.show()