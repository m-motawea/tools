from parsers.xlsx_parser import XLSXParser
from ssh_tools.test_ping import ping
from ssh_tools.test_login import SSHConnection


parser = XLSXParser(tab_names=['hosts'], keys_list=['ip address', 'password', 'key_path', 'username'])

result = parser.parse('file.xlsx')

for host in result:
    res, msg = ping(host['ip address'])
    if res:
        print('ping {} successful'.format(host['ip_address']))
    else:
        print('ping {} failed. {}'.format(host['ip address'], msg))


for host in result:
    con = SSHConnection(host['ip address'])
    res, msg = con.test_password_login(username=host['username'], password=host['password'])
    if res:
        print('login successful {}'.format(host['ip address']))
    else:
        print('login {} failed. {}'.format(host['ip address'], msg))
