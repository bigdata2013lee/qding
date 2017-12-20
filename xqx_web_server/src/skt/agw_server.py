import asyncio
import logging
import os
import ssl

import time

from .protocol import AlarmGatewayProtocol
log = logging.getLogger("skt")

dir_path = os.path.dirname(__file__)
"""
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(certfile=os.path.join(dir_path, "ssl/qd_talk_cert.pem"),
                        keyfile=os.path.join(dir_path, "ssl/qd_talk_key.pem"))
"""
context = None
port = 9555
transport_timeout = 30
check_interval = int(transport_timeout/2)


def _clear_timeout_transport():
    """
    清除一段时间内没有与服务器交互的连接
    1. 前提->要求客户端主动关闭连接
    """
    now = int(time.time())
    _clients = []

    for client in AlarmGatewayProtocol.clients:
        if now - client._last_received_at >= transport_timeout: _clients.append(client)

    log.debug("All Clients:%d, Timeout Clients:%d", len(AlarmGatewayProtocol.clients), len(_clients))

    for client in _clients:
        client.close()
        try:
            AlarmGatewayProtocol.clients.remove(client)
        except Exception as e:
            pass


def clear_timeout_transport_task(loop):
    """模拟定时任务"""
    _clear_timeout_transport()
    loop.call_later(check_interval, clear_timeout_transport_task, loop)


def start_skt_server():
    """启动服务器"""
    loop = asyncio.get_event_loop()

    loop.call_later(check_interval, clear_timeout_transport_task, loop)

    # Each client connection will create a new protocol instance
    coro = loop.create_server(AlarmGatewayProtocol, '0.0.0.0', port, backlog=500, ssl=context)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    log.info('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

if __name__ == '__main__':
    start_skt_server()
