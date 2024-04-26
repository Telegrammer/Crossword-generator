from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog, QMainWindow

from Models import *
from UI import PythonClasses


class MainWindow(QMainWindow, PythonClasses.MainWindowView):

    def __init__(self, signals: dict[str, AbstractEmitter]):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.outer_signals = signals
        self.dialog_canceled = VoidEmitter()
        self.generate_action.triggered.connect(self.open_regenerate_input)
        self.load_action.triggered.connect(self.open_reload_input)

        self.hide_descriptions_action.changed.connect(self.change_descriptions_view)

    def change_descriptions_view(self):
        if self.hide_descriptions_action.isChecked():
            self.descriptions_label.hide()
            self.descriptions.hide()
        else:
            self.descriptions_label.show()
            self.descriptions.show()

    def open_regenerate_input(self):
        dialog_window = GenerateDialogWindow(self.dialog_canceled, self.outer_signals["generate"])
        dialog_window.show()
        dialog_window.exec_()

    def open_reload_input(self):
        dialog_window = LoadDialogWindow(self.dialog_canceled, self.outer_signals["load"])
        dialog_window.show()
        dialog_window.exec_()

    def resizeEvent(self, event):
        self.paintEvent(event)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_background_lines(qp)
        qp.end()

    def print_descriptions(self, descriptions: list[str]):
        self.descriptions.clear()
        font: QFont = self.descriptions.font()
        print(font.pixelSize())
        for i in range(0, len(descriptions)):
            description_words: list[str] = descriptions[i].split()
            letter_width = self.descriptions.fontMetrics().averageCharWidth() + 1
            line = f"{i + 1}. "
            while len(description_words) != 0:
                current_word = description_words.pop(0)
                if len(line + current_word) * letter_width <= self.descriptions.width():
                    line += current_word
                    line += " "
                else:
                    self.descriptions.addItem(line)
                    line = "    " + current_word + " "
            self.descriptions.addItem(line)
        while self.descriptions.count() * (font.pixelSize() + 6) > self.descriptions.height():
            font.setPixelSize(font.pixelSize() - 1)
        self.descriptions.setFont(font)

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


class StartScreen(QWidget, PythonClasses.StartScreenView):
    def __init__(self, signals: dict[str, AbstractEmitter]):
        QWidget.__init__(self)
        self.setupUi(self)

        self.outer_signals = signals
        self.dialog_canceled = VoidEmitter()
        self.dialog_canceled.signal.connect(self.show)

        self.generateButton.clicked.connect(self.open_generate_input)
        self.loadButton.clicked.connect(self.open_load_input)

    def open_generate_input(self):
        dialog_window = GenerateDialogWindow(self.dialog_canceled, self.outer_signals["generate"])
        dialog_window.show()
        dialog_window.exec_()

    def open_load_input(self):
        dialog_window = LoadDialogWindow(self.dialog_canceled, self.outer_signals["load"])
        dialog_window.show()
        dialog_window.exec_()


class GenerateDialogWindow(QDialog, PythonClasses.GenerateDialogWindowView):

    def __init__(self, dialog_canceled: VoidEmitter, got_generate_data: StringEmitter):
        QDialog.__init__(self)
        self.setModal(True)
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
        self.setModal(True)
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
            self.__browseWindow.setModal(True)
            self.__browseWindow.show()
        if self.__browseWindow.exec_():
            self.pathInput.setText(self.__browseWindow.selectedFiles()[0])
            self.__browseWindow.close()
            self.__browseWindow = None


class CrosswordPresenter:
    def __init__(self):
        self.dialog_signals = {"generate": TupleEmitter(),
                               "load": StringEmitter()}
        self.error_signals = {"incorrect word": StringEmitter(),
                              "file not found": StringEmitter(),
                              "wrong extension": StringEmitter(),
                              "corrupted file": TupleEmitter()}

        self.dialog_signals["generate"].signal.connect(self.start_generate)
        self.dialog_signals["load"].signal.connect(self.start_load)
        self.error_signals["file not found"].signal.connect(self.display_nonexisting_file_error)
        self.error_signals["wrong extension"].signal.connect(self.display_wrong_extension_error)

        self.__main_window = MainWindow(self.dialog_signals)
        self.__start_screen = StartScreen(self.dialog_signals)
        self.__main_window.hide()
        self.__start_screen.show()
        self.__crossword = []

    def start_generate(self, data: tuple[str]):
        self.__main_window.descriptions.clear()
        for i in range(len(data)):
            self.__main_window.descriptions.addItem(f"{i + 1}. {data[i]};")
        self.__crossword = CrosswordGenerator(data).generate()
        self.show()

    def start_load(self, path: str):
        self.__crossword = load_crossword(find_sub_dict(self.error_signals,
                                                        ("file not found", "wrong extension", "corrupted file")),
                                          path)
        print(self.__crossword)
        self.show()
        pass

    def display_nonexisting_file_error(self, incorrect_path: str):
        error_window = QDialog()
        error_window.setWindowTitle(incorrect_path)
        error_window.setModal(True)
        error_window.show()
        error_window.exec_()

    def display_wrong_extension_error(self, incorrect_extension: str):
        error_window = QDialog()
        error_window.setWindowTitle(incorrect_extension + " != .csv")
        error_window.setModal(True)
        error_window.show()
        error_window.exec_()

    def show(self):
        self.__main_window.print_descriptions([crossword_part["description"] for crossword_part in self.__crossword])

        self.__start_screen.close()
        self.__main_window.show()
