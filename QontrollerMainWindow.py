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
        self.currentDeviceID = None

        # Signals

        self.btnRefresh.clicked.connect(self.refresh_view)
        self.btnRescanDevices.clicked.connect(self.scan_devices)
        #self.listBoxDevices.clicked.connect(self.on_listBoxDevices_clicked)


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

    def refresh_view(self):
        if self.currentDeviceID is not None:
            currentDevice = self.host_list[self.currentDeviceID]
            self.labelDisplay.setPixmap(currentDevice.get_frame())
        else:
            print("Please first select a device")

    def on_listBoxDevices_clicked(self, index):
        #print('selected item index found at %s with data: %s' % (index.row(), index.data()))
        self.currentDeviceID = index.row()
        self.refresh_view()

