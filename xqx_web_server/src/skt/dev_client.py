#coding=utf-8

import ssl
import socket
import time



HOST = 'www.dudulive.cn'    # The remote host
PORT = 9555              # The same port as used by the server

def send_data(data):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    # s = ssl.wrap_socket(s, ca_certs="ssl/qd_talk_cert.pem", cert_reqs=ssl.CERT_REQUIRED)
    s.connect((HOST, PORT))

    #time.sleep(3)
    s.sendall(data)

    _data = s.recv(1024)
    print('Received:', repr(_data))



def get_alarm_settings():
    dd = b'\xa5\xa5ZZm\x00\x00\x00\x02\x06\x02`\x00004a00314b33570b2034353257ff2e3a7ff63b1661dd0fbf\x00\x00\x00\x00\x00\x00\x00\x001234567890\x00\x00\x00\x00\x00\x000.1\x00\x00\x00\x00\x000.1\x00\x00\x00\x00\x000.1\x00\x00\x00\x00\x00'

    send_data(dd)


def report_alarm():
    dd3= b'\xa5\xa5ZZs\x00\x00\x00\x03\x06\x02`\x000037002247335714203634371-2-3-4-5-6-7-8-9-10-11-12-13-141234567890\x00\x00\x00\x00\x00\x000.1\x00\x00\x00\x00\x000.1\x00\x00\x00\x00\x000.1\x00\x00\x00\x00\x00\x05\x01\x02\x00\x01\x02'

    send_data(dd3)

if __name__ == "__main__":
    get_alarm_settings()