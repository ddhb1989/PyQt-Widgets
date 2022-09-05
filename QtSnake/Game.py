#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Bernhard Hofer  -   bernhard.hofer@voestalpine.com
#
# Game widget in snake style
# Made for fun and learning effect
# Have fun !
# ---------------------------------------------------------------------------
import random

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer, pyqtSignal

# game over widget
class GameOver(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi('_QWidgets/Snake/Interface/GameOver.ui', self)

    def Score(self, f_Text):
        """ change score text """
        self.label_Score.setText(str(f_Text))

class Game(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        uic.loadUi('_QWidgets/Snake/Interface/GameBoard.ui', self)

        # define some config variables
        self.m_Score = 0                    # store the current score
        self.m_Game_Speed = 50              # timer in milliseconds
        self.m_GameBoard_Grid = [25, 25]    # rows and lines

        # define some class vars
        self.m_GameBoard_Frame = [0, 0]         # [height, width]
        self.m_GameBoard_GridField = [0, 0]     # [height, width]
        self.m_Snake_Direction = "N"            # N/E/S/W
        self.m_Snake = []                       # grid positions of all snake elements [x, y]
        self.m_Snake_Labels = []                # stores all snake elements
        self.m_Fruits = []                      # grid positions of all fruit elements [x, y]
        self.m_Fruits_Labels = []               # stores all fruit elements

        # connect and calculate resize event for frame
        self.frame_GameBoard.resizeEvent = lambda e: self._CalculateGameBoard()
        self._CalculateGameBoard()

        # start the game
        self.m_Snake_Timer = QTimer()
        self.m_Snake_Timer.timeout.connect(self._Game)
        self.m_Snake_Timer.start(self.m_Game_Speed)

    def _Game(self):
        """
        Start our snake game
        """
        # if we have no snake element we start in the middle
        if len(self.m_Snake) == 0:
            _X = self.m_GameBoard_Grid[1]
            _Y = self.m_GameBoard_Grid[0]
            self.m_Snake.append([_X, _Y])

        # clear frame before we update the frame
        for _Item in self.m_Snake_Labels:
            _Item.deleteLater()
        self.m_Snake_Labels = []

        for _Item in self.m_Fruits_Labels:
            _Item.deleteLater()
        self.m_Fruits_Labels = []

        # we add a snake element to our start of the snake list based on the direction
        if self.m_Snake_Direction == "N":
            _Element = self.m_Snake[0]
            self.m_Snake.insert(0, [_Element[0] - 1, _Element[1]])
        elif self.m_Snake_Direction == "E":
            _Element = self.m_Snake[0]
            self.m_Snake.insert(0, [_Element[0], _Element[1] + 1])
        elif self.m_Snake_Direction == "S":
            _Element = self.m_Snake[0]
            self.m_Snake.insert(0, [_Element[0] + 1, _Element[1]])
        elif self.m_Snake_Direction == "W":
            _Element = self.m_Snake[0]
            self.m_Snake.insert(0, [_Element[0] , _Element[1] - 1])

        # check if we need a fruit
        if len(self.m_Fruits) == 0:
            while True:
                # generate random coords
                _X = random.randint(0, self.m_GameBoard_Grid[1])
                _Y = random.randint(0, self.m_GameBoard_Grid[0])
                self.m_Fruits = [_X, _Y]
                # check if we collide instantly with a snake tile
                if [_X, _Y] not in self.m_Snake:
                    break

        # print our fruit
        _Fruit = QtWidgets.QLabel(self.frame_GameBoard)
        _Fruit.setStyleSheet("border: 0px solid #A2A2A2; background: #cc1100;")
        _Fruit.setFixedHeight(self.m_GameBoard_GridField[0])
        _Fruit.setFixedWidth(self.m_GameBoard_GridField[1])
        _Fruit.show()

        _X = self.m_Fruits[1] / 2 * self.m_GameBoard_GridField[1]
        _Y = self.m_Fruits[0] / 2 * self.m_GameBoard_GridField[0]
        _Fruit.move(_X, _Y)

        self.m_Fruits_Labels.append(_Fruit)

        # print our snake
        for _i, _Grid in enumerate(self.m_Snake):
            _Snake = QtWidgets.QLabel(self.frame_GameBoard)
            _Snake.setStyleSheet("border: 0px solid #A2A2A2; background: #a8ea6a;")
            _Snake.setFixedHeight(self.m_GameBoard_GridField[0])
            _Snake.setFixedWidth(self.m_GameBoard_GridField[1])
            _Snake.show()

            _X = _Grid[1] / 2 * self.m_GameBoard_GridField[1]
            _Y = _Grid[0] / 2 * self.m_GameBoard_GridField[0]
            _Snake.move(_X, _Y)

            self.m_Snake_Labels.append(_Snake)

        # delete last element of the snake list... this disappears
        # except we collide with a fruit
        if self.m_Fruits in self.m_Snake:
            self._UpdateScore(10)
            self.m_Fruits = []
        else:
            self.m_Snake.pop()

        # eaten by itself
        if self.m_Snake[0] in self.m_Snake[1:] or \
                self.m_Snake[0][0] == -1 or self.m_Snake[0][1] == -1 or \
                self.m_Snake[0][0] == (self.m_GameBoard_Grid[0]*2)-1 or self.m_Snake[0][1] == (self.m_GameBoard_Grid[1]*2)-1:
            self.m_Snake_Timer.stop()
            self._GameOver()

    def _GameOver(self):
        """
        sorry! GameOver
        """
        _GameOver = GameOver()
        _GameOver.Score("Deine Punkte: {}".format(self.m_Score))
        self.layout_GameBoard.addWidget(_GameOver)

    def _UpdateScore(self, f_Add):
        """
        Update score
        Args:
            f_Add: how much should we add?
        """
        self.m_Score += f_Add
        self.label_Score.setText("Punkte: {}".format(self.m_Score))

    def _CalculateGameBoard(self):
        """
        calculate the size of a grid field based on the gameboard frame size
        and the amounts of rows and lines
        """
        # get the frame size
        _Frame_Height = self.frame_GameBoard.height()
        _Frame_Width = self.frame_GameBoard.width()
        self.m_GameBoard_Frame = [_Frame_Height, _Frame_Width]

        # calculate the size of a grid field
        _Grid_Height = _Frame_Height / self.m_GameBoard_Grid[0]
        _Grid_Width = _Frame_Width / self.m_GameBoard_Grid[1]
        self.m_GameBoard_GridField = [_Grid_Height, _Grid_Width]

    def keyPressEvent(self, e):
        """ rewrite keypressevent to control our snake """
        super(Game, self).keyPressEvent(e)

        if e.key() == QtCore.Qt.Key_Up and self.m_Snake_Direction != "S":
            self.m_Snake_Direction = "N"
        if e.key() == QtCore.Qt.Key_Right and self.m_Snake_Direction != "W":
            self.m_Snake_Direction = "E"
        if e.key() == QtCore.Qt.Key_Down and self.m_Snake_Direction != "N":
            self.m_Snake_Direction = "S"
        if e.key() == QtCore.Qt.Key_Left and self.m_Snake_Direction != "E":
            self.m_Snake_Direction = "W"
