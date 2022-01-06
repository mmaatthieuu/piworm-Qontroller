from PyQt5 import QtGui, QtCore
import paramiko

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

    def ssh_connect(self):
        #if self.ssh:
        #    self.ssh.close()
        self.ssh.load_system_host_keys()
        self.ssh.connect(self.name, port=22, username='matthieu', timeout=3)
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())



    def get_frame(self):
        if self.is_running:
            return self.import_last_frame_from_device()
        else:
            return self.acquire_new_frame()

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

    def acquire_new_frame(self):
        command = 'picam -o /home/matthieu/tmp/preview.jpg -v -t 1 -avg %d -ti 0 -q 90 -ss %d -br %d' % \
                  (5, 0, 50)

        stdin, stdout, stderr = self.ssh.exec_command(command, get_pty=True)
        for line in iter(stdout.readline, ""):
            print(line, end="")

        return self.read_remote_frame("/home/matthieu/tmp/preview.jpg")
"""

    def get_frame(self):




        # time.sleep(4)
        # out = stdout.read()
        # for line in stdout.readlines():
        #     print(line, end="")
        # print("Changing image to %s" % preview_file)
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(preview_file, frame_width, -1, True)
        except gi.repository.GLib.Error as e:
            print(e)
            print("The NAS is probably not mounted...")

"""