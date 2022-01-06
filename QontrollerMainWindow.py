from PyQt5 import QtCore, QtGui, QtWidgets
import os
import qontroller

from command_functions import *
from device import Device


class QontrollerMainWindow(QtWidgets.QMainWindow, qontroller.Ui_MainWindow):
    def __init__(self, parent=None):
        super(QontrollerMainWindow, self).__init__(parent)
        self.setupUi(self)

        # Attributes

        self.host_list = []


        # Signals

        self.btnRefresh.clicked.connect(test)
        self.btnRescanDevices.clicked.connect(self.scan_devices)


        # Execute on startup

        self.scan_devices()


    def add_device(self, name):
        id = self.listBoxDevices.count()
        new_device = Device(name, id=id)
        new_item = QtWidgets.QListWidgetItem(name)

        self.listBoxDevices.addItem(new_item)
        self.host_list.append(new_device)

    def scan_devices(self):
        self.listBoxDevices.clear()
        self.host_list = []
        with open("hosts_list.txt", 'r') as hosts_list:
            for host in hosts_list.read().splitlines():
                # device = "piworm%02d.epfl.ch" % i
                if os.system("ping -c 1 -q -W 0.3 " + host) == 0:
                    self.add_device(host)

