from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QTextEdit, QApplication, QStyle, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import os

from src.diagnostic_tools.diagnostic_manager import DiagnosticManager
from src.diagnostic_tools.task import Task


class DiagnosticWorker(QThread):
    update_status = pyqtSignal(int, str)
    log_message = pyqtSignal(str)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager  # ✅ Work with DiagnosticManager

    def run(self):
        self.manager.run()

class SelfCheckWindow(QDialog):
    def __init__(self, remote_config_file=None):
        super().__init__()
        self.setWindowTitle("System Self-Diagnosis")
        self.resize(600, 600)
        self.setModal(True)
        self.remote_config_file = remote_config_file

        self.manager = DiagnosticManager(remote_config_file)  # ✅ Initialize with logger
        self.manager.log_signal.connect(self.append_log)  # ✅ Connect signal
        self.manager.status_update_signal.connect(self.update_task_status)



        self.init_icons()  # ✅ Initialize icons with fallbacks
        self.init_ui()
        self.start_diagnostics()

    def init_icons(self):
        """Initialize status icons with cross-platform fallbacks."""
        self.icon_waiting = QIcon.fromTheme(
            "view-refresh", QApplication.style().standardIcon(QStyle.SP_BrowserReload)
        )  # 🔄 Waiting icon

        self.icon_running = QIcon.fromTheme(
            "system-run", QApplication.style().standardIcon(QStyle.SP_MediaPlay)
        )  # ▶️ Running icon

        self.icon_success = QIcon.fromTheme(
            "dialog-ok-apply", QApplication.style().standardIcon(QStyle.SP_DialogApplyButton)
        )  # ✅ Success icon

        self.icon_failure = QIcon.fromTheme(
            "dialog-error", QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical)
        )  # ❌ Failure icon

        self.icon_warning = QIcon.fromTheme(
            "dialog-warning-symbolic", QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning)
        )  # ⚠️ Warning icon

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        self.task_items = []
        for task in self.manager.get_tasks():
            item = QListWidgetItem(self.icon_waiting, task.get_display_text())
            self.task_list.addItem(item)
            self.task_items.append(item)

        # 🔘 Show Details Button
        self.toggle_button = QPushButton("Show Details")
        self.toggle_button.clicked.connect(self.toggle_log)
        layout.addWidget(self.toggle_button)

        # 💾 Save Log Button
        self.save_log_button = QPushButton("Save Log")
        self.save_log_button.clicked.connect(self.save_log_to_file)
        layout.addWidget(self.save_log_button)

        # 📝 Log Area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setVisible(False)
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    def start_diagnostics(self):
        self.worker = DiagnosticWorker(self.manager)
        self.worker.update_status.connect(self.update_task_status)
        self.worker.log_message.connect(self.append_log)
        self.worker.finished.connect(self.cleanup_worker)
        self.worker.start()

    def update_task_status(self, index, status):
        task = self.manager.get_tasks()[index]
        task.status = status

        # ✅ Update icon and text based on status
        if status == Task.STATUS_WAITING:
            icon = self.icon_waiting
        elif status == Task.STATUS_RUNNING:
            icon = self.icon_running
        elif status == Task.STATUS_SUCCESS:
            icon = self.icon_success
        elif status == Task.STATUS_FAILURE:
            icon = self.icon_failure
        elif status == Task.STATUS_WARNING:
            icon = self.icon_warning
        else:
            icon = self.icon_waiting  # Fallback

        self.task_items[index].setIcon(icon)
        self.task_items[index].setText(task.get_display_text())

    def append_log(self, message):
        self.log_area.append(message)

    def toggle_log(self):
        is_visible = self.log_area.isVisible()
        self.log_area.setVisible(not is_visible)
        self.toggle_button.setText("Hide Details" if is_visible else "Show Details")

    def save_log_to_file(self):
        """Open a dialog to save the log content to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log File",
            "diagnostic_log.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.log_area.toPlainText())
                QMessageBox.information(self, "Success", "Log saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save log: {e}")

    def closeEvent(self, event):

        # if self.remote_config_file exists delete it the file
        if self.remote_config_file:
            try:
                print(f"Deleting config file: {self.remote_config_file}")
                os.remove(self.remote_config_file)
            except Exception as e:
                print(f"Failed to delete remote config file: {e}")


        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        event.accept()

    def cleanup_worker(self):
        self.worker = None


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SelfCheckWindow()
    window.exec_()
    sys.exit(app.exec_())
