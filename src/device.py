import paramiko
import os
import subprocess
import getpass
import threading
import sys
import select
import time
import signal

from PyQt5 import QtCore, QtGui

class Device:

    def __init__(self, name, uptodate=None, username="scientist"):
        self.name = name
        #self.id = id
        self.uptodate = uptodate
        self.username = username
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connected = False
        self.ssh_connect()

    def __del__(self):
        self.ssh.close()

    @property
    def is_running(self):
        stdin, stdout, stderr = self.ssh.exec_command("pgrep picam", get_pty=True)
        return stdout.readline() != ''

    @property
    def recording_status(self):
        """Check the status of the recording over SSH."""
        try:
            # Try to read the status file
            stdin, stdout, stderr = self.ssh.exec_command(f"cat /home/{self.username}/tmp/status.txt", get_pty=True)
            status = stdout.readline().strip()

            print(f"DEBUG : Device {self.name} status: {status}")

            if status == 'Recording':
                return 'Recording is ongoing'
            elif status == 'Paused':
                return 'Recording is paused'
            elif status == 'Not Running':
                return 'Recording is not running'
            else:
                return 'Unknown status'
        except FileNotFoundError:
            # If the file does not exist, handle the error gracefully
            return 'Status file not found, recording might not have started'

    @property
    def is_uptodate(self):
        stdin, stdout, stderr = self.ssh.exec_command(f"cd /home/{self.username}/piworm && git fetch --dry-run", get_pty=True)
        if stdout.readline() == '':
            print(self.name + " up to date")
            return True
        else:
            print("Update available for " + self.name)
            return False

    def update(self):
        if self.is_running:
            print("Device %s is running : update skipped" % self.name)
        else:
            stdin, stdout, stderr = self.ssh.exec_command(f"cd /home/{self.username}/piworm && git pull", get_pty=True)
            for line in iter(stdout.readline, ""):
                print(line, end="")
            print("Device %s updated" % self.name)

    def ssh_connect(self):
        self.connected = False
        i = 0
        while (not self.connected and i < 3):
            try:
                self.ssh.load_system_host_keys()
                self.ssh.connect(self.name, port=22, username=self.username, timeout=3)
                self.connected = True
            except paramiko.ssh_exception.SSHException as e:
                print(e)
                if os.name == 'nt':
                    subprocess.run([r'type', r'%userprofile%\.ssh\id_rsa.pub', '|', 'ssh', f'{self.username}@{self.name}', r"cat >> .ssh/authorized_keys"], shell=True)
                else:
                    os.system(f"ssh-copy-id {self.username}@{self.name}")
                i += 1
            except paramiko.ssh_exception.NoValidConnectionsError as e:
                print(e)
                print(f'Device {self.name} is unreachable.')
                i += 1
        return self.connected

    def receive_json_config_file(self, file):
        with self.ssh.open_sftp() as sftp:
            remote_folder = f"/home/{self.username}/.config/wormstation"
            remote_path = f'{remote_folder}/{os.path.basename(file)}'
            try:
                sftp.mkdir(remote_folder)
            except IOError:
                pass  # Folder already exists
            sftp.put(file, remote_path)
        return remote_path

    def get_frame(self, settings_remote_path):
        status = self.recording_status

        #print(f"DEBUG : Device {self.name} status: {status}")
        if self.is_running:
            if status == 'Recording is ongoing':
                # If the recording is ongoing, import the last frame
                return self.import_last_frame_from_device()
            elif status == 'Recording is paused':
                # If the recording is paused, send signal to get a new frame and then import it
                self.send_signal_to_server(signal.SIGUSR1)
                time.sleep(2)  # Wait a little for the server to capture the new frame
                return self.import_last_frame_from_device()
            elif status == 'Recording is not running':
                # If recording is not running, acquire a new frame
                return self.acquire_new_frame(settings_remote_path)
            else:
                print("Unknown recording status. Cannot get frame.")
                return None

        else:
            return self.acquire_new_frame(settings_remote_path)

    def send_signal_to_server(self, signal_type):
        """Send a signal to the server to trigger a new frame capture."""
        # Get the PID of the recording script on the server
        stdin, stdout, stderr = self.ssh.exec_command("pgrep -f picam", get_pty=True)
        pid = stdout.readline().strip()

        if pid:
            # Send the custom signal to the server process
            self.ssh.exec_command(f"kill -{signal_type} {pid}")
            print(f"Sent signal {signal_type} to server process {pid}.")
        else:
            print("Server recording script is not running.")

    def read_remote_frame(self, filename):
        with self.ssh.open_sftp() as sftp:
            frame_bytes = sftp.file(filename, mode='r').read()
            ba = QtCore.QByteArray(frame_bytes)
            new_pixmap = QtGui.QPixmap()
            new_pixmap.loadFromData(ba, "JPG")
        return new_pixmap

    def import_last_frame_from_device(self):
        try:
            print("Device is running : getting last frame")
            return self.read_remote_frame(f"/home/{self.username}/tmp/last_frame.jpg")
        except FileNotFoundError:
            print("No frame ready")
            return None

    def acquire_new_frame(self, config_file):
        self.start(config_file, background_mode=False)
        return self.read_remote_frame(f"/home/{self.username}/tmp/last_frame.jpg")

    def record(self, config_file):
        print(self.name)
        if self.is_running:
            print("WARNING : Device %s is already running. Recording ignored")
        else:
            self.start(config_file, background_mode=True)

    def start(self, config_file, background_mode=False):
        rec_command = f'picam {config_file}'
        command = f'nohup {rec_command}' if background_mode else rec_command
        print(command)
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                print(line, end="")
        except paramiko.ssh_exception.SSHException as e:
            print(e)
            print(f"Connection with device {self.name} lost")

    def stop(self):
        stdin, stdout, stderr = self.ssh.exec_command("pkill picam", get_pty=True)
        print("Device %s stopped" % self.name)

    def shutdown(self):
        print("shutting down %s" % self.name)
        stdin, stdout, stderr = self.ssh.exec_command("sudo poweroff", get_pty=True)
        del self

    def reboot(self):
        print("Rebooting %s" % self.name)
        stdin, stdout, stderr = self.ssh.exec_command("sudo reboot", get_pty=True)
        del self

    def turn_on_led(self, color, current='37.5mA'):
        """Turn on the LED of the specified color remotely."""
        self.ssh.exec_command(
            f"python ~/piworm/led_switch.py --color {color} --state 1 --current {current}",
            get_pty=True)

    def turn_off_led(self, color, current='37.5mA'):
        """Turn off the LED of the specified color remotely."""
        self.ssh.exec_command(
            f"python ~/piworm/led_switch.py --color {color} --state 0 --current {current}",
            get_pty=True)

    def turn_on_led_gpio(self, pin):
        """Old PCB. Turn on the LED of the specified color remotely."""
        self.ssh.exec_command(f"python ~/piworm/src/led_control/turn_on_led.py {pin}", get_pty=True)

    def turn_off_led_gpio(self, pin):
        self.ssh.exec_command(f"python ~/piworm/src/led_control/turn_off_led.py {pin}", get_pty=True)

    def switch_led(self, color, state, current):
        """Switch the specified LED on or off with the specified current."""
        # Execute the command and capture output
        stdin, stdout, stderr = self.ssh.exec_command(
            f"python ~/piworm/led_switch.py --color {color} --state {state} --current {current}",
            get_pty=True
        )

        # Read output and error streams
        error_message = stdout.read().decode()

        # Check if there was an error related to the missing file
        if "No such file or directory" in error_message:
            #print("Error detected. Falling back to GPIO control.")

            # Determine pin based on color
            pin = 17 if color == "IR" else 18

            # Use GPIO-based method depending on state
            if state == 1:
                self.turn_on_led_gpio(pin)
            else:
                self.turn_off_led_gpio(pin)

    def create_log_folder(self):
        log_folder = f"/home/{self.username}/log"
        with self.ssh.open_sftp() as sftp:
            try:
                sftp.mkdir(log_folder)
            except IOError:
                pass  # Folder already exists
        return log_folder

    def clear_tmp_folder(self):
        print(f'Clear folder /home/{self.username}/wormstation_recordings/ on {self.name}')
        self.ssh.exec_command(f"rm -rf /home/{self.username}/wormstation_recordings/*", get_pty=True)



