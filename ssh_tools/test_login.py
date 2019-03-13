import paramiko
import time


class SSHConnection:
    def __init__(self, ip):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ip = ip


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
            # wait for prompt
            prompt_flag = False
            while not prompt_flag:
                #time.sleep(1)
                rcv = channel.recv(1024).decode()
                prompt_flag = "Password:" in rcv or "sudo" in rcv
                if not prompt_flag:
                    time.sleep(1)
            channel.send("%s\n" % password)
            #time.sleep(1)
            rcv = channel.recv(1024).decode()
            channel.send("whoami\n")
            time.sleep(1)
            rcv = channel.recv(1024).decode()

            if "root" in rcv:
                return True, None
            else:
                return False, rcv
        except Exception as e:
            return None, e

    def __del__(self):
        self.ssh.close()