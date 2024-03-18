from PyQt5.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QRadioButton, QLineEdit, QLabel, QGroupBox, QFormLayout, QCheckBox
from PyQt5.QtWidgets import (QWizardPage, QVBoxLayout, QRadioButton, QLineEdit, QLabel, QGroupBox, QStackedWidget, QWidget, QFormLayout)
import json


class ConfigWizard(QWizard):
    InitialConfigPageId = 0
    YourFirstConfigPageId = 1

    def __init__(self, parent=None):
        super(ConfigWizard, self).__init__(parent)

        # Check if configuration file exists
        configExists = load_config() is not None

        # Add the initial configuration page
        self.addPage(InitialConfigPage(configExists))

        # Add subsequent configuration pages
        self.addPage(YourFirstConfigPage())

        self.setWindowTitle("Configuration Wizard")

    def collectData(self):
        # Initialize an empty dictionary to hold all collected data
        allData = {}

        # Iterate through all pages
        for pageId in self.pageIds():
            page = self.page(pageId)
            if hasattr(page, 'collect_data'):
                # Collect data from pages that have a 'collect_data' method
                pageData = page.collect_data()
                allData.update(pageData)

        return allData



class InitialConfigPage(QWizardPage):
    def __init__(self, configExists, parent=None):
        super(InitialConfigPage, self).__init__(parent)
        self.setTitle("Initial Configuration")

        self.layout = QVBoxLayout(self)
        self.configExists = configExists

        # Always initialize these checkboxes but will decide later to show or hide them
        self.textLabel = QLabel()
        self.useExistingCheckBox = QCheckBox("Use existing configuration")
        self.dontAskAgainCheckBox = QCheckBox("Don't ask me again")
        self.layout.addWidget(self.textLabel)
        self.layout.addWidget(self.useExistingCheckBox)
        self.layout.addWidget(self.dontAskAgainCheckBox)

        if self.configExists:
            self.textLabel.setText("An existing configuration was found. Would you like to use it?")
        else:
            self.textLabel.setText("No existing configuration found. Would you like to create a new configuration?")
            # Hide checkboxes since there's no existing configuration
            self.useExistingCheckBox.hide()
            self.dontAskAgainCheckBox.hide()

        self.setLayout(self.layout)

    def isComplete(self):
        # If there's no configuration or if the user opts to not use the existing one, always complete
        if not self.configExists or self.useExistingCheckBox.isChecked() or self.dontAskAgainCheckBox.isChecked():
            return True
        return False

    def nextId(self):
        if self.configExists and (self.useExistingCheckBox.isChecked() or self.dontAskAgainCheckBox.isChecked()):
            # Logic to save preferences based on the checkbox states
            preferences = {'use_existing_config': self.useExistingCheckBox.isChecked(),
                           'skip_config_wizard': self.dontAskAgainCheckBox.isChecked()}
            save_config(preferences)
            return -1  # This will end the wizard
        return ConfigWizard.YourFirstConfigPageId



class YourFirstConfigPage(QWizardPage):
    def __init__(self, parent=None):
        super(YourFirstConfigPage, self).__init__(parent)
        self.setTitle("Configuration Settings")
        self.layout = QVBoxLayout(self)

        # Save Location Options
        self.localSaveOption = QRadioButton("Save Locally")
        self.serverSaveOption = QRadioButton("Save on Server (NAS)")
        self.localSaveOption.setChecked(True)  # Default selection

        # Group for exclusive options
        self.saveOptionGroup = QGroupBox("Select Save Option")
        self.optionLayout = QVBoxLayout()
        self.optionLayout.addWidget(self.localSaveOption)
        self.optionLayout.addWidget(self.serverSaveOption)
        self.saveOptionGroup.setLayout(self.optionLayout)

        # Stacked Widget
        self.stackedWidget = QStackedWidget()
        self.localSaveWidget = QWidget()
        self.serverSaveWidget = QWidget()

        # Setup widgets
        self.setupLocalSaveWidget()
        self.setupServerSaveWidget()

        # Adding widgets to layout
        self.layout.addWidget(self.saveOptionGroup)
        self.layout.addWidget(self.stackedWidget)

        # Signal Connections
        self.localSaveOption.toggled.connect(self.onSaveOptionChanged)

        self.setLayout(self.layout)

    def setupLocalSaveWidget(self):
        layout = QVBoxLayout()
        self.localHostInput = QLineEdit()  # Assign to an attribute
        self.localDestinationFolderInput = QLineEdit()  # Assign to an attribute
        layout.addWidget(QLabel("Local Host IP:"))
        layout.addWidget(self.localHostInput)
        layout.addWidget(QLabel("Local Destination Folder:"))
        layout.addWidget(self.localDestinationFolderInput)
        self.localSaveWidget.setLayout(layout)
        self.stackedWidget.addWidget(self.localSaveWidget)

    def setupServerSaveWidget(self):
        layout = QFormLayout()
        self.serverServiceInput = QLineEdit()  # Assign to an attribute
        self.workgroupInput = QLineEdit()  # Assign to an attribute
        self.credentialsFileInput = QLineEdit()  # Assign to an attribute
        self.sambaDirectoryInput = QLineEdit()  # Assign to an attribute
        layout.addRow("Samba Service:", self.serverServiceInput)
        layout.addRow("Workgroup:", self.workgroupInput)
        layout.addRow("Credentials File:", self.credentialsFileInput)
        layout.addRow("Samba Directory:", self.sambaDirectoryInput)
        self.serverSaveWidget.setLayout(layout)
        self.stackedWidget.addWidget(self.serverSaveWidget)

    def onSaveOptionChanged(self, checked):
        if self.localSaveOption.isChecked():
            self.stackedWidget.setCurrentWidget(self.localSaveWidget)
        else:
            self.stackedWidget.setCurrentWidget(self.serverSaveWidget)

    def collect_data(self):
        # Collect data from UI components
        data = {
            "save_option": "local" if self.localSaveOption.isChecked() else "server",
            "local_host_ip": self.localHostInput.text(),
            "local_destination_folder": self.localDestinationFolderInput.text(),
            "samba_service": self.serverServiceInput.text(),
            "workgroup": self.workgroupInput.text(),
            "samba_credential_file": self.credentialsFileInput.text(),
            "samba_directory": self.sambaDirectoryInput.text()
        }
        return data



def save_config(config, filename='config.json'):
    with open(filename, 'w') as f:
        json.dump(config, f)

def load_config(filename='config.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

