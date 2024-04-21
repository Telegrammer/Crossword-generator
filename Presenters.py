from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog

from UI import PythonClasses


class StartScreen(QWidget, PythonClasses.StartScreenView):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.generateButton.clicked.connect(self.start_generate)
        self.loadButton.clicked.connect(self.start_load)

    def start_generate(self):
        self.hide()
        dialog_window = GenerateDialogWindow(self)
        dialog_window.show()
        dialog_window.exec_()

    def start_load(self):
        self.hide()
        dialog_window = LoadDialogWindow(self)
        dialog_window.show()
        dialog_window.exec_()


class GenerateDialogWindow(QDialog, PythonClasses.GenerateDialogWindowView):

    def __init__(self, start_screen: StartScreen):
        QDialog.__init__(self)
        self.setupUi(self)
        self._start_screen = start_screen
        self.buttonBox.accepted.connect(self.send_data_for_generation)
        self.buttonBox.rejected.connect(self.return_start_screen)

    def send_data_for_generation(self):
        self._start_screen.close()
        self.close()

    def return_start_screen(self):
        self._start_screen.show()
        self.close()


class LoadDialogWindow(QDialog, PythonClasses.LoadDialogWindowView):
    def __init__(self, start_screen: StartScreen):
        QDialog.__init__(self)
        self.setupUi(self)
        self._start_screen = start_screen
        self.buttonBox.accepted.connect(self.send_data_for_load)
        self.buttonBox.rejected.connect(self.return_start_screen)
        self.browseButton.clicked.connect(self.browse)

    def send_data_for_load(self):
        self._start_screen.close()
        self.close()

    def return_start_screen(self):
        self._start_screen.show()
        self.close()

    def browse(self):
        file_dialog = QFileDialog()
        file_dialog.show()
        if file_dialog.exec_():
            self.pathInput.setText(file_dialog.selectedFiles()[0])

