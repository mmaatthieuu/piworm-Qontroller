from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
import sys

from QontrollerUI import QontrollerUI

def main():
    app = QApplication(sys.argv)
    form = QontrollerUI()

    form.show()
    app.exec_()


if __name__ == '__main__':
    main()