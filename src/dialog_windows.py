from PyQt5 import QtWidgets

def showdialogInfo(main_text):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(main_text)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()

def showdialogWarning(main_text, additional_text=None):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText(main_text)
    if additional_text is not None:
        msg.setInformativeText(additional_text)
    msg.setWindowTitle("Warning")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    retval = msg.exec_()
