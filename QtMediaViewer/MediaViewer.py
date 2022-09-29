#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Bernhard Hofer  -   Mail@Bernhard-Hofer.at
#
# Media Viewer Widget
#
# IMPORTANT: os.listdir is the fastest way to scan directories
#
# NOTES:
# (process:16080): WARNING **: 16:50:28.480: unknown line join style undefined
#  Add RedirectStandardError=True in igconfig.xml
# ---------------------------------------------------------------------------
import os
<<<<<<< Updated upstream
import pathlib
from PyQt5 import uic
from PyQt5.QtWidgets import *
=======
<<<<<<< HEAD
import subprocess
from PyQt5 import uic
from PyQt5.QtWidgets import *

from .Threads import *
=======
import pathlib
from PyQt5 import uic
from PyQt5.QtWidgets import *
>>>>>>> 84b7a19edb4df4457ce030c36071c378b2aaadb7
>>>>>>> Stashed changes
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtMultimedia import QSound, QCamera

<<<<<<< Updated upstream
=======
<<<<<<< HEAD
""" POPUP Window for delete confirmation """
class PopUp_Delete(QWidget):
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

""" POPUP Window for Error Messages """
class PopUp_Error(QWidget):
    def __init__(self, parent, f_Msg: str=""):
        super().__init__(parent)
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/PopUp-Error.ui', self)
        self.show()

        # center window
        self.setContentsMargins(0, 0, 0, 0)
        self.move(parent.frameGeometry().center()-self.frameGeometry().center())

        self.UI_Label.setText(f_Msg)

        # add bindings
        self.pushButton_Close.clicked.connect(lambda e: self.deleteLater())

class QWidget_Preview(QWidget):

    m_Path_Abs: str = ""    # absolute file path
    m_Path: str = ""        # Path to file without file itself
    m_Filename: str = ""    # filename without extension and path
    m_Extension: str = ""   # extension from file

    m_Signal_NewName: pyqtSignal = pyqtSignal(str)  # signal with the new filename when everything works fine
    m_Signal_Error: pyqtSignal = pyqtSignal(str)    # error message if something went wrong

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self)
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/List_Item.ui', self)
        self.UI_Filename.setReadOnly(True)

    def SetFilePath(self, f_Path: str=""):
        """ set path to file """
        self.m_Path_Abs = f_Path
        self.m_Path = os.path.split(os.path.abspath(self.m_Path_Abs))[0]
        self.m_Extension = os.path.splitext(self.m_Path_Abs)[1]
        self.m_Filename = os.path.basename(os.path.splitext(self.m_Path_Abs)[0])
        self.UI_Filename.setText(os.path.basename(self.m_Filename))

    def EnableFilenameEdit(self, f_Enable: bool=True):
        """
        enable on the fly renaming for files
        :param f_Enable: bool True/False
        :return:
        """
        self.m_Timer = QTimer()
        self.m_Timer.setSingleShot(True)
        self.m_Timer.timeout.connect(self._RenameFile)
        self.UI_Filename.setReadOnly(False)
        self.UI_Filename.keyReleaseEvent = lambda e: self.m_Timer.start(1000)

    def _RenameFile(self):
        """ rename our file in a new thread """
        self.m_Thread_File_OnTheFlyRename = File_OnTheFlyRename()
        self.m_Thread_File_OnTheFlyRename.m_Original = self.m_Path_Abs
        self.m_Thread_File_OnTheFlyRename.m_NewName = os.path.join(self.m_Path, self.UI_Filename.text() + self.m_Extension)
        self.m_Thread_File_OnTheFlyRename.m_Signal_NewName.connect(self._Finish_RenameFile)
        self.m_Thread_File_OnTheFlyRename.m_Signal_Error.connect(self._Error_RenameFile)
        self.m_Thread_File_OnTheFlyRename.start()

    def _Finish_RenameFile(self, f_Result: str=""):
        """ finish method for renameing """
        # send signal and then update the vars
        self.m_Signal_NewName.emit(f_Result)
        self.SetFilePath(f_Result)

    def _Error_RenameFile(self, f_Result: str=""):
        """ finish method for error """
        self.UI_Filename.setText(self.m_Filename)   # set Text back to original
        self.m_Signal_Error.emit(f_Result)

""" QListWidgetItem Header for our list """
class QWidget_Header(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self)
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/List_Header.ui', self)


""" QWidget Class for using MediaViewer """
class MediaViewer(QWidget):

    # Configurations
    m_Directory: str = "/"      # media folder
    m_PreviewSize: int = 200     # size for preview

    m_Structure = {}          # saves our folder and file structire

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self)
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======
>>>>>>> 84b7a19edb4df4457ce030c36071c378b2aaadb7
>>>>>>> Stashed changes
        uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/Interface/MediaViewer.ui', self)

        # if valid **kwargs are available we set class vars
        for _Key in kwargs:
            if hasattr(self, _Key):
                self.__setattr__(_Key, kwargs[_Key])

        # some UI Modifications
        # First show loading widget
        self.UI_StackedWidget.setCurrentIndex(self.UI_StackedWidget.indexOf(self.UI_Page_Loading))
        _Effect = QGraphicsOpacityEffect()
        _Effect.setOpacity(0.3)
        self.UI_ImageLoading.setGraphicsEffect(_Effect)

