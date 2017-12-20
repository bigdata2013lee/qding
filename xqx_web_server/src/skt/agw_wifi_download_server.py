# coding=utf-8

import asyncio
import ctypes
import logging
import struct

import time

from apis.upgrade import AgwUpgradeApi

log = logging.getLogger("wifi_skt")

host = '0.0.0.0'
port = 9556
header_flg = b'\xf1\xf2\xf3\xf4\xe1\xe2\xe3\xe4'

class DownloadProtocol(asyncio.Protocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log.debug('Connection from {}'.format(peername))
        self.transport = transport

    def error_received(self, exc):
        log.debug('Error received:%s', exc)
        self.transport.close()

    def data_received(self, data):
        log.debug("data_received")
        if not data or data != header_flg:
            log.debug("error header flg")
            self.transport.close()
            return

        try:
            self._download()

        except Exception as e:
            log.exception(e)

        finally:
            self.transport.close()

    def _download(self):
        """
        下载数据
        :return:
        """
        log.debug("exec _download")
        file_data = b''
        try:
            file_data = AgwUpgradeApi._get_wifi_last_version_file_bytes()
        except Exception as e:
            log.exception(e)

        if not file_data:
            log.debug("Not found wifi upgrade file.")

        chksum, fsize = self._file_data_checksum(file_data), len(file_data)
        t3 = time.time()

        # send chksum + padding 0 + fsize
        # 低位在前
        head_data = struct.pack("=LLL", chksum, 0, fsize)
        log.debug("chksum:%s, fsize:%s, head_data:%s", chksum, fsize, head_data)
        self.transport.write(head_data)

        for chunk in self._download_chunks(file_data, buf_size=512):
            self.transport.write(chunk)


    def _download_chunks(self, file_data=b'', buf_size=512):
        offset, file_size = 0, len(file_data)
        while offset < file_size:
            yield file_data[offset:offset+buf_size]
            offset += buf_size

    def _file_data_checksum(self, file_data=b''):
        sum = ctypes.c_uint32(0)
        for b in file_data: sum.value += b
        return sum.value

    def connection_lost(self, exc):
        log.debug('The server/client closed the connection')
        self.transport.close()


def start_skt_server():

    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    coro = loop.create_server(DownloadProtocol, host, port)
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
