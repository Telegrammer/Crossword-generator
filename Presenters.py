from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPen, QFont, QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog, QMainWindow, QMessageBox

from Models import *
from UI import PythonClasses


class MainWindow(QMainWindow, PythonClasses.MainWindowView):

    def __init__(self, signals: dict[str, AbstractEmitter]):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.__crossword: Crossword = Crossword([])

        self.outer_signals = signals
        self.generate_action.triggered.connect(self.open_regenerate_input)
        self.load_action.triggered.connect(self.open_reload_input)
        self.save_action.triggered.connect(self.open_save_input)

        self.hide_descriptions_action.changed.connect(self.change_descriptions_view)
        self.hide_words_action.changed.connect(self.change_crossword_view)
        self.roll_action.triggered.connect(self.roll_crossword)

    def set_crossword(self, crossword: Crossword = Crossword([])):
        self.__crossword = crossword

    def get_crossword(self):
        return self.__crossword

    def open_regenerate_input(self):
        dialog_window = GenerateDialogWindow(self.outer_signals["generate"])
        dialog_window.show()
        dialog_window.exec_()

    def open_reload_input(self):
        dialog_window = LoadDialogWindow(self.outer_signals["load"])
        dialog_window.show()
        dialog_window.exec_()

    def take_screenshot(self):
        result = QPixmap(self.centralwidget.width(), self.centralwidget.height())
        qp = QPainter()
        qp.begin(result)
        self.draw_background_lines(qp)
        self.draw_crossword(qp)
        if not self.descriptions.isHidden():
            qp.drawPixmap(QPoint(self.descriptions.x(), self.descriptions.y()),
                          self.descriptions.grab(self.descriptions.rect()))
        qp.end()
        return result

    def open_save_input(self):
        window_screenshot = self.take_screenshot()
        dialog_window = SafeDialogWindow(self.outer_signals["save"],
                                         window_screenshot)
        dialog_window.show()
        dialog_window.exec_()

    def resizeEvent(self, event):
        self.paintEvent(event)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_background_lines(qp)
        self.draw_crossword(qp)
        qp.end()

    def change_descriptions_view(self):
        if self.hide_descriptions_action.isChecked():
            self.descriptions_label.hide()
            self.descriptions.hide()
        else:
            self.descriptions_label.show()
            self.descriptions.show()

    def change_crossword_view(self):
        self.__crossword.is_visible = not self.__crossword.is_visible
        self.update()

    def roll_crossword(self):
        self.__crossword.is_vertical = not self.__crossword.is_vertical
        self.update()

    def print_descriptions(self):
        if not self.__crossword.words_data:
            return

        descriptions = [word["description"] for word in self.__crossword.words_data]
        self.descriptions.clear()
        font: QFont = self.descriptions.font()
        font.setPixelSize(19)
        self.print_lines(font, descriptions)
        self.descriptions.setFont(font)

    def print_lines(self, font: QFont, descriptions: list[str]):
        letter_width = font.pixelSize()
        for i in range(0, len(descriptions)):
            description_words: list[str] = descriptions[i].capitalize().split()
            line = f"{i + 1}. "
            while len(description_words) != 0:
                current_word = description_words.pop(0)
                if len(line + current_word) * (letter_width - 7) <= self.descriptions.width():
                    line += current_word
                    line += " "
                else:
                    self.descriptions.addItem(line)
                    line = "    " + current_word + " "
            self.descriptions.addItem(line)
        if self.descriptions.count() * (letter_width + 4) > self.descriptions.height():
            font.setPixelSize(letter_width - 1)
            self.descriptions.clear()
            self.print_lines(font, descriptions)

    def draw_background_lines(self, qp: QPainter):
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

    def draw_crossword(self, qp: QPainter):
        if not self.__crossword.words_data:
            return
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        font = QFont("Calibri", 12, QFont.Bold)
        qp.setPen(pen)
        qp.setFont(font)
        icon = QImage("UI/media/FrameIcon.png")
        center = QPoint(self.centralwidget.width() // 3, self.centralwidget.height() // 2)

        row_offset = QPoint(0, icon.height())
        column_offset = QPoint(icon.width(), 0)
        if not self.__crossword.is_vertical:
            row_offset, column_offset = column_offset, row_offset

        for i in range(0, len(self.__crossword.words_data) // 2):
            center -= row_offset
        for i in range(0, len(self.__crossword.words_data)):
            for j in range(0, self.__crossword.words_data[i]["match position"]):
                center -= column_offset
            for j in range(0, len(self.__crossword.words_data[i]["word"])):
                qp.drawImage(center, icon)
                if self.__crossword.is_visible or j == self.__crossword.words_data[i]["match position"]:
                    qp.drawText(QPoint(center.x() + icon.width() // 2, center.y() + icon.height() // 2),
                                self.__crossword.words_data[i]["word"][j].upper())
                if j == self.__crossword.words_data[i]["match position"]:
                    qp.drawText(QPoint(center.x() + icon.width() // 4, int(center.y() + icon.height() // 1.5)),
                                str(i + 1))
                center += column_offset
            for j in range(0, len(self.__crossword.words_data[i]["word"]) - self.__crossword.words_data[i][
                "match position"]):
                center -= column_offset
            center += row_offset


class StartScreen(QWidget, PythonClasses.StartScreenView):
    def __init__(self, signals: dict[str, AbstractEmitter]):
        QWidget.__init__(self)
        self.setupUi(self)

        self.outer_signals = signals

        self.generateButton.clicked.connect(self.open_generate_input)
        self.loadButton.clicked.connect(self.open_load_input)

    def open_generate_input(self):
        dialog_window = GenerateDialogWindow(self.outer_signals["generate"])
        dialog_window.show()
        dialog_window.exec_()

    def open_load_input(self):
        dialog_window = LoadDialogWindow(self.outer_signals["load"])
        dialog_window.show()
        dialog_window.exec_()


class GenerateDialogWindow(QDialog, PythonClasses.GenerateDialogWindowView):

    def __init__(self, got_generate_data: StringEmitter):
        QDialog.__init__(self)
        self.setModal(True)
        self.setupUi(self)
        self.__difficulty = "Средний"

        self.__accepted = got_generate_data
        self.buttonBox.accepted.connect(self.send_data_for_generation)
        self.buttonBox.rejected.connect(self.return_start_screen)
        self.difficultyButtonGroup.buttonClicked.connect(lambda btn: self.set_difficulty(btn.text()))

    def send_data_for_generation(self):
        self.__accepted.signal.emit((self.keyWordInput.text(), self.__difficulty))
        self.close()

    def return_start_screen(self):
        self.close()

    def set_difficulty(self, difficulty: str):
        self.__difficulty = difficulty


class LoadDialogWindow(QDialog, PythonClasses.LoadDialogWindowView):
    def __init__(self, got_load_data: StringEmitter):
        QDialog.__init__(self)
        self.setModal(True)
        self.setupUi(self)
        self.__browseWindow = None

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


class SafeDialogWindow(QDialog, PythonClasses.SaveDialogWindowView):
    def __init__(self, got_save_data: TupleEmitter, crossword_screenshot: QPixmap):
        QDialog.__init__(self)
        self.setModal(True)
        self.setupUi(self)
        self.crosswordImageLabel.setPixmap(crossword_screenshot)
        self.__browseWindow = None
        self.__file_format = "Фото"

        self.__accepted = got_save_data

        self.buttonBox.accepted.connect(self.send_data_for_save)
        self.buttonBox.rejected.connect(self.return_start_screen)
        self.fileFormatButtonGroup.buttonClicked.connect(lambda btn: self.set_file_format(btn.text()))
        self.browseButton.clicked.connect(self.browse)

    def send_data_for_save(self):
        filename = self.fileNameInput.text()
        if not filename:
            filename = "untitiled"
        self.__accepted.signal.emit((filename, self.pathInput.text(), self.__file_format))
        self.close()

    def return_start_screen(self):
        if self.__browseWindow is not None:
            self.__browseWindow.close()
        self.close()

    def browse(self):
        if self.__browseWindow is None:
            self.__browseWindow = QFileDialog()
            self.__browseWindow.setModal(True)
            self.__browseWindow.setFileMode(QFileDialog.Directory)
            self.__browseWindow.show()
        if self.__browseWindow.exec_():
            self.pathInput.setText(self.__browseWindow.selectedFiles()[0])
            self.__browseWindow.close()
            self.__browseWindow = None

    def set_file_format(self, file_format: str):
        self.__file_format = file_format


class CrosswordPresenter:
    def __init__(self):
        self.__difficulty_identifier = {
            "Легкий": 1,
            "Средний": 2,
            "Тяжелый": 3
        }
        self.dialog_signals = {"generate": TupleEmitter(),
                               "load": StringEmitter(),
                               "save": TupleEmitter()}
        self.error_signals = {"incorrect word": StringEmitter(),
                              "file not found": StringEmitter(),
                              "wrong extension": StringEmitter(),
                              "corrupted file": TupleEmitter(),
                              "directory not found": StringEmitter(),
                              "keyword not found": StringEmitter(),
                              "words are over": StringEmitter()}

        self.dialog_signals["generate"].signal.connect(self.start_generate)
        self.dialog_signals["load"].signal.connect(self.start_load)
        self.dialog_signals["save"].signal.connect(self.start_save)
        self.error_signals["file not found"].signal.connect(self.display_nonexisting_file_error)
        self.error_signals["wrong extension"].signal.connect(self.display_wrong_extension_error)
        self.error_signals["corrupted file"].signal.connect(self.display_corrupted_file_error)
        self.error_signals["directory not found"].signal.connect(self.display_nonexisting_dir_error)
        self.error_signals["keyword not found"].signal.connect(self.display_unexcepted_keyword_error)
        self.error_signals["words are over"].signal.connect(self.display_empty_matches)

        self.__main_window = MainWindow(self.dialog_signals)
        self.__start_screen = StartScreen(self.dialog_signals)
        self.__main_window.hide()
        self.__start_screen.show()

    def start_generate(self, data: tuple[str]):
        self.__main_window.set_crossword(Crossword([]))
        self.__main_window.descriptions.clear()
        crossword = generate_crossword(find_sub_dict(self.error_signals, ("keyword not found", "words are over")),
                                       data[0],
                                       self.__difficulty_identifier[data[1]])
        self.__main_window.set_crossword(crossword)
        self.show()

    def start_load(self, path: str):
        self.__main_window.set_crossword(Crossword([]))
        crossword = Crossword(load_crossword(find_sub_dict(self.error_signals,
                                                           ("file not found", "wrong extension",
                                                            "corrupted file")),
                                             path))
        self.__main_window.set_crossword(crossword)
        self.show()
        pass

    def start_save(self, data: tuple[str]):
        if data[2] == "Фото":
            window_screenshot = self.__main_window.take_screenshot()
            window_screenshot.save(data[0] + ".png")
        else:
            save_crossword_table(find_sub_dict(self.error_signals, ["directory not found"]),
                                 f"{data[1]}/{data[0]}.csv", self.__main_window.get_crossword())

    @staticmethod
    def display_error(error_window: QMessageBox):
        error_window.setWindowTitle("Ошибка!")
        error_window.setModal(True)
        error_window.show()
        error_window.exec_()

    def display_nonexisting_file_error(self, incorrect_path: str):
        error_window = QMessageBox()
        if not incorrect_path:
            empty_str = "пустым"
        else:
            incorrect_path = " " + incorrect_path
            empty_str = ""
        error_window.setText(f"Не существует файла с {empty_str} путем {incorrect_path}")
        self.display_error(error_window)

    def display_wrong_extension_error(self, incorrect_extension: str):
        error_window = QMessageBox()
        error_window.setText(f"Выбранный файл должен быть формата .csv, а не {incorrect_extension}")
        self.display_error(error_window)

    def display_corrupted_file_error(self, data: tuple):
        error_window = QMessageBox()
        if not data:
            error_window.setText("Неправильно определены заголовки")
        else:
            error_window.setText(
                f"Буква с индексом {data[2]} слова {data[1]} не совпадает"
                f" с буквой ключевого слова {data[0]} с индексом {data[3]}")
        self.display_error(error_window)

    def display_nonexisting_dir_error(self, incorrect_path: str):
        error_window = QMessageBox()
        if not incorrect_path:
            empty_str = "пустым"
        else:
            incorrect_path = " " + incorrect_path
            empty_str = ""
        error_window.setText(f"Не существует директории с {empty_str} путем {incorrect_path}")
        self.display_error(error_window)

    def display_unexcepted_keyword_error(self, wrong_keyword: str):
        error_window = QMessageBox()
        error_window.setText(f"Ключевое слово {wrong_keyword} не найдено.")
        self.display_error(error_window)

    def display_empty_matches(self, key_char: str):
        error_window = QMessageBox()
        error_window.setText(f"Слов с буквой {key_char} не хватает для создания кроссворда.")
        self.display_error(error_window)

    def show(self):
        self.__main_window.print_descriptions()
        self.__start_screen.close()
        self.__main_window.show()
