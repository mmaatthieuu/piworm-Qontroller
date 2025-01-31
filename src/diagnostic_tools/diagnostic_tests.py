import time
import random
import shutil
import socket
import os

from src.config_wizard import load_config
from src.device_manager import DeviceManager

def find_project_root(target_file='config.json'):
    current_dir = os.path.abspath(__file__)

    # Get only the file name from the path
    target_file = os.path.basename(target_file)

    while True:
        current_dir = os.path.dirname(current_dir)
        if target_file in os.listdir(current_dir):
            return os.path.join(current_dir, target_file)
        if current_dir == os.path.dirname(current_dir):
            raise FileNotFoundError(f"{target_file} not found.")


def load_config_file(logger, environment):
    """Load the configuration file."""

    config_file = find_project_root('config.json')

    logger(f"Loading configuration file from {config_file}...")

    config = load_config(config_file)

    if config:
        logger("Configuration loaded successfully.")
        environment.config = config
        return 1 # Return 1 for success
    else:
        logger("Failed to load configuration.")
        return 0 # Return 0 for failure

def connect_to_remote_devices(logger=None, environment=None):

    unreachable_devices = []

    if not environment.config:
        logger("No configuration loaded. Attempting to load configuration...")
        load_config_file(logger, environment)

    host_list_relative_path = environment.config["hosts_list_file"]
    logger(f"Connecting to remote devices using the host list file {host_list_relative_path}...")

    host_list_file = find_project_root(host_list_relative_path)
    logger(f"Host list file found at {host_list_file}.")

    environment.device_manager = DeviceManager()

    list_of_devices_to_connect = environment.device_manager.get_selected_devices(host_list_file)
    logger(f"Devices to connect:")
    for device in list_of_devices_to_connect:
        logger(f" - {device}")

    for device in list_of_devices_to_connect:
        logger(f"Connecting to {device}...")
        if environment.device_manager.is_device_reachable(device):
            environment.device_manager.add_device(device, username=environment.config["username"])
        else:
            unreachable_devices.append(device)
            logger(f"Failed to connect to {device}.")

    if environment.device_manager.is_empty():
        logger("Failed to connect to all devices.")
        return 0
    if unreachable_devices:
        logger(f"Failed to connect to {len(unreachable_devices)} devices.")
        return 2
    else:
        logger("Connected to all devices.")
        return 1


def check_clients_software_version(logger=None, environment=None):
    """Check if the clients' software is up to date."""
    logger("Checking clients' software version...")
    updatable_devices = environment.device_manager.check_updates()

    if not updatable_devices:
        logger("All clients are up to date.")
        return 1
    else:
        for device in updatable_devices:
            logger(f"Device {device.name} needs updating.")
        return 2


def random_bool_delay(logger=None, environment=None):
    """Simulate a random success/failure with a delay."""

    if logger:
        logger("Simulating a random test...")
    time.sleep(2)
    return random.choice([True, False])


def check_network(logger=None, environment=None):
    """Check if the internet connection is working."""
    time.sleep(1)
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def check_disk_space(logger=None, environment=None):
    """Check if there's enough disk space (at least 10%)."""
    time.sleep(1)
    total, used, free = shutil.disk_usage("/")
    percent_free = free / total * 100
    return percent_free > 10


def check_database(logger=None, environment=None):
    """Simulate checking database connection."""
    time.sleep(1)
    return random.choice([True, False])


def check_hardware(logger=None, environment=None):
    """Simulate hardware status check."""
    time.sleep(1)
    return random.choice([True, False])


def validate_configurations(logger=None, environment=None):
    """Simulate configuration validation."""
    time.sleep(1)
    return random.choice([True, False])
