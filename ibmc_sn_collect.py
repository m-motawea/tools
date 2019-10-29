"""
Author: Maged Motawea
Email: magedmotawea@gmail.com
Description: Collect serial numbers of Huawei servers through iBMC.
Usage: ./ibmc_sn_collect.py <path to template> (-P)
Options:
    -P: used to expect login banner for changing the password
Template Format:
    Hostname1 IP1 Username1 Password1
    Hostname2 IP2 Username2 Password2
"""


import paramiko
import json
import sys

if len(sys.argv) > 1:
    TEMPLATE_PATH = sys.argv[1]
else:
    TEMPLATE_PATH = "./ibmc_template"

if "-P" in sys.argv:
    EXCPECT = True
else:
    EXCPECT = False

def parse_template(path="./ibmc_template"):
    hosts_info = []
    with open(path, "r") as template:
        for line in template.readlines():
            if not line:
                continue
            com = line.split()
            if len(com) < 4:
                print("failed to read the ibmc template. error line: {}".format(line))
                exit()

            hosts_info.append({
                "hostname": com[0],
                "ip": com[1],
                "username": com[2],
                "password": com[3]
            })
    return hosts_info


def shell_wait_ready(shell):
    while True:
        if shell.recv_ready():
            break

def shell_exec_cmd(shell, cmd):
    output = ""
    shell.settimeout(2)
    shell.send(cmd + "\n")
    shell_wait_ready(shell)
    buffer = shell.recv(1024).decode()
    while buffer:
        print(buffer)
        output += str(buffer)
        try:
            buffer = shell.recv(1024).decode()
        except:
            buffer = None
    return output


def get_connection(host_dict):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host_dict["ip"], username=host_dict["username"], password=host_dict["password"])
    return ssh


def get_serial_number_by_connection(connection):
    stdin, stdout, stderr = connection.exec_command("ipmcget -d serialnumber")
    stdin.close()
    err = stderr.read()
    out = stdout.read().decode()
    stderr.close()
    stdout.close()
    if err:
        print("failed to get serial number. stderr: {}".format(err))
        return None
    parsed_out = out.split("System SN is:")
    if len(parsed_out) > 1:
        serial_number = parsed_out[-1]
    else:
        serial_number = parsed_out[0]
    return serial_number

def get_serial_number_by_shell(shell):
    buffer = shell_exec_cmd(shell, "ipmcget -d serialnumber")
    paresed_lines = buffer.split("System SN is:")
    if len(paresed_lines) > 1:
        serial_number = paresed_lines[-1].split("\n")[0]
    else:
        serial_number = paresed_lines[0].split("\n")[0]

    return serial_number


def main():
    hosts = parse_template(TEMPLATE_PATH)
    for host_dict in hosts:
        print("collecting host: {}, ip: {}".format(host_dict["hostname"], host_dict["ip"]))
        try:
            print("connecting...")
            conn = get_connection(host_dict)
            print("connected")
            if EXCPECT:
                shell = conn.invoke_shell()
                shell_exec_cmd(shell, "N")
                serial_number = get_serial_number_by_shell(shell)
            else:
                serial_number = get_serial_number_by_connection(conn)
        except Exception as e:
            print("exception occured: {}".format(str(e)))
            host_dict["success"] = False
            host_dict["Error"] = str(e)
            continue
        print("host: {}, SN: {}".format(host_dict["hostname"], serial_number))
        host_dict["success"] = True
        host_dict["SN"] = serial_number

    with open("result", "w") as result:
        json.dump(hosts, result, indent=4)

if __name__ == "__main__":
    print("collecting Serial Numbers")
    try:
        main()
    except Exception as e:
        print(str(e))
    print("finished. press enter to exit")
    input()
