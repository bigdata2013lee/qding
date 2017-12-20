#coding=gb2312

from ctypes import *
import json
import sys
import signal

import re
from SimpleWebSocketServer import SimpleSSLWebSocketServer, SimpleWebSocketServer, WebSocket

# card_reader = cdll.LoadLibrary('libs/QDCardReader2.dll')
card_reader = None

clients = []

class Service(object):

    def read_card(self):
        str_buffer = create_string_buffer(20)
        card_reader.readeCard(str_buffer, 20)
        result = str_buffer.raw

        # 删除buff中空字节
        result = "".join(re.findall("\w+", result))
        return result

    def write_card(self, str_data=""):
        data = create_string_buffer(str_data)
        result = card_reader.writeCard(data)
        return result


class SimpleWS(WebSocket):

    def handleMessage(self):

        #print self.data
        json_result=""
        try:
            json_result = self.handleReq()
            json_result = json.dumps(json_result).decode("utf-8")
        except Exception, e:
            print e.message
            return

        self.sendMessage(json_result)

    def handleConnected(self):
        print self.address, 'connected'
        clients.append(self)



    def handleClose(self):
        print self.address, 'closed'
        clients.remove(self)

    def handleReq(self):
        service = Service()
        pdata = json.loads(self.data)
        method_name = pdata.get("method", "")
        method_params = pdata.get("params", {})
        method = getattr(service, method_name, None)

        #print method
        if not method:
            return {'invoke': "error", 'result': "No method"}

        result = method(**method_params)

        return {'invoke': method_name, 'result': result}



if __name__== '__main__':

    server = SimpleWebSocketServer('', 8777, SimpleWS)
    # server = SimpleSSLWebSocketServer('', 8777, SimpleWS, 'libs/server.crt', 'libs/server.key')
    print "QDing TX Card Reader Start Up !"

    def close_sig_handler(signal, frame):
        server.close()
        sys.exit()


    signal.signal(signal.SIGINT, close_sig_handler)
    server.serveforever()
