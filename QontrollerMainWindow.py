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
        self.currentDevice = None

        self.comboTimeoutUnit.addItems(["Seconds", "Minutes", "Hours"])

        # Signals

        self.btnRefresh.clicked.connect(self.refresh_view)
        self.btnRescanDevices.clicked.connect(self.scan_devices)

        self.listBoxDevices.currentItemChanged.connect(self.current_item_changed)

        # Execute on startup

        self.scan_devices()



    def add_device(self, name):
        id = self.listBoxDevices.count()
        new_device = Device(name, id=id)
        new_item = QtWidgets.QListWidgetItem(name)

        #item = QtWidgets.QListWidgetItem(testcase_name)
        new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsUserCheckable)
        new_item.setCheckState(QtCore.Qt.Checked)
        #self.listWidgetTestCases.addItem(item)

        ch = QtWidgets.QCheckBox()
        #new_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        self.listBoxDevices.addItem(new_item)
        self.host_list.append(new_device)

    def scan_devices(self):
        self.listBoxDevices.clear()
        self.host_list = []
        with open("hosts_list.txt", 'r') as hosts_list:
            for host in hosts_list.read().splitlines():
                # device = "piworm%02d.epfl.ch" % i
                # Check if device name is marked as comment
                if host[0] != '#':
                    if os.system("ping -c 1 -q -W 0.3 " + host) == 0:
                        self.add_device(host)

    def refresh_view(self):
        if self.currentDeviceID is not None:
            currentDevice = self.host_list[self.currentDeviceID]
            s = PicamSettings(self)
            self.labelDisplay.setPixmap(currentDevice.get_frame(s))
        else:
            print("Please first select a device")

    def on_listBoxDevices_clicked(self, index):
        pass
        #print(self.listBoxDevices.currentItemChanged())

    def get_devices_marked_for_recording(self):
        devices_marked_for_recording = []
        for i in range(self.listBoxDevices.count()):
            item = self.listBoxDevices.item(i)
            if item.checkState():
                devices_marked_for_recording.append(self.host_list[i])

        return devices_marked_for_recording

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem, QtWidgets.QListWidgetItem)
    def current_item_changed(self, d0,d1):
        self.currentDeviceID = self.listBoxDevices.currentRow()
        self.refresh_view()


    @QtCore.pyqtSlot(int)
    def on_comboTimeoutUnit_currentIndexChanged(self, index):
        if index == 0:
            self.labelTimeout.setText("Timeout (s)")
        elif index == 1:
            self.labelTimeout.setText("Timeout (min)")
        elif index == 2:
            self.labelTimeout.setText("Timeout (h)")

    @QtCore.pyqtSlot()
    def on_btnCheckUpdates_clicked(self, device_list=None):
        if device_list is None:
            device_list = self.host_list

        updatable_devices = []
        for d in device_list:
            if not d.is_uptodate:
                updatable_devices.append(d)

        return updatable_devices

    @QtCore.pyqtSlot()
    def on_btnUpdateAll_clicked(self):
        for d in self.on_btnCheckUpdates_clicked():
            d.update()

    def showdialogWarning(self, main_text, additional_text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)

        msg.setText(main_text)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle("Warning")
        #msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

        retval = msg.exec_()

    @QtCore.pyqtSlot()
    def on_btnRecord_clicked(self):

        devices_marked_for_recording = self.get_devices_marked_for_recording()

        # Check if all the devices are up-to-date.
        # If all devices are up-to-date (on_btnCheckUpdates_clicked empty, then do recording)
        if not self.on_btnCheckUpdates_clicked(devices_marked_for_recording):
            s = PicamSettings(self)
            for d in devices_marked_for_recording:
                d.record(s)
        # Else ask to do the update
        else:
            self.showdialogWarning(main_text="Some devices are out of date. Please update them before recording.")




    @QtCore.pyqtSlot()
    def on_btnStopRecord_clicked(self):
        for d in self.running_devices():
            d.stop()

    def running_devices(self):
        running_list = []
        for d in self.host_list:
            if d.is_running:
                running_list.append(d)
        return running_list
