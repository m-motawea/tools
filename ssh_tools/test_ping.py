from subprocess import Popen, PIPE

def ping(ip, number=1):
    process = Popen(['ping', '-n', number, ip], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        return False, stderr
    else:
        return True, stdout