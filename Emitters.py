from PyQt5.QtCore import pyqtSignal, QObject


class StringEmitter(QObject):
    signal = pyqtSignal(str)


class TupleEmitter(QObject):
    signal = pyqtSignal(tuple)


class VoidEmitter(QObject):
    signal = pyqtSignal()
