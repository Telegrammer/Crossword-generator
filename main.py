import sys

from UI.StartScreen import *


def window():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    ex = UiStartScreen()
    ex.setupUi(w)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    window()
