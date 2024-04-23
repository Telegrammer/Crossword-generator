from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog, QMainWindow

from Emitters import *
from UI import PythonClasses
from Models import CrosswordGenerator


class StartScreen(QWidget, PythonClasses.StartScreenView):
    def __init__(self, signals: dict[str, StringEmitter]):
        QWidget.__init__(self)
        self.setupUi(self)

        self.outer_signals = signals
        self.dialog_canceled = VoidEmitter()
        self.dialog_canceled.signal.connect(self.show)

        self.generateButton.clicked.connect(self.open_generate_input)
        self.loadButton.clicked.connect(self.open_load_input)

    def open_generate_input(self):
        self.hide()
        dialog_window = GenerateDialogWindow(self.dialog_canceled, self.outer_signals["generate"])
        dialog_window.show()
        dialog_window.exec_()

    def open_load_input(self):
        self.hide()
        dialog_window = LoadDialogWindow(self.dialog_canceled, self.outer_signals["load"])
        dialog_window.show()
        dialog_window.exec_()


class GenerateDialogWindow(QDialog, PythonClasses.GenerateDialogWindowView):

    def __init__(self, dialog_canceled: VoidEmitter, got_generate_data: StringEmitter):
        QDialog.__init__(self)
        self.setupUi(self)
        self.__difficulty = "Средний"

        self.__rejected = dialog_canceled
        self.__accepted = got_generate_data
        self.buttonBox.accepted.connect(self.send_data_for_generation)
        self.buttonBox.rejected.connect(self.return_start_screen)
        self.difficultyButtonGroup.buttonClicked.connect(lambda btn: self.set_difficulty(btn.text()))

    def send_data_for_generation(self):
        self.__accepted.signal.emit((self.keyWordInput.text(), self.__difficulty))
        self.close()

    def return_start_screen(self):
        self.__rejected.signal.emit()
        self.close()

    def set_difficulty(self, difficulty: str):
        self.__difficulty = difficulty


class LoadDialogWindow(QDialog, PythonClasses.LoadDialogWindowView):
    def __init__(self, dialog_canceled: VoidEmitter, got_load_data: StringEmitter):
        QDialog.__init__(self)
        self.setupUi(self)
        self.__browseWindow = None

        self.__rejected = dialog_canceled
        self.__accepted = got_load_data

        self.buttonBox.accepted.connect(self.send_data_for_load)
        self.buttonBox.rejected.connect(self.return_start_screen)
        self.browseButton.clicked.connect(self.browse)

    def send_data_for_load(self):
        self.__accepted.signal.emit(self.pathInput.text())
        self.close()

    def return_start_screen(self):
        if self.__browseWindow is not None:
            self.__browseWindow.close()
        self.__rejected.signal.emit()
        self.close()

    def browse(self):
        if self.__browseWindow is None:
            self.__browseWindow = QFileDialog()
            self.__browseWindow.show()
        if self.__browseWindow.exec_():
            self.pathInput.setText(self.__browseWindow.selectedFiles()[0])
            self.__browseWindow.close()
            self.__browseWindow = None


class MainWindow(QMainWindow, PythonClasses.MainWindowView):

    def __init__(self, signals: dict[str, StringEmitter]):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.hide_descriptions_action.changed.connect(self.change_descriptions_view)

        self.hide()
        self.start_screen = StartScreen(signals)
        self.start_screen.show()

    def change_descriptions_view(self):
        if self.hide_descriptions_action.isChecked():
            self.descriptions_label.hide()
            self.descriptions.hide()
        else:
            self.descriptions_label.show()
            self.descriptions.show()

    def resizeEvent(self, event):
        self.paintEvent(event)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_background_lines(qp)
        qp.end()

    def draw_background_lines(self, qp):

        pen = QPen(Qt.gray, 1, Qt.SolidLine)
        qp.setPen(pen)

        start_pos = 30
        current_line_pos_x = start_pos
        current_line_pos_y = start_pos
        while current_line_pos_x < self.centralwidget.width():
            qp.drawLine(current_line_pos_x, 0, current_line_pos_x, self.centralwidget.height())
            current_line_pos_x += start_pos
        while current_line_pos_y < self.centralwidget.height():
            qp.drawLine(0, current_line_pos_y, self.centralwidget.width(), current_line_pos_y)
            current_line_pos_y += start_pos


class CrosswordPresenter:
    def __init__(self):
        self.gotGenerateData = TupleEmitter()
        self.gotLoadData = StringEmitter()
        self.gotGenerateData.signal.connect(self.start_generate)
        self.gotLoadData.signal.connect(self.start_load)
        signals = {"generate": self.gotGenerateData, "load": self.gotLoadData}

        self.__main_window = MainWindow(signals)
        self.__crossword = None

    def start_generate(self, data: tuple[str]):
        for i in range(len(data)):
            self.__main_window.descriptions.addItem(f"{i + 1}. {data[i]};")
        self.__crossword = CrosswordGenerator(data).generate()
        self.show()

    def start_load(self, path: str):
        self.show()
        pass

    def show(self):
        self.__main_window.start_screen.close()
        self.__main_window.show()
