# coding=utf8
import datetime
import logging

from apis.base import BaseApi
from models.bell import BellDevice
from utils.tools import get_default_result

log = logging.getLogger('django')

__doc__ = """
家门卫士设备 与服务器交互
"""


class BellApi(BaseApi):

    def heartbeat(self, device_sn):
        result = get_default_result()
        dev = BellDevice.objects(sn=device_sn).first()
        if not dev:return result

        dev.heartbeat = {"at": datetime.datetime.now(), "status": 'up'}
        dev.saveEx()

        return result

