import paramiko
import time

import glanceclient.client
class SSHConnection:
    def __init__(self, ip):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ip = ip
        self.root_channel = None


    def test_password_login(self, username, password, timeout=5):
        try:
            self.ssh.connect(hostname=self.ip, username=username, password=password, timeout=timeout,  look_for_keys=False, allow_agent=False)
        except Exception as e:
            return False, e.__repr__()

        else:
            return True, None


    def test_key_login(self, username, key_path, passphrase=None, timeout=5):
        try:
            self.ssh.connect(hostname=self.ip, username=username, key_filename=key_path, passphrase=passphrase, timeout=timeout)
        except Exception as e:
            return False, e.__repr__()

        else:
            return True, None


    def test_switch_root(self, password, sudo=False):
        try:
            if sudo:
                cmd = 'sudo su -\n'
            else:
                cmd = 'su -\n'

            channel = self.ssh.invoke_shell()
            channel.send(cmd)
            while not channel.recv_ready():
                print('waiting for password ready')
                pass
            channel.send("%s\n" % password)
            #time.sleep(1)
            rcv = channel.recv(1024).decode()
            channel.send("whoami\n")
            time.sleep(1)
            rcv = channel.recv(1024).decode()

            if "root" in rcv:
                self.root_channel = channel
                return True, None
            else:
                return False, rcv
        except Exception as e:
            return None, e

    def exec_as_root(self, main_cmd):
        rcv = ''
        try:
            self.root_channel.send(main_cmd)
            self.root_channel.send("\n")
            while not self.root_channel.recv_ready():
                print('waaiting for read ready')
                pass
            buffer = self.root_channel.recv(1024).decode()
            rcv = buffer
            while self.root_channel.recv_ready():
                buffer = self.root_channel.recv(1024).decode()
                rcv += buffer
            print(rcv)
            return True, rcv
        except Exception as e:
            return None, e

    def __del__(self):
        self.ssh.close()