<<<<<<< HEAD
        # load all files in a thread from our folder
        self._Start_Thread_Files_LoadAllFilesFromFolder()

        # watch filessystemwatcher
        self.m_Watcher = QFileSystemWatcher()
        self.m_Watcher.directoryChanged.connect(lambda e: self._Watcher_Directory(e))

    def _Start_Thread_Files_LoadAllFilesFromFolder(self):
        """ load files and folder in an async thread and create filelist """
        self.UI_StackedWidget.setCurrentIndex(self.UI_StackedWidget.indexOf(self.UI_Page_Loading))
        self._Layout_Clear(self.Contents_Layout)

        self.m_Thread_Files_LoadAllFilesFromFolder = Files_LoadAllFilesFromFolder()
        self.m_Thread_Files_LoadAllFilesFromFolder.m_Directory = self.m_Directory
        self.m_Thread_Files_LoadAllFilesFromFolder.m_Signal_Result.connect(lambda e: self._Finish_Thread_Files_LoadAllFilesFromFolder(e))
        self.m_Thread_Files_LoadAllFilesFromFolder.finished.connect(lambda: self.UI_StackedWidget.setCurrentIndex(self.UI_StackedWidget.indexOf(self.UI_MediaViewer)))
        self.m_Thread_Files_LoadAllFilesFromFolder.start()

    def _Watcher_Directory(self, f_Path):
        """ watches changes in our directory """
        try: # on massive file changes this could crush here.. it is not as important so we skip it on error
            if self.m_Thread_Files_LoadAllFilesFromFolder.isRunning():
                return
            self.m_Thread_Files_LoadAllFilesFromFolder = Files_LoadAllFilesFromFolder()
            self.m_Thread_Files_LoadAllFilesFromFolder.m_Directory = self.m_Directory
            self.m_Thread_Files_LoadAllFilesFromFolder.m_Signal_Result.connect(self.m_Watcher_Directory_Finish)
            self.m_Thread_Files_LoadAllFilesFromFolder.start()
        except:
            pass

    def m_Watcher_Directory_Finish(self, f_Result: dict):
        """ watch our files and folders """
        # check if a folder is added
        if len(f_Result) != len(self.m_Structure):
            self._Start_Thread_Files_LoadAllFilesFromFolder()
            return

        for _Folder in f_Result:
            if _Folder not in self.m_Structure:
                self._Start_Thread_Files_LoadAllFilesFromFolder()
                return
            if len(f_Result[_Folder]) != len(self.m_Structure[_Folder]):
                self._Start_Thread_Files_LoadAllFilesFromFolder()
                return


    def _Finish_Thread_Files_LoadAllFilesFromFolder(self, f_Result: dict):
        """
        create our folder and file list from f_Result
        :param f_Result: contains all files and folder
        :return:
        """
        self.m_Structure = f_Result

        _Mime_Picture = QPixmap()
        _Mime_Picture.load(os.path.dirname(os.path.realpath(__file__)) + "/Images/Picture.png")
        _Mime_Video = QPixmap()
        _Mime_Video.load(os.path.dirname(os.path.realpath(__file__)) + "/Images/Video.png")

        # loop through all folder
        for _Folder in self.m_Structure:
            # start filesystem watchers
            self.m_Watcher.addPath(self.m_Directory + _Folder)

            _List = QListWidget()

            # create header button with folder name only if we have mor than the root directory
            if len(self.m_Structure) > 1 and len(self.m_Structure[_Folder]) > 0:
                _Widget = QWidget_Header()
                _Widget.UI_Button.setText(_Folder if _Folder != "" else "\\")
                _Widget.UI_Button.mouseReleaseEvent = lambda e, x=self.m_Directory + _Folder: self._OpenFile(x)
                self.Contents_Layout.addWidget(_Widget)

                # toggle lists
                def _Toggle(f_List, f_Label):
                    _Hide = QPixmap()
                    _Hide.load(os.path.dirname(os.path.realpath(__file__)) + "/Images/Plus.png")
                    _Show = QPixmap()
                    _Show.load(os.path.dirname(os.path.realpath(__file__)) + "/Images/Minus.png")
                    if f_List.isVisible():
                        f_Label.setPixmap(_Show)
                        f_List.hide()
                    else:
                        f_Label.setPixmap(_Hide)
                        f_List.show()
                _Widget.UI_Label.mouseReleaseEvent = lambda e, x=_List, y=_Widget.UI_Label: _Toggle(x, y)

            _List.setViewMode(QListView.IconMode)
            _List.setResizeMode(QListView.Adjust)
            _List.setAcceptDrops(False)
            _List.setVerticalScrollMode(QListWidget.ScrollPerPixel)

            _List.setSizeAdjustPolicy(QListWidget.AdjustToContents)
            _List.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            self.Contents_Layout.addWidget(_List)
            self.m_Thread_Files_CalculatePreview = {} # store our threads for preview generation
            for _File in self.m_Structure[_Folder]:
                if _File[:1] == "\\": # if \ is the first char in _File os.path.join is not working
                    _File = _File[1:]

                _Item = QListWidgetItem()
                _Widget = QWidget_Preview()
                _Widget.SetFilePath(os.path.join(self.m_Directory, _File))
                _Widget.EnableFilenameEdit(True)
                _Widget.m_Signal_Error.connect(lambda e: PopUp_Error(self, e))
                # always keep our m_Structure up to date! Very Important for QFileSystemWatcher
                #_Widget.m_Signal_NewName.connect(lambda e, x=_Folder, y=_Widget: [self.m_Structure[x].remove(y.m_Filename+y.m_Extension), self.m_Structure[x].append(os.path.basename(e))])

                _Widget.UI_Preview.setStyleSheet("border: 1px solid #AAA;;")
                _Widget.UI_Preview.setAlignment(Qt.AlignCenter)
                _Widget.UI_Preview.mouseReleaseEvent = lambda e, x=_Widget: self._OpenFile(x.m_Path_Abs)
                _Widget.UI_Delete.mouseReleaseEvent = lambda e, x=_Item, y=_Widget: self._DeleteFile(x, y.m_Path_Abs)

                _Item.setSizeHint(_Widget.sizeHint())
                _List.addItem(_Item)
                _List.setItemWidget(_Item, _Widget)

                # create preview in a seperate thread
                # because it could take some time
                self.m_Thread_Files_CalculatePreview[os.path.join(self.m_Directory, _File)] = Files_CalculatePreview()
                self.m_Thread_Files_CalculatePreview[os.path.join(self.m_Directory, _File)].m_PreviewSize = self.m_PreviewSize
                self.m_Thread_Files_CalculatePreview[os.path.join(self.m_Directory, _File)].m_File = os.path.join(self.m_Directory, _File)
                # what did i do here?
                # get pixmap from thread and set it to qlabel
                # update minimum width and height
                # get size hint for widget and update itemwidget
                # that takes time to figure out -.-
                # doItemsLayout() updates GUI that it is shown without scaling problems
                self.m_Thread_Files_CalculatePreview[os.path.join(self.m_Directory, _File)].m_Signal_Preview.connect(
                    lambda w, x=_Widget, y=_Item, z=_List:
                    [x.UI_Preview.setPixmap(w),
                     x.setMinimumWidth(w.width()),
                     x.setMinimumHeight(w.height()),
                     y.setSizeHint(x.sizeHint()),
                     z.setItemWidget(y, x),
                     z.doItemsLayout()])

                # set mime type image
                self.m_Thread_Files_CalculatePreview[os.path.join(self.m_Directory, _File)].m_Signal_MediaType.connect(lambda e, x=_Widget: x.UI_Mime.setPixmap(_Mime_Picture) if e=="picture" else x.UI_Mime.setPixmap(_Mime_Video))
                self.m_Thread_Files_CalculatePreview[os.path.join(self.m_Directory, _File)].start()

    def _DeleteFile(self, f_Widget: QListWidgetItem, f_File:str):
        """
        delete a picture from the preview list
        :param f_Frame: QItem Widget to delete
        :param f_File: filename to delete
        :return:
        """
        def _Delete(f_Bool):
            try:
                os.remove(f_File)
                f_Widget.setHidden(True)
            except:
                _P = PopUp_Error(self, "Die Datei konnte nicht gelöscht werden.\nDer Zugriff wurde verweigert!")

        _PopUp = PopUp_Delete(self)
        _PopUp.m_Signal_Ack.connect(_Delete)

    def _OpenFile(self, f_Path: str=""):
        """
        try to open a path or media file
        :param f_Path: file path
        :return:
        """
        # folder
        if os.path.isdir(f_Path):
            os.startfile(f_Path)
            return
        # video
        if os.path.splitext(f_Path)[1] in (".mpg"," .mpeg", ".mp4", ".avi", ".mov"):
            os.startfile(f_Path)
            return

        # picture
        cmd = os.path.dirname(os.path.realpath(__file__)) + "/Win_ImageGlass/ImageGlass.exe \"{}\"".format(os.path.normpath(f_Path))
        subprocess.Popen(cmd, shell=False)

    def _Layout_Clear(self, f_Layout: QLayout):
        """
        clear a qwidget layout
        :param f_Layout: QLayout
        :return:
        """
        for i in reversed(range(f_Layout.count())):
            f_Layout.itemAt(i).widget().setParent(None)



=======
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
<<<<<<< Updated upstream
=======
>>>>>>> 84b7a19edb4df4457ce030c36071c378b2aaadb7
>>>>>>> Stashed changes


