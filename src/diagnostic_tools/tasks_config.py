import os
import json

from src.diagnostic_tools.task import Task
from src.diagnostic_tools.diagnostic_tests import *


"""
Tasks to implement
 - check local ssk key (for ssh-copy_id)
 - check if ssh-copy-id is installed
 - check if credentials are correct
 - check if all install steps are successful
 - check if led board is connected
 - check if nas is available
 - check if nas is mounted
 - check that camera is connected
 - check that leds are working


"""

# Automatically map task names to their corresponding functions
TASK_FUNCTIONS = {
    "LoadConfiguration": load_config_file,
    "ConnectToRemoteDevices": connect_to_remote_devices,
    "CheckClientsSoftwareVersion": check_clients_software_version,
    "CheckNasConnection": check_NAS_connection,
    "CheckNasMount": check_NAS_mount,
    "CheckDiskSpace": check_disk_space,
    "CheckCamera": check_camera,
    "AutoLedCheck": auto_LED_test,
    "GetTmpFiles": get_tmp_files
}


def load_task_messages():
    """Load task messages from JSON."""
    path = os.path.join(os.path.dirname(__file__), "task_messages.json")
    with open(path, 'r') as file:
        return json.load(file)

def load_diagnostic_tasks():
    """Dynamically create tasks based on the message file."""
    messages = load_task_messages()
    tasks = []

    for task_name, message_data in messages.items():
        function = TASK_FUNCTIONS.get(task_name)

        if not function:
            print(f"⚠️ Warning: No function found for task '{task_name}'")
            continue  # Skip if no function is mapped

        # Automatically handle optional fields like 'warning'
        warning_message = message_data.get("warning")

        # Dynamically create the Task instance
        task = Task(
            name=task_name.replace("_", " "),
            description=message_data["description"],
            success_message=message_data["success"],
            failure_message=message_data["failure"],
            function=function,
            warning_message=warning_message
        )
        tasks.append(task)

    return tasks