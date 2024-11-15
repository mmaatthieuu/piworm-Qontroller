#from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing.pool import ThreadPool

from itertools import compress
from PyQt5 import QtCore
import getpass
from .device import Device
import os
import subprocess
import sys
import select


class DeviceManager:
    def __init__(self, host_list=None):
        self.host_list = host_list if host_list is not None else []

    def execute_on_multiple_devices(self, func, device_list, *args, **kwargs):
        """Execute a function on all devices in parallel using map."""

        #Check if device_list is empty
        if not device_list:
            print("No devices selected.")
            return

        # Use ThreadPool to execute the function on all devices in parallel
        with ThreadPool(len(device_list)) as pool:
            # Prepare a list of partial functions with arguments for each device
            results = pool.map(lambda device: func(device, *args, **kwargs), device_list)

        return results  # Collect and return results if needed

    def add_device(self, name, username):
        """Add a new device to the list if it is connected."""
        new_device = Device(name, username=username)
        if new_device.connected:
            self.host_list.append(new_device)
            return new_device
        return None

    def get_device_by_id(self, device_id):
        """Get the device by its ID, or None if ID is invalid."""
        if 0 <= device_id < len(self.host_list):
            return self.host_list[device_id]
        return None

    def is_device_reachable(self, host):
        """Check if a device is reachable via ping."""
        try:
            if os.name == 'nt':
                subprocess.run(["ping", "-n", "1", "-w", "50", host], check=True)
            else:
                subprocess.run(["ping", "-c", "1", "-q", "-W", "0.05", host], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def add_reachable_device(self, host, username="default_user"):
        """Add a device if it is reachable."""
        if self.is_device_reachable(host):
            self.add_device(host, username=username)

    def scan_devices(self, filename="hosts_list.txt", username="default_user"):
        """Scan and add devices from the host list file in the order they appear."""
        self.host_list.clear()
        hosts = []

        # Load hosts from file, maintaining order
        with open(filename, 'r') as hosts_list:
            for host in hosts_list.read().splitlines():
                if host and host[0] != '#':  # Skip comments
                    hosts.append(host)

        # Perform reachability check in parallel and collect results
        reachability_results = self.execute_on_multiple_devices(self.is_device_reachable, hosts)

        # Add reachable devices in the correct order
        for host, is_reachable in zip(hosts, reachability_results):
            if is_reachable:
                self.add_device(host, username=username)

    def clear_tmp_folders(self, device_list=None):
        """Clear temporary folders on all selected devices in parallel."""
        # Use self.host_list as default if device_list is None (clear all devices)
        device_list = device_list or self.host_list

        print(f'Clearing tmp folders on {len(device_list)} devices')
        self.execute_on_multiple_devices(lambda device: device.clear_tmp_folder(), device_list)


    def check_updates(self, device_list=None):
        """Check if devices need updates and return the updatable ones."""
        device_list = device_list or self.host_list
        # Use execute_on_multiple_devices to check if each device is up to date
        updatable_status = self.execute_on_multiple_devices(lambda device: not device.is_uptodate, device_list)

        # Filter and return only devices that need updates
        return list(compress(device_list, updatable_status))

    def update_all_devices(self):
        """Update all updatable devices."""
        updatable_devices = self.check_updates()

        if not updatable_devices:
            print("No devices need updating.")
            return

        # Execute updates on all updatable devices in parallel
        self.execute_on_multiple_devices(lambda device: device.update(), updatable_devices)

    def reboot_devices(self):
        """Reboot all devices in parallel."""
        self.execute_on_multiple_devices(lambda device: device.reboot(), self.host_list)

    def shutdown_devices(self):
        """Shutdown all devices in parallel."""
        self.execute_on_multiple_devices(lambda device: device.shutdown(), self.host_list)

    def install_on_all_devices(self):
        """Run installation on all devices with sudo password."""
        sudo_password = getpass.getpass(prompt='Enter your sudo password: ')
        self.execute_on_multiple_devices(lambda device: DeviceInstaller(device, sudo_password).run_install_script(), self.host_list)

    def switch_led(self, color, state, current, device_list):
        """Switch the LED on or off on all or selected devices in parallel."""
        self.execute_on_multiple_devices(lambda device: device.switch_led(color=color, state=state, current=current), device_list)

    def running_devices(self):
        """Return a list of devices that are currently running."""
        return [d for d in self.host_list if d.is_running]

    def stop_devices(self, device_list):
        """Stop the specified devices."""
        for device in device_list:
            device.stop()

    def record_devices(self, device_list, config_file):
        """Start recording on the specified devices with the given config file."""
        for device in device_list:
            remote_path = device.receive_json_config_file(config_file)
            device.record(remote_path)



class DeviceInstaller:
    def __init__(self, device, sudo_password):
        self.name = device.name
        self.username = device.username
        self.ssh = device.ssh
        self.sudo_password = sudo_password

    def run_install_script(self):
        print(f'\n\n\nRUNNING INSTALL SCRIPT ON {self.name}\n')
        stdin, stdout, stderr = self.ssh.exec_command(f"bash /home/{self.username}/piworm/INSTALL.sh -y", get_pty=True)

        # Function to send the password when sudo prompts for it
        def handle_password(stdin, stdout):
            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                    if rl:
                        line = stdout.channel.recv(1024).decode('utf-8')
                        sys.stdout.write(line)
                        if 'password' in line.lower():
                            stdin.write(f"{self.sudo_password}\n")
                            stdin.flush()

        # Process output from the command and handle password prompt sequentially
        handle_password(stdin, stdout)

        # Ensure all output is read
        stdout.channel.recv_exit_status()

        # Read any remaining output
        for line in iter(stdout.readline, ""):
            print(line, end="")

        print(f"Finished install script on {self.name}")