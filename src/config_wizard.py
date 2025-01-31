from PyQt5.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QRadioButton, QLineEdit, QWidget
from PyQt5.QtWidgets import QMessageBox, QLabel, QGroupBox, QFormLayout, QCheckBox, QStackedWidget
import json
import os
import subprocess
import platform

CONFIG_FILE = 'config.json'

class ConfigWizard(QWizard):
    InitialConfigPageId = 0
    FirstConfigPageId = 1

    def __init__(self, parent=None):
        super(ConfigWizard, self).__init__(parent)

        # Check if configuration file exists
        configExists = load_config() is not None

        # Add the initial configuration page
        self.addPage(InitialConfigPage(configExists))

        self.addPage(SshKeyConfigPage())

        self.addPage(HostConfigPage())

        # Add subsequent configuration pages
        self.addPage(RemoteSaveConfigPage())

        self.setWindowTitle("Configuration Wizard")

    def reject(self):
        """Override the Cancel button behavior to confirm exit."""
        reply = QMessageBox.warning(
            self,
            "Exit Configuration",
            "⚠️ Configuration is required to run the software.\n\nAre you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            super(ConfigWizard, self).reject()  # Exit the wizard
        else:
            pass  # Stay in the wizard

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
            self.textLabel.setText("No existing configuration found. Please proceed with the configuration.")
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
        return ConfigWizard.FirstConfigPageId


class SshKeyConfigPage(QWizardPage):
    def __init__(self, parent=None):
        super(SshKeyConfigPage, self).__init__(parent)
        self.setTitle("SSH Key Configuration")
        self.layout = QVBoxLayout(self)

        # ✅ Instructional Text
        instruction_label = QLabel(
            "Please review the default SSH key path below. "
            "You may proceed by clicking 'Next' or modify the path if needed."
        )
        instruction_label.setStyleSheet("color: grey; font-style: italic;")
        instruction_label.setWordWrap(True)
        self.layout.addWidget(instruction_label)

        info_label = QLabel(
            "The SSH key path is the location of your private key file.\n"
            "If the key is not found, a new key will be generated automatically.\n\n"
            "Keep default path unless you know what you're doing."
        )
        info_label.setWordWrap(True)
        self.layout.addWidget(info_label)

        # ✅ SSH Key Input
        self.sshKeyInput = QLineEdit()
        self.layout.addWidget(QLabel("SSH Key Path:"))
        self.layout.addWidget(self.sshKeyInput)

        # ✅ Set OS-specific default SSH key path
        self.sshKeyInput.setText(self.get_default_ssh_path())

        self.setLayout(self.layout)

    def get_default_ssh_path(self):
        """Set default SSH key path based on the operating system."""
        system_platform = platform.system()
        if system_platform == "Windows":
            return os.path.join(os.environ["USERPROFILE"], ".ssh", "id_rsa")
        else:  # Linux and macOS
            return os.path.expanduser("~/.ssh/id_rsa")

    def collect_data(self):
        """Collect data from the UI and generate the SSH key if missing."""
        ssh_key_path = os.path.expanduser(self.sshKeyInput.text().strip())

        # Check if the SSH key path is empty or invalid
        if not ssh_key_path:
            QMessageBox.critical(self, "Error", "Please enter a valid SSH key path.")
            return None

        # ✅ Check if the SSH key exists; generate it if missing
        if not os.path.exists(ssh_key_path):
            self.generate_ssh_key(ssh_key_path)

        return {
            "ssh_key_path": ssh_key_path,
        }

    def generate_ssh_key(self, ssh_key_path):
        """Generate a new SSH key, compatible with Linux, macOS, and Windows."""
        ssh_dir = os.path.dirname(ssh_key_path)

        # ✅ Create .ssh directory if it doesn't exist
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, mode=0o700)

        system_platform = platform.system()

        # ✅ Linux/macOS
        if system_platform in ["Linux", "Darwin"]:
            command = ["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-f", ssh_key_path]

        # ✅ Windows
        elif system_platform == "Windows":
            # Check if ssh-keygen is available
            if self.is_openssh_installed():
                command = ["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-f", ssh_key_path]
            else:
                QMessageBox.critical(
                    self,
                    "OpenSSH Not Found",
                    "OpenSSH is not installed on your system.\n\n"
                    "Please install OpenSSH from 'Apps & Features' or manually generate an SSH key."
                )
                return
        else:
            QMessageBox.critical(self, "Unsupported OS", f"Unsupported OS: {system_platform}")
            return

        # ✅ Run the command to generate the SSH key
        try:
            subprocess.run(command, check=True)
            QMessageBox.information(self, "SSH Key Generated", f"SSH key generated at {ssh_key_path}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to generate SSH key:\n{e}")

    def is_openssh_installed(self):
        """Check if OpenSSH is available on Windows."""
        try:
            subprocess.run(["ssh-keygen", "-V"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


class HostConfigPage(QWizardPage):
    def __init__(self, parent=None):
        super(HostConfigPage, self).__init__(parent)
        self.setTitle("Host Configuration")
        self.layout = QVBoxLayout(self)

        # ✅  Instructional Text
        instruction_label = QLabel(
            "Please review the default values below. "
            "You may proceed by clicking 'Next' or modify the fields as needed."
        )
        instruction_label.setStyleSheet("color: grey; font-style: italic;")
        instruction_label.setWordWrap(True)
        self.layout.addWidget(instruction_label)

        # Hostname Input
        self.hostInput = QLineEdit()
        self.layout.addWidget(QLabel("Hosts list path:"))
        self.layout.addWidget(self.hostInput)
        self.hostInput.setText("./hosts_list.txt")

        # Username Input
        self.usernameInput = QLineEdit()
        self.layout.addWidget(QLabel("Remote username:"))
        self.layout.addWidget(self.usernameInput)
        self.usernameInput.setText("scientist")

        self.setLayout(self.layout)

    def collect_data(self):
        # Collect data from UI components
        data = {
            "hosts_list_file": self.hostInput.text() or "./hosts_list.txt",  # ✅ Fallback to placeholder
            "username": self.usernameInput.text() or "scientist"  # ✅ Fallback to placeholder
        }
        return data


class RemoteSaveConfigPage(QWizardPage):
    def __init__(self, parent=None):
        super(RemoteSaveConfigPage, self).__init__(parent)
        self.setTitle("Configuration Settings")
        self.layout = QVBoxLayout(self)

        # ✅  Instructional Text
        instruction_label = QLabel(
            "Please review the default values below. "
            "You may proceed by clicking 'Next' or modify the fields as needed."
        )
        instruction_label.setStyleSheet("color: grey; font-style: italic;")
        instruction_label.setWordWrap(True)
        self.layout.addWidget(instruction_label)

        # Save Location Options
        self.localSaveOption = QRadioButton("Save Locally (Coming Soon)")
        self.serverSaveOption = QRadioButton("Save on Server (NAS)")

        self.serverSaveOption.setChecked(True)  # ✅ Set Server Save as default
        self.localSaveOption.setEnabled(False)  # ✅ Disable Local Save option

        # Group for exclusive options
        self.saveOptionGroup = QGroupBox("Select Save Option")
        self.optionLayout = QVBoxLayout()
        self.optionLayout.addWidget(self.serverSaveOption)
        self.optionLayout.addWidget(self.localSaveOption)  # ✅ Keep for future use
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
        self.serverSaveOption.toggled.connect(self.onSaveOptionChanged)

        self.setLayout(self.layout)

        # ✅ Ensure the server widget is shown by default
        self.stackedWidget.setCurrentWidget(self.serverSaveWidget)

    def setupLocalSaveWidget(self):
        layout = QVBoxLayout()
        self.localHostInput = QLineEdit()
        self.localDestinationFolderInput = QLineEdit()
        layout.addWidget(QLabel("Local Host IP:"))
        layout.addWidget(self.localHostInput)
        layout.addWidget(QLabel("Local Destination Folder:"))
        layout.addWidget(self.localDestinationFolderInput)
        self.localSaveWidget.setLayout(layout)
        self.stackedWidget.addWidget(self.localSaveWidget)

    def setupServerSaveWidget(self):
        layout = QFormLayout()
        self.serverServiceInput = QLineEdit()
        self.workgroupInput = QLineEdit()
        self.credentialsFileInput = QLineEdit()
        self.sambaDirectoryInput = QLineEdit()
        layout.addRow("Samba Service:", self.serverServiceInput)
        layout.addRow("Workgroup:", self.workgroupInput)
        layout.addRow("Credentials File:", self.credentialsFileInput)
        layout.addRow("Samba Directory:", self.sambaDirectoryInput)
        self.serverSaveWidget.setLayout(layout)
        self.stackedWidget.addWidget(self.serverSaveWidget)

        # ✅ Set default values
        self.serverServiceInput.setText("//lpbsnas1.epfl.ch/LPBS2")
        self.workgroupInput.setText("")
        self.credentialsFileInput.setText("/etc/.smbpicreds")
        self.sambaDirectoryInput.setText("Misc/Matthieu-Schmidt/WORMSTATION_RECORDINGS/")

    def onSaveOptionChanged(self, checked):
        if self.serverSaveOption.isChecked():
            self.stackedWidget.setCurrentWidget(self.serverSaveWidget)
        else:
            self.stackedWidget.setCurrentWidget(self.localSaveWidget)

    def collect_data(self):
        # Collect data from UI components
        data = {
            "save_option": "server" if self.serverSaveOption.isChecked() else "local",
            "local_host_ip": self.localHostInput.text(),
            "local_destination_folder": self.localDestinationFolderInput.text(),
            "samba_service": self.serverServiceInput.text(),
            "workgroup": self.workgroupInput.text(),
            "samba_credential_file": self.credentialsFileInput.text(),
            "samba_directory": self.sambaDirectoryInput.text()
        }
        return data



def save_config(config, filename=CONFIG_FILE):
    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)

def load_config(filename=CONFIG_FILE):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

