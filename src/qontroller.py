# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/qontroller.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2303, 1142)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.scrollArea = QtWidgets.QScrollArea(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignCenter)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_6 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_6.setGeometry(QtCore.QRect(0, 0, 1975, 1072))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents_6.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents_6.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents_6.setObjectName("scrollAreaWidgetContents_6")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.labelDisplay = QtWidgets.QLabel(self.scrollAreaWidgetContents_6)
        self.labelDisplay.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.labelDisplay.setText("")
        self.labelDisplay.setPixmap(QtGui.QPixmap("blank.jpg"))
        self.labelDisplay.setScaledContents(False)
        self.labelDisplay.setObjectName("labelDisplay")
        self.gridLayout_2.addWidget(self.labelDisplay, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_6)
        self.frame = QtWidgets.QFrame(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(0, 0))
        self.frame.setMaximumSize(QtCore.QSize(300, 16777215))
        self.frame.setBaseSize(QtCore.QSize(300, 0))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.pushButton.setText("")
        icon = QtGui.QIcon.fromTheme("zoom-out")
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_6.addWidget(self.pushButton, 0, 1, 1, 1)
        self.btnLiveView = QtWidgets.QPushButton(self.frame)
        self.btnLiveView.setText("")
        icon = QtGui.QIcon.fromTheme("media-playback-start")
        self.btnLiveView.setIcon(icon)
        self.btnLiveView.setCheckable(True)
        self.btnLiveView.setObjectName("btnLiveView")
        self.gridLayout_6.addWidget(self.btnLiveView, 2, 1, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.pushButton_2.setText("")
        icon = QtGui.QIcon.fromTheme("zoom-in")
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_6.addWidget(self.pushButton_2, 0, 0, 1, 1)
        self.btnRefresh = QtWidgets.QPushButton(self.frame)
        self.btnRefresh.setText("")
        icon = QtGui.QIcon.fromTheme("view-refresh")
        self.btnRefresh.setIcon(icon)
        self.btnRefresh.setObjectName("btnRefresh")
        self.gridLayout_6.addWidget(self.btnRefresh, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_6.addItem(spacerItem, 1, 0, 1, 1)
        self.btnFitView = QtWidgets.QPushButton(self.frame)
        self.btnFitView.setText("")
        icon = QtGui.QIcon.fromTheme("gtk-zoom-fit")
        self.btnFitView.setIcon(icon)
        self.btnFitView.setCheckable(True)
        self.btnFitView.setObjectName("btnFitView")
        self.gridLayout_6.addWidget(self.btnFitView, 3, 0, 1, 1)
        self.btnOriginalView = QtWidgets.QPushButton(self.frame)
        self.btnOriginalView.setText("")
        icon = QtGui.QIcon.fromTheme("zoom-draw")
        self.btnOriginalView.setIcon(icon)
        self.btnOriginalView.setObjectName("btnOriginalView")
        self.gridLayout_6.addWidget(self.btnOriginalView, 3, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_6)
        self.sliderZoom = QtWidgets.QSlider(self.frame)
        self.sliderZoom.setMinimum(100)
        self.sliderZoom.setMaximum(500)
        self.sliderZoom.setSingleStep(1)
        self.sliderZoom.setOrientation(QtCore.Qt.Horizontal)
        self.sliderZoom.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.sliderZoom.setTickInterval(100)
        self.sliderZoom.setObjectName("sliderZoom")
        self.verticalLayout_2.addWidget(self.sliderZoom)
        spacerItem1 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)
        self.label = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.spinAveraging = QtWidgets.QSpinBox(self.frame)
        self.spinAveraging.setProperty("value", 4)
        self.spinAveraging.setObjectName("spinAveraging")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.spinAveraging)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.spinShutterSpeed = QtWidgets.QSpinBox(self.frame)
        self.spinShutterSpeed.setMaximum(1000000)
        self.spinShutterSpeed.setObjectName("spinShutterSpeed")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.spinShutterSpeed)
        spacerItem2 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.formLayout.setItem(7, QtWidgets.QFormLayout.FieldRole, spacerItem2)
        self.labelTimeout = QtWidgets.QLabel(self.frame)
        self.labelTimeout.setObjectName("labelTimeout")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.labelTimeout)
        self.spinTimeout = QtWidgets.QSpinBox(self.frame)
        self.spinTimeout.setMaximum(1000000)
        self.spinTimeout.setProperty("value", 300000)
        self.spinTimeout.setObjectName("spinTimeout")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.spinTimeout)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(13, QtWidgets.QFormLayout.FieldRole, spacerItem3)
        self.spinJpgQuality = QtWidgets.QSpinBox(self.frame)
        self.spinJpgQuality.setProperty("value", 90)
        self.spinJpgQuality.setObjectName("spinJpgQuality")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.spinJpgQuality)
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.spinBrightness = QtWidgets.QSpinBox(self.frame)
        self.spinBrightness.setProperty("value", 50)
        self.spinBrightness.setObjectName("spinBrightness")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.spinBrightness)
        self.label_7 = QtWidgets.QLabel(self.frame)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.label_8 = QtWidgets.QLabel(self.frame)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.spinTimeInterval = QtWidgets.QDoubleSpinBox(self.frame)
        self.spinTimeInterval.setSingleStep(0.5)
        self.spinTimeInterval.setProperty("value", 2.5)
        self.spinTimeInterval.setObjectName("spinTimeInterval")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.spinTimeInterval)
        self.spinArchiveSize = QtWidgets.QSpinBox(self.frame)
        self.spinArchiveSize.setMaximum(50000)
        self.spinArchiveSize.setProperty("value", 2000)
        self.spinArchiveSize.setObjectName("spinArchiveSize")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.FieldRole, self.spinArchiveSize)
        self.label_9 = QtWidgets.QLabel(self.frame)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.label_10 = QtWidgets.QLabel(self.frame)
        self.label_10.setObjectName("label_10")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.comboTimeoutUnit = QtWidgets.QComboBox(self.frame)
        self.comboTimeoutUnit.setObjectName("comboTimeoutUnit")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.comboTimeoutUnit)
        self.spinStartingFrame = QtWidgets.QSpinBox(self.frame)
        self.spinStartingFrame.setObjectName("spinStartingFrame")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole, self.spinStartingFrame)
        self.label_6 = QtWidgets.QLabel(self.frame)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.spinISO = QtWidgets.QSpinBox(self.frame)
        self.spinISO.setObjectName("spinISO")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.spinISO)
        self.label_11 = QtWidgets.QLabel(self.frame)
        self.label_11.setObjectName("label_11")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_11)
        spacerItem4 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.formLayout.setItem(1, QtWidgets.QFormLayout.LabelRole, spacerItem4)
        self.label_12 = QtWidgets.QLabel(self.frame)
        self.label_12.setObjectName("label_12")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_12)
        self.spinLEDIntensity = QtWidgets.QSpinBox(self.frame)
        self.spinLEDIntensity.setMaximum(4095)
        self.spinLEDIntensity.setProperty("value", 4095)
        self.spinLEDIntensity.setObjectName("spinLEDIntensity")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.spinLEDIntensity)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.gridLayout_10 = QtWidgets.QGridLayout()
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.btnStopRecord = QtWidgets.QPushButton(self.frame)
        self.btnStopRecord.setText("")
        icon = QtGui.QIcon.fromTheme("media-playback-stop")
        self.btnStopRecord.setIcon(icon)
        self.btnStopRecord.setObjectName("btnStopRecord")
        self.gridLayout_10.addWidget(self.btnStopRecord, 0, 1, 1, 1)
        self.btnRecord = QtWidgets.QPushButton(self.frame)
        self.btnRecord.setText("")
        icon = QtGui.QIcon.fromTheme("camera-on")
        self.btnRecord.setIcon(icon)
        self.btnRecord.setObjectName("btnRecord")
        self.gridLayout_10.addWidget(self.btnRecord, 0, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_10)
        spacerItem5 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem5)
        self.label_2 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.listBoxDevices = QtWidgets.QListWidget(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listBoxDevices.sizePolicy().hasHeightForWidth())
        self.listBoxDevices.setSizePolicy(sizePolicy)
        self.listBoxDevices.setObjectName("listBoxDevices")
        self.verticalLayout_2.addWidget(self.listBoxDevices)
        self.btnRescanDevices = QtWidgets.QPushButton(self.frame)
        self.btnRescanDevices.setObjectName("btnRescanDevices")
        self.verticalLayout_2.addWidget(self.btnRescanDevices)
        self.btnCheckUpdates = QtWidgets.QPushButton(self.frame)
        self.btnCheckUpdates.setObjectName("btnCheckUpdates")
        self.verticalLayout_2.addWidget(self.btnCheckUpdates)
        self.btnUpdateAll = QtWidgets.QPushButton(self.frame)
        self.btnUpdateAll.setObjectName("btnUpdateAll")
        self.verticalLayout_2.addWidget(self.btnUpdateAll)
        self.btnShutdown = QtWidgets.QPushButton(self.frame)
        self.btnShutdown.setObjectName("btnShutdown")
        self.verticalLayout_2.addWidget(self.btnShutdown)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 2303, 25))
        self.menubar.setObjectName("menubar")
        self.menutype_here = QtWidgets.QMenu(self.menubar)
        self.menutype_here.setObjectName("menutype_here")
        self.menumenu = QtWidgets.QMenu(self.menutype_here)
        self.menumenu.setObjectName("menumenu")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionin_menu = QtWidgets.QAction(MainWindow)
        self.actionin_menu.setObjectName("actionin_menu")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.menumenu.addAction(self.actionin_menu)
        self.menutype_here.addAction(self.menumenu.menuAction())
        self.menutype_here.addAction(self.actionOpen)
        self.menutype_here.addAction(self.actionSave)
        self.menubar.addAction(self.menutype_here.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Qontroller"))
        self.label.setText(_translate("MainWindow", "Parameters"))
        self.label_3.setText(_translate("MainWindow", "Averaging"))
        self.label_4.setText(_translate("MainWindow", "Shutter Speed (us)"))
        self.labelTimeout.setText(_translate("MainWindow", "Timeout"))
        self.label_5.setText(_translate("MainWindow", "JPEG Quality"))
        self.label_7.setText(_translate("MainWindow", "Brightness"))
        self.label_8.setText(_translate("MainWindow", "Time Interval (s)"))
        self.label_9.setText(_translate("MainWindow", "Archives Size"))
        self.label_10.setText(_translate("MainWindow", "Timeout Unit"))
        self.label_6.setText(_translate("MainWindow", "Starting Frame"))
        self.label_11.setText(_translate("MainWindow", "ISO"))
        self.label_12.setText(_translate("MainWindow", "LED Intensity"))
        self.label_2.setText(_translate("MainWindow", "Devices"))
        self.btnRescanDevices.setText(_translate("MainWindow", "Rescan Devices"))
        self.btnCheckUpdates.setText(_translate("MainWindow", "Check for updates"))
        self.btnUpdateAll.setText(_translate("MainWindow", "Update All"))
        self.btnShutdown.setText(_translate("MainWindow", "Shutdown All"))
        self.menutype_here.setTitle(_translate("MainWindow", "File"))
        self.menumenu.setTitle(_translate("MainWindow", "New recording"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionin_menu.setText(_translate("MainWindow", "in menu"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionSave.setText(_translate("MainWindow", "Save"))

