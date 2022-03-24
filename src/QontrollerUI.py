import time

from PyQt5 import QtCore, QtGui, QtWidgets
import os
from . import qontroller
import json
import datetime as dt

from .device import Device
from .picam_settings import PicamSettings


class Worker(QtCore.QObject):

    finished = QtCore.pyqtSignal()  # give worker class a finished signal

    def __init__(self, main_window, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class
        self.main_window = main_window

    def do_work(self):
        while self.continue_run:  # give the loop a stoppable condition
            #QtCore.QThread.sleep(1)
            self.main_window.refresh_view()
        self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        self.continue_run = False  # set the run condition to false on stop

class ContextmenuDevice(QtWidgets.QMenu):
    def __init__(self):
        QtWidgets.QMenu.__init__(self)
        test_action = QtWidgets.QAction("print yo", triggered=self.test_function)
        self.addAction(test_action)

class QontrollerUI(QtWidgets.QMainWindow, qontroller.Ui_MainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(QontrollerUI, self).__init__(parent)
        self.setupUi(self)

        #self.resize(QtWidgets.QDesktopWidget().availableGeometry(self).size() * 0.8)
        self.centerandresize()

        # Attributes

        self.host_list = []
        self.currentDeviceID = None

        self.full_pixmap = None
        self.zoom_value = self.sliderZoom.value()
        self.fit_view_status = self.btnFitView.isChecked()

        self.do_auto_refresh = self.btnLiveView.isChecked()

        self.comboTimeoutUnit.addItems(["Seconds", "Minutes", "Hours"])

        # Signals

        self.btnRefresh.clicked.connect(self.refresh_view)
        self.btnRescanDevices.clicked.connect(self.scan_devices)

        self.listBoxDevices.currentItemChanged.connect(self.current_item_changed)
        self.sliderZoom.valueChanged.connect(self.zoom)


        self.listBoxDevices.installEventFilter(self)

        # create context menu - not used anymore
        self.popMenu = QtWidgets.QMenu(self)
        self.popMenu.addAction(QtWidgets.QAction('test0', self, triggered=self.test_function))
        self.popMenu.addAction(QtWidgets.QAction('test1', self))
        self.popMenu.addSeparator()
        self.popMenu.addAction(QtWidgets.QAction('test2', self))

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

    #def on_context_menu(self, point): # not used anymore
    #    # show context menu
     #   self.popMenu.exec_(self.listBoxDevices.mapToGlobal(point))
    def centerandresize(self, rat=[0.75, 0.75]):
        geo = QtWidgets.QDesktopWidget().availableGeometry()
        w, h = geo.width(), geo.height()
        self.resize(int(w * rat[0]), int(h * rat[1]))
        qr = self.frameGeometry()
        cp = geo.center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def stop_thread(self):
        self.stop_signal.emit()  # emit the finished signal on stop

    def test_function(self):
        print("yo")

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.ContextMenu and
                source is self.listBoxDevices):
            menu = ContextmenuDevice()
            if menu.exec_(event.globalPos()):
                item = source.itemAt(event.pos())

            # je pense que c'est plus simple comme en dessous
            """
            menu = QtWidgets.QMenu()
            menu.addAction('Open Window')
            if menu.exec_(event.globalPos()):
                item = source.itemAt(event.pos())
                print(item.text())
            """
            return True
        return super(QontrollerUI, self).eventFilter(source, event)

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

    def right_menu_device(self, pos):
        menu = QMenu(self.listBoxDevices)

        # Add menu options
        hello_option = menu.addAction('Hello World')
        goodbye_option = menu.addAction('GoodBye')
        exit_option = menu.addAction('Exit')

        # Menu option events
        hello_option.triggered.connect(lambda: print('Hello World'))
        goodbye_option.triggered.connect(lambda: print('Goodbye'))
        exit_option.triggered.connect(lambda: exit())

        # Position
        menu.exec_(self.mapToGlobal(pos))

    def scan_devices(self):
        self.listBoxDevices.clear()
        self.host_list = []
        with open("hosts_list.txt", 'r') as hosts_list:
            for host in hosts_list.read().splitlines():
                # device = "piworm%02d.epfl.ch" % i
                # Check if device name is marked as comment
                if host[0] != '#':
                    if os.name == 'nt':
                        if os.system("ping -n 1 -w 300 " + host) == 0:
                            self.add_device(host)
                    else:
                        if os.system("ping -c 1 -q -W 0.3 " + host) == 0:
                            self.add_device(host)

    def refresh_view(self):
        if self.currentDeviceID is not None:
            currentDevice = self.host_list[self.currentDeviceID]
            #s = PicamSettings(self)

            config = self.generate_json_config_from_GUI_widgets(preview_mode=True)
            file = self.save_json_config_file(config)

            remote_path = currentDevice.receive_json_config_file(file)

            self.full_pixmap = currentDevice.get_frame(remote_path)
            # self.labelDisplay.setPixmap(self.full_pixmap)

            self.display_frame_pixmap(self.full_pixmap)

        else:
            print("Please first select a device")

    def display_frame_pixmap(self, pxm):
        if self.fit_view_status:
            self.labelDisplay.setPixmap(pxm.scaled(self.scrollArea.size(), QtCore.Qt.KeepAspectRatio))
        else:
            self.labelDisplay.setPixmap(pxm.scaled(self.full_pixmap.size() * self.sliderZoom.value() / 100,
                                                                QtCore.Qt.KeepAspectRatio))

    def auto_refresh(self):
        while self.do_auto_refresh:
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

    def fit_view(self, pxm):
        if self.fit_view_status:
            return pxm.scaled(self.scrollArea.size(), QtCore.Qt.KeepAspectRatio)
        return pxm

    def set_pixmap_scaling(self, pxm):
        pass

    def generate_json_config_from_GUI_widgets(self, preview_mode):
        """
        :param preview_mode: bool, if true, only one frame is captured
        :return: dictionary containing all the GUI input
        """

        json_dict = {"verbosity_level":	0,
                     "timeout": 		self.spinTimeout.value() * (60 ** self.comboTimeoutUnit.currentIndex()),
                     "time_interval": 	self.spinTimeInterval.value(),
                     "average": 		self.spinAveraging.value(),
                     "quality": 		self.spinJpgQuality.value(),
                     "ISO":				self.spinISO.value(),
                     "shutter_speed":	self.spinShutterSpeed.value(),
                     "brightness":	    self.spinBrightness.value(),
                     "compress": 		self.spinArchiveSize.value(),
                     "start_frame":		self.spinStartingFrame.value(),
                     "LED_intensity":   self.spinLEDIntensity.value(),
                     "annotate_frames": True,
                     "use_samba":		True,
                     "smb_service":		"//lpbsnas1.epfl.ch/LPBS",
                     "workgroup":		None,
                     "credentials_file": "/etc/.smbpicreds",
                     "smb_dir": 		"Users/Matthieu-Schmidt/WORMSTATION/",
                     "local_output_dir":  None,
                     "output_filename":	"auto",
                     "local_tmp_dir":    ".wormstation_tmp",
                     "capture_timeout":	3.0}

        if preview_mode:
            json_dict["timeout"] = 0
            json_dict["use_samba"] = False
            json_dict["local_tmp_dir"] = json_dict["local_tmp_dir"]

        #return f'"{json.dumps(json_dict)}"'
        return json_dict

    def save_json_config_file(self, json_config, filename=None):
        """
        :param json_config: dictionary of the configuration
        :param filename: output filename to save the file containing the json configuration
        :return: the output filename
        """
        if filename is None:
            filename = f'wormstation_{dt.datetime.now().strftime("%Y%m%d_%H%M")}.json'
        with open(filename, 'w') as jfile:
            json.dump(json_config, jfile, indent=4)

        return filename




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

    def showdialogWarning(self, main_text, additional_text=None):
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

        config = self.generate_json_config_from_GUI_widgets(preview_mode=False)
        file = self.save_json_config_file(config)




        # Check if all the devices are up-to-date.
        # If all devices are up-to-date (on_btnCheckUpdates_clicked empty, then do recording)
        if not self.on_btnCheckUpdates_clicked(devices_marked_for_recording):
            s = PicamSettings(self)
            for d in devices_marked_for_recording:

                remote_path = d.receive_json_config_file(file)

                d.record(remote_path)

        # Else ask to do the update
        else:
            self.showdialogWarning(main_text="Some devices are out of date. Please update them before recording.")




    @QtCore.pyqtSlot()
    def on_btnStopRecord_clicked(self):
        devices_marked_for_recording = self.get_devices_marked_for_recording()
        for d in self.running_devices():
            if d in devices_marked_for_recording:
                d.stop()

    def running_devices(self):
        running_list = []
        for d in self.host_list:
            if d.is_running:
                running_list.append(d)
        return running_list



    @QtCore.pyqtSlot(bool)
    def on_btnFitView_clicked(self, checked):

        self.fit_view_status = checked

        if checked:
            self.sliderZoom.setValue(100)
            self.display_frame_pixmap(self.full_pixmap)

            #print(self.sliderZoom.getMinimum())




    @QtCore.pyqtSlot()
    def on_btnOriginalView_clicked(self):
        self.labelDisplay.setPixmap(self.full_pixmap)

    @QtCore.pyqtSlot(bool)
    def on_btnLiveView_clicked(self, checked):
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

    @QtCore.pyqtSlot()
    def on_btnShutdown_clicked(self):
        for d in self.host_list:
            d.shutdown()

    ### TAB 2

    @QtCore.pyqtSlot()
    def on_btnOpenFile_clicked(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                      '/home/matthieu/data/PIWORM', "Image files (*.jpg *.gif)")
        self.labelDisplay_2.setPixmap(QtGui.QPixmap(fname[0]))