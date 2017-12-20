# coding=utf-8

import datetime
from mongoengine import *

from models.base import QdModelMixin
from models.aptm import Project
from utils import tools


class AlarmArea(EmbeddedDocument):
    """
    防区
    """

    alarm_id = IntField(default=1)  # 报警器端口
    alarm_type = IntField(default=1)  # 报警类型
    conn_type = IntField(default=1)  # 连接方式 1-常开, 0-常闭

    enable = BooleanField(default=True)  # 布撤防
    loc_name = StringField(default="")  # 位置

    delay_enable_ts = IntField(default=0)  # 布防延时
    delay_alarm_ts = IntField(default=0)  # 报警延时

    @classmethod
    def make_from_dict(cls, infos={}):
        alarm_id = infos.get("alarm_id", "")
        alarm_type = infos.get("alarm_type", "")
        conn_type = infos.get("conn_type", "open")
        enable = infos.get("enable", True)
        loc_name = infos.get("loc_name", "")

        delay_enable_ts = infos.get("delay_enable_ts", 0)
        delay_alarm_ts = infos.get("delay_alarm_ts", 0)

        if alarm_id not in [1, 2, 3, 4, 5, 6]:
            raise Exception("参数[alarm_id]异常")

        if alarm_type not in [1, 2, 3, 4, 5, 6]:
            raise Exception("参数[alarm_type]异常")

        if conn_type not in [0, 1]:
            raise Exception("参数[conn_type]异常")

        alarm_area = AlarmArea(alarm_id=alarm_id, alarm_type=alarm_type, conn_type=conn_type, enable=enable,
                               loc_name=loc_name, delay_enable_ts=delay_enable_ts, delay_alarm_ts=delay_alarm_ts)
        return alarm_area


class AlarmGateway(QdModelMixin, Document):
    """
    报警网关设备
    """

    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField('Project')  # 项目
    aptm = ReferenceField('Room')  # 房间
    aptm_uuid = StringField(default="")

    dev_uid = StringField(default="", unique=True)  # 硬件识别的唯一编号
    sn = StringField(default="")
    mac = StringField(default="", unique=True)
    net = StringField(default="Wi-Fi")

    sw_version = StringField(default="")  # 软件版本
    hw_version = StringField(default="")  # 硬件版本
    res_version = StringField(default="")  # 资源版本
    wifi_version = StringField(default="")  # wifi版本

    heartbeat = DictField(default={'status': 'up', 'at': datetime.datetime.now()}) # 心跳

    alarm_areas_version = IntField(default=0)  # 防区版本序号
    alarm_areas = ListField(EmbeddedDocumentField(AlarmArea), default=[])  # 防区

    meta = {
        "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "aptm", "aptm_uuid", "$aptm_uuid", "sn"
        ]
    }

    def get_alarm_area(self, alarm_id):

        for alarm_area in self.alarm_areas:
            if alarm_area.alarm_id == alarm_id: return alarm_area
        return None

    def clear_aptm_infos(self):
        self.aptm = None
        self.project = None
        self.saveEx()

    def outputEx(self, inculde_fields=[], exculde_fields=["source_data_info"], ex_fun=None):
        obj = self.to_python(inculde_fields=inculde_fields, exculde_fields=exculde_fields)
        obj["aptm_pre_names"] = ["", "", ""]
        obj["aptm_name"] = ""

        if ex_fun: ex_fun(self, obj)
        if self.aptm:
            obj["aptm_pre_names"] = self.aptm.get_aptm_pre_names()
            obj["aptm_name"] = self.aptm.name

        return obj


class AioManager(QdModelMixin, Document):
    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField('Project')  # 社区项目
    dev_uuid = StringField(default="0-0-0-0-0-0-0")   # 硬件识别的唯一编号
    sort_id = StringField(default="00" * 8)
    sn = StringField(default="")
    heartbeat = DictField(default={'status': 'up', 'at': datetime.datetime.now()})
    versions = DictField(default={})  # 版本号
    label = StringField(default="")  # 标签描述
    dpassword = StringField(default="")  # 动态密码

    meta = {
        "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "sn"
        ]
    }

    @classmethod
    def create_inst(cls, dev_uuid, label=""):
        inst = cls(dev_uuid=dev_uuid)
        dev_codes = tools.parse_device_uuid(dev_uuid)
        inst.label = label
        inst.name = "{1}期{6}号".format(*dev_codes)
        inst.sort_id = "{0:0>2}{1:0>2}{2:0>2}{3:0>2}{4:0>2}{5:0>2}{5:0>2}{6:0>2}".format(*dev_codes)
        return inst



class Gate(QdModelMixin, Document):
    """
    门
    """
    cls_desc_name = '门机'

    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField('Project')  # 社区项目
    dev_uuid = StringField(default="0-0-0-0-0-0-0")  # 类型-期-栋-单元-楼层-房间-序号
    sort_id = StringField(default="00" * 8)
    sn = StringField(default="", unique=True)
    label = StringField(default="")      # 标签描述

    heartbeat = DictField(default={"at": datetime.datetime(2000, 1, 1), "status": "down"})  # 设备在线状态
    versions = DictField(default={})  # 版本号

    dpassword = StringField(default="")  # 动态密码
    pass_password = StringField(default="")  # 物业通行密码

    # 门口开关状态
    lock = DictField(default={
        "last_open_at": datetime.datetime(2000, 1, 1),
        "last_closed_at": datetime.datetime(2000, 1, 1),
        "is_locked": False
    })


    meta = {
        "strict": False, 'allow_inheritance': True, 'index_background': True,
        "indexes": [
            "domain", "project", "sn"
        ]
    }

    def get_title(self):
        return "{0} {1}".format(self.cls_desc_name, self.name)

    def update_lock_status(self, is_locked=False):
        if is_locked:
            self.lock["last_closed_at"] = datetime.datetime.now()
            self.lock["is_locked"] = True
        else:
            self.lock["last_open_at"] = datetime.datetime.now()
            self.lock["is_locked"] = False

        self.saveEx()




class UnitGate(Gate):
    """ 单元门口机
    """
    cls_desc_name = '单元门'
    meta = {'allow_inheritance': True, "strict": False}

    @classmethod
    def create_inst(cls, dev_uuid, label=""):
        inst = cls(dev_uuid=dev_uuid)
        dev_codes = tools.parse_device_uuid(dev_uuid)
        inst.label = label
        inst.name = "{1}期{2}栋{3}单元{4}层{6}号".format(*dev_codes)
        inst.sort_id = "{0:0>2}{1:0>2}{2:0>2}{3:0>2}{4:0>2}{5:0>2}{5:0>2}{6:0>2}".format(*dev_codes)
        return inst


class FenceGate(Gate):
    """ 围墙机
    """
    cls_desc_name = '围墙门'
    meta = {'allow_inheritance': True, "strict": False}

    @classmethod
    def create_inst(cls, dev_uuid, label=""):
        inst = cls(dev_uuid=dev_uuid)
        dev_codes = tools.parse_device_uuid(dev_uuid)
        inst.label = label

        inst.name = "{1}期{6}号".format(*dev_codes)
        inst.sort_id = "{0:0>2}{1:0>2}{2:0>2}{3:0>2}{4:0>2}{5:0>2}{5:0>2}{6:0>2}".format(*dev_codes)
        return inst




