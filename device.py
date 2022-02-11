from PyQt5 import QtGui, QtCore
import paramiko
import os
import time
from datetime import datetime

from math import log10,ceil

from picam_settings import PicamSettings

class Device:

    def __init__(self, name, id, uptodate=None):
        self.name = name
        self.id = id
        self.uptodate = uptodate

        self.ssh = paramiko.SSHClient()

        self.ssh_connect()



    def __del__(self):
        self.ssh.close()

    @property
    def is_running(self):
        stdin, stdout, stderr = self.ssh.exec_command("pgrep picam", get_pty=True)
        if stdout.readline() == '':
            return False
        else:
            return True

    @property
    def is_uptodate(self):
        stdin, stdout, stderr = self.ssh.exec_command("cd /home/matthieu/piworm && git fetch --dry-run", get_pty=True)
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
            stdin, stdout, stderr = self.ssh.exec_command("cd /home/matthieu/piworm && git pull", get_pty=True)
            for line in iter(stdout.readline, ""):
                print(line, end="")
            print("Device %s updated" % self.name)

    def ssh_connect(self):
        connected = False
        i = 0
        while (not connected and i < 3):
            try:
                self.ssh.load_system_host_keys()
                self.ssh.connect(self.name, port=22, username='matthieu', timeout=3)
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                connected = True
            except paramiko.ssh_exception.SSHException as e:
                print(e)
                os.system("ssh-copy-id %s" % self.name)
                i += 1



    def get_frame(self,settings):
        if self.is_running:
            return self.import_last_frame_from_device()
        else:
            return self.acquire_new_frame(settings)

    def read_remote_frame(self, filename):
        sftp = self.ssh.open_sftp()
        frame_bytes = sftp.file(filename, mode='r').read()

        ba = QtCore.QByteArray(frame_bytes)
        new_pixmap = QtGui.QPixmap()
        ok = new_pixmap.loadFromData(ba, "JPG")

        return new_pixmap

    def import_last_frame_from_device(self):
        print("Device is running : getting last frame")
        return self.read_remote_frame("/home/matthieu/tmp/last_frame.jpg")

    def acquire_new_frame(self, s):
        command = 'picam -o /home/matthieu/tmp/preview.jpg -v -t 0 -avg %d -ti %f -q %d -ss %d -br %d -iso %d' % \
                  (s.averaging, s.time_interval, s.jpg_quality, s.shutter_speed, s.brightness, s.iso)

        stdin, stdout, stderr = self.ssh.exec_command(command, get_pty=True)
        for line in iter(stdout.readline, ""):
            print(line, end="")

        return self.read_remote_frame("/home/matthieu/tmp/preview.jpg")

    def record(self, s):
        dt = datetime.now()


        folder_created = False
        print(self.name)
        if self.is_running:
            print("WARNING : Device %s is already running. Recording ignored")
        else:

            # Create the new parent folder
            if not folder_created:
                new_folder_name = "/home/matthieu/NAS/PIWORM/%s" % dt.strftime('%Y%m%d')
                stdin, stdout, stderr = self.ssh.exec_command("mkdir " + new_folder_name, get_pty=True)
                if stdout.readline() == '':
                    print(new_folder_name + " created")
                    folder_created = True
                else:
                    for line in iter(stdout.readline, ""):
                        print(line, end="")
                    # raise Exception(stdout.readline())
            # nohup ./test_job.sh > test_job_log.out 2>&1 &

            # create the new child folder
            new_folder_name_child = new_folder_name + "/" + self.name
            stdin, stdout, stderr = self.ssh.exec_command("mkdir " + new_folder_name_child, get_pty=True)
            if stdout.readline() == '':
                print(new_folder_name_child + " created")
            else:
                for line in iter(stdout.readline, ""):
                    print(line, end="")
                # raise Exception(stdout.readline())
            rec_command = f'picam ' \
                          f'--timeout {s.timeout} ' \
                          f'--time-interval {s.time_interval} ' \
                          f'--average {s.averaging} ' \
                          f'--quality {s.jpg_quality} ' \
                          f'--iso {s.iso} ' \
                          f'--shutter-speed {s.shutter_speed} ' \
                          f'--brightness {s.brightness} ' \
                          f'--compress {s.compress} ' \
                          f'--start-frame {s.start_frame} ' \
                          f'--output {new_folder_name_child}/%0{int(ceil(log10(s.timeout)))}d.jpg ' \
                          f'--save-nfo'
            # rec_command = "picam --help"
            command = "nohup %s > %s/log.out 2<&1 &" % (rec_command, new_folder_name_child)

            print(command)
            stdin, stdout, stderr = self.ssh.exec_command(command, get_pty=True)

    def stop(self):
        stdin, stdout, stderr = self.ssh.exec_command("pkill picam", get_pty=True)
        print("Device %s stopped" % self.name)

    def shutdown(self):
        print("shutting down %s" % self.name)
        stdin, stdout, stderr = self.ssh.exec_command("sudo poweroff", get_pty=True)
        del self

