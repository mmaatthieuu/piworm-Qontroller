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

    if environment.device_manager.is_empty:
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

def check_NAS_connection(logger=None, environment=None):
    """Check if the NAS is reachable."""
    logger("Checking NAS connection...")

    if environment.device_manager is None:
        logger("No device manager found. Attempting to connect to remote devices...")
        connect_to_remote_devices(logger, environment)

    if not environment.device_manager.is_empty:
        NAS_status = (
            environment.device_manager.execute_on_multiple_devices(lambda device: device.get_NAS_status(environment.remote_config_file), environment.device_manager.host_list))
        if all(NAS_status):
            logger("All devices can reach the NAS.")
            return 1
        else:
            logger("At least one device cannot reach the NAS.")
            # find the devices that cannot reach the NAS
            unreachable_devices = [device for device, status in zip(environment.device_manager.host_list, NAS_status) if not status]
            for device in unreachable_devices:
                logger(f"Device {device.name} cannot reach the NAS.")
            return 0

def check_NAS_mount(logger=None, environment=None):
    """Check if the NAS is mounted on all devices."""
    logger("Checking NAS mount...")

    if environment.device_manager is None:
        logger("No device manager found. Attempting to connect to remote devices...")
        connect_to_remote_devices(logger, environment)

    if environment.device_manager.is_empty:
        logger("No devices found.")
        return 0  # Fail if no devices are found

    # Run NAS mount check on all devices (Expecting a boolean return)
    NAS_mount_status = environment.device_manager.execute_on_multiple_devices(
        lambda device: device.mount_NAS(environment.remote_config_file),
        environment.device_manager.host_list
    )

    # Process results
    failed_devices = []

    for device, is_mounted in zip(environment.device_manager.host_list, NAS_mount_status):
        if not isinstance(is_mounted, bool):  # Ensure valid boolean result
            logger(f"Device {device.name}: Invalid NAS mount response.")
            failed_devices.append(device.name)
            continue

        if is_mounted:
            logger(f"Device {device.name}: NAS is mounted (OK)")
        else:
            logger(f"Device {device.name}: NAS is not mounted (Critical)")
            failed_devices.append(device.name)

    # Final status return
    if failed_devices:
        logger("Some devices have the NAS not mounted.")
        return 0  # Fail if any device has the NAS not mounted

    logger("All devices have the NAS mounted.")
    return 1  # Success if all devices have the NAS mounted



def check_camera(logger=None, environment=None):
    """Check if the camera is connected."""
    logger("Checking camera connection...")

    if environment.device_manager is None:
        logger("No device manager found. Attempting to connect to remote devices...")
        connect_to_remote_devices(logger, environment)

    not_running_devices = get_non_running_devices(logger, environment)

    if not environment.device_manager.is_empty and not_running_devices:
        camera_status = (
            environment.device_manager.execute_on_multiple_devices(
                lambda device: device.check_camera(environment.remote_config_file),
                not_running_devices))
        # logger(camera_status)
        if all(camera_status):
            logger("All devices have a camera connected.")
            return 1
        else:
            logger("At least one device does not have a camera connected.")
            # find the devices that do not have a camera connected
            unreachable_devices = [device for device, status in zip(environment.device_manager.host_list, camera_status) if not status]
            for device in unreachable_devices:
                logger(f"Device {device.name} does not have a camera connected.")
            return 0
    else:
        logger("All devices are running. Skipping camera check.")
        return 2

def check_disk_space(logger=None, environment=None):
    """Check if there is enough disk space on all devices."""
    logger("Checking disk space on all devices...")

    if environment.device_manager is None:
        logger("No device manager found. Attempting to connect to remote devices...")
        connect_to_remote_devices(logger, environment)

    if environment.device_manager.is_empty:
        logger("No devices found.")
        return 0  # Fail if no devices are found

    # Run disk space check on all devices
    disk_space_status = environment.device_manager.execute_on_multiple_devices(
        lambda device: device.check_disk_space(environment.remote_config_file),
        environment.device_manager.host_list
    )

    # Process results
    all_devices_successful = True
    warning_devices = []
    failed_devices = []

    for device, disk_info in zip(environment.device_manager.host_list, disk_space_status):
        if not isinstance(disk_info, dict):  # Ensure valid disk info
            logger(f"Device {device.name}: Failed to retrieve disk space info.")
            failed_devices.append(device.name)
            all_devices_successful = False
            continue

        print(disk_info)

        free_space = disk_info["free"]

        if free_space > 10:  # Success: More than 10GB free
            logger(f"Device {device.name}: {free_space} GB free (OK)")
        elif 5 <= free_space <= 10:  # Warning: Between 5GB and 10GB
            logger(f"Device {device.name}: {free_space} GB free (Warning)")
            warning_devices.append(device.name)
            all_devices_successful = False
        else:  # Error: Less than 5GB free
            logger(f"Device {device.name}: {free_space} GB free (Critical)")
            failed_devices.append(device.name)
            all_devices_successful = False

    # Final status return
    if failed_devices:
        logger("Some devices have critically low disk space.")
        return 0  # Fail if any device has <5GB

    if warning_devices:
        logger("Some devices have low disk space but are still operational.")
        return 2  # Warning if any device has 5-10GB

    logger("All devices have sufficient disk space.")
    return 1  # Success if all devices have >10GB



