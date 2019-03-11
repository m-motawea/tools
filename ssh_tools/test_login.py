import paramiko

class SSHConnection:
    def __init__(self, ip):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ip = ip


    def test_password_login(self, username, password):
        try:
            self.ssh.connect(hostname=self.ip, username=username, password=password)
        except Exception as e:
            return False, e.__repr__()

        else:
            return True, None


    def test_key_login(self, username, key_path, passphrase=None):
        try:
            self.ssh.connect(hostname=self.ip, username=username, key_filename=key_path, passphrase=passphrase)
        except Exception as e:
            return False, e.__repr__()

        else:
            return True, None


    def test_switch_root(self, password, sudo=False):
        if sudo:
            cmd = 'sudo su -'
        else:
            cmd = 'su -'
        chan = self.ssh.exec_command(command=cmd, get_pty=True)
        chan.send(password)
        chan.send("\n")
        stderr = chan.recv_stderr()
        if stderr:
            return False, stderr
        else:
            return True, None

    def __del__(self):
        self.ssh.close()