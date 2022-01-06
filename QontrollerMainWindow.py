from PyQt5 import QtCore, QtGui, QtWidgets
import os
import qontroller

from command_functions import *
from device import Device
from picam_settings import PicamSettings


class QontrollerMainWindow(QtWidgets.QMainWindow, qontroller.Ui_MainWindow):
    def __init__(self, parent=None):
        super(QontrollerMainWindow, self).__init__(parent)
        self.setupUi(self)

        # Attributes

        self.host_list = []
        self.currentDeviceID = None

        self.comboTimeoutUnit.addItems(["Seconds", "Minutes", "Hours"])

        # Signals

        self.btnRefresh.clicked.connect(self.refresh_view)
        self.btnRescanDevices.clicked.connect(self.scan_devices)

        # Execute on startup

        self.scan_devices()

        s = PicamSettings(self)
        print(s.time_interval)


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
        self.currentDeviceID = index.row()
        self.refresh_view()

    @QtCore.pyqtSlot(int)
    def on_comboTimeoutUnit_currentIndexChanged(self, index):
        if index == 0:
            self.labelTimeout.setText("Timeout (s)")
        elif index == 1:
            self.labelTimeout.setText("Timeout (min)")
        elif index == 2:
            self.labelTimeout.setText("Timeout (h)")

