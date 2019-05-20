from parsers import ThreadedXLSXParser
from ssh_tools import ping
from ssh_tools import SSHConnection
from threading import Thread
import json
import datetime


def validate_hosts(hosts=[]):
    for host in result:
        host["ping"] = {"state": None, "msg": None}
        host["ssh"] = {"login": {"state": None, "msg": None}, "root_sw": {"state": None, "msg": None}}
        res, msg = ping(host['ip'])
        if res:
            host["ping"]["state"] = True
            print('ping {} successful'.format(host['ip']))
        else:
            host["ping"]["state"] = False
            host["ping"]["msg"] = msg
            print('ping {} failed. {}'.format(host['ip'], msg))
        con = SSHConnection(host['ip'])
        res, msg = con.test_password_login(username=host['username'], password=host['password'], timeout=5)
        #res, msg = con.test_key_login(username=host['username'], timeout=5, key_path='id_rsa.pri')
        if res:
            host["ssh"]["login"]["state"] = True
            print('login successful {}'.format(host['ip']))
            res, msg = con.test_switch_root(host['password'], sudo=True)
            if res:
                cmd = "ls /home -R"
                success, exec_result = con.exec_as_root(cmd)
                host['exec'] = {cmd: {'state': success, 'msg': exec_result}}
                host["ssh"]["root_sw"]["state"] = True
                print('switch root success using sudo {}'.format(host['ip']))
            else:
                host["ssh"]["root_sw"]["state"] = False
                host["ssh"]["root_sw"]["msg"] = msg
                print('switchroot failed using sudo {}.\n{}'.format(host['ip'], msg))
        else:
            host["ssh"]["login"]["state"] = False
            host["ssh"]["login"]["msg"] = msg
            print('login {} failed. {}'.format(host['ip'], msg))




if __name__ == "__main__":
    # parse the file,
    parser = ThreadedXLSXParser(tab_names=['hosts'], keys=['ip', 'password', 'username'], no_threads=1)
    result = parser.parse('Test.xlsx')
    print("parsing finished. {} hosts.".format(len(result)))
    print("result: \n")

    # Starting to validate the Hosts.
    # Initlize Thread list
    threads = []
    # Define number of Threads, one thread is used for at least one host, no of threads <= no of hosts.
    '''
    Threads Methodology:
    1- Each thread will have the same number of hosts to check
    2- if the number of hosts is not dividable over the number of threads, a seperate threat will be created for the reminders
    e.g: Hosts=17 , threads= 3  , result: 3 threads with 5 Hosts, + 1 Thread with 2 Hosts'''
    no_threads = 1

    if no_threads == 1:
        validate_hosts(result)
    else:
        no_hosts = len(result)
        add_hosts = no_hosts % no_threads
        dividable_no_hosts = no_hosts - add_hosts
        step = int(dividable_no_hosts / no_threads)
        for i in range(0, dividable_no_hosts, step):
            batch = result[i:i+step]
            t = Thread(target=validate_hosts, args=[batch], daemon=True)
            t.start()
            threads.append(t)
        if add_hosts:
            batch = result[-add_hosts:]
            t = Thread(target=validate_hosts, args=[batch], daemon=True)
            t.start()
            threads.append(t)

        end = False
        try:
            while not end:
                end = True
                for thread in threads:
                    if thread.is_alive():
                        end = False
        except KeyboardInterrupt:
            pass
    print("-----------------------------------------------------------------------")
    print("result: \n{}".format(json.dumps(result, default=str)))
    with open('result.json', "w") as log:
        json.dump(result, log, default=str, indent=4)