def auto_LED_test(logger=None, environment=None):
    """Check the status of the LEDs on all devices."""
    logger("Checking the status of the LEDs...")

    if environment.device_manager is None:
        logger("No device manager found. Attempting to connect to remote devices...")
        connect_to_remote_devices(logger, environment)

    if environment.device_manager.is_empty:
        logger("No devices found.")
        return 0  # Fail if no devices are found

    not_running_devices = get_non_running_devices(logger, environment)

    if not_running_devices:
        # ✅ Run LED test on all devices
        led_results = environment.device_manager.execute_on_multiple_devices(
            lambda device: device.auto_LED_test(environment.remote_config_file),
            not_running_devices
        )

        # ✅ Process results
        all_leds_working = True  # Assume all LEDs work unless proven otherwise
        faulty_devices = []  # List of devices with faulty LEDs

        for result in led_results:
            if isinstance(result, dict) and "device" in result and "results" in result:
                device_name = result["device"]
                led_status = result["results"]  # Extract LED results dictionary

                logger(f"Device {device_name}: {led_status}")

                # ✅ If ANY LED is OFF, the test should fail
                if any(status != "ON" for status in led_status.values()):
                    all_leds_working = False
                    faulty_devices.append((device_name, led_status))
                    logger(f"Device {device_name} has faulty LEDs: {led_status}")

        # ✅ Return 0 if at least one LED is OFF
        if all_leds_working:
            logger("All LEDs are working correctly.")
            return 1
        else:
            logger("Some LEDs are not working.")
            for device, status in faulty_devices:
                logger(f"Device {device} has issues: {status}")
            return 0
    else:
        logger("All devices are running. Skipping LED test.")
        return 2


def get_tmp_files(logger=None, environment=None):
    """Get a list of temporary files on all devices and evaluate cleanup status."""
    logger("Checking for temporary files on all devices...")

    if environment.device_manager is None:
        logger("No device manager found. Attempting to connect to remote devices...")
        connect_to_remote_devices(logger, environment)

    if environment.device_manager.is_empty:
        logger("No devices found.")
        return 0  # Fail if no devices are found

    # Run temporary file check on all devices
    tmp_file_status = environment.device_manager.execute_on_multiple_devices(
        lambda device: device.get_tmp_files(environment.remote_config_file),
        environment.device_manager.host_list
    )

    # Process results
    all_devices_successful = True
    warning_devices = []
    failed_devices = []

    for device, files in zip(environment.device_manager.host_list, tmp_file_status):
        if not isinstance(files, list):  # Ensure valid file list
            logger(f"Device {device.name}: Failed to retrieve temporary file list.")
            failed_devices.append(device.name)
            all_devices_successful = False
            continue

        # **Classify files and folders based on extensions**
        file_count = sum(1 for f in files if os.path.splitext(f)[1])  # Has an extension → file
        folder_count = sum(1 for f in files if not os.path.splitext(f)[1])  # No extension → folder


        if folder_count <= 1 and file_count <= 1:
            logger(f"Device {device.name}: Temporary files/folders OK (Success)")
        elif file_count == 2:
            logger(f"Device {device.name}: Two temporary files found (Warning)")
            warning_devices.append(device.name)
            all_devices_successful = False
        elif folder_count >= 2 or file_count >= 3:
            logger(f"Device {device.name}: Too many temporary files/folders (Error)")
            failed_devices.append(device.name)
            all_devices_successful = False
        logger(f"Device {device.name}: {file_count} files, {folder_count} folders")
        logger(f"Device {device.name}: {files}")

    # Final status return
    if failed_devices:
        logger("Some devices have excessive temporary files.")
        return 0  # Fail if any device has too many files or folders

    if warning_devices:
        logger("Some devices have temporary files but are within limits.")
        return 2  # Warning if any device has exactly two files

    logger("All devices have a clean temporary file status.")
    return 1  # Success if all devices meet the condition





def random_bool_delay(logger=None, environment=None):
    """Simulate a random success/failure with a delay."""

    if logger:
        logger("Simulating a random test...")
    time.sleep(2)
    return random.choice([True, False])


def get_non_running_devices(logger=None, environment=None):
    """Get a list of devices that are not running."""
    if environment.device_manager is None:
        # logger("No device manager found. Attempting to connect to remote devices...")
        connect_to_remote_devices(logger, environment)

    if environment.device_manager.is_empty:
        logger("No devices found.")
        return []

    running_devices = environment.device_manager.running_devices()
    not_running_devices = [device for device in environment.device_manager.host_list if device not in running_devices]

    if not_running_devices:
        # logger(f"Found {len(not_running_devices)} devices that are not running.")
        for device in not_running_devices:
            logger(f" - {device.name}")
    else:
        logger("All devices are running.")

    return not_running_devices


