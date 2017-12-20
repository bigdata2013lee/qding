# coding=utf-8
import datetime
from mongoengine import *
from models.base import QdModelMixin


class BellDevice(QdModelMixin, Document):
    """门铃设备"""
    sn = StringField(default="", unique=True)
    outer_device_sn_list = ListField(default=[])
    app_list = ListField(default=[])  # {"app_id":"", "app_name":"qding"}
    heartbeat = DictField(default={"at": datetime.datetime.now, "status": 'down'})
