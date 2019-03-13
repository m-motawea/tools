from parsers import ThreadedXLSXParser
from ssh_tools import ping
from ssh_tools import SSHConnection
from threading import Thread


def validate_hosts(hosts=[]):
    print("starting batch: {}".format(hosts))
    for host in result:
        res, msg = ping(host['ip_address'])
        if res:
            print('ping {} successful'.format(host['ip_address']))
        else:
            print('ping {} failed. {}'.format(host['ip_address'], msg))

        con = SSHConnection(host['ip_address'])
        res, msg = con.test_password_login(username=host['username'], password=host['password'], timeout=2)
        if res:
            print('login successful {}'.format(host['ip_address']))
            res, msg = con.test_switch_root(host['password'], sudo=True)
            if res:
                print('switch root success using sudo {}'.format(host['ip_address']))
            else:
                print('switchroot failed using sudo {}.\n{}'.format(host['ip_address'], msg))
        else:
            print('login {} failed. {}'.format(host['ip_address'], msg))




if __name__ == "__main__":
    parser = ThreadedXLSXParser(tab_names=['hosts'], keys=['ip_address', 'password', 'key_path', 'username', 'id'], no_threads=4)
    result = parser.parse('Test.xlsx')
    print("parsing finished. {} hosts.".format(len(result)))
    print("result: \n")

    threads = []
    no_threads = 4
    add_hosts = len(result) % no_threads
    no_hosts = len(result) - add_hosts
    step = int(no_hosts / no_threads)
    for i in range(0, no_hosts, step):
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
    while not end:
        end = True
        for thread in threads:
            if thread.is_alive():
                end = False


