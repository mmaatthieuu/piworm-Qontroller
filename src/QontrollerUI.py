import time

import paramiko.ssh_exception
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QMenu
import os
from . import qontroller
import json
import datetime as dt
import time
import subprocess
import sys
import shutil

from concurrent.futures import ThreadPoolExecutor

import threading

import getpass

#from multiprocessing import Pool
#from multiprocessing.pool import ThreadPool
#from itertools import compress

#from .device import Device, DeviceInstaller
#from .picam_settings import PicamSettings

from .device_manager import DeviceManager

from .dialog_windows import showdialogInfo, showdialogWarning
from .config_wizard import ConfigWizard, load_config, save_config


IR_PIN = 17
OG_PIN = 18


def get_device_updatable_status(device):
    return not device.is_uptodate


def update_device(device):
    device.update()


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

    def test_function(self):
        print("hello")

class QontrollerUI(QtWidgets.QMainWindow, qontroller.Ui_MainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(QontrollerUI, self).__init__(parent)
        self.setupUi(self)

        #self.resize(QtWidgets.QDesktopWidget().availableGeometry(self).size() * 0.8)
        self.centerandresize()


        # Set the default help text
        self.default_help_text = "Help: Hover any item to display help"
        self.label_help.setText(self.default_help_text)

        # Set tooltips for widgets
        self.set_tooltips()

        # Install event filters
        self.install_event_filters()


        # Attributes

        self.host_list = []
        self.currentDeviceID = None

        self.full_pixmap = None
        self.zoom_value = self.sliderZoom.value()
        self.fit_view_status = self.btnFitView.isChecked()

        self.do_auto_refresh = self.btnLiveView.isChecked()

        self.comboTimeoutUnit.addItems(["Seconds", "Minutes", "Hours"])
        self.comboOptoColor.addItems(["Orange","Blue"])
        self.comboCurrent.addItems(["7.5mA","12.5mA","25mA","37.5mA","50mA","75mA","100mA"])
        # sel default value for comboCurrent to 37.5mA
        self.comboCurrent.setCurrentIndex(3)

        self.dm = DeviceManager()

        # Signals

        self.btnRefresh.clicked.connect(self.refresh_view)
        self.btnRescanDevices.clicked.connect(self.scan_devices)

        self.listBoxDevices.currentItemChanged.connect(self.current_item_changed)
        self.sliderZoom.valueChanged.connect(self.zoom)

        # Connect sliders to the generalized LED switch function
        self.slider_switch_led.valueChanged.connect(
            lambda: self.switch_led(color='IR', current='37.5mA', all_devices=False))
        self.slider_switch_led_OG.valueChanged.connect(
            lambda: self.switch_led(color='Orange', current='37.5mA', all_devices=False))
        self.slider_switch_led_blue.valueChanged.connect(
            lambda: self.switch_led(color='Blue', current='37.5mA', all_devices=False))

        # When the combo box for the current is changed, update the current value
        # self.comboCurrent.currentIndexChanged.connect(
        #     lambda: self.switch_led(color='IR', current=self.comboCurrent.currentText(), all_devices=False))

        self.listBoxDevices.installEventFilter(self)

        self.btnStopRecord.clicked.connect(self.uncheck_live_view)

        # create context menu - not used anymore
        self.popMenu = QtWidgets.QMenu(self)
        self.popMenu.addAction(QtWidgets.QAction('test0', self, triggered=self.test_function))
        self.popMenu.addAction(QtWidgets.QAction('test1', self))
        self.popMenu.addSeparator()
        self.popMenu.addAction(QtWidgets.QAction('test2', self))

        # Execute on startup

        self.scan_devices()

        # Load or initialize configuration
        self.config = load_config()
        if not self.config:
            wizard = ConfigWizard()
            if wizard.exec_():
                self.config = wizard.collectData() # Implement collectData to gather data from the wizard
                save_config(self.config)
            else:
                # Handle cancellation or exit
                self.close()

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

        # Wait for 5 second and check date
        QtCore.QTimer.singleShot(4000, self.check_date)

        # When stop_btn is clicked this runs. Terminates the worker and the thread.

    def closeEvent(self, event):
        self.cleanup()  # Call the cleanup function
        event.accept()  # Accept the event to close the window


    #def on_context_menu(self, point): # not used anymore
    #    # show context menu
     #   self.popMenu.exec_(self.listBoxDevices.mapToGlobal(point))

    def cleanup(self):
        print("Cleaning up")

        # Set all sliders to 0 (which should represent the 'off' state)
        # This is to ensure that the LEDs are turned off when the program is closed (it will call the switch_led function)
        self.slider_switch_led.setValue(0)
        self.slider_switch_led_OG.setValue(0)
        self.slider_switch_led_blue.setValue(0)


    def check_date(self):
        # set limit date to 28.02.2024
        limit_date = dt.datetime(2024, 3, 4).date()

        # skip this check
        return True

        # Check if the software is up to date
        self.show()

        # Get current date
        current_date = dt.datetime.now().date()

        if current_date > limit_date:

            #Disable start button
            self.btnRecord.setEnabled(False)

            print("A new version of the software is available. Please update it.")
            showdialogInfo(main_text="A new version of the software is available. Please update it.")

            return False

        else:
            return True



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

    '''
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.ContextMenu and
                source is self.listBoxDevices):
            print("ok")
            menu = ContextmenuDevice()
            if menu.exec_(menu.mapToGlobal(event.pos())):
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
        
    '''

    def set_tooltips(self):

        self.labelDisplay.setToolTip("Displays the current view of the selected device.")

        self.btnRefresh.setToolTip("Refreshes the current view. If the selected device is running, it will display the last recorded frame. "
                                   "Otherwise, it will acquire a new frame.")
        self.sliderZoom.setToolTip("Adjust the zoom level of the displayed image.")
        self.btnFitView.setToolTip("Fit the image to the view area.")
        self.btnOriginalView.setToolTip("Reset the image to its original size.")
        self.btnLiveView.setToolTip("Toggle live view mode. When enabled, the view will automatically refresh every second. "
                                    "Avoid using on recording devices as it may slow down the recording process.")

        LED_switch_text = ("Switch the LEDs on or off. The current level can be adjusted with the dropdown menu. "
                           "For colored LEDs, if the current exceed 37.5mA, the LED will automatically switch off after 3 seconds.")
        self.slider_switch_led_OG.setToolTip(LED_switch_text)
        self.slider_switch_led.setToolTip(LED_switch_text)
        self.slider_switch_led_blue.setToolTip(LED_switch_text)

        # Parameters
        self.spinShutterSpeed.setToolTip("Shutter speed in microseconds. If set to 0, the camera will automatically adjust the shutter speed.")
        self.comboTimeoutUnit.setToolTip("Select the time unit for the timeout value.")
        self.spinTimeout.setToolTip("Total duration of the experiment to record. If set to 0, it will take only one frame.")
        self.spinBoxRecForS.setToolTip("Use this parameter with the next one (Every (s)) to only record at some specific intervals. "
                                       "Use this parameter to set the duration of the recording sessions (in seconds)." 
                                       "If set to 0, it will record continuously.")
        self.spinBoxEveryH.setToolTip("Use this parameter with the previous one (Record for (s)) to only record at some specific intervals. "
                                      "Use this parameter to set the period of recording sessions (in hours). "
                                      "If set to 0, it will record continuously.")
        self.spinTimeInterval.setToolTip("Period of frame acquisition.")
        self.spinArchiveSize.setToolTip("Number of individual frames compressed into a single video file.")
        self.spinStartingFrame.setToolTip("Frame number to start recording from.")
        self.spinIlluminationPulse.setToolTip("Duration of the infrared illumination pulse, in milliseconds.")
        self.checkBoxOptogen.setToolTip("Enable optogenetic stimulation.")
        self.comboOptoColor.setToolTip("Select the color of the optogenetic stimulation. If the illumination board has only one color, this parameter is ignored.")
        self.spinPulseDuration.setToolTip("Total duration of the optogenetic pulse, in seconds. The optogenetic pulse then consists "
                                          "of a series of pulses with a duration of one second every two seconds (between each frame acquisition).")
        self.spinPulseInterval.setToolTip("Interval between each optogenetic pulse, in seconds.")


        self.checkBoxComputeChemotax.setToolTip("Directly compute chemotaxis index and mobility stats from the recorded video. "
                                                "(Experimental, not working for single worm experiments)")
        self.checkBoxLog.setToolTip("Log the experiment parameters and timestamps of actions in a text file.")
        self.spinBoxVerbosity.setToolTip("Set the verbosity level of the log file. 0: no log, 1: only errors, 2: +warnings, 3: +info, "
                                         "4. +debug outputs, 5. +trace of each step.")
        self.lineEditUsername.setToolTip("Username to connect to the devices.")
        self.lineEditSshDest.setToolTip("[SSH mode only] Destination host address of the device to store the recorded files.")

        # Record
        self.textRecordName.setToolTip("Name of the recording. It will be appended to the date and time of the recording.")
        self.btnRecord.setToolTip("Start recording on the selected devices with the parameters defined above.")
        self.btnStopRecord.setToolTip("Interrupt the recording on the selected devices by killing the process.")

        self.btnDestDir.setToolTip("Open the destination directory of the recorded files.")

        self.listBoxDevices.setToolTip("List of connected devices. Devices in italic are currently running. "
                                       "Edit the file hosts_list.txt to add or remove devices.")
        self.btnRescanDevices.setToolTip("Rescans all available devices (from hosts_list.txt).")
        self.btnCheckUpdates.setToolTip("Check if updates are available for the selected devices.")
        self.btnUpdateAll.setToolTip("Update all devices with available updates.")

        self.btnClearTmpFolder.setToolTip("Clear the temporary folders on the selected devices. "
                                          "These folders are used to store the recorded frames before they are compressed into a video file"
                                          "and the video files before they are transferred to the NAS server.")

        self.btnRunInstall.setToolTip("Run the installation script on all devices. This script will install the necessary dependencies "
                                      "for the wormstation software, set permissions, etc.")

        self.btnReboot.setToolTip("Reboot all devices. EVEN RUNNING ONES. Use with caution. Comment devices in hosts_list.txt to exclude them.")
        self.btnShutdown.setToolTip("Shutdown all devices. EVEN RUNNING ONES. Use with caution. Comment devices in hosts_list.txt to exclude them.")


        # Add more tooltips as needed

    def install_event_filters(self):
        # Scan for all child widgets of the current UI
        widgets = self.findChildren(QtWidgets.QWidget)

        # Automatically filter widgets that have a tooltip set
        for widget in widgets:
            if widget.toolTip():  # Check if the widget has a tooltip
                widget.installEventFilter(self)  # Install the event filter

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Enter:
            if isinstance(source, QtWidgets.QWidget):
                help_text = source.toolTip()
                self.label_help.setText(help_text)
        elif event.type() == QtCore.QEvent.Leave:
            self.label_help.setText(self.default_help_text)

        return super(QontrollerUI, self).eventFilter(source, event)

    def contextMenuEvent(self, event):
        contextMenu = QtWidgets.QMenu(self)
        newAct = contextMenu.addAction("New")
        openAct = contextMenu.addAction("Open")
        quitAct = contextMenu.addAction("Quit")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            self.close()

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
        """Scan and display devices in the UI."""
        username = self.lineEditUsername.text()
        self.dm.scan_devices(username=username)  # Populate devices in DeviceManager

        self.listBoxDevices.clear()
        for device in self.dm.host_list:
            new_item = QtWidgets.QListWidgetItem(device.name)
            new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            new_item.setCheckState(QtCore.Qt.Checked)

            # If the device is running, make the text italic
            if device.is_running:
                font = new_item.font()
                font.setItalic(True)
                new_item.setFont(font)

            self.listBoxDevices.addItem(new_item)

    def refresh_view(self):
        try:
            if self.currentDeviceID is not None:
                # get the device currently selected
                currentDevice = self.dm.get_device_by_id(self.currentDeviceID)

                config = self.generate_json_config_from_GUI_widgets(preview_mode=True)
                file = self.save_json_config_file(config)

                remote_path = currentDevice.receive_json_config_file(file)
                os.remove(file)

                self.full_pixmap = currentDevice.get_frame(remote_path)
                # self.labelDisplay.setPixmap(self.full_pixmap)

                self.display_frame_pixmap(self.full_pixmap)

                # self.switch_led_IR()
                # self.switch_led_OG()

            else:
                print("Please first select a device")
        except paramiko.ssh_exception.SSHException:
            print("Connection with devices lost, please rescan for devices")
        except ConnectionResetError:
            print("Connection with devices lost, please rescan for devices")

    def display_frame_pixmap(self, pxm):
        if pxm is not None:
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


    def zoom(self):
        self.labelDisplay.setPixmap(self.full_pixmap.scaled(self.full_pixmap.size()*self.sliderZoom.value()/100, QtCore.Qt.KeepAspectRatio))

    def fit_view(self, pxm):
        if self.fit_view_status:
            return pxm.scaled(self.scrollArea.size(), QtCore.Qt.KeepAspectRatio)
        return pxm

    def set_pixmap_scaling(self, pxm):
        pass

    def get_timeout(self):
        # Return timeout in seconds
        return self.spinTimeout.value() * (60 ** self.comboTimeoutUnit.currentIndex())

    def generate_json_config_from_GUI_widgets(self, preview_mode):
        """
        :param preview_mode: bool, if true, only one frame is captured
        :return: dictionary containing all the GUI input
        """

        json_dict = {"verbosity_level":	self.spinBoxVerbosity.value(),
                     "timeout": 		self.get_timeout(),
                     "record_for_s":    self.spinBoxRecForS.value(),
                     "record_every_h":  self.spinBoxEveryH.value(),
                     "time_interval": 	self.spinTimeInterval.value(),
                     "shutter_speed":	self.spinShutterSpeed.value(),
                     "compress": 		self.spinArchiveSize.value(),
                     "start_frame":		self.spinStartingFrame.value(),
                     "illumination_pulse":  self.spinIlluminationPulse.value(),
                     "optogenetic":     self.checkBoxOptogen.isChecked(),
                     "optogenetic_color": self.comboOptoColor.currentText(),
                     "pulse_duration":  self.spinPulseDuration.value(),
                     "pulse_interval":  self.spinPulseInterval.value(),
                     "annotate_frames": True,
                     "use_samba":		True,
                     "use_ssh":			False,
                     "ssh_destination": self.lineEditSshDest.text(),
                     "ssh_dir":         "/media/scientist/SanDisk",
                     "nas_server":		"//lpbsnas1.epfl.ch",
                     "share_name":		"LPBS2",
                     "workgroup":		None,
                     "credentials_file": "/etc/.smbpicreds",
                     "smb_dir": 		"Misc/Matthieu-Schmidt/WORMSTATION_RECORDINGS/",
                     "local_output_dir":  None,
                     "output_filename":	"auto",
                     "local_tmp_dir":    "wormstation_recordings",
                     "capture_timeout":	5.0,
                     "recording_name":  self.textRecordName.toPlainText(),
                     "compute_chemotaxis": self.checkBoxComputeChemotax.isChecked()}

        if preview_mode:
            json_dict["timeout"] = 0
            json_dict["use_samba"] = False
            #json_dict["local_tmp_dir"] = json_dict["local_tmp_dir"]

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
    def on_btnCheckUpdates_clicked(self, devices_list=None):
        """Check for devices that need updates and return them."""
        return self.dm.check_updates(devices_list)

    @QtCore.pyqtSlot()
    def on_btnUpdateAll_clicked(self):
        """Update all devices that need updating."""
        self.dm.update_all_devices()

    '''
    def showdialogWarning(self, main_text, additional_text=None):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)

        msg.setText(main_text)
        #msg.setInformativeText("This is additional information")
        msg.setWindowTitle("Warning")
        #msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

        retval = msg.exec_()

    def showdialogInfo(self, main_text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(main_text)
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
    '''

    @QtCore.pyqtSlot()
    def on_btnRecord_clicked(self):
        devices_marked_for_recording = self.get_devices_selected_devices()

        config = self.generate_json_config_from_GUI_widgets(preview_mode=False)
        file = self.save_json_config_file(config)

        # Check if all devices are up-to-date
        updatable_devices = self.on_btnCheckUpdates_clicked(devices_marked_for_recording)
        if updatable_devices:
            # Show a dialog with options: Cancel, Run Anyway, Update & Run
            dialog = QMessageBox()
            dialog.setWindowTitle("Devices Out of Date")
            dialog.setText("Some devices are out of date. Do you want to update them before recording?")
            dialog.setIcon(QMessageBox.Warning)

            # Add buttons
            cancel_button = dialog.addButton("Cancel", QMessageBox.RejectRole)
            run_anyway_button = dialog.addButton("Run Anyway", QMessageBox.AcceptRole)
            update_and_run_button = dialog.addButton("Update & Run", QMessageBox.ActionRole)

            dialog.exec_()

            if dialog.clickedButton() == cancel_button:
                # User chose to cancel
                print("Recording canceled by user.")
                os.remove(file)
                return

            elif dialog.clickedButton() == run_anyway_button:
                # User chose to run without updating
                print("Running recording without updating devices.")

            elif dialog.clickedButton() == update_and_run_button:
                # User chose to update and then run
                print("Updating devices before recording.")
                self.dm.update_all_devices()

        # If no updates are needed or user chose to proceed, start the recording
        for d in devices_marked_for_recording:
            remote_path = d.receive_json_config_file(file)
            d.record(remote_path)

        os.remove(file)


    def start_timer(self):
        timeout = self.get_timeout()
        start_time = time.time()

        """
        while some device are running, write theri remaining time next to their name
        """


    @QtCore.pyqtSlot()
    def on_btnStopRecord_clicked(self):
        self.on_btnLiveView_clicked(False)
        devices_marked_for_recording = self.get_devices_selected_devices(exclude_running=False)
        for d in self.dm.running_devices():
            if d in devices_marked_for_recording:
                d.stop()


    def switch_led(self, color, current='37.5mA', all_devices=False):
        """Switch the specified LED on or off based on slider value."""
        # Determine the correct slider for the color
        slider = {
            'IR': self.slider_switch_led,
            'Orange': self.slider_switch_led_OG,
            'Blue': self.slider_switch_led_blue
        }.get(color)

        if slider is None:
            print(f"Invalid color '{color}'")
            return

        # Get the current slider status and selected current level
        status = slider.value()
        current = self.comboCurrent.currentText()

        # Get the devices that should have their LEDs controlled
        device_list = self.host_list if all_devices else self.get_devices_selected_devices()

        # Filter out running devices
        device_list = [d for d in device_list if not d.is_running]

        self.dm.switch_led(color, status, current, device_list)

    def get_devices_selected_devices(self, exclude_running=True):
        """Get devices marked for recording based on list box selections, optionally excluding running devices."""
        selected_devices = []
        list_box = self.listBoxDevices
        for i in range(list_box.count()):
            item = list_box.item(i)
            if item.checkState():
                device = self.dm.host_list[i]
                if not (exclude_running and device.is_running):
                    selected_devices.append(device)
        return selected_devices






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
    def uncheck_live_view(self):
        if self.btnLiveView.isChecked():
            self.btnLiveView.setChecked(False)

    @QtCore.pyqtSlot()
    def on_btnClearTmpFolder_clicked(self):
        devices_list = self.get_devices_selected_devices()
        self.dm.clear_tmp_folders(devices_list)

    @QtCore.pyqtSlot()
    def on_btnRunInstall_clicked(self):
        self.dm.install_on_all_devices()

    @QtCore.pyqtSlot()
    def on_btnShutdown_clicked(self):
        self.dm.shutdown_devices()

    @QtCore.pyqtSlot()
    def on_btnReboot_clicked(self):
        self.dm.reboot_devices()

    ### TAB 2

    @QtCore.pyqtSlot()
    def on_btnOpenFile_clicked(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                      '/home/matthieu/data/PIWORM', "Image files (*.jpg *.gif)")
        self.labelDisplay_2.setPixmap(QtGui.QPixmap(fname[0]))

    @QtCore.pyqtSlot()
    def on_btnDestDir_clicked(self):
        config = self.generate_json_config_from_GUI_widgets(preview_mode=False)

        # Determine the destination directory based on use_samba
        if config.get("use_samba"):
            nas_server = config.get("nas_server", "").lstrip("/").rstrip("/")
            share_name = config.get("share_name", "").lstrip("/").rstrip("/")
            smb_dir = config.get("smb_dir", "").lstrip("/")

            if os.name == 'nt':  # Windows
                # Construct the network path for Windows
                smb_dir_windows = smb_dir.replace('/', '\\')
                destination_directory = f"\\\\{nas_server}\\{share_name}\\{smb_dir_windows}"

                try:
                    # Use the start command to open the network path correctly in Windows Explorer
                    subprocess.run(["cmd", "/c", "start", destination_directory], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to open the directory: {e}")

            elif os.name == 'posix':  # macOS or Linux
                # Construct the SMB path
                smb_path = f"smb://{nas_server}/{share_name}/{smb_dir}"

                try:
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(["open", smb_path], check=True)
                    else:  # Linux
                        # Attempt to use the default file manager to open the SMB path
                        if shutil.which("nautilus"):
                            subprocess.run(["nautilus", smb_path], check=True)
                        elif shutil.which("xdg-open"):
                            subprocess.run(["xdg-open", smb_path], check=True)
                        else:
                            print("No suitable file manager found.")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to open the directory: {e}")
        else:
            # Retrieve the local output directory from the configuration
            destination_directory = config.get("local_output_dir")

            # If the directory is not set, use the user's home directory as default
            if not destination_directory:
                destination_directory = os.path.expanduser("~")  # Default to the user's home directory

            # Ensure the directory exists (for local directories)
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)

            # Open the directory in the file explorer
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(destination_directory)
                elif os.name == 'posix':  # macOS or Linux
                    subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', destination_directory])
            except Exception as e:
                print(f"Failed to open the directory: {e}")






