from subprocess import Popen, PIPE

def ping(ip, number=1):
    process = Popen(['ping', '-n', str(number), ip], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr or 'TTL' not in stdout.decode():
        return False, stdout
    else:
        return True, stdout