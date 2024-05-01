import random
import sys

from PyQt5.QtWidgets import QApplication

from Presenters import *


def window():
    app = QApplication(sys.argv)
    w = CrosswordPresenter()
    sys.exit(app.exec_())


if __name__ == '__main__':
    window()
