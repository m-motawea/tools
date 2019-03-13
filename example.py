from parsers import ThreadedXLSXParser
from ssh_tools import ping
from ssh_tools import SSHConnection



parser = ThreadedXLSXParser(tab_names=['hosts'], keys=['ip_address', 'password', 'key_path', 'username', 'id'], no_threads=4)

result = parser.parse('Test.xlsx')

print("parsing finished. {} hosts.".format(len(result)))
print("result: \n")
for host_dict in result:
    print(host_dict)

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
