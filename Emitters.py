from abc import abstractmethod

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QPainter


class AbstractEmitter(QObject):

    @abstractmethod
    def __str__(self):
        pass


class StringEmitter(AbstractEmitter):
    signal = pyqtSignal(str)

    def __str__(self):
        return "Wrapper for signal that receive string"


class TupleEmitter(AbstractEmitter):
    signal = pyqtSignal(tuple)

    def __str__(self):
        return "Wrapper for signal that receive tuple"


class VoidEmitter(AbstractEmitter):
    signal = pyqtSignal()

    def __str__(self):
        return "Wrapper for signal that receive nothing"


class QPainterEmitter(AbstractEmitter):
    signal = pyqtSignal(QPainter)

    def __str__(self):
        return "Special wrapper for qpainter"
