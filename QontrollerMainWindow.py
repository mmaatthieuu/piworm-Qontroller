import time

from PyQt5 import QtCore, QtGui, QtWidgets
import os
import qontroller


from command_functions import *
from device import Device
from picam_settings import PicamSettings


class Worker(QtCore.QObject):

    finished = QtCore.pyqtSignal()  # give worker class a finished signal

    def __init__(self, main_window, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class
        self.main_window = main_window

    def do_work(self):
        i = 1
        while self.continue_run:  # give the loop a stoppable condition
            print(i)
            #QtCore.QThread.sleep(1)
            self.main_window.refresh_view()
            i = i + 1
        self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        self.continue_run = False  # set the run condition to false on stop


class QontrollerMainWindow(QtWidgets.QMainWindow, qontroller.Ui_MainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(QontrollerMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.resize(QtWidgets.QDesktopWidget().availableGeometry(self).size() * 0.8)

        # Attributes

        self.host_list = []
        self.currentDeviceID = None

        self.full_pixmap = None
        self.zoom_value = self.sliderZoom.value()

        self.do_auto_refresh = self.btnLiveView.isChecked()

        self.comboTimeoutUnit.addItems(["Seconds", "Minutes", "Hours"])

        # Signals

        self.btnRefresh.clicked.connect(self.refresh_view)
        self.btnRescanDevices.clicked.connect(self.scan_devices)

        self.listBoxDevices.currentItemChanged.connect(self.current_item_changed)
        self.sliderZoom.valueChanged.connect(self.zoom)

        # Execute on startup

        self.scan_devices()

        # Thread:

        self.thread = QtCore.QThread()
        self.worker = Worker(self)
        self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        # self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        # self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

        self.thread.started.connect(self.worker.do_work)
        self.thread.finished.connect(self.worker.stop)


        # When stop_btn is clicked this runs. Terminates the worker and the thread.

    def stop_thread(self):
        self.stop_signal.emit()  # emit the finished signal on stop



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
            self.full_pixmap = currentDevice.get_frame(s)
            # self.labelDisplay.setPixmap(self.full_pixmap)
            self.labelDisplay.setPixmap(self.full_pixmap.scaled(self.full_pixmap.size() * self.sliderZoom.value() / 100,
                                                                QtCore.Qt.KeepAspectRatio))
        else:
            print("Please first select a device")

    def auto_refresh(self):
        while self.do_auto_refresh:
            print("yo")
            QtCore.QThread.sleep(1)

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

    def zoom(self):
        self.labelDisplay.setPixmap(self.full_pixmap.scaled(self.full_pixmap.size()*self.sliderZoom.value()/100, QtCore.Qt.KeepAspectRatio))


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


    @QtCore.pyqtSlot()
    def on_btnFitView_clicked(self):
        pxm = self.labelDisplay.pixmap()
        self.labelDisplay.setPixmap(self.scaled(self.scrollArea.size(), QtCore.Qt.KeepAspectRatio))

    @QtCore.pyqtSlot()
    def on_btnOriginalView_clicked(self):
        self.labelDisplay.setPixmap(self.full_pixmap)

    @QtCore.pyqtSlot(bool)
    def on_btnLiveView_clicked(self, checked):
        print(checked)
        self.do_auto_refresh = checked
        if checked:
            self.thread = QtCore.QThread()
            self.worker = Worker(self)
            self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
            self.worker.moveToThread(self.thread)

            self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
            self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
            self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

            self.thread.started.connect(self.worker.do_work)
            self.thread.finished.connect(self.worker.stop)
            # self.auto_refresh()
            self.thread.start()
        else:
            self.stop_thread()