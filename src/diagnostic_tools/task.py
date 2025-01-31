

class Task:
    """Represents a diagnostic task with a test function and status."""

    STATUS_WAITING = "waiting"
    STATUS_RUNNING = "running"
    STATUS_SUCCESS = "success"
    STATUS_FAILURE = "failure"
    STATUS_WARNING = "warning"

    def __init__(self, name, description, success_message, failure_message, function, warning_message=None):
        self.name = name
        self.description = description
        self.success_message = success_message
        self.failure_message = failure_message
        self.warning_message = warning_message
        self.status = self.STATUS_WAITING
        self.function = function

    def run(self, logger=None, environment=None):
        """
        Runs the task function with logger and environment.
        """
        try:
            return self.function(logger=logger, environment=environment)
        except Exception as e:
            if logger:
                logger(f"❌ Error in task '{self.name}': {e}")
            else:
                print(f"Error in task '{self.name}': {e}")
            return False

    def get_display_text(self):
        """Get the task status message."""
        if self.status == self.STATUS_WAITING:
            return self.name
        elif self.status == self.STATUS_RUNNING:
            return self.description
        elif self.status == self.STATUS_SUCCESS:
            return self.success_message
        elif self.status == self.STATUS_FAILURE:
            return self.failure_message
        elif self.status == self.STATUS_WARNING:
            if hasattr(self, "warning_message"):
                return self.warning_message
            else:
                return self.success_message