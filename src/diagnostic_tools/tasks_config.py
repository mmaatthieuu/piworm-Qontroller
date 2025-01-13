from src.diagnostic_tools.task import Task
from src.diagnostic_tools.diagnostic_tests import *


def load_diagnostic_tasks():
    """Creates a list of diagnostic tasks."""

    return [
        Task("Fake Task",
             "This task does nothing.",
             "Task completed successfully.",
             "Task failed.",
             function=random_bool_delay),
        Task("Check Network",
             "Checking network connection...",
             "Network is accessible.",
             "Failed to access network.",
             function=check_network),

        Task("Verify Disk Space",
             "Verifying disk space...",
             "Disk space is sufficient.",
             "Disk space is low.",
             function=check_disk_space),

        Task("Test Database",
             "Testing database connection...",
             "Database is reachable.",
             "Failed to connect to the database.",
             function=check_database),

        Task("Check Hardware",
             "Checking hardware status...",
             "Hardware is functioning.",
             "Hardware issue detected.",
             function=check_hardware),

        Task("Validate Configurations",
             "Validating configurations...",
             "Configurations are valid.",
             "Invalid configurations found.",
             function=validate_configurations)
    ]
