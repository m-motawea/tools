from parsers.xlsx_parser import XLSXParser, ThreadedXLSXParser
from ssh_tools.test_ping import ping
from ssh_tools.test_login import SSHConnection


#parser = XLSXParser(tab_names=['hosts'], keys=['ip_address', 'password', 'key_path', 'username'])

parser = ThreadedXLSXParser(tab_names=['hosts'], keys=['ip_address', 'password', 'key_path', 'username'], no_threads=2)

result = parser.parse('Test.xlsx')

for host in result:
    res, msg = ping(host['ip_address'])
    if res:
        print('ping {} successful'.format(host['ip_address']))
    else:
        print('ping {} failed. {}'.format(host['ip_address'], msg))


for host in result:
    con = SSHConnection(host['ip_address'])
    res, msg = con.test_password_login(username=host['username'], password=host['password'])
    if res:
        print('login successful {}'.format(host['ip_address']))
        res, msg = con.test_switch_root(host['password'], sudo=True)
        if res:
            print('switch root success using sudo {}'.format(host['ip_address']))
        else:
            print('switchroot failed using sudo {}'.format(host['ip_address']))
    else:
        print('login {} failed. {}'.format(host['ip_address'], msg))
