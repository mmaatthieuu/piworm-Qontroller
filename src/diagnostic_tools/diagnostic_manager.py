import time

from PyQt5.QtCore import QObject, pyqtSignal

from src.diagnostic_tools.tasks_config import load_diagnostic_tasks
from src.diagnostic_tools.task import Task


class DiagnosticEnvironment:
    """Represents a diagnostic environment with a list of tasks."""

    def __init__(self):
        self.device_manager = None



class DiagnosticManager(QObject):
    """Handles task management and diagnostics execution."""

    log_signal = pyqtSignal(str)  # ✅ Signal for thread-safe logging
    status_update_signal = pyqtSignal(int, str)  # ✅ Signal for task status updates


    def __init__(self):
        super().__init__()
        self.tasks = load_diagnostic_tasks()  # ✅ Load tasks internally
        self.logs = []
        self.environment = DiagnosticEnvironment()  # ✅ Initialize environment

    def get_tasks(self):
        """Return the list of tasks."""
        return self.tasks

    def log(self, message):
        """Log messages with a timestamp."""
        timestamped_message = f"[{time.strftime('%H:%M:%S')}] {message}"
        self.logs.append(timestamped_message)
        self.log_signal.emit(timestamped_message)  # ✅ Emit signal
        print(timestamped_message)

    def update_task_status(self, index, status):
        """Update the status of a specific task."""
        self.tasks[index].status = status
        self.status_update_signal.emit(index, status)  # ✅ Emit update


    def run(self):
        """Run all tasks."""
        for i, _ in enumerate(self.tasks):
            self.run_task(i)

    def run_task(self, index):
        """Run a specific task and handle its status."""
        task = self.tasks[index]
        self.update_task_status(index, Task.STATUS_RUNNING)
        self.log(f"Starting task: {task.name}")

        success = task.run(logger=self.log, environment=self.environment)  # ✅ Pass context

        if success:
            self.update_task_status(index, Task.STATUS_SUCCESS)
            self.log(f"Task succeeded: {task.name}")
        else:
            self.update_task_status(index, Task.STATUS_FAILURE)
            self.log(f"Task failed: {task.name}")