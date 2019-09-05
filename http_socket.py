import socket
import json
​
class HTTPResponse(object):
    def __init__(self, text):
        self.status_code = None
        self._http_text = text
        self.headers = {}
        self.text = ""
​
    def parse(self):
        print(self._http_text)
        lines = self._http_text.split("\n")
        self.status_code = int(lines[0].split(" ")[1])
        print("response status_code: {}".format(self.status_code))
        http_body_start_line = None
​
        # parsing headers
        for i in range(1, len(lines)):
            if lines[i] == "\r":
                http_body_start_line = i + 1
                break
            header = lines[i].split(":")[0]
            value = lines[i].split(header + ":")
            if len(value) > 1:
                value = value[1].replace("\r", "")
            else:
                value = value[0].replace("\r", "")
            self.headers[header] = value
        print("response headers: {}".format(json.dumps(self.headers)))
​
        self.text = "\n".join(lines[http_body_start_line:])
        print("response text: {}".format(self.text))
​
​
​
class Request(object):
    def __init__(self, url, body="", headers={}, accept_size=1500):
        print("====================http_socket_start==================")
        self.url = url
        self.body = body
        self.headers = headers
        self._text = ""
        self.response = None
        self.accept_size = accept_size
​
    def _parse_url(self, url):
        if "https" == self.url[0:5]:
            raise NotImplementedError("HTTPS support is not implemented yet.")
        if "http://" != self.url[0:7]:
            raise TypeError("Unsupported scheme {}".format(self.url[0:6]))
        sock_addr = url[7:]
        sock_port = 80
        if ":" in sock_addr:
            sock_port = int(sock_addr.split(":")[1].split("/")[0])
            sock_addr = sock_addr.split(":" + str(sock_port))[0]
        else:
            sock_addr = sock_addr.split("/")[0]
​
        if len(self.url.split(sock_addr)) > 1:
            location = self.url.split(sock_addr+":"+str(sock_port))[1]
            if not location:
                location = "/"
        else:
            location = "/"
​
        return sock_addr, sock_port, location
​
    def _build_http_text(self, method, host, location, body="", headers={}):
        message = "{} {} HTTP/1.1\n".format(method.upper(), location)
        message += "HOST: {}\n".format(host)
        message += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3\n"
        message += "Accept-Language: en-US,en;q=0.9\n"
        #message += "Accept-Encoding: gzip, deflate, br\n"
        message += "Cache-Control: no-cache\n"
        for header in headers:
            message += "{}: {}\n".format(header, headers[header])
        message += "Content-Length: {}\n\n".format(len(body))
        message += body
​
        return message
​
    def get(self):
        http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr, port, location = self._parse_url(self.url)
        http_sock.connect((addr, port))
        http_text = self._build_http_text("get", addr, location, self.body, self.headers)
        print("request plain text: \n" + http_text)
        http_sock.send(http_text.encode("utf-8"))
        response = http_sock.recv(self.accept_size)
        res = HTTPResponse(response.decode("utf-8"))
        res.parse()
        return res
​
    def put(self):
        http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr, port, location = self._parse_url(self.url)
        http_sock.connect((addr, port))
        http_text = self._build_http_text("put", addr, location, self.body, self.headers)
        print("request plain text: \n" + http_text)
        http_sock.send(http_text.encode("utf-8"))
        response = http_sock.recv(self.accept_size)
        res = HTTPResponse(response.decode("utf-8"))
        res.parse()
        return res
​
    def __del__(self):
        print("====================http_socket_end==================")
​
​
def main():
    req = Request("http://www.google.com:80", body="hello")
    req.put()
​
​
if __name__ == "__main__":
    main()
