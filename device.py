import paramiko

class Device:

    def __init__(self, name, id, uptodate=None):
        self.name = name
        self.id = id
        self.uptodate = uptodate

        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()

        self.is_running = None

    def ssh_connect(self):
        #if self.ssh:
        #    self.ssh.close()
        self.ssh.connect(self.name, port=22, username='matthieu', timeout=3)
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())