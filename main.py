from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
import sys

from QontrollerMainWindow import QontrollerMainWindow

def main():
    app = QApplication(sys.argv)
    form = QontrollerMainWindow()

    form.show()
    app.exec_()


if __name__ == '__main__':
    main